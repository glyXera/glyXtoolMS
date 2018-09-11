# Tool for calculating peptide scores for HCD and ETD fragments

import glyxtoolms
import sys 


def handle_args(argv=None):
    import argparse
    usage = "\nFile HexNAcRatio\n Calculates the ratio between HexNAc1-H2O(+) and HexNAc1(1+) fragment ions of each identification"
    parser = argparse.ArgumentParser(description=usage)
    parser.add_argument("--in", dest="infile",help="File input Analysis file with annotated fragments.xml") 
    parser.add_argument("--out", dest="outfile",help="File output Analysis file with filtered glycans")
    
    if not argv:
        args = parser.parse_args(sys.argv[1:])
    else:
        args = parser.parse_args(argv)
    return args



def main(options):
    print "parsing input file"
    glyML = glyxtoolms.io.GlyxXMLFile()
    glyML.readFromFile(options.infile)
    glyML.addToolValueDefault("HexNAcRatio", 0.0)
    
    for feat in glyML.features:
        ions = {}
        for s in feat.spectra:
            for key in s.ions:
                for ionname in s.ions[key]:
                    ions[ionname] = ions.get(ionname, 0.0) + s.ions[key][ionname]["intensity"]
        iHexNAc = ions.get("(HexNAc)1(H+)1", 0.0)
        iHexNAcH2O = ions.get("(HexNAc)1(H2O)-1(H+)1", 0.0)
        if iHexNAc <= 0.0:
            value = 0.0
        else:
            value = iHexNAcH2O / iHexNAc
        feat.toolValues["HexNAcRatio"] = round(value,3)
    
    for h in glyML.glycoModHits:
        fHexNAc = h.fragments.get("HexNAc1(1+)",None)
        fHexNAcH2O = None
        for name in ["HexNAc1-H2O(1+)", "HexNAc1-H2O(+)"]:
            if name in h.fragments:
                fHexNAcH2O = h.fragments.get(name, None)
                break
        if fHexNAc == None:
            continue
        if fHexNAcH2O == None:
            continue
        value = fHexNAcH2O.peak.y/fHexNAc.peak.y
        h.toolValues["HexNAcRatio"] = round(value,3)
    glyML.writeToFile(options.outfile)
    print "done"
    return

if __name__ == "__main__":
    options = handle_args()
    main(options)

