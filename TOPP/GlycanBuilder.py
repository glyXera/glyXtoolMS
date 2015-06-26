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
    parser.add_argument("--out", dest="outfile",help="File output Glycanstructure file .txt")
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
    
    
    print "generating glycan compositions"
    glycans = []
    for NEUAC,DHEX,HEX,HEXNAC in product(
                                        rangeNeuAc,
                                        rangeDHex,
                                        rangeHex,
                                        rangeHexNAc):
        # The sum of the number of hexose plus HexNAc residues cannot 
        # be zero, i.e., an N-linked glycan contain either a hexose 
        # or a HexNAc residue, or both.
        if HEX+HEXNAC == 0:
            continue
        # The number of fucose residues plus 1 must be less than or 
        # equal to the sum of the number of hexose plus HexNAc residues.
        if DHEX >= HEX+HEXNAC:
            continue
        # If the number of HexNAc residues is less than or equal to 2 
        # and the number of hexose residues is greater than 2, 
        # then the number of NeuAc and NeuGc residues must be zero. 
        if HEXNAC <= 2 and HEX > 2 and NEUAC > 0:
            continue
        # calc mass
        mass = 0
        mass += glyxsuite.masses.GLYCAN["NEUAC"]*NEUAC
        mass += glyxsuite.masses.GLYCAN["DHEX"]*DHEX
        mass += glyxsuite.masses.GLYCAN["HEX"]*HEX
        mass += glyxsuite.masses.GLYCAN["HEXNAC"]*HEXNAC
        if mass > 8000:
            continue
        # write composition to file
        fout.write("DHEX"+str(DHEX)+
                    "HEX"+str(HEX)+
                    "HEXNAC"+str(HEXNAC)+
                    "NEUAC"+str(NEUAC)+"\n")
            
    fout.close()

    print "done"
    return

import sys
import glyxsuite
from itertools import product

if __name__ == "__main__":
    options = handle_args()
    main(options)

