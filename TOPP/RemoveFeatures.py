# Check identifications for peptide evidence



import glyxtoolms
import re
import sys 



def handle_args(argv=None):
    import argparse
    usage = "\nFile RemoveFeatures"
    parser = argparse.ArgumentParser(description=usage)
    parser.add_argument("--inAnalysis", dest="inAnalysis",help="File input Analysis file .xml")
    parser.add_argument("--inFeatureFile", dest="inFeatureFile",help="File containing the features to remove")
    parser.add_argument("--out", dest="outfile",help="File containing the features to remove")
    if not argv:
        args = parser.parse_args(sys.argv[1:])
    else:
        args = parser.parse_args(argv)
    return args

def main(options):

    featuresIds = set()
    print "parsing feature list"
    f = file(options.inFeatureFile,"r")
    for line in f:
        featuresIds.add(line.strip())
    f.close()
    
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
