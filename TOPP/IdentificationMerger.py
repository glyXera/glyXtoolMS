# Transfer identifications from one analysis file to another - (needed for further analysis on different fragmentation techniques)



import glyxtoolms
import re
import sys 



def handle_args(argv=None):
    import argparse
    usage = "\nFile IdentificationMerger"
    parser = argparse.ArgumentParser(description=usage)
    parser.add_argument("--in1", dest="in1",help="File input Analysis file .xml, containing the identifications") 
    parser.add_argument("--in2", dest="in2",help="File input Analysis file .xml, containing the identifications") 
    parser.add_argument("--out", dest="outfile",help="File output Analysis file")
    
    if not argv:
        args = parser.parse_args(sys.argv[1:])
    else:
        args = parser.parse_args(argv)
    return args

def main(options):
    print "parsing input file 1"
    in1 = glyxtoolms.io.GlyxXMLFile()
    in1.readFromFile(options.in1)

    print "parsing input file 2"
    in2 = glyxtoolms.io.GlyxXMLFile()
    in2.readFromFile(options.in2)
    

    print "merge identifications"
    for value in in1.toolValueDefaults:
        if not value in in2.toolValueDefaults:
            in2.toolValueDefaults[value] = in1.toolValueDefaults[value]

    in2.glycoModHits += in1.glycoModHits

    print "writing output"
    in2.writeToFile(options.outfile)
    print "done"
    return

if __name__ == "__main__":
    options = handle_args()
    main(options)
