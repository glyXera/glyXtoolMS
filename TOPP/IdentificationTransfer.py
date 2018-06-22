# Transfer identifications from one analysis file to another - (needed for further analysis on different fragmentation techniques)



import glyxtoolms
import re
import sys 



def handle_args(argv=None):
    import argparse
    usage = "\nFile IdentificationTransfer"
    parser = argparse.ArgumentParser(description=usage)
    parser.add_argument("--inIdentifications", dest="inIdentifications",help="File input Analysis file .xml, containing the identifications") 
    parser.add_argument("--inAnalysis", dest="inAnalysis",help="File input Analysis file .xml, containing the new fragmentation data") 
    parser.add_argument("--out", dest="outfile",help="File output Analysis file")
    
    if not argv:
        args = parser.parse_args(sys.argv[1:])
    else:
        args = parser.parse_args(argv)
    return args

def main(options):
    print "parsing input file containing identifications"
    identFile = glyxtoolms.io.GlyxXMLFile()
    identFile.readFromFile(options.inIdentifications)

    print "parsing input file containing identifications"
    newFile = glyxtoolms.io.GlyxXMLFile()
    newFile.readFromFile(options.inAnalysis)
    
    

    print "merge identifications"
    newFile.toolValueDefaults = identFile.toolValueDefaults
    features = {}
    for feat in newFile.features: # switch with etd file
        features[feat.id] = feat

    newHits = []
    for h in identFile.glycoModHits:
        if not h.featureID in features:
            continue
        feat = features[h.featureID]
        h.feature = feat
        h.fragments = {}
        newHits.append(h)

    print "could not transfer " + str(len(identFile.glycoModHits)-len(newHits)) + " of " + str(len(identFile.glycoModHits)) + " identifications"
    
    newFile.glycoModHits = newHits
    print "writing output"
    newFile.writeToFile(options.outfile)
    print "done"
    return

if __name__ == "__main__":
    options = handle_args()
    main(options)
