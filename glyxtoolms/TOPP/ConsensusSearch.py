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
    toleranceType = options.toleranceType
    ionthreshold = float(options.ionthreshold)
    pepIons = set(options.pepIons.split(" "))
    print "pepIons", pepIons
    
    # load analysis file
    glyxXMLFile = glyxtoolms.io.GlyxXMLFile()
    glyxXMLFile.readFromFile(options.inGlyML)

    keep = []
    # storage of already calculated fragments
    fragmentProvider = glyxtoolms.fragmentation.FragmentProvider(types=pepIons)
    lenHits = float(len(glyxXMLFile.glycoModHits))
    for i,hit in enumerate(glyxXMLFile.glycoModHits):
        # TODO: handle status settings
        if i%1000 == 0:
            print i/lenHits *100, "%"
        feature = hit.feature
        hit.fragments = {}
        result = fragmentProvider.annotateSpectrumWithFragments(hit.peptide,
                                                                hit.glycan,
                                                                feature.consensus,
                                                                tolerance,
                                                                toleranceType,
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
                        help="Mass tolerance in either Da or ppm",
                        type=float)
    parser.add_argument("--toleranceType", dest="toleranceType",
                        help="Type of the given mass tolerance",
                        choices=["Da", "ppm"])
    parser.add_argument("--ionthreshold", dest="ionthreshold",
                        help="Threshold for peptide ions",
                        type=int)
    parser.add_argument("--pepIons", dest="pepIons",
                        help="Peptide ion types to search")
    if not argv:
        print "parameters", sys.argv[1:]
        args = parser.parse_args(sys.argv[1:])
    else:
        print "parameters", argv
        args = parser.parse_args(argv)
    return args

if __name__ == "__main__":
    main(handle_args())
