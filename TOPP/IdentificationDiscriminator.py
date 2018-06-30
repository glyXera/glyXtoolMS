# Tool for calculating peptide scores for HCD and ETD fragments

import glyxtoolms
import sys 

class Feature(object):
    
    def __init__(self,featureId):
        self.featureId = featureId
        self.identifications = set()
        self.chosenIdentification = None
       
        self.bestETDScore = None
        self.bestHCDScore = None
        self.explainedETD = None
        self.explainedHCD = None
    
    def getBestScores(self):
        self.bestETDScore = max([ident.etdScore for ident in self.identifications])
        self.bestHCDScore = max([ident.hcdScore for ident in self.identifications])

class Identification(object):
    
    def __init__(self,featureId, peptide, glycan,rt):
        self.featureId = featureId
        self.peptide = peptide
        self.glycan = glycan
        self.rt = rt
        self.etdScore = None
        self.hcdScore = None
        self.key = "|".join((featureId,peptide,glycan))
        self.feature = None
        self.removed = 0 # shows at which point the identification was removed
        self.valid = False
        self.proteins = set()
        self.intensity = 0
        self.hits = set()
        
    def accept(self,iteration):
        if self.removed > 0:
            return False
        self.removed = iteration
        # reject all other identifications within the same feature
        for ident in self.feature.identifications:
            ident.reject(iteration)
        self.valid = True
        self.feature.chosenIdentification = self
        return True

    def reject(self,iteration):
        if self.removed > 0:
            return
        self.removed = iteration
        self.valid = False        

def handle_args(argv=None):
    import argparse
    usage = "\nFile IdentificationDiscriminator"
    parser = argparse.ArgumentParser(description=usage)
    parser.add_argument("--in", dest="infile",help="File input Analysis file identifications scored on ETD and HCD .xml") 
    parser.add_argument("--outAnalysis", dest="outAnalysis",help="File output Analysis file with accepted identifications and explained features")
    parser.add_argument("--outExplained", dest="outExplained",help="File output text file containing the accepted featureids")
    parser.add_argument("--minScore", dest="minScore",help="minimum score  if identification should be accepted in the first round")
    parser.add_argument("--minExplainedIntensity", dest="minExplainedIntensity",help="minimum explained fragment spectrum intensity if identification should be accepted in the first round")

    if not argv:
        args = parser.parse_args(sys.argv[1:])
    else:
        args = parser.parse_args(argv)
    return args

