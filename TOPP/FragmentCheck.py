# Check identifications for peptide evidence



import glyxtoolms
import re
import sys 



def handle_args(argv=None):
    import argparse
    usage = "\nFile FragmentCheck"
    parser = argparse.ArgumentParser(description=usage)
    parser.add_argument("--in", dest="infile",help="File input Analysis file .xml") 
    parser.add_argument("--out", dest="outfile",help="File output Analysis file")
    parser.add_argument("--checkNeuAc", dest="checkNeuAc",help="Check if oxonium ion NeuAc exists for glycans containing NeuAc")
    parser.add_argument("--existsPepHexNAc", dest="existsPepHexNAc",help="Check if peptide+HexNAc exists")
    parser.add_argument("--tolerance", dest="tolerance",
                        help="Mass tolerance in either Da or ppm",
                        type=float)
    parser.add_argument("--toleranceType", dest="toleranceType",
                        help="Type of the given mass tolerance",
                        choices=["Da", "ppm"])
    
    if not argv:
        args = parser.parse_args(sys.argv[1:])
    else:
        args = parser.parse_args(argv)
    return args

def main(options):
    print "parsing input parameters"
    checkNeuAc = False
    if options.checkNeuAc == "true":
        checkNeuAc = True
    checkPepHexNAc = False
    if options.existsPepHexNAc == "true":
        checkPepHexNAc = True
    
    toleranceType = options.toleranceType
    tolerance = float(options.tolerance)
    
    print "parsing input file"
    glyML = glyxtoolms.io.GlyxXMLFile()
    glyML.readFromFile(options.infile)

    print "scoring fragment spectra"

    keepHits = []
    for hit in glyML.glycoModHits:
        if checkNeuAc == True:
            # check existence of neuac
            ions = set()
            for s in hit.feature.spectra:
                ions = ions.union(set(s.ions.get(None,{}).keys()))

            if hit.glycan.sugar.get("NEUAC",0) > 0:
                if not "(NeuAc)1(H+)1" in ions:
                    continue
        if checkPepHexNAc == True:
            hasPeak = False
            for charge in range(1,hit.feature.getCharge()):
                mass = (hit.peptide.mass+glyxtoolms.masses.GLYCAN["HEXNAC"]+glyxtoolms.masses.MASS["H+"]*charge)/float(charge)
                for p in hit.feature.consensus:
                    error = glyxtoolms.lib.calcMassError(p.x,mass,toleranceType)
                    if abs(error) <= tolerance:
                        hasPeak = True
                        break
                if hasPeak == True:
                    break
            if hasPeak == False:
                continue
        keepHits.append(hit)
    print "keeping " + str(len(keepHits)) + " of " +  str(len(glyML.glycoModHits)) + " identifications"
    glyML.glycoModHits = keepHits
    print "writing output"
    glyML.writeToFile(options.outfile)
    print "done"
    return

if __name__ == "__main__":
    options = handle_args()
    main(options)
