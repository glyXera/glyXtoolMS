# Tool for generating excel data

import glyxtoolms
import sys  

def getSpectrum(exp,nativeId):
    msmsSpec = None
    msSpec = None
    index = int(nativeId.split("=")[-1])-1
    msmsSpec = exp[index]
    try:
        assert msmsSpec.getNativeID() == nativeId
        assert msmsSpec.getMSLevel() == 2
    except:
        for index,s in enumerate(exp):
            if s.getNativeID() == nativeId:
                assert s.getMSLevel() == 2
                msmsSpec = s
                break
    # find precursor spectrum
    while index > 0:
        index -= 1
        s = exp[index]
        if s.getMSLevel() == 1:
            msSpec = s
            break
    return msSpec,msmsSpec


def generateData(exp,s,hit,fragTyp,fileTyp,comment):
    
    msSpec, msmsSpec = getSpectrum(exp,s.getNativeId())
    if msmsSpec == None or msSpec == None:
        return {}
    assert msSpec.getMSLevel() == 1
    assert msmsSpec.getMSLevel() == 2
    
    if fragTyp == "ETD":
        if fileTyp == "A":
            fragTyp = "ETciD"
        else:
            fragTyp = "EThcD"
        
    
    data = {}
    data["File"] = fileTyp
    data["MSScan"] = msSpec.getNativeID().split("=")[-1]
    msid = ""
    if fragTyp != "":
        msid = msmsSpec.getNativeID().split("=")[-1]
    data["MS/MSScan"] = msid
    data["RT"] = round(msSpec.getRT()/60.0,2)
    data["DissMethod"] = fragTyp
    data["SpectralAnn"] = "glyXtoolMS"
    evidence = "MS, MS/MS"
    if fragTyp == "":
        evidence = "MS"
    data["Evidence"] = evidence
    score = ""
    if fragTyp == "EThcD":
        score = round(hit.toolValues.get("etdScore2",0.0),2)
    elif fragTyp == "HCD":
        score = round(hit.toolValues.get("hcdScore2",0.0),2)
    data["IdConv1"] = score
    data["IdConv2"] = ""
    data["IdConv3"] = ""
    data["ObserverdMZ"] = round(hit.feature.getMZ(),4)
    data["ObserverdCharge"] = int(hit.feature.getCharge())
    data["off"] = "0" # check!!
    z = hit.feature.getCharge()
    data["MassGPObserved"] = round(hit.feature.getMZ()*z-(z-1)*glyxtoolms.masses.MASS["H+"],4)
    data["MassGPTh"] = round(hit.peptide.mass+hit.glycan.mass+glyxtoolms.masses.MASS["H+"],4)
    data["Delta"] = round(data["MassGPObserved"]-data["MassGPTh"],4)
    data["ppm"] = round(data["Delta"]/data["MassGPTh"]*1E6,4)
    data["sequence"] = hit.peptide.sequence
    data["start"] = hit.peptide.start+1
    data["sites"] = ", ".join([str(pos) for pos in sorted([pos+1 for pos,typ in hit.peptide.glycosylationSites])])
    modifications = []
    for m in hit.peptide.modifications:
        pos = hit.peptide.start+m.position+2
        mass = round(glyxtoolms.masses.PROTEINMODIFICATION[m.name]["mass"],4)
        modifications.append((pos, str(mass)))
    modifications = sorted(modifications)
    data["modsRes"] = ", ".join([str(pos) for pos,mass in modifications])
    data["modsMass"] = ", ".join([mass for pos,mass in modifications])
    data["Hex"] = hit.glycan.sugar.get("HEX",0) if hit.glycan.sugar.get("HEX",0) > 0  else ""
    data["HexNAc"] = hit.glycan.sugar.get("HEXNAC",0) if hit.glycan.sugar.get("HEXNAC",0) > 0  else ""
    data["Fuc"] = hit.glycan.sugar.get("DHEX",0) if hit.glycan.sugar.get("DHEX",0) > 0  else ""
    data["NeuAc"] = hit.glycan.sugar.get("NEUAC",0) if hit.glycan.sugar.get("NEUAC",0) > 0  else ""
    data["NeuGc"] = hit.glycan.sugar.get("NEUGC",0) if hit.glycan.sugar.get("NEUGC",0) > 0  else ""
    data["GlycanMass"] = round(hit.glycan.mass,4)
    glycantyp = []
    for tag in ["N1","N2","O1","O2","O3"]:
        if tag in hit.tags:
            glycantyp.append(tag)
    data["GlycanTyp"] = ", ".join(glycantyp)
    protSplit = hit.peptide.proteinID.split("|")
    data["ProtName"] = protSplit[2]
    data["UniProtKB"] = protSplit[1]
    data["Comment"] = comment
    return data


