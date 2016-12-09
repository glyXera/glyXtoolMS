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
      
def generateGlycosylationSiteKey(peptide):
    parts = []
    for nr,amino in sorted(peptide.glycosylationSites):
        parts.append(amino + str(nr+1)) # correct counting of amino acids
    return "/".join(parts)
    
def main(options): 

    # parse analysis file
    fin = glyxtoolms.io.GlyxXMLFile()
    fin.readFromFile(options.infileAnalysis) 

    # get features
    features = {}
    for feature in fin.features:
        features[feature.getId()] = feature
    
    # get spectra
    spectra = {}
    for spectrum in fin.spectra:
        spectra[spectrum.getNativeId()] = spectrum
    
    # get hits
    data = {}
    comps = {}
    glycoSites = {}
    peptideMasses = {}
    newdata = []
    for h in fin.glycoModHits:
        if not h.status in data:
            data[h.status] = {}
        #if h.status == "Rejected":
        #    continue
        #if h.status == "Deleted":
        #    continue       
        feature = features[h.featureID]
        #if feature.status == "Rejected":
        #    continue
        #if feature.status == "Deleted":
        #    continue
        peptide = h.peptide
        glycan = h.glycan
        charge = feature.getCharge()
        rt = feature.getRT()
        # calculate theoretical glycopeptide mass
        mass = (peptide.mass+
                glycan.mass+
                glyxtoolms.masses.MASS["H+"]*charge)/charge
        # convert glycan to check  consistency of glycancomposition and mass
        g = glyxtoolms.lib.Glycan(glycan.composition)

        comp = g.toString()
        comps[comp] = g.mass
        seq = peptide.toString()
        peptideMasses[seq] = peptide.mass+glyxtoolms.masses.MASS["H+"]
        
        # generate glycosite
        glycoSiteKey = generateGlycosylationSiteKey(peptide)
        glycoSites[seq] = (peptide.proteinID, glycoSiteKey)
        
        if not seq in data[h.status]:
            data[h.status][seq] = {}
        if not comp in data[h.status][seq]:
            data[h.status][seq][comp] = set()
        data[h.status][seq][comp].add("{}({})[{}]".format(str(round(mass,1)),str(charge),str(round(rt/60.0,1))))
        dataHit = {}
        dataHit["peptide"] = seq
        dataHit["glycan"] = comp
        dataHit["m peptide"] = str(round(peptide.mass,4))
        dataHit["m glycan"] = str(round(glycan.mass,4))
        dataHit["rt"] = str(round(rt/60.0,1))
        dataHit["m/z"] = str(round(mass,4))
        dataHit["z"] = str(charge)
        dataHit["protID"] = peptide.proteinID
        dataHit["sites"] = glycoSiteKey
        dataHit["status"] = h.status
        dataHit["intensity"] = feature.intensity
        newdata.append(dataHit)
        

    # write output
    compsHeader = sorted(list(comps))

    wb = xlwt.Workbook()
    # -------------------------- Spectra -----------------------------#
    ws1 = wb.add_sheet("Spectra")
    row = 1
    ionlist = {}
    columnions = 4
    for spectrum in fin.spectra:
        # rt / mz / charge / intensity / logscore / ions
        ws1.write(row, 0, round(spectrum.rt/60.0, 2))
        ws1.write(row, 1, round(spectrum.precursorMass, 4))
        ws1.write(row, 2, int(spectrum.precursorCharge))
        ws1.write(row, 3, round(spectrum.precursorIntensity, 2))
        ws1.write(row, 4, round(spectrum.logScore, 3))
        # write ions
        for glycan in spectrum.ions:
            for ionname in spectrum.ions[glycan]:
                intensity = round(spectrum.ions[glycan][ionname]["intensity"], 2)
                # find column position
                if not ionname in ionlist:
                    columnions += 1
                    ionlist[ionname] = columnions
                ws1.write(row, ionlist[ionname], intensity)
        row += 1
    
    # write header
    ws1.write(0, 0, "RT [min]")
    ws1.write(0, 1, "MZ")
    ws1.write(0, 2, "Charge")
    ws1.write(0, 3, "Intensity")
    ws1.write(0, 4, "Logscore")
    for ionname in ionlist:
        ws1.write(0, ionlist[ionname], ionname)
    
    # -------------------------- Features -----------------------------#
    ws2 = wb.add_sheet("Features")
    
    # write header
    # rt, monoisotopic mass, charge, Logscore
    
    row = 0
    ws2.write(row, 0, "Feature Nr")
    ws2.write(row, 1, "RT [min]")
    ws2.write(row, 2, "Mass [Th]")
    ws2.write(row, 3, "Charge")
    ws2.write(row, 4, "LogScore")
    
    featNr = 0
    for featureID in features:
        feature = features[featureID]
        featNr += 1
        # get spectra
        for specID in feature.getSpectraIds():
            row += 1
            spectrum = spectra[specID]
            ws2.write(row, 0, featNr)
            ws2.write(row, 1, round(spectrum.getRT()/60.0, 2))
            ws2.write(row, 2, round(feature.getMZ(), 4))
            ws2.write(row, 3, int(feature.getCharge()))
            ws2.write(row, 4, round(spectrum.getLogScore(), 3))
    # ---------------------- Identifications --------------------------#
    ws3 = wb.add_sheet("Identifications")
    # header
    header = ["peptide","glycan","m peptide","m glycan","rt","m/z","z","protID","sites","status", "intensity"]
    for col,name in enumerate(header):
        ws3.write(0, col, name)
    row = 1
    for hit in newdata:
        for col,name in enumerate(header):
            ws3.write(row, col, hit[name])
        row += 1
    wb.save(options.outfile)
    #ws3 = wb.add_sheet("Identifications")
    #row = 0
    #for status in data:
    #    # write header
    #    ws3.write(row, 0, status)
    #    for col,comp in enumerate(["Protein", "GlycoSite", "Peptide", "Peptidemass"]+compsHeader):
    #        ws3.write(row+1, col, comp)
    #    
    #    for col,comp in enumerate(compsHeader):
    #        ws3.write(row, col+4, round(comps[comp], 1))
    #    
    #    row +=1
    #    for seq in data[status]:
    #        row += 1
    #        # write sequence
    #        ws3.write(row, 0, glycoSites[seq][0])
    #        ws3.write(row, 1, glycoSites[seq][1])
    #        ws3.write(row, 2, seq)
    #        ws3.write(row, 3, round(peptideMasses[seq], 2))
    #        col = 3
    #        for comp in compsHeader:
    #            col += 1
    #            print 
    #            if comp in data[status][seq]:
    #                ws3.write(row, col, ";".join(data[status][seq][comp]))
    #    row += 3
    #wb.save(options.outfile)

    
import sys
import glyxtoolms
import xlwt
import re

if __name__ == "__main__":
    options = handle_args()
    main(options)
 
