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
        foundA = False
        foundB = False
        masslist = []
        for spectrumID in feature.getSpectraIds():
            spectrum = rawSpectra[spectrumID]
            for peak in spectrum:
                masslist.append(peak.getMZ())
                if abs(peak.getMZ()-pepIon) < tolerance:
                    foundA = True
                elif abs(peak.getMZ()-pepGlcNAcIon) < tolerance:
                    foundB = True
        if foundA == False and foundB == False:
            continue
        hit.fragments = {}
        if foundA:
            fragment = {}
            fragment["mass"] = pepIon
            fragment["sequence"] = hit.peptide.sequence
            hit.fragments["peptide"] = fragment
        if foundB:
            fragment = {}
            fragment["mass"] = pepGlcNAcIon
            fragment["sequence"] = hit.peptide.sequence+"+HexNAC"
            hit.fragments["peptide+HexNAc"] = fragment
        # search for peptide fragments
        p = hit.peptide
        fragmenthits = (None,{})
        for i in glyxsuite.fragmentation.getModificationVariants(p):
            
            pepvariant = p.copy()
            pepvariant.modifications = i
            fragments = glyxsuite.fragmentation.generatePeptideFragments(pepvariant)
            fhit = {}
            for fragmentkey in fragments:
                fragmentmass = fragments[fragmentkey][0]
                for mass in masslist:
                    if abs(fragmentmass-mass) < tolerance:
                        fhit[fragmentkey] = fragments[fragmentkey]
                        break

            if len(fhit) > len(fragmenthits[1]):
                fragmenthits = (pepvariant,fhit)
        if fragmenthits[0] is not None:
            pepvariant,fhit = fragmenthits
            
            # write fragments to hit
            hit.peptide = pepvariant
            for fragmentname in fhit:
                fragment = {}
                fragment["mass"] = fhit[fragmentname][0]
                fragment["sequence"] = fhit[fragmentname][1]
                hit.fragments[fragmentname] = fragment
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
