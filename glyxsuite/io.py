from lxml import etree as ET


class GlyxXMLSpectrum:
    
    def __init__(self):
        self._nativeId = ""
        self._rt = 0.0
        self._ionCount = 0
        self._precursor_mass = 0
        self._precursor_charge = 0
        self._logScore = 10
        self._ions = {}

    def setNativeId(self,nativeId):
        self._nativeId = nativeId
    
    def setRT(self,rt):
        self._rt = rt

    def setIonCount(self,ionCount):
        if ionCount == 0:
            self._ionCount = 0
        else:
            self._ionCount = ionCount

    def setPrecursor(self,mass,charge):
        self._precursor_mass = mass
        self._precursor_charge = charge

    def setLogScore(self,logScore):
        self._logScore = logScore

    def addIon(self,glycan,ionName,mass,intensity):
        if not glycan in self._ions:
            self._ions[glycan] = {}
        self._ions[glycan][ionName] = {}
        self._ions[glycan][ionName]["mass"] = mass
        self._ions[glycan][ionName]["intensity"] = intensity


    def getNativeId(self):
        return self._nativeId

    def getRT(self):
        return self._rt

    def getIonCount(self):
        return self._ionCount

    def getPrecursorMass(self):
        return self._precursor_mass

    def getPrecursorCharge(self):
        return self._precursor_charge

    def getLogScore(self):
        return self._logScore

    def getIons(self):
        return self._ions


class GlyxXMLParameters:

    def __init__(self):
        self._timestamp = ""
        self._glycans = []
        self._tolerance = 0.0
        self._ionThreshold = 0
        self._nrNeutrallosses = 0
        self._maxOxoniumCharge = 0
        self._scoreThreshold = 0


    def setTimestamp(self,timestamp):
        self._timestamp = timestamp

    def setMassTolerance(self,tolerance):
        self._tolerance = tolerance

    def setIonThreshold(self,ionThreshold):
        self._ionThreshold = ionThreshold

    def setNrNeutrallosses(self,nrNeutrallosses):
        self._nrNeutrallosses = nrNeutrallosses

    def setMaxOxoniumCharge(self,maxOxoniumCharge):
        self._maxOxoniumCharge = maxOxoniumCharge

    def setScoreThreshold(self,scoreThreshold):
        self._scoreThreshold = scoreThreshold

    def setGlycanList(self,glycans):
        self._glycans = glycans

    def addGlycan(self,glycan):
        self._glycans.append(glycan)

    def getTimestamp(self):
        return self._timestamp

    def getMassTolerance(self):
        return self._tolerance

    def getIonThreshold(self):
        return self._ionThreshold

    def getNrNeutrallosses(self):
        return self._nrNeutrallosses


    def getMaxOxoniumCharge(self):
        return self._maxOxoniumCharge

    def getScoreThreshold(self):
        return self._scoreThreshold

    def getGlycans(self):
        return self._glycans

