"""
Searches for peptide fragments within the MS2 spectra.
Especially peptide-ion and peptide+HexNAc occurence.
Ions are assumed to be singly charged.

""" 

import sys
import glyxtoolms

def searchMassInSpectrum(mass,tolerance,spectrum):
    intensity = 0
    for peak in spectrum:
        if abs(peak.x - mass) < tolerance:
            intensity += peak.y
    return intensity
    
def calcChargedMass(singlyChargedMass,charge):
    mass = singlyChargedMass+(charge-1)*glyxtoolms.masses.MASS["H"]
    return mass/float(charge)

def main(options):
    
    # parse parameters
    tolerance = float(options.tolerance)
    ionthreshold = float(options.ionthreshold)
    
    # load analysis file
    glyxXMLFile = glyxtoolms.io.GlyxXMLFile()
    glyxXMLFile.readFromFile(options.inGlyML)
    
    scoredSpectra = {}
    for spectrum in glyxXMLFile.spectra:
        scoredSpectra[spectrum.getNativeId()] = spectrum

    keep = []
    for hit in glyxXMLFile.glycoModHits:
        # TODO: handle status settings
        feature = hit.feature
        hit.fragments = {}
        result = glyxtoolms.fragmentation.annotateSpectrumWithFragments(hit.peptide,
                                                                       hit.glycan,
                                                                       feature.consensus, 
                                                                       tolerance, 
                                                                       feature.getCharge())
        peptidevariant = result["peptidevariant"] 
        fragments = result["fragments"]
        # write fragments to hit
        if peptidevariant != None:
            hit.peptide = peptidevariant
            hit.fragments = fragments
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
