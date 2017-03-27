import sys
import glyxtoolms
import xlwt
import re

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


def generateFragmentString(names):
    pep = []
    y = []
    b = []
    yb = []
    other = []

    for name in names:
        if "peptide" in name:
            pep.append(name)
        elif re.match("^y\d+b\d+",name):
            yb.append(name)
        elif re.match("^b\d+", name):
            b.append(name)
        elif re.match("^y\d+", name):
            y.append(name)
        else:
            other.append(name)
    collect = []
    if len(pep) > 0:
        collect.append(",".join(sorted(pep)))
    if len(y) > 0:
        collect.append(",".join(sorted(y)))
    if len(b) > 0:
        collect.append(",".join(sorted(b)))
    if len(yb) > 0:
        collect.append(",".join(sorted(yb)))
    if len(other) > 0:
        collect.append(",".join(sorted(other)))
    string = "|".join(collect)
    return string

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
    identificationData = []
    for h in fin.glycoModHits:
        feature = features[h.featureID]

        peptide = h.peptide
        glycan = h.glycan
        
        # convert glycan to check  consistency of glycancomposition and mass
        g = glyxtoolms.lib.Glycan(glycan.composition)

        # calculate theoretical glycopeptide mass
        charge = feature.getCharge()
        mass = (peptide.mass+
                g.mass+
                glyxtoolms.masses.MASS["H+"]*charge)/charge

        error = str(round(h.error,4))
        
        
        if not error.startswith("-"):
            error = "+"+error
        
        # generate glycosite
        glycoSiteKey = generateGlycosylationSiteKey(peptide)
        
        dataHit = {}
        dataHit["Peptide"] = peptide.toString()
        dataHit["Glycan"] = g.toString()
        dataHit["m peptide"] = str(round(peptide.mass,4))
        dataHit["m glycan"] = str(round(g.mass,4))
        dataHit["RT"] = str(round(feature.getRT()/60.0,1))
        dataHit["m/z"] = str(round(mass,4))
        dataHit["Charge"] = str(charge)
        dataHit["ProtID"] = peptide.proteinID
        dataHit["Sites"] = glycoSiteKey
        dataHit["Status"] = h.status
        dataHit["Intensity"] = str(feature.intensity)
        dataHit["Fragments"] = generateFragmentString(h.fragments.keys())
        identificationData.append(dataHit)

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
    ws2.write(row, 1, "RT apx [min]")
    ws2.write(row, 2, "RT min [min]")
    ws2.write(row, 3, "RT max [min]")
    ws2.write(row, 4, "m/z")
    ws2.write(row, 5, "Charge")
    ws2.write(row, 6, "Intensity")
    ws2.write(row, 7, "best LogScore")
    ws2.write(row, 8, "Nr. Identifications")
    ws2.write(row, 9, "Status")
    
    featNr = 0
    for featureID in features:
        feature = features[featureID]
        featNr += 1
        row += 1
        ws2.write(row, 0, featNr)
        ws2.write(row, 1, round(feature.getRT()/60.0, 2))
        ws2.write(row, 2, round(feature.minRT/60.0, 2))
        ws2.write(row, 3, round(feature.maxRT/60.0, 2))
        ws2.write(row, 4, round(feature.getMZ(), 4))
        ws2.write(row, 5, int(feature.getCharge()))
        ws2.write(row, 6, str(feature.intensity))
        scores = [10.0]
        for s in feature.spectra:
            scores.append(s.logScore)
        ws2.write(row, 7, min(scores))
        ws2.write(row, 8, len(feature.hits))
        ws2.write(row, 9, feature.status)

    # ---------------------- Identifications --------------------------#
    ws3 = wb.add_sheet("Identifications")

    # header
    header = ["Peptide","Glycan","m peptide","m glycan","RT","m/z","Charge","ProtID","Sites","Status", "Intensity", "Fragments"]
    for col,name in enumerate(header):
        ws3.write(0, col, name)
    row = 1
    for hit in identificationData:
        for col,name in enumerate(header):
            ws3.write(row, col, hit[name])
        row += 1
    # Save excel sheet
    wb.save(options.outfile)

if __name__ == "__main__":
    options = handle_args()
    main(options)
 