def main(options):
    
    print "parsing parameters"
    minExplainedIntensity = float(options.minExplainedIntensity)
    minScoreValue = float(options.minScore)
    print "minExplainedIntensity: ", minExplainedIntensity
    print "minScore: ", minScoreValue
    
    print "parsing input file"
    glyML = glyxtoolms.io.GlyxXMLFile()
    glyML.readFromFile(options.infile)
    
    
    print "generating lookup data"
    data = {}
    for hit in glyML.glycoModHits:
        key = "|".join((hit.feature.id,hit.peptide.toString(),hit.glycan.toString()))
        if not key in data:
            ident = Identification(hit.feature.id,hit.peptide.toString(),hit.glycan.toString(),hit.feature.getRT())
            ident.intensity = hit.feature.intensity
            ident.etdScore = hit.toolValues.get("etdScore2",0.0)
            ident.hcdScore = hit.toolValues.get("hcdScore2",0.0)
            ident.explainedETD = hit.toolValues.get("explainedETD",0.0)
            ident.explainedHCD = hit.toolValues.get("explainedHCD",0.0)
            data[key] = ident
        ident = data[key]
        ident.proteins.add(hit.peptide.proteinID)
        ident.hits.add(hit)
    
    features = {}
    peptides = {}
    for ident in data.values():
        if not ident.featureId in features:
            feature = Feature(ident.featureId)
            features[ident.featureId] = feature
        else:
            feature = features[ident.featureId]
        ident.feature = feature
        feature.identifications.add(ident)
        peptides[ident.peptide] = peptides.get(ident.peptide,[]) + [ident]
    
    for feature in features.values():
        feature.getBestScores()
    
    sortedIdentifications = sorted(data.values(),key=lambda ident:max((ident.etdScore,ident.hcdScore)),reverse=True)
    
    # identify best scored identifications
    iteration = 0
    identified = []
    explainedInt = 1.0
    minScore = 200
    print "start finding best peptides"
    while True:
        iteration += 1
        start = None
        for ident in sortedIdentifications:
            if ident.removed != 0:
                continue
            passes = False
            for bestScore,explained,typ in [(ident.etdScore,ident.explainedETD,"ETD"),(ident.hcdScore,ident.explainedHCD,"HCD")]:
                if bestScore >= minScore and explained >= explainedInt:
                    passes = True
                    break
            if passes == True:
                start = ident
                break
        if start == None:
            if minScore < minScoreValue:
                break
            else:
                explainedInt -= 0.1
                if explainedInt <= minExplainedIntensity:
                    explainedInt = 1.0
                    minScore -= 1
                continue
        if start.accept(iteration) == True:
            identified.append(start)
    print "found ", len(identified), " good scoring peptides"
    
    # add tags
    for ident in identified:
        for bestScore,explained,typ in [(ident.etdScore,ident.explainedETD,"ETD"),(ident.hcdScore,ident.explainedHCD,"HCD")]:
            if bestScore >= minScoreValue and explained >= minExplainedIntensity:
                # add explanation tags
                for hit in ident.hits:
                    hit.tags.add("explainedBy"+typ)
    
    # accept all remaining identification of the same peptide
    newidentified = []
    for start in identified:
        iteration += 1
        for ident in peptides[start.peptide]:
            if ident.accept(iteration) == True:
                newidentified.append(ident)
                # add explanation tags
                for hit in ident.hits:
                    hit.tags.add("explainedByPeptideInference")
    identified += newidentified
    print "found ", len(newidentified), " peptides with the same sequence but lesser scores"
    
    newidentified = []
    # accept all remaining identifications of the same protein/glycosylationsite
    for start in identified:
        iteration += 1
        # collect proteins and the already identified glycosylation sites
        prots = {}
        for hit in start.hits:
            prot = hit.peptide.proteinID
            sites = set([typ+str(pos) for pos,typ in hit.peptide.glycosylationSites])
            prots[prot] = prots.get(prot,set()).union(sites)
        
        for ident in sortedIdentifications:
            if ident.removed != 0:
                continue
            intersects = False
            for hit in ident.hits:
                prot = hit.peptide.proteinID
                if not prot in prots:
                    continue            
                sites = set([typ+str(pos) for pos,typ in hit.peptide.glycosylationSites])
                if len(prots[prot].intersection(sites)) > 0:
                    intersects = True
                    break
            if intersects == True and ident.accept(iteration) == True:
                newidentified.append(ident)
                # add explanation tags
                for hit in ident.hits:
                    hit.tags.add("explainedByProteinInference")
    identified += newidentified
    print "found ", len(newidentified), " peptides with the same glycosylation site but other sequence (misse cleavage, protein modifications)"
    
    # accept and reject identifications
    accepted = set()
    rejected = set()
    for ident in identified:
        for ident2 in ident.feature.identifications:
            rejected = rejected.union(ident2.hits) 
        accepted = accepted.union(ident.hits)
    
    rejected = rejected.difference(accepted)
    print "accepted hits", len(accepted)
    print "rejected hits", len(rejected)
    
    print "identified", len(identified), " of ", len(glyML.glycoModHits), " within ", len(glyML.features), " features"
    
    print "writing file  with accepted and rejected identifications and features"
    identifiedFeatureIds = set()
    for hit in glyML.glycoModHits:
        if hit in rejected:
            hit.status = "Rejected"
        elif hit in accepted:
            hit.status = "Accepted"
            hit.feature.status = "Accepted"
            identifiedFeatureIds.add(hit.feature.id)
        else:
            hit.status = "Unknown"
    glyML.writeToFile(options.outAnalysis)
    
    print "writing feature list containing the identified feature ids from this run"
    f = file(options.outExplained, "w")
    for featureId in identifiedFeatureIds:
        f.write(str(featureId) + "\n")
    f.close()

    print "done"
    return

if __name__ == "__main__":
    options = handle_args()
    main(options)