def handle_args(argv=None):
    import argparse
    usage = "\nFile IdentificationDiscriminator"
    parser = argparse.ArgumentParser(description=usage)
    parser.add_argument("--inMZML", dest="inMZML",help="MzML file containing both ETD and HCD spectra") 
    parser.add_argument("--inETD", dest="inETD",help="ETD Analysis File, also containing the identifications") 
    parser.add_argument("--inHCD", dest="inHCD",help="HCD Analysis File")
    parser.add_argument("--out", dest="outfile",help="Table containing the necessary spectra information")
    parser.add_argument("--fileTyp", dest="fileTyp",help="Experiment A or B")
    
    if not argv:
        args = parser.parse_args(sys.argv[1:])
    else:
        args = parser.parse_args(argv)
    return args

def main(options):
    
    exp = glyxtoolms.lib.openOpenMSExperiment(options.inMZML)

    print "reading in ETD Analysis file"
    etdFile = glyxtoolms.io.GlyxXMLFile()
    etdFile.readFromFile(options.inETD)

    print "reading in HCD Analysis file"
    hcdFile = glyxtoolms.io.GlyxXMLFile()
    hcdFile.readFromFile(options.inHCD)

    print "generate feature lookup"
    featureLookup = {}
    for feature in etdFile.features:
        featureLookup[feature.id] = [feature,None]
        
    for feature in etdFile.features:
        featureLookup[feature.id] = featureLookup.get(feature.id,[None,None])
        featureLookup[feature.id][1] = feature

    # set identification origin
    identifications = etdFile.glycoModHits

    line = []
    line.append("File")
    line.append("MSScan")
    line.append("MS/MSScan")
    line.append("RT")
    line.append("DissMethod")
    line.append("SpectralAnn")
    line.append("Evidence")
    line.append("IdConv1")
    line.append("IdConv2")
    line.append("IdConv3")
    line.append("ObserverdMZ")
    line.append("ObserverdCharge")
    line.append("off")
    line.append("MassGPObserved")
    line.append("MassGPTh")
    line.append("Delta")
    line.append("ppm")
    line.append("sequence")
    line.append("start")
    line.append("sites")
    line.append("modsRes")
    line.append("modsMass")
    line.append("Hex")
    line.append("HexNAc")
    line.append("Fuc")
    line.append("NeuAc")
    line.append("NeuGc")
    line.append("GlycanMass")
    line.append("GlycanTyp")
    line.append("ProtName")
    line.append("UniProtKB")
    line.append("Comment")

    f = file(options.outfile,"w")

    for hit in identifications:
        if hit.status != "Accepted":
            continue
        # generate comment

        if "explainedByPeptideInference" in hit.tags:
            comment = "glycopeptide infered from the existence of the same peptide and other glycans (MS only)"
            continue
        elif "explainedByProteinInference" in hit.tags:
            comment = "glycopeptide infered from the existence of other peptides with shared glycosylation site"
            continue
        elif "explainedByETD" in hit.tags and "explainedByHCD" in hit.tags:
            comment = "glycopeptide identified by HCD and ETD"
        elif "explainedByETD" in hit.tags:
            comment = "glycopeptide identified by ETD"
        else:
            comment = "glycopeptide identified by HCD"

        if "explainedByETD" in hit.tags:
            etdFeature = featureLookup[hit.feature.id][0]
            for s in etdFeature.spectra:
                data = generateData(exp,s,hit,"ETD",options.fileTyp,comment)
                f.write("\t".join([str(data.get(col,"")) for col in line]) +"\n")
        if "explainedByHCD" in hit.tags:
            hcdFeature = featureLookup[hit.feature.id][1]
            for s in hcdFeature.spectra:
                data = generateData(exp,s,hit,"HCD",options.fileTyp,comment)
                f.write("\t".join([str(data.get(col,"")) for col in line]) +"\n")
        if "explainedByPeptideInference" in hit.tags or "explainedByProteinInference" in hit.tags:
            hcdFeature = featureLookup[hit.feature.id][0]
            etdFeature = featureLookup[hit.feature.id][1]
            for s in etdFeature.spectra+hcdFeature.spectra:
                data = generateData(exp,s,hit,"",options.fileTyp,comment)
                f.write("\t".join([str(data.get(col,"")) for col in line]) +"\n")
                
    f.close()

    print "done"
    return

if __name__ == "__main__":
    options = handle_args()
    main(options)
