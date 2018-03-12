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
        if name.startswith("peptide(") or name.startswith("peptide+("):
            pep = True
        if name.startswith("peptide-NH3(") or name.startswith("peptide-NH3+("):
            pepNH3 = True
        if name.startswith("peptide+N1(") or name.startswith("peptide+HexNAc+("):
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
        scoreFuc = (1 + ("(HexNAc)1(Hex)1(dHex)1(H+)1" in ions))/2.0
    else:
        scoreFuc = (1+ ("(HexNAc)1(Hex)1(dHex)1(H+)1" not in ions))/2.0
    
    # sanitize peptide length
    length = float(len(hit.peptide.sequence))-1
    if length == 0:
        length = 1.0
        
    # collect peaks with fragment info
    peakset = set()
    for key in keys:
        p = hit.fragments[key].peak
        peakset.add(p)
    explainedIntensity = 0.0
    for p in peakset:
        explainedIntensity += p.y
    totalIntensity = 0.0
    for p in hit.feature.consensus:
        totalIntensity += p.y
    
    # calc score
    score = 1.0
    all_scores = {}
    if options.scorePepFrag == "true":
        score1 = (len(y)/length+len(b)/length)/2.0
        score = score*score1
        all_scores["scorePepFrag"] = score1
    if options.scorePep == "true":
        score2 = (1+pep)/2.0
        score = score*score2
        all_scores["scorePep"] = score2
    if options.scorePepNH3 == "true":
        score3 = (1+pepNH3)/2.0
        score = score*score3
        all_scores["scorePepNH3"] = score3
    if options.scorePepHEXNAC == "true":
        score4 = (1+pepHexNAc)/2.0
        score = score*score4
        all_scores["scorePepHEXNAC"] = score4
    if options.scoreOxonium == "true":
        score5 = scoreNeuAc*scoreFuc
        score = score*score5
        all_scores["scoreOxonium"] = score5
    if options.scoreExplained == "true":
        score6 = explainedIntensity/totalIntensity
        score = score*score6
        all_scores["scoreExplained"] = score6
        
    return score, all_scores

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
    parser.add_argument("--scoreExplained", dest="scoreExplained",help="Score explained intensity of the match")
    

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
    
    # add scores
    glyML.addToolValueDefault("scoreTotal", 0.0)
    if options.scorePepFrag == "true":
        glyML.addToolValueDefault("scorePepFrag", 0.0)
    if options.scorePep == "true":
        glyML.addToolValueDefault("scorePep", 0.0)
    if options.scorePepNH3 == "true":
        glyML.addToolValueDefault("scorePepNH3", 0.0)
    if options.scorePepHEXNAC == "true":
        glyML.addToolValueDefault("scorePepHEXNAC", 0.0)
    if options.scoreOxonium == "true":
        glyML.addToolValueDefault("scoreOxonium", 0.0)
    if options.scoreExplained == "true":
        glyML.addToolValueDefault("scoreExplained", 0.0)
    newhits = []
    N_removed = 0
    for h in glyML.glycoModHits:
        score, all_scores = calcScore(h, options)
        if score < cutoff:
            N_removed += 1
            continue
        h.toolValues["scoreTotal"] = score
        if options.scorePepFrag == "true":
            h.toolValues["scorePepFrag"] = all_scores["scorePepFrag"]
        if options.scorePep == "true":
            h.toolValues["scorePep"] = all_scores["scorePep"]
        if options.scorePepNH3 == "true":
            h.toolValues["scorePepNH3"] = all_scores["scorePepNH3"]
        if options.scorePepHEXNAC == "true":
            h.toolValues["scorePepHEXNAC"] = all_scores["scorePepHEXNAC"]
        if options.scoreOxonium == "true":
            h.toolValues["scoreOxonium"] = all_scores["scoreOxonium"]
        if options.scoreOxonium == "true":
            h.toolValues["scoreExplained"] = all_scores["scoreExplained"]
        
        newhits.append(h)
    print "removed " + str(N_removed) + " identifications with a score lower than " + str(cutoff) + " from " + str(len(glyML.glycoModHits)) + " total identifications."
    glyML.glycoModHits = newhits
    glyML.writeToFile(options.outfile)
    print "done"
    return

if __name__ == "__main__":
    options = handle_args()
    main(options)

 
