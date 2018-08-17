# Tool for selecting possible glycan + peptide masses for given precursor masses

# out: Glycancompositionfile.txt, each line containing one structure

    
class GlycanLookup(object):
    
    def __init__(self):
        self.lookup = {}
        
    def addGlycan(self, glycan):
        index = int(glycan.mass)
        self.lookup[index-1] = self.lookup.get(index-1,[]) + [glycan]
        self.lookup[index] = self.lookup.get(index,[]) + [glycan]
        self.lookup[index+1] = self.lookup.get(index+1,[]) + [glycan]
        
    def getGlycansFromMass(self, mass):
        index = int(mass)
        return self.lookup.get(index,[])
        

def handle_args(argv=None):
    import argparse
    usage = "\nFile Glycan composition builder"
    parser = argparse.ArgumentParser(description=usage)
    parser.add_argument("--inAnalysis", dest="infileAnalysis",help="File input Analysis file .xml")
    parser.add_argument("--inGlycan", dest="infileGlycan",help="File input Glycan composition file .txt")
    parser.add_argument("--inPeptide", dest="infilePeptide",help="File input Glycopeptide file .xml")    
    parser.add_argument("--out", dest="outfile",help="File output Analysis file with appended Glycopeptide hits")
    parser.add_argument("--tolerance", dest="tolerance",
                        help="Mass tolerance in either Da or ppm",
                        type=float)
    parser.add_argument("--toleranceType", dest="toleranceType",
                        help="Type of the given mass tolerance",
                        choices=["Da", "ppm"])
    parser.add_argument("--checkPep", dest="checkPep",help="Check existence of the peptide ion within the consensus spectrum")
    parser.add_argument("--checkPepHexNAc", dest="checkPepHexNAc",help="Check existence of the peptide+HexNAc ion within the consensus spectrum")
                
    if not argv:
        args = parser.parse_args(sys.argv[1:])
    else:
        args = parser.parse_args(argv)
    return args


def hasMassInSpectrum(unchargedMass, feature, tolerance,toleranceType):
    """ Search for the existence of an uncharged mass within the charge range of the feature charge """
    # mass = (hit.peptide.mass+glyxtoolms.masses.GLYCAN["HEXNAC"]+glyxtoolms.masses.MASS["H+"]*charge)/float(charge)
    for charge in range(1,feature.getCharge()+1):
        mass = (unchargedMass+glyxtoolms.masses.MASS["H+"]*charge)/float(charge)
        peak = feature.getConsensusPeakAt(mass,tolerance,toleranceType)
        if peak != None:
            return True
    return False

def main(options):
    print "parsing input parameters"
    tolerance = float(options.tolerance)
    toleranceType = options.toleranceType
    checkPep = False
    if options.checkPep == "true":
        checkPep = True
    
    checkPepHexNAc = False
    if options.checkPepHexNAc == "true":
        checkPepHexNAc = True
        
    print "parsing input files"
    # Analysis file
    glyML = glyxtoolms.io.GlyxXMLFile()
    glyML.readFromFile(options.infileAnalysis)
    # Peptide file
    pepFile = glyxtoolms.io.XMLPeptideFile()
    pepFile.loadFromFile(options.infilePeptide)
    # Glycan file
    glycans = []
    glycanFile = glyxtoolms.io.GlycanCompositionFile()
    glycanFile.read(options.infileGlycan)
    
    # generate glycan lookup table
    glycanLookup = GlycanLookup()
    for glycan in glycanFile.glycans:
        glycanLookup.addGlycan(glycan)
    
    # remove old hits
    keepHits = []
    glyML.glycoModHits = keepHits
    print "starting search for new identifcation hits"
    for feature in glyML.features:
        if feature.status == glyxtoolms.io.ConfirmationStatus.Rejected:
            continue
        found = False
        for peptide in pepFile.peptides:
            # check if peptide mass is existing within the consensus spectrum
            hasPep = True
            if checkPep == True:
                hasPep = hasMassInSpectrum(peptide.mass, feature, tolerance,toleranceType)
            hasPepHexNAc = True
            if checkPepHexNAc == True:
                hasPepHexNAc = hasMassInSpectrum(peptide.mass+glyxtoolms.masses.GLYCAN["HEXNAC"],feature, tolerance,toleranceType)
            if hasPep == False and hasPepHexNAc == False:
                continue
            # collect glycosylation types for peptide
            glycosites = {"N":0, "O":0}
            
            for pos,site in peptide.glycosylationSites:
                glycosites[site] += 1
                
            glycanmass = (feature.getMZ()-glyxtoolms.masses.MASS["H+"])*feature.getCharge()-peptide.mass
            for glycan in glycanLookup.getGlycansFromMass(glycanmass):
                mass = (peptide.mass+glycan.mass+glyxtoolms.masses.MASS["H+"]*feature.getCharge())/float(feature.getCharge())
                error = glyxtoolms.lib.calcMassError(feature.getMZ(), mass, toleranceType)
                if abs(error) > tolerance:
                    continue
                # check if glycan type can exist on the peptides glycosylationsites
                glycoSiteSubsets = []
                for typ in glycan.types:
                    if glycosites.get("N",0) < typ.get("N",0):
                        continue
                    if glycosites.get("O",0) < typ.get("O",0):
                        continue
                    hasVariants = glyxtoolms.fragmentation.getModificationVariants(peptide,typ,check=True)
                    if hasVariants == True:
                        glycoSiteSubsets.append(typ)

                if len(glycoSiteSubsets) == 0:
                    continue
                    
                # check if an accepted hit exists already for feature
                hit = glyxtoolms.io.GlyxXMLGlycoModHit()
                hit.featureID = feature.getId()
                hit.glycan = glycan
                hit.peptide = peptide
                hit.error = mass - feature.getMZ()
                # add glycosites as tags to the hit
                for typ in glycoSiteSubsets:
                    tag = ""
                    if typ.get("N",0) > 0:
                        tag += "N"+str(typ.get("N",0))
                    if typ.get("O",0) > 0:
                        tag += "O"+str(typ.get("O",0))
                    hit.tags.add(tag)
                glyML.glycoModHits.append(hit)

    print "found ",len(glyML.glycoModHits), " hits"
    print "writing output"
    glyML.writeToFile(options.outfile)
    print "done"
    return

import sys
import glyxtoolms
from itertools import product
import re

if __name__ == "__main__":
    options = handle_args()
    main(options)
 
