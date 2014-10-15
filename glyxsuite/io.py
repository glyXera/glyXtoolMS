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

class GlyxXMLFeature:
    
    def __init__(self):
        self._id = 0
        self._mz = 0.0
        self._rt = 0.0
        self._intensity = 0.0
        self._charge = 0
        self._minRT = 0.0
        self._maxRT = 0.0
        self._minMZ = 0.0
        self._maxMZ = 0.0
        self._spectraIds = []
        
    def setId(self,id):
        self._id = id
    
    def getId(self):
        return self._id
        
    def setMZ(self,mz):
        self._mz = mz
        
    def getMZ(self):
        return self._mz
        
    def setIntensity(self,intensity):
        self._intensity = intensity
        
    def getIntensity(self):
        return self._intensity        

    def setRT(self,rt):
        self._rt = rt
        
    def getRT(self):
        return self._rt
        
    def setCharge(self,charge):
        self._charge = charge
    
    def getCharge(self):
        return self._charge

    def setBoundingBox(self,minRT,maxRT,minMZ,maxMZ):
        self._minRT = minRT
        self._maxRT = maxRT
        self._minMZ = minMZ
        self._maxMZ = maxMZ
        
    def getBoundingBox(self):
        return self._minRT,self._maxRT,self._minMZ,self._maxMZ
 
    def addSpectrumId(self,spectrumId):
        self._spectraIds.append(spectrumId)
               
    def getSpectraIds(self):
        return self._spectraIds


class GlyxXMLFile:
    # Input/Output file of glyxXML file
    def __init__(self):
        self.parameters = GlyxXMLParameters()
        self.spectra = []
        self.features = []

    def _parseParameters(self,xmlParameters):
        timestamp = xmlParameters.find("./timestamp").text
        tolerance = float(xmlParameters.find("./tolerance").text)
        ionThreshold = int(xmlParameters.find("./ionthreshold").text)
        nrNeutrallosses = int(xmlParameters.find("./nrNeutrallosses").text)
        maxOxoniumCharge = int(xmlParameters.find("./maxOxoniumionCharge").text)
        scoreThreshold = float(xmlParameters.find("./scorethreshold").text)
        glycans = []
        for glycanElement in xmlParameters.findall("./glycans/glycan"):
            glycans.append(glycanElement.text)
            
        parameters = GlyxXMLParameters()
        parameters.setTimestamp(timestamp)
        parameters.setMassTolerance(tolerance)
        parameters.setIonThreshold(ionThreshold)
        parameters.setNrNeutrallosses(nrNeutrallosses)
        parameters.setMaxOxoniumCharge(maxOxoniumCharge)
        parameters.setScoreThreshold(scoreThreshold)
        parameters.setGlycanList(glycans)
        
        return parameters
        
    def _parseSpectra(self,xmlSpectra):
        spectra = []
        for s in xmlSpectra:
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
        return spectra
        

     
    def _writeParameters(self,xmlParameters):
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
        
    def _writeSpectra(self,xmlSpectra):
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
                    
    def _writeFeatures(self,xmlFeatures):
        for feature in self.features:
            xmlFeature = ET.SubElement(xmlFeatures,"feature")
            
            xmlFeatureId = ET.SubElement(xmlFeature,"id")
            xmlFeatureId.text = str(feature.getId())
            
            xmlFeatureRT = ET.SubElement(xmlFeature,"rt")
            xmlFeatureRT.text = str(feature.getRT())
            
            xmlFeatureMZ = ET.SubElement(xmlFeature,"mz")
            xmlFeatureMZ.text = str(feature.getMZ())
            
            xmlFeatureIntensity = ET.SubElement(xmlFeature,"intensity")
            xmlFeatureIntensity.text = str(feature.getIntensity())
            
            xmlFeatureCharge = ET.SubElement(xmlFeature,"charge")
            xmlFeatureCharge.text = str(feature.getCharge())
            
            minRT,maxRT,minMZ,maxMZ = feature.getBoundingBox()
            
            xmlFeatureMinRT = ET.SubElement(xmlFeature,"minRT")
            xmlFeatureMinRT.text = str(minRT)               
            
            xmlFeatureMaxRT = ET.SubElement(xmlFeature,"maxRT")
            xmlFeatureMaxRT.text = str(maxRT)
            
            xmlFeatureMinMZ = ET.SubElement(xmlFeature,"minMZ")
            xmlFeatureMinMZ.text = str(minMZ)               
            
            xmlFeatureMaxMZ = ET.SubElement(xmlFeature,"maxMZ")
            xmlFeatureMaxMZ.text = str(maxMZ)
            
            xmlFeatureSpectraIds = ET.SubElement(xmlFeature,"spectraIds")
            
            for spectrumId in feature.getSpectraIds():
                xmlFeatureSpectraId = ET.SubElement(xmlFeatureSpectraIds,"id")
                xmlFeatureSpectraId.text = str(spectrumId)
                
                
    def _parseFeatures(self,xmlFeatures):
        features = []
        for xmlFeature in xmlFeatures:
            feature = GlyxXMLFeature()
            feature.setId(int(xmlFeature.find("./id").text))
            feature.setRT(float(xmlFeature.find("./rt").text))
            feature.setMZ(float(xmlFeature.find("./mz").text))
            feature.setIntensity(float(xmlFeature.find("./intensity").text))
            feature.setCharge(int(xmlFeature.find("./charge").text))
            
            minRT = float(xmlFeature.find("./minRT").text)
            maxRT = float(xmlFeature.find("./maxRT").text)
            minMZ = float(xmlFeature.find("./minMZ").text)
            maxMZ = float(xmlFeature.find("./maxMZ").text)
            
            feature.setBoundingBox(minRT,maxRT,minMZ,maxMZ)
            for spectrumId in xmlFeature.findall("./spectraIds/id"):
                feature.addSpectrumId(spectrumId.text)
            features.append(feature)
            
        return features
       
    def writeToFile(self,path):
        xmlRoot = ET.Element("glyxXML")
        xmlParameters = ET.SubElement(xmlRoot,"parameters")
        xmlSpectra = ET.SubElement(xmlRoot,"spectra")
        xmlFeatures = ET.SubElement(xmlRoot,"features")
        # write parameters
        self._writeParameters(xmlParameters)
        # write spectra
        self._writeSpectra(xmlSpectra)
        # write features
        self._writeFeatures(xmlFeatures)
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
        parameters = self._parseParameters(root.find(".//parameters"))
        # parse spectra
        spectra = self._parseSpectra(root.findall("./spectra/spectrum"))
        # parse features
        features = self._parseFeatures(root.findall("./features/feature"))
        # assign data to object
        self.parameters = parameters
        self.spectra = spectra
        self.features = features

    def setParameters(self,parameters):
        self.parameters = parameters

    def getParameters(self):
        return self.parameters
    
    def addSpectrum(self,glyxXMLSpectrum):
        self.spectra.append(glyxXMLSpectrum)
        
    def addFeature(self,glyxXMLFeature):
        self.features.append(glyxXMLFeature)


    
    
        



