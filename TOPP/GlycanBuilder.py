# Tool for building Glycancompositions used in Glycan + Peptide comparison tool

# Range Hex
# Range HexNAc
# Range Fucose
# Range NeuAc

# out: Glycancompositionfile.txt, each line containing one structure

def handle_args(argv=None):
    import argparse
    usage = "\nFile Glycan composition builder"
    parser = argparse.ArgumentParser(description=usage)
    parser.add_argument("--in", dest="infile",help="File input Glycanstructure file .txt")
    parser.add_argument("--out", dest="outfile",help="File output Glycanstructure file .txt")
    parser.add_argument("--useinfile", dest="useinfile",help="Use file input as basis and filter with the given ranges (true)")
    parser.add_argument("--rangeHex", dest="rangeHex",help="Range of Hexoses in the glycan structure min:max")
    parser.add_argument("--rangeHexNAc", dest="rangeHexNAc",help="Range of HexNAc in the glycan structure min:max")
    parser.add_argument("--rangeFuc", dest="rangeDHex",help="Range of Fucose in the glycan structure min:max")
    parser.add_argument("--rangeNeuAc", dest="rangeNeuAc",help="Range of Fucose in the glycan structure min:max")
                
    if not argv:
        args = parser.parse_args(sys.argv[1:])
    else:
        args = parser.parse_args(argv)
    return args

def main(options):
    print "parsing input parameters"
    
    minHex,maxHex = map(int,options.rangeHex.split(":"))
    minHexNAc,maxHexNAc = map(int,options.rangeHexNAc.split(":"))
    minDHex,maxDHex = map(int,options.rangeDHex.split(":"))
    minNeuAc,maxNeuAc = map(int,options.rangeNeuAc.split(":"))
    print minHex,maxHex
    print minHexNAc,maxHexNAc
    print minDHex,maxDHex
    print minNeuAc,maxNeuAc
    
    rangeHex = range(minHex,maxHex+1)
    rangeHexNAc = range(minHexNAc,maxHexNAc+1)
    rangeDHex = range(minDHex,maxDHex+1)
    rangeNeuAc = range(minNeuAc,maxNeuAc+1)
    
    
    
    # open output file
    fout = file(options.outfile,"w")
    if options.useinfile == "true":
        print "checking glycans in file"
        fin = file(options.infile,"r")
        for line in fin:
            glycan = glyxsuite.lib.Glycan(line[:-1])
            if not glycan.checkComposition():
                continue
            
            print minHex,glycan.sugar["HEX"],maxHex
            if not minHex <= glycan.sugar["HEX"] <= maxHex:
                continue
            
            if not minHexNAc <= glycan.sugar["HEXNAC"] <= maxHexNAc:
                continue
            if not minDHex <= glycan.sugar["DHEX"] <= maxDHex:
                continue
            if not minNeuAc <= glycan.sugar["NEUAC"] <= maxNeuAc:
                continue
            if glycan.mass > 8000:
                continue
            
            # write composition to file
            fout.write(glycan.toString() + "\n")
        fin.close()
    else:
        print "generating glycan compositions"
        for NEUAC,DHEX,HEX,HEXNAC in product(
                                        rangeNeuAc,
                                        rangeDHex,
                                        rangeHex,
                                        rangeHexNAc):
            # calc mass
            glycan = glyxsuite.lib.Glycan()
            glycan.setComposition(NEUAC,DHEX,HEX,HEXNAC)
            if not glycan.checkComposition():
                continue
            if glycan.mass > 8000:
                continue
            # write composition to file
            fout.write(glycan.toString() + "\n")
    
    fout.close()

    print "done"
    return
    
    

import sys
import glyxsuite
from itertools import product

if __name__ == "__main__":
    options = handle_args()
    main(options)

