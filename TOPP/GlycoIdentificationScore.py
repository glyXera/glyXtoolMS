# Tool for calculating glycopeptide identifications scores



import glyxtoolms
import re
import sys

def calcScore(hit, options):
    keys = hit.fragments.keys()
    # count ions
    y = set()
    b = set()
    pep = False
    pepNH3 = False
    pepHexNAc = False
    for name in keys:
        if re.match("^y\d+(-NH3|-H2O|\+HexNAc)?$", name):
            y.add(re.search("\d+", name).group())
        if re.match("^b\d+(-NH3|-H2O|\+HexNAc)?$", name):
            b.add(re.search("\d+", name).group())
        if name.startswith("peptide+("):
            pep = True
        if name.startswith("peptide-NH3+("):
            pepNH3 = True
        if name.startswith("peptide+HexNAc+("):
            pepHexNAc = True

    # check oxonium ions for glycan moeity
    # collect spectra ion names
    ions = set()
    for s in hit.feature.spectra:
        for i in s.ions.values():
            ions = ions.union(i.keys())
    if hit.glycan.sugar.get("NEUAC",0) > 0:
        scoreNeuAc = (1+("(NeuAc)1(H+)1" in ions))/2.0
    else:
        scoreNeuAc = (1+("(NeuAc)1(H+)1" not in ions))/2.0
    if hit.glycan.sugar.get("DHEX",0) > 0:
        scoreFuc = (1+("(dHex)1(H+)1" in ions) + ("(HexNAc)1(Hex)1(dHex)1(H+)1" in ions))/3.0
    else:
        scoreFuc = (1+("(dHex)1(H+)1" not in ions) + ("(HexNAc)1(Hex)1(dHex)1(H+)1" not in ions))/3.0
    
    # sanitize peptide length
    length = float(len(hit.peptide.sequence))-1
    if length == 0:
        length = 1.0
    
    # calc score
    score = 1.0
    if options.scorePepFrag == "true":
        score = score*(len(y)/length+len(b)/length)/2.0 
    if options.scorePep == "true":
        score = score*(1+pep)/2.0
    if options.scorePepNH3 == "true":
        score = score*(1+pepNH3)/2.0
    if options.scorePepHEXNAC == "true":
        score = score*(1+pepHexNAc)/2.0
    if options.scoreOxonium == "true":
        score = score*scoreNeuAc*scoreFuc
    return score

def handle_args(argv=None):
    import argparse
    usage = "\nFile Glycan composition builder"
    parser = argparse.ArgumentParser(description=usage)
    parser.add_argument("--in", dest="infile",help="File input Analysis file .xml") 
    parser.add_argument("--out", dest="outfile",help="File output Analysis file with scored glycopeptide identifications")
    parser.add_argument("--cutoff", dest="scoreCutoff",help="Remove identifications with score lower than cutoff")
    parser.add_argument("--scoreFrag", dest="scorePepFrag",help="Score y- and b-ion coverage (true/false), not applicable for HCD low")
    parser.add_argument("--scorePep", dest="scorePep",help="Score existence of the peptide ion")
    parser.add_argument("--scorePepNH3", dest="scorePepNH3",help="Score existence of the peptide-NH3 ion")
    parser.add_argument("--scorePepHEXNAC", dest="scorePepHEXNAC",help="Score existence of the peptide+HEXNAC ion")
    parser.add_argument("--scoreOxonium", dest="scoreOxonium",help="Score consistency between glycan composition and oxonium ions")

    if not argv:
        args = parser.parse_args(sys.argv[1:])
    else:
        args = parser.parse_args(argv)
    return args

def main(options):
    print "parsing input parameters"
    cutoff = float(options.scoreCutoff)
    
    print "parsing input file"
    glyML = glyxtoolms.io.GlyxXMLFile()
    glyML.readFromFile(options.infile)
    
    glyML.addToolValueDefault("identScore", 0.0)
    newhits = []
    N_removed = 0
    for h in glyML.glycoModHits:
        score = calcScore(h, options)
        if score <= cutoff:
            N_removed += 1
            continue
        h.toolValues["identScore"] = score
        newhits.append(h)
    print "removed " + str(N_removed) + " identifications with a score lower than " + str(cutoff) + " from " + str(len(glyML.glycoModHits)) + " total identifications."
    glyML.glycoModHits = newhits
    glyML.writeToFile(options.outfile)
    print "done"
    return

if __name__ == "__main__":
    options = handle_args()
    main(options)

 