class GlyxXMLFile:
    # Input/Output file of glyxXML file
    def __init__(self):
        self.parameters = GlyxXMLParameters()
        self.spectra = []


    def writeToFile(self,path):
        xmlRoot = ET.Element("glyxXML")
        xmlParameters = ET.SubElement(xmlRoot,"parameters")
        xmlSpectra = ET.SubElement(xmlRoot,"spectra")

        # write search parameters
        xmlParametersDate = ET.SubElement(xmlParameters,"timestamp")
        xmlParametersDate.text = str(self.parameters.getTimestamp())

        xmlParametersGlycans = ET.SubElement(xmlParameters,"glycans")
        for glycan in self.parameters.getGlycans():
            xmlParametersGlycan = ET.SubElement(xmlParametersGlycans,"glycan")
            xmlParametersGlycan.text = glycan

        xmlParametersTol = ET.SubElement(xmlParameters,"tolerance")
        xmlParametersTol.text = str(self.parameters.getMassTolerance())

        xmlParametersIonthreshold = ET.SubElement(xmlParameters,"ionthreshold")
        xmlParametersIonthreshold.text = str(self.parameters.getIonThreshold())

        xmlParametersNeutral = ET.SubElement(xmlParameters,"nrNeutrallosses")
        xmlParametersNeutral.text = str(self.parameters.getNrNeutrallosses())

        xmlParametersOxionCharge = ET.SubElement(xmlParameters,"maxOxoniumionCharge")
        xmlParametersOxionCharge.text = str(self.parameters.getMaxOxoniumCharge())

        xmlParametersScorethreshold = ET.SubElement(xmlParameters,"scorethreshold")
        xmlParametersScorethreshold.text = str(self.parameters.getScoreThreshold())

        # write spectra
        for spectrum in self.spectra:
            xmlSpectrum = ET.SubElement(xmlSpectra,"spectrum")
            xmlSpectrumNativeId = ET.SubElement(xmlSpectrum,"nativeId")
            xmlSpectrumNativeId.text = str(spectrum.getNativeId())
            xmlSpectrumRT = ET.SubElement(xmlSpectrum,"rt")
            xmlSpectrumRT.text = str(spectrum.getRT())
            xmlSpectrumIonCount = ET.SubElement(xmlSpectrum,"ionCount")
            xmlSpectrumIonCount.text = str(spectrum.getIonCount())

            xmlPrecursor = ET.SubElement(xmlSpectrum,"precursor")
            xmlPrecursorMass = ET.SubElement(xmlPrecursor,"mass")
            xmlPrecursorMass.text = str(spectrum.getPrecursorMass())
            xmlPrecursorCharge = ET.SubElement(xmlPrecursor,"charge")
            xmlPrecursorCharge.text = str(spectrum.getPrecursorCharge())
            xmlTotalScore = ET.SubElement(xmlSpectrum,"logScore")
            xmlTotalScore.text = str(spectrum.getLogScore())

            xmlScoreList = ET.SubElement(xmlSpectrum,"scores")        
            ions = spectrum.getIons()
            for glycan in ions:
                xmlScore = ET.SubElement(xmlScoreList,"score")
                xmlGlycanName = ET.SubElement(xmlScore,"glycan")
                xmlGlycanName.text = glycan
                xmlIons = ET.SubElement(xmlScore,"ions")
                for ionName in ions[glycan]:
                    xmlIon = ET.SubElement(xmlIons,"ion")
                    xmlIonName = ET.SubElement(xmlIon,"name")
                    xmlIonName.text = ionName
                    xmlIonMass = ET.SubElement(xmlIon,"mass")
                    xmlIonMass.text = str(ions[glycan][ionName]["mass"])
                    xmlIonIntensity = ET.SubElement(xmlIon,"intensity")
                    xmlIonIntensity.text = str(ions[glycan][ionName]["intensity"])
   
        # writing to file
        xmlTree = ET.ElementTree(xmlRoot)
        f = file(path,"w")
        f.write(ET.tostring(xmlTree,pretty_print=True))
        f.close()


    def readFromFile(self,path):
        f = file(path,"r")
        root = ET.fromstring(f.read())
        f.close()

        # read parameters 
        p = root.find(".//parameters")
        timestamp = p.find("./timestamp").text
        tolerance = float(p.find("./tolerance").text)
        ionThreshold = int(p.find("./ionthreshold").text)
        nrNeutrallosses = int(p.find("./nrNeutrallosses").text)
        maxOxoniumCharge = int(p.find("./maxOxoniumionCharge").text)
        scoreThreshold = float(p.find("./scorethreshold").text)
        glycans = []
        for glycanElement in p.findall("./glycans/glycan"):
            glycans.append(glycanElement.text)
            
        parameters = GlyxXMLParameters()
        parameters.setTimestamp(timestamp)
        parameters.setMassTolerance(tolerance)
        parameters.setIonThreshold(ionThreshold)
        parameters.setNrNeutrallosses(nrNeutrallosses)
        parameters.setMaxOxoniumCharge(maxOxoniumCharge)
        parameters.setScoreThreshold(scoreThreshold)
        parameters.setGlycanList(glycans)

        spectra = []
        for s in root.findall("./spectra/spectrum"):
            spectrum = GlyxXMLSpectrum()
            
            nativeId = s.find("./nativeId").text
            spectrum.setNativeId(nativeId)
            ionCount = float(s.find("./ionCount").text)
            spectrum.setIonCount(ionCount)
            logScore = float(s.find("./logScore").text)
            spectrum.setLogScore(logScore)
            rt = float(s.find("./rt").text)
            spectrum.setRT(rt)
            precursor_mass= float(s.find("./precursor/mass").text)
            precursor_charge= int(s.find("./precursor/charge").text)
            spectrum.setPrecursor(precursor_mass,precursor_charge)
            for score in s.findall("./scores/score"):
                glycan = score.find("./glycan").text
                for ion in score.findall("./ions/ion"):
                    ionName = ion.find("./name").text
                    ionMass = float(ion.find("./mass").text)
                    ionIntensity = float(ion.find("./intensity").text)
                    spectrum.addIon(glycan,ionName,ionMass,ionIntensity)

            spectra.append(spectrum)
        # assign data to object
        self.parameters = parameters
        self.spectra = spectra

    def setParameters(self,parameters):
        self.parameters = parameters

    def getParameters(self):
        return self.parameters
    
    def addSpectrum(self,glyxXMLSpectrum):
        self.spectra.append(glyxXMLSpectrum)


    
    
        



