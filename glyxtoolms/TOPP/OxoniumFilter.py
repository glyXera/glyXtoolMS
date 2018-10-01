# Tool for calculating peptide scores for HCD and ETD fragments

import glyxtoolms
import sys 


def handle_args(argv=None):
    import argparse
    usage = "\nFile OxoniumFilter"
    parser = argparse.ArgumentParser(description=usage)
    parser.add_argument("--in", dest="infile",help="File input Analysis file with annotated fragments.xml") 
    parser.add_argument("--out", dest="outfile",help="File output Analysis file with filtered glycans")
    parser.add_argument("--threshold", dest="threshold",help="Threshold used for ratio between HexNAc and NeuAc-H2O ion. ")
    
    if not argv:
        args = parser.parse_args(sys.argv[1:])
    else:
        args = parser.parse_args(argv)
    return args



def main(options):
    print "parsing input file"
    glyML = glyxtoolms.io.GlyxXMLFile()
    glyML.readFromFile(options.infile)

    threshold = float(options.threshold)
    keepHits = []
    for hit in glyML.glycoModHits:
        values = []
        for s in hit.feature.spectra:
            for ions in s.ions.values():
                hexnac = 0
                if "(HexNAc)1(H+)1" in ions:
                    hexnac = ions["(HexNAc)1(H+)1"]["intensity"]
                if hexnac == 0:
                    continue
                neuac = 0
                if "(NeuAc)1(H+)1" in ions:
                    neuac = ions["(NeuAc)1(H+)1"]["intensity"]

                neuacH2O = 0
                if "(NeuAc)1(H2O)-1(H+)1" in ions:
                    neuacH2O = ions["(NeuAc)1(H2O)-1(H+)1"]["intensity"]
                
                values.append(neuacH2O/hexnac)
        if len(values) == 0:
            continue
        isValid = True
        if max(values) < threshold and hit.glycan.sugar.get("NEUAC",0) > 0:
            isValid = False
        elif max(values) > threshold and hit.glycan.sugar.get("NEUAC",0) == 0:
            isValid = False
        if isValid == True:
            keepHits.append(hit)

            
    print "keeping " + str(len(keepHits)) + " hits of " + str(len(glyML.glycoModHits))
    glyML.glycoModHits = keepHits

    glyML.writeToFile(options.outfile)
    print "done"
    return

if __name__ == "__main__":
    options = handle_args()
    main(options)
