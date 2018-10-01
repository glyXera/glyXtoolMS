# Tool for calculating peptide scores for HCD and ETD fragments

import glyxtoolms
import sys 


def handle_args(argv=None):
    import argparse
    usage = "\nFile GlycanScorer"
    parser = argparse.ArgumentParser(description=usage)
    parser.add_argument("--in", dest="infile",help="File input Analysis file with annotated fragments.xml") 
    parser.add_argument("--out", dest="outfile",help="File output Analysis file with glyca score")
    
    if not argv:
        args = parser.parse_args(sys.argv[1:])
    else:
        args = parser.parse_args(argv)
    return args

def scoreHit(hit):
    glycans = set()
    oxions = set()
    for f in hit.fragments.values():
        isGlyco = False
        isOx = False
        if f.typ == "ISOTOPE":
            for parention in f.parents:
                fp = hit.fragments[parention]
                if fp.typ in ['GLYCOPEPTIDEION', 'PEPTIDEION']:
                    isGlyco = True
                if fp.typ ==  'OXONIUMION':
                    isOx = True
        elif f.typ in ['GLYCOPEPTIDEION', 'PEPTIDEION']:
            isGlyco = True
        elif f.typ ==  'OXONIUMION':
            isOx = True
        if isGlyco == True:
            glycans.add(f.peak)
        if isOx == True:
            oxions.add(f.peak)

    # calc score
    totalCount = 0.0
    oxIonsCount = 0.0
    glycanCount = 0.0

    for p in hit.feature.consensus:
        totalCount += p.y
        if p in glycans:
            glycanCount += p.y
        elif p in oxions:
            oxIonsCount += p.y
    denom = (totalCount-oxIonsCount)
    if denom <= 0:
        return 0.0
    return glycanCount/denom

def main(options):
    print "parsing input file"
    glyML = glyxtoolms.io.GlyxXMLFile()
    glyML.readFromFile(options.infile)
    
    glyML.addToolValueDefault("glycanScore", 0.0)


    print "scoring fragment spectra"
    for hit in glyML.glycoModHits:
        score = scoreHit(hit)
        hit.toolValues["glycanScore"] = score
    glyML.writeToFile(options.outfile)
    print "done"
    return

if __name__ == "__main__":
    options = handle_args()
    main(options)
