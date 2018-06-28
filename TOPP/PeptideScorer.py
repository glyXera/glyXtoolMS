# Tool for calculating peptide scores for HCD and ETD fragments



import glyxtoolms
import re
import sys 


def parseFragmentname(name):
    b = re.sub("\(.+\)","",name)
    sp = re.split("(\+|-)",b)
    ion = sp[0]
    mods = []
    for i in range(1,len(sp),2):
        mods.append(sp[i]+sp[i+1])
    
    fragType = ""
    abc = -1
    for match in re.findall("(a\d+|b\d+|c\d+)",ion):
        typ = re.sub("\d","",match)
        pos = int(re.sub("\D","",match))
        abc = pos
        fragType += typ
    xyz = -1
    for match in re.findall("(x\d+|y\d+|z\*?\d+)",ion):
        typ = re.sub("\d","",match)
        pos = int(re.sub("\D","",match))
        xyz = pos
        fragType += typ
    return fragType, abc,xyz, mods

def scoreHit(hit,fragmentTyp):
    
        
    
    sequence = hit.peptide.sequence
    start = hit.peptide.start
    end = hit.peptide.end-start
    
    # calculate explained intensity
    totalIntensity = 0.0
    for p in hit.feature.consensus:
        totalIntensity += p.y
    
    sites = []
    for pos, typ in hit.peptide.glycosylationSites:
        sites.append((pos-start+1,typ))
        
    keys = []
    annotatedPeaks = set()
    for key in hit.fragments:
        annotatedPeaks.add(hit.fragments[key].peak)
        if "/" in key:
            continue
        if "-" in key:
            continue
        if fragmentTyp == "HCD":
            if key.startswith("b") or key.startswith("y"):
                keys.append(key)
        elif fragmentTyp == "ETD":
            if key.startswith("z") or key.startswith("c"):
                keys.append(key)
        else:
            raise Exception("Unknown framgentation type")
    keys = sorted(keys)
    
    explainedIntensity = 0.0
    for p in annotatedPeaks:
        explainedIntensity += p.y
    
    abcSeries = {}
    xyzSeries = {}
    for key in keys:
        typ,abc,xyz, mods = parseFragmentname(key)
        if typ in ["b","c"]:
            abcSeries[abc] = abcSeries.get(abc, []) + mods
        elif typ in ["y","z","z*"]:
            xyzSeries[xyz] = xyzSeries.get(xyz, []) + mods

    # score every glycsylation site
    siteScoring = []
    glycanString = "+"+hit.glycan.toString()
    
    for site,typ in sites:
        score = 0
        # score c-ion series
        for pos in range(1,len(sequence)+1):
            if not pos in abcSeries:
                score -= 1
                continue
            else:
                score += 2
            # check if a glycan is attached
            glycan = False
            full_glycan = False
            for mod in abcSeries[pos]:
                if mod.startswith("+"):
                    if mod != glycanString:
                        continue
                    glycan = True
                if mod == glycanString:
                    full_glycan = True
            if pos < site: # should have no glycan
                if glycan == True:
                    score -= 1
                else:
                    score += 1
            else: # should have glycan
                if glycan == True:
                    score += 1
                    if full_glycan == True:
                        score += 2
                else:
                    score -= 1
            
                    
        for pos in range(1,len(sequence)+1):
            if not pos in xyzSeries:
                score -= 1
                continue
            else:
                score += 2
            # check if the corresponding b ion also exisits
            if len(sequence)-pos in abcSeries:
                score += 1
            
            # check if a glycan is attached
            glycan = False
            full_glycan = False
            for mod in xyzSeries[pos]:
                if mod.startswith("+"):
                    if mod != glycanString:
                        continue
                    glycan = True
                if mod == glycanString:
                    full_glycan = True
            if pos < len(sequence)-site+1: # should have no glycan
                if glycan == True:
                    score -= 1
                else:
                    score += 1
            else: # should have glycan
                if glycan == True:
                    score += 1
                    if full_glycan == True:
                        score += 2
                else:
                    score -= 1
        score = score/float(len(sequence))
        score = score*explainedIntensity/totalIntensity
        siteScoring.append((score,site,explainedIntensity/totalIntensity))
    
    bestScore = max(siteScoring)
    return bestScore


def handle_args(argv=None):
    import argparse
    usage = "\nFile PeptideScorer"
    parser = argparse.ArgumentParser(description=usage)
    parser.add_argument("--in", dest="infile",help="File input Analysis file with annotated fragments.xml") 
    parser.add_argument("--out", dest="outfile",help="File output Analysis file with peptide score")
    parser.add_argument("--type", dest="typ",help="Spectra typ (currently either 'HCD' or 'ETD'")
    
    if not argv:
        args = parser.parse_args(sys.argv[1:])
    else:
        args = parser.parse_args(argv)
    return args

def main(options):
    print "parsing input parameters"
    typ = options.typ
    if typ == "HCD":
        scoreName = "scoreHCD"
        explainedName = "explainedHCD"
    elif typ == "ETD":
        scoreName = "scoreETD"
        explainedName = "explainedETD"
    else:
        raise Exception("Unknown fragmentation type!")
    
    print "parsing input file"
    glyML = glyxtoolms.io.GlyxXMLFile()
    glyML.readFromFile(options.infile)
    
    glyML.addToolValueDefault(scoreName, 0.0)
    glyML.addToolValueDefault(explainedName, 0.0)

    print "scoring fragment spectra"
    for hit in glyML.glycoModHits:
        score,site,explained = scoreHit(hit,typ)
        hit.toolValues[scoreName] = score
        hit.toolValues[explainedName] = explained
    glyML.writeToFile(options.outfile)
    print "done"
    return

if __name__ == "__main__":
    options = handle_args()
    main(options)