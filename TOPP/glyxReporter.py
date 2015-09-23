def handle_args(argv=None):
    import argparse
    usage = "\nReporter for analysis file"
    parser = argparse.ArgumentParser(description=usage)
    parser.add_argument("--in", dest="infileAnalysis",help="File input Analysis file .xml")
    parser.add_argument("--out", dest="outfile",help="File output xls file")
                
    if not argv:
        args = parser.parse_args(sys.argv[1:])
    else:
        args = parser.parse_args(argv)
    return args

def parseComposition(comp):
    string = ""
    names = {"DHEX":"F","HEX":"H","HEXNAC":"HN","NEUAC":"NA","NEUGC":"NG"}
    for match in re.findall("[A-z]+\d+",comp):
        unit = re.search("[A-z]+",match).group()
        amount = int(re.search("\d+",match).group())
        if amount == 0:
            continue
        string += names[unit] + str(amount)
    return string
      
def generateGlycoylationSiteKey(peptide):
    parts = []
    for nr,amino in sorted(peptide.glycosylationSites):
        parts.append(amino + str(nr))
    return "/".join(parts)
    
def main(options): 

    # parse analysis file
    fin = glyxsuite.io.GlyxXMLFile()
    fin.readFromFile(options.infileAnalysis) 

    # get features
    features = {}
    for feature in fin.features:
        features[feature.getId()] = feature

    # get hits
    data = {}
    comps = {}
    glycoSites = {}
    peptideMasses = {}
    for h in fin.glycoModHits:
       
        feature = features[h.featureID]
        peptide = h.peptide
        glycan = h.glycan
        charge = feature.getCharge()
        rt = feature.getRT()
        # calculate theoretical glycopeptide mass
        mass = (peptide.mass+
                glycan.mass+
                glyxsuite.masses.MASS["H+"]*charge)/charge

        comp = glycan.composition
        comp = glycan.composition
        comps[comp] = glycan.mass
        seq = peptide.toString()
        peptideMasses[seq] = peptide.mass+glyxsuite.masses.MASS["H+"]
        
        # generate glycosite
        glycoSiteKey = generateGlycoylationSiteKey(peptide)
        glycoSites[seq] = glycoSiteKey
        
        if not seq in data:
            data[seq] = {}
        if not comp in data[seq]:
            data[seq][comp] = set()
        data[seq][comp].add("{}({})[{}]".format(str(round(mass,1)),str(charge),str(round(rt/60.0,1))))
        

    # write output
    compsHeader = sorted(list(comps))

    wb = xlwt.Workbook()
    ws0 = wb.add_sheet("Resultstable")

    # write header
    for col,comp in enumerate(["GlycoSite", "Peptide", "Peptidemass"]+[parseComposition(comp) for comp in compsHeader]):
        ws0.write(1,col,comp)
    
    for col,comp in enumerate(compsHeader):
        ws0.write(0,col+3,str(round(comps[comp],1)))
    
    row = 1
    for seq in data:
        row += 1
        # write sequence
        ws0.write(row,0,glycoSites[seq])
        ws0.write(row,1,seq)
        ws0.write(row,2,str(round(peptideMasses[seq],2)))
        col = 2
        for comp in compsHeader:
            col += 1
            print 
            if comp in data[seq]:
                ws0.write(row,col,";".join(data[seq][comp]))
                
    wb.save(options.outfile)


import sys
import glyxsuite
import xlwt
import re

if __name__ == "__main__":
    options = handle_args()
    main(options)
 
