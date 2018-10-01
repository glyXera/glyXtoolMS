# Check identifications for peptide evidence



import glyxtoolms
import re
import sys 



def handle_args(argv=None):
    import argparse
    usage = "\nFile RemoveFeatures"
    parser = argparse.ArgumentParser(description=usage)
    parser.add_argument("--inAnalysis", dest="inAnalysis",help="File input Analysis file .xml")
    parser.add_argument("--inFeatureFile",  nargs='+', dest="inFeatureFile",help="File(s) containing the feature Ids to remove")
    parser.add_argument("--out", dest="outfile",help="File input Analysis file .xml without features from the provided feature list")
    if not argv:
        args = parser.parse_args(sys.argv[1:])
    else:
        args = parser.parse_args(argv)
    return args

def getInputFile(option):
    files = []
    if option:
        for mergepath in option:
            files += mergepath.split(" ")
    return files

def main(options):

    featuresIds = set()
    print "parsing feature list"
    for path in getInputFile(options.inFeatureFile):
        print "parsing features from ", path
        f = file(path,"r")
        for line in f:
            featuresIds.add(line.strip())
        f.close()
        print "list now contains ", len(featuresIds), " features"
    
    print "parsing input file"
    glyML = glyxtoolms.io.GlyxXMLFile()
    glyML.readFromFile(options.inAnalysis)
    remainingHits = []
    remainingFeatures = []
    for hit in glyML.glycoModHits:
        if not str(hit.feature.id) in featuresIds:
            remainingHits.append(hit)
            
    for feature in glyML.features:
        if not str(feature.id) in featuresIds:
            remainingFeatures.append(feature)
    
    print "keeping ", len(remainingFeatures), " remaining features from ", len(glyML.features)
    print "keeping ", len(remainingHits), " remaining identifications from ", len(glyML.glycoModHits)
    
    glyML.features = remainingFeatures
    glyML.glycoModHits = remainingHits
    
    print "writing output"
    glyML.writeToFile(options.outfile)
    print "done"
    return

if __name__ == "__main__":
    options = handle_args()
    main(options)
