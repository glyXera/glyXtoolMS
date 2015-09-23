"""
Searches for peptide fragments within the MS2 spectra.
Especially peptide-ion and peptide+HexNAc occurence.
Ions are assumed to be singly charged.

""" 

import sys
import glyxsuite

def main(options):
    
    # parse parameters
    tolerance = float(options.tolerance)
    ionthreshold = float(options.ionthreshold)
    
    # load analysis file
    glyxXMLFile = glyxsuite.io.GlyxXMLFile()
    glyxXMLFile.readFromFile(options.inGlyML)
    
    # loading mzML file
    exp = glyxsuite.lib.openOpenMSExperiment(options.inMZML)

    rawSpectra = {}
    for spectrum in exp:
        rawSpectra[spectrum.getNativeID()] = spectrum

    features = {}
    for feature in glyxXMLFile.features:
        features[feature.getId()] = feature

    keep = []

    for hit in glyxXMLFile.glycoModHits:

        feature = features[hit.featureID]
            
        pepIon = hit.peptide.mass+glyxsuite.masses.MASS["H+"]
        pepGlcNAcIon = pepIon+glyxsuite.masses.GLYCAN["HEX"]

        # search for hits in spectra
        found = False
        for spectrumID in feature.getSpectraIds():
            spectrum = rawSpectra[spectrumID]
            for peak in spectrum:
                if ionthreshold > 0 and peak.getIntensity() < ionthreshold:
                    continue
                if abs(peak.getMZ()-pepIon) < tolerance:
                    found = True
                    break
                elif abs(peak.getMZ()-pepGlcNAcIon) < tolerance:
                    found = True
                    break
        if found == True:
            keep.append(hit)
    print "keeping " + str(len(keep)) + " glycopeptide hits from " + str(len(glyxXMLFile.glycoModHits))
    glyxXMLFile.glycoModHits = keep

    # write to output
    glyxXMLFile.writeToFile(options.outGlyML)
    print "done" 
    

def handle_args(argv=None):
    """ Handles input arguments """
    import argparse
    usage = "\nSearches for peptide evidence in HCD spectra"
    parser = argparse.ArgumentParser(description=usage)
    parser.add_argument("--inMZML", dest="inMZML",
                        help="mzML file input")
    parser.add_argument("--inGlyML", dest="inGlyML",
                        help="glyML input")
    parser.add_argument("--outGlyML", dest="outGlyML",
                        help="glyML output")
    parser.add_argument("--tolerance", dest="tolerance",
                        help="Mass tolerance in th",
                        type=float)
    parser.add_argument("--ionthreshold", dest="ionthreshold",
                        help="Threshold for peptide ions",
                        type=int)
    if not argv:
        print "parameters", sys.argv[1:]
        args = parser.parse_args(sys.argv[1:])
    else:
        print "parameters", argv
        args = parser.parse_args(argv)
    return args

if __name__ == "__main__":
    main(handle_args())
