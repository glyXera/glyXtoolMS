"""
Provides the i/o methods used in the pipeline
Contains for example:
- GlyxXMLSpectrum
- XMLPeptideFile
- GlyxXMLFeature
- GlyxXMLFile

For example usage of the glyML file:
f = GlyxXMLFile()
f.loadFromFile(path)
f.writeToFile(path)

"""

from lxml import etree as ET
import re
import numpy as np
import glyxtoolms
   

class Annotation(object):
    
    def __init__(self):
        self.x1 = 0
        self.x2 = 0
        #self.y = 0
        self.text = ""
        self.lookup = ""
        self.series = ""
        self.show = "lookup" #{"mass", "lookup", "text", "none"}
        #self.nr = 0
        self.level = 0
        self.items = {}
        self.valid = True
        
class AnnotationSeries(object):
    
    def __init__(self):
        self.name = "None"
        self.color = "black"
        self.hidden = False
        self.annotations = []

class GlyxXMLSpectrum(object):
    """ Define the GlyxXMLSpectrum as used in the glyML format """
    def __init__(self):
        self.nativeId = ""
        self.rt = 0.0
        self.ionCount = 0
        self.monoisotopicMass = 0.0
        self.precursorMass = 0
        self.precursorCharge = 0
        self.precursorIntensity = 0
        self.logScore = 10
        self.ions = {}
        self.isGlycopeptide = False
        self.status = ConfirmationStatus.Unknown
        self.annotations = []
        self.features = set() # convinience accessor for features

    def setNativeId(self, nativeId):
        """ Set the native spectrum ID """
        self.nativeId = nativeId

    def setRT(self, rt):
        """ Set the spectrum retention time """
        self.rt = rt

    def setIonCount(self, ionCount):
        """ Set the ion count of the spectrum """
        if ionCount == 0:
            self.ionCount = 0
        else:
            self.ionCount = ionCount

    def setLogScore(self, logScore):
        """ Set the calculated logScore of the spectrum """
        self.logScore = logScore

    def setIsGlycopeptide(self, boolean):
        """ Set the glycopeptide identify of the spectrum True/False """
        self.isGlycopeptide = boolean

    def addIon(self, glycan, ionName, mass, intensity):
        """ Add a reporter ion to the spectrum with the glycan,
            the ionname, the theorectical mass and intensity of the ion"""
        if not glycan in self.ions:
            self.ions[glycan] = {}
        self.ions[glycan][ionName] = {}
        self.ions[glycan][ionName]["mass"] = mass
        self.ions[glycan][ionName]["intensity"] = intensity


    def getNativeId(self):
        """ Get the native spectrum ID """
        return self.nativeId

    def getRT(self):
        """ Get the retention time of the spectrum """
        return self.rt

    def getIonCount(self):
        """ Get the ion count of the spectrum """
        return self.ionCount

    def getPrecursorMass(self):
        """ Get the precursor mass"""
        return self.precursorMass

    def getPrecursorCharge(self):
        """ Get the precursor charge"""
        return self.precursorCharge

    def getLogScore(self):
        """ Get the calculate logScore of the spectrum """
        return self.logScore

    def getIons(self):
        """ Get the reporter ions of the spectrum
        Contains a dictionary of the format
        dict[glycan][ionname]["mass"] or dict[glycan][ionname]["intensity"]"""
        return self.ions

    def getIsGlycopeptide(self):
        """ Get if the spectrum was identified as a glycopeptide spectrum"""
        return self.isGlycopeptide




class GlyxXMLParameters(object):
    """ Parameter class for glyML file"""
    def __init__(self):
        self._timestamp = ""
        self._glycans = []
        self._tolerance = 0.0
        self._ionThreshold = 0
        self._nrNeutrallosses = 0
        self._maxOxoniumCharge = 0
        self._scoreThreshold = 0
        self._sourceFilePath = ""
        self._sourceFileChecksum = ""


    def setTimestamp(self, timestamp):
        self._timestamp = timestamp

    def setMassTolerance(self, tolerance):
        self._tolerance = tolerance

    def setIonThreshold(self, ionThreshold):
        self._ionThreshold = ionThreshold

    def setNrNeutrallosses(self, nrNeutrallosses):
        self._nrNeutrallosses = nrNeutrallosses

    def setMaxOxoniumCharge(self, maxOxoniumCharge):
        self._maxOxoniumCharge = maxOxoniumCharge

    def setScoreThreshold(self, scoreThreshold):
        self._scoreThreshold = scoreThreshold

    def setGlycanList(self, glycans):
        self._glycans = glycans

    def addGlycan(self, glycan):
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

    def getSourceFilePath(self):
        return self._sourceFilePath

    def setSourceFilePath(self, path):
        self._sourceFilePath = path

    def getSourceFileChecksum(self):
        return self._sourceFileChecksum

    def setSourceFileChecksum(self, checksum):
        self._sourceFileChecksum = checksum

class ConfirmationStatus(object):
    
    Unknown = "Unknown"
    Deleted = "Deleted"
    Accepted = "Accepted"
    Rejected = "Rejected"
    Glycopeptide = "Glycopeptide"
    NonGlycopeptide = "NonGlycopeptide"
    PoorGlycopeptide = "PoorGlycopeptide"
    PoorNonGlycopeptide = "PoorNonGlycopeptide"
    _types = ["Unknown",
              "Deleted", 
              "Accepted", 
              "Rejected", 
              "Glycopeptide", 
              "NonGlycopeptide", 
              "PoorGlycopeptide", 
              "PoorNonGlycopeptide"]

class GlyxXMLFeature(object):

    def __init__(self):
        self.id = ""
        self.mz = 0.0
        self.rt = 0.0
        self.intensity = 0.0
        self.charge = 0
        self.minRT = 0.0
        self.maxRT = 0.0
        self.minMZ = 0.0
        self.maxMZ = 0.0
        self.status = ConfirmationStatus.Unknown
        self.spectraIds = set()
        self.spectra = []
        self.annotations = []
        self.consensus = []
        self.hits = set()

    def setId(self, id):
        self.id = id

    def getId(self):
        return self.id

    def setMZ(self, mz):
        self.mz = mz

    def getMZ(self):
        return self.mz

    def setIntensity(self, intensity):
        self.intensity = intensity

    def getIntensity(self):
        return self.intensity

    def setRT(self, rt):
        self.rt = rt

    def getRT(self):
        return self.rt

    def setCharge(self, charge):
        self.charge = charge

    def getCharge(self):
        return self.charge

    def setBoundingBox(self, minRT, maxRT, minMZ, maxMZ):
        self.minRT = minRT
        self.maxRT = maxRT
        self.minMZ = minMZ
        self.maxMZ = maxMZ

    def getBoundingBox(self):
        return self.minRT, self.maxRT, self.minMZ, self.maxMZ

    def addSpectrumId(self, spectrumId):
        self.spectraIds.add(spectrumId)
        
    def addSpectrum(self, spectrum):
        """ Add spectrum to feature """
        if not spectrum in self.spectra:
            self.addSpectrumId(spectrum.nativeId)
            self.spectra.append(spectrum)
            spectrum.features.add(self)
            
    def removeSpectrum(self, spectrum):
        """ Remove spectrum from feature, if exists """
        if spectrum in self.spectra:
            self.spectra.remove(spectrum)
        if spectrum.nativeId in self.spectraIds:
            self.spectraIds.remove(spectrum.nativeId)
        if self in spectrum.features:
            spectrum.features.remove(self)

    def getSpectraIds(self):
        return self.spectraIds
        
    def copy(self):
        new = GlyxXMLFeature()
        new.id = self.id
        new.mz = self.mz
        new.rt = self.rt
        new.intensity = self.intensity
        new.charge = self.charge
        new.minRT = self.minRT
        new.maxRT = self.maxRT
        new.minMZ = self.minMZ
        new.maxMZ = self.maxMZ
        new.status = self.status
        new.spectraIds = set(self.spectraIds)
        new.spectra = list(self.spectra)
        new.annotations = list(self.annotations)
        new.consensus = list(self.consensus)
        new.hits = set(self.hits)
        return new

class XMLGlycan(object):

    def __init__(self):
        self.composition = ""
        self.mass = 0.0


class GlyxXMLGlycoModHit(object):

    def __init__(self):
        self.featureID = ""
        self.feature = None
        self.peptide = None
        self.glycan = None
        self.error = 0.0
        self.status = ConfirmationStatus.Unknown
        self.fragments = {}

class GlyxXMLConsensusPeak(object):

    def __init__(self, x, y):
        self.x = x
        self.y = y

class GlyxXMLFile(object):
    # Input/Output file of glyxXML file
    def __init__(self):
        self.parameters = GlyxXMLParameters()
        self.spectra = []
        self.features = []
        self.glycoModHits = []
        self._version_ = "0.1.1" # current version
        self.version = self._version_ # will be overwritten by file

    def _parseParameters(self, xmlParameters):
        timestamp = xmlParameters.find("./timestamp").text
        if self.version > "0.0.2":
            sourcePath = xmlParameters.find("./source/path").text
            sourceHash = xmlParameters.find("./source/checksum").text

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
        if self.version > "0.0.2":
            parameters.setSourceFilePath(sourcePath)
            parameters.setSourceFileChecksum(sourceHash)

        return parameters

    def _parseSpectra(self, xmlSpectra):
        spectra = []
        for s in xmlSpectra:
            spectrum = GlyxXMLSpectrum()
            # Version 0.0.1
            nativeId = s.find("./nativeId").text
            spectrum.setNativeId(nativeId)
            ionCount = float(s.find("./ionCount").text)
            spectrum.setIonCount(ionCount)
            logScore = float(s.find("./logScore").text)
            spectrum.setLogScore(logScore)
            rt = float(s.find("./rt").text)
            spectrum.setRT(rt)
            
            if self.version > "0.0.8":                
                spectrum.precursorMass = float(s.find("./precursorMass").text)
                spectrum.precursorCharge = int(s.find("./precursorCharge").text)
                spectrum.precursorIntensity = float(s.find("./precursorIntensity").text)
                spectrum.monoisotopicMass = float(s.find("./monoisotopicMass").text)
                
            else:
                spectrum.precursorMass = float(s.find("./precursor/mass").text)
                spectrum.precursorCharge = int(s.find("./precursor/charge").text)
                if self.version > "0.0.6":
                    spectrum.precursorIntensity = float(s.find("./precursor/intensity").text)
                spectrum.monoisotopicMass  = spectrum.precursorMass
                
            for score in s.findall("./scores/score"):
                glycan = score.find("./glycan").text
                for ion in score.findall("./ions/ion"):
                    ionName = ion.find("./name").text
                    ionMass = float(ion.find("./mass").text)
                    ionIntensity = float(ion.find("./intensity").text)
                    spectrum.addIon(glycan, ionName, ionMass, ionIntensity)
            # version 0.0.2
            if self.version > "0.0.1":
                spectrum.setIsGlycopeptide(bool(int(s.find("./isGlycopeptide").text)))
            if self.version > "0.0.5":
                spectrum.status = s.find("./status").text
            if self.version > "0.0.7":
                self._parseAnnotations(s, spectrum)
                #spectrum.annotations = {}
                #annotations = []
                #for xmlAnn in s.findall("./annotations/annotation"):
                #    ann = Annotation()
                #    ann.text = xmlAnn.find("./text").text
                #    ann.x1 = float(xmlAnn.find("./x1").text)
                #    ann.x2 = float(xmlAnn.find("./x2").text)
                #spectrum.annotations["NoName"] = annotations
                
            spectra.append(spectrum)

        return spectra

    def _writeParameters(self, xmlParameters):
        # write search parameters
        xmlParametersDate = ET.SubElement(xmlParameters, "timestamp")
        xmlParametersDate.text = str(self.parameters.getTimestamp())

        xmlParametersSource = ET.SubElement(xmlParameters, "source")

        xmlSourcePath = ET.SubElement(xmlParametersSource, "path")
        xmlSourcePath.text = self.parameters.getSourceFilePath()

        xmlSourceHash = ET.SubElement(xmlParametersSource, "checksum")
        xmlSourceHash.text = self.parameters.getSourceFileChecksum()

        xmlParametersGlycans = ET.SubElement(xmlParameters, "glycans")
        for glycan in self.parameters.getGlycans():
            xmlParametersGlycan = ET.SubElement(xmlParametersGlycans, "glycan")
            xmlParametersGlycan.text = glycan

        xmlParametersTol = ET.SubElement(xmlParameters, "tolerance")
        xmlParametersTol.text = str(self.parameters.getMassTolerance())

        xmlParametersIonthreshold = ET.SubElement(xmlParameters, "ionthreshold")
        xmlParametersIonthreshold.text = str(self.parameters.getIonThreshold())

        xmlParametersNeutral = ET.SubElement(xmlParameters, "nrNeutrallosses")
        xmlParametersNeutral.text = str(self.parameters.getNrNeutrallosses())

        xmlParametersOxionCharge = ET.SubElement(xmlParameters, "maxOxoniumionCharge")
        xmlParametersOxionCharge.text = str(self.parameters.getMaxOxoniumCharge())

        xmlParametersScorethreshold = ET.SubElement(xmlParameters, "scorethreshold")
        xmlParametersScorethreshold.text = str(self.parameters.getScoreThreshold())

    def _writeSpectra(self, xmlSpectra):
        for spectrum in self.spectra:
            xmlSpectrum = ET.SubElement(xmlSpectra, "spectrum")
            xmlSpectrumNativeId = ET.SubElement(xmlSpectrum, "nativeId")
            xmlSpectrumNativeId.text = str(spectrum.getNativeId())
            xmlSpectrumRT = ET.SubElement(xmlSpectrum, "rt")
            xmlSpectrumRT.text = str(spectrum.getRT())
            xmlSpectrumIonCount = ET.SubElement(xmlSpectrum, "ionCount")
            xmlSpectrumIonCount.text = str(spectrum.getIonCount())
            if self._version_ > "0.0.8":
                xmlMonoMass = ET.SubElement(xmlSpectrum, "monoisotopicMass")
                xmlMonoMass.text = str(spectrum.monoisotopicMass)
                xmlPreMass = ET.SubElement(xmlSpectrum, "precursorMass")
                xmlPreMass.text = str(spectrum.getPrecursorMass())
                xmlPreCharge = ET.SubElement(xmlSpectrum, "precursorCharge")
                xmlPreCharge.text = str(spectrum.getPrecursorCharge())
                xmlPreIntensity = ET.SubElement(xmlSpectrum, "precursorIntensity")
                xmlPreIntensity.text = str(spectrum.precursorIntensity)
            else:
                xmlPrecursor = ET.SubElement(xmlSpectrum, "precursor")
                xmlPrecursorMass = ET.SubElement(xmlPrecursor, "mass")
                xmlPrecursorMass.text = str(spectrum.getPrecursorMass())
                xmlPrecursorCharge = ET.SubElement(xmlPrecursor, "charge")
                xmlPrecursorCharge.text = str(spectrum.getPrecursorCharge())
                xmlPrecursorIntensity = ET.SubElement(xmlPrecursor, "intensity")
                xmlPrecursorIntensity.text = str(spectrum.precursorIntensity)

            xmlTotalScore = ET.SubElement(xmlSpectrum, "logScore")
            xmlTotalScore.text = str(spectrum.getLogScore())
            if self.version > "0.0.1":
                xmlIsGlyco = ET.SubElement(xmlSpectrum, "isGlycopeptide")
                xmlIsGlyco.text = str(int(spectrum.getIsGlycopeptide()))
            xmlScoreList = ET.SubElement(xmlSpectrum, "scores")
            
            xmlStatus = ET.SubElement(xmlSpectrum, "status")
            xmlStatus.text = spectrum.status
            
            ions = spectrum.getIons()
            for glycan in ions:
                xmlScore = ET.SubElement(xmlScoreList, "score")
                xmlGlycanName = ET.SubElement(xmlScore, "glycan")
                xmlGlycanName.text = glycan
                xmlIons = ET.SubElement(xmlScore, "ions")
                for ionName in ions[glycan]:
                    xmlIon = ET.SubElement(xmlIons, "ion")
                    xmlIonName = ET.SubElement(xmlIon, "name")
                    xmlIonName.text = ionName
                    xmlIonMass = ET.SubElement(xmlIon, "mass")
                    xmlIonMass.text = str(ions[glycan][ionName]["mass"])
                    xmlIonIntensity = ET.SubElement(xmlIon, "intensity")
                    xmlIonIntensity.text = str(ions[glycan][ionName]["intensity"])
            # write spectrum annotations
            self._writeAnnotations(xmlSpectrum, spectrum)


    def _writeFeatures(self, xmlFeatures):
        for feature in self.features:
            xmlFeature = ET.SubElement(xmlFeatures, "feature")

            xmlFeatureId = ET.SubElement(xmlFeature, "id")
            xmlFeatureId.text = str(feature.getId())

            xmlFeatureRT = ET.SubElement(xmlFeature, "rt")
            xmlFeatureRT.text = str(feature.getRT())

            xmlFeatureMZ = ET.SubElement(xmlFeature, "mz")
            xmlFeatureMZ.text = str(feature.getMZ())

            xmlFeatureIntensity = ET.SubElement(xmlFeature, "intensity")
            xmlFeatureIntensity.text = str(feature.getIntensity())

            xmlFeatureCharge = ET.SubElement(xmlFeature, "charge")
            xmlFeatureCharge.text = str(feature.getCharge())

            minRT, maxRT, minMZ, maxMZ = feature.getBoundingBox()

            xmlFeatureMinRT = ET.SubElement(xmlFeature, "minRT")
            xmlFeatureMinRT.text = str(minRT)

            xmlFeatureMaxRT = ET.SubElement(xmlFeature, "maxRT")
            xmlFeatureMaxRT.text = str(maxRT)

            xmlFeatureMinMZ = ET.SubElement(xmlFeature, "minMZ")
            xmlFeatureMinMZ.text = str(minMZ)

            xmlFeatureMaxMZ = ET.SubElement(xmlFeature, "maxMZ")
            xmlFeatureMaxMZ.text = str(maxMZ)

            xmlFeatureSpectraIds = ET.SubElement(xmlFeature, "spectraIds")

            for spectrumId in feature.getSpectraIds():
                xmlFeatureSpectraId = ET.SubElement(xmlFeatureSpectraIds, "id")
                xmlFeatureSpectraId.text = str(spectrumId)

            xmlFeatureConsensus = ET.SubElement(xmlFeature, "consensusSpectrum")

            x = ";".join([str(round(c.x, 4)) for c in feature.consensus])
            y = ";".join([str(round(c.y, 2)) for c in feature.consensus])

            xmlFeatureConsensusX = ET.SubElement(xmlFeatureConsensus, "x")
            xmlFeatureConsensusX.text = x
            xmlFeatureConsensusY = ET.SubElement(xmlFeatureConsensus, "y")
            xmlFeatureConsensusY.text = y
            
            xmlStatus = ET.SubElement(xmlFeature, "status")
            xmlStatus.text = feature.status
            
            # write annotations
            self._writeAnnotations(xmlFeature, feature)
            


    def _writeGlycoModHits(self, xmlGlycoModHits):
        for glycoModHit  in self.glycoModHits:
            xmlHit = ET.SubElement(xmlGlycoModHits, "hit")

            xmlHitId = ET.SubElement(xmlHit, "featureId")
            xmlHitId.text = str(glycoModHit.featureID)

            # write peptide
            xmlPeptide = ET.SubElement(xmlHit, "peptide")
            glycoModHit.peptide._write(xmlPeptide)

            # write glycan, composition, mass
            xmlGlycan = ET.SubElement(xmlHit, "glycan")
            xmlGlycanComposition = ET.SubElement(xmlGlycan, "composition")
            xmlGlycanComposition.text = glycoModHit.glycan.composition
            xmlGlycanMass = ET.SubElement(xmlGlycan, "mass")
            xmlGlycanMass.text = str(glycoModHit.glycan.mass)

            xmlError = ET.SubElement(xmlHit, "error")
            xmlError.text = str(glycoModHit.error)
            
            xmlStatus = ET.SubElement(xmlHit, "status")
            xmlStatus.text = str(glycoModHit.status)

            # write identified fragments
            fragments = glycoModHit.fragments
            # sort fragments after mass
            sortedFragmentNames = sorted(fragments.keys(), key=lambda name: fragments[name]["mass"])
            xmlFragments = ET.SubElement(xmlHit, "fragments")
            for fragmentname in sortedFragmentNames:
                xmlFragment = ET.SubElement(xmlFragments, "fragment")
                xmlFragmentName = ET.SubElement(xmlFragment, "name")
                xmlFragmentName.text = fragmentname

                xmlFragmentSequence = ET.SubElement(xmlFragment, "sequence")
                xmlFragmentSequence.text = fragments[fragmentname]["sequence"]

                xmlFragmentMass = ET.SubElement(xmlFragment, "mass")
                xmlFragmentMass.text = str(fragments[fragmentname]["mass"])

                xmlFragmentCounts = ET.SubElement(xmlFragment, "counts")
                xmlFragmentCounts.text = str(fragments[fragmentname]["counts"])


    def _parseGlycoModHits(self, xmlGlycoModHits):
        hits = []
        for xmlHit in xmlGlycoModHits:
            hit = GlyxXMLGlycoModHit()
            hit.featureID = str(xmlHit.find("./featureId").text)
            hit.error = float(xmlHit.find("./error").text)

            glycan = XMLGlycan()
            glycan.composition = str(xmlHit.find("./glycan/composition").text)
            glycan.mass = float(xmlHit.find("./glycan/mass").text)
            hit.glycan = glycan

            peptide = XMLPeptide()
            peptide._parse(xmlHit.find("./peptide"))
            hit.peptide = peptide

            hit.fragments = {}
            if self.version > "0.0.3":
                for xmlfragment in xmlHit.findall("./fragments/fragment"):
                    fragment = {}
                    fragmentname = xmlfragment.find("./name").text
                    fragment["sequence"] = xmlfragment.find("./sequence").text
                    fragment["mass"] = float(xmlfragment.find("./mass").text)
                    fragment["counts"] = float(xmlfragment.find("./counts").text)
                    hit.fragments[fragmentname] = fragment
            if self.version > "0.0.5":
                hit.status = xmlHit.find("./status").text
            hits.append(hit)
        return hits

    def _parseFeatures(self, xmlFeatures):
        features = []
        for xmlFeature in xmlFeatures:
            feature = GlyxXMLFeature()
            feature.setId(xmlFeature.find("./id").text)
            feature.setRT(float(xmlFeature.find("./rt").text))
            feature.setMZ(float(xmlFeature.find("./mz").text))
            feature.setIntensity(float(xmlFeature.find("./intensity").text))
            feature.setCharge(int(xmlFeature.find("./charge").text))

            minRT = float(xmlFeature.find("./minRT").text)
            maxRT = float(xmlFeature.find("./maxRT").text)
            minMZ = float(xmlFeature.find("./minMZ").text)
            maxMZ = float(xmlFeature.find("./maxMZ").text)

            feature.setBoundingBox(minRT, maxRT, minMZ, maxMZ)
            for spectrumId in xmlFeature.findall("./spectraIds/id"):
                feature.addSpectrumId(spectrumId.text)

            if self.version > "0.0.4":
                try:
                    xString = xmlFeature.find("./consensusSpectrum/x").text
                    yString = xmlFeature.find("./consensusSpectrum/y").text
                    feature.consensus = []
                    for x, y in zip(xString.split(";"), yString.split(";")):
                        x = float(x)
                        y = float(y)
                        feature.consensus.append(GlyxXMLConsensusPeak(x, y))
                except:
                    print "Parsing error at "+feature.id
                    raise
            if self.version > "0.0.5":
                feature.status = xmlFeature.find("./status").text
            
            if self.version > "0.0.7":
                self._parseAnnotations(xmlFeature, feature)
                #feature.annotations = []
                #for xmlAnn in xmlFeature.findall("./annotations/annotation"):
                #    ann = Annotation()
                #    ann.text = xmlAnn.find("./text").text
                #    ann.x1 = float(xmlAnn.find("./x1").text)
                #    ann.x2 = float(xmlAnn.find("./x2").text)
                #    ann.y = float(xmlAnn.find("./y").text)
                #    feature.annotations.append(ann)
            features.append(feature)

        return features

    def _writeAnnotations(self, xmlAnnotationParent, parent):
        xmlAnnotations = ET.SubElement(xmlAnnotationParent, "annotations")
        for seriesName in parent.annotations:
            series = parent.annotations[seriesName]
            if len(series.annotations) == 0:
                continue
            xmlSeries = ET.SubElement(xmlAnnotations, "series", name=seriesName, color=series.color)
            for annotation in series.annotations:
                xmlAnn = ET.SubElement(xmlSeries, "annotation")
                xmlAnnText = ET.SubElement(xmlAnn, "text")
                xmlAnnText.text = annotation.text
                xmlAnnX1 = ET.SubElement(xmlAnn, "x1")
                xmlAnnX1.text = str(annotation.x1)
                xmlAnnX2 = ET.SubElement(xmlAnn, "x2")
                xmlAnnX2.text = str(annotation.x2)
                xmlAnnShow = ET.SubElement(xmlAnn, "show")
                xmlAnnShow.text = str(annotation.show)
                
    def _parseAnnotations(self,xmlAnnotationParent, parent):
        parent.annotations = {}
        if self.version < "0.1.0":
            series = AnnotationSeries()
            series.name = "None"
            seriesAnnotations = []
            for xmlAnn in xmlAnnotationParent.findall("./annotations/annotation"):
                ann = Annotation()
                ann.text = xmlAnn.find("./text").text
                ann.x1 = float(xmlAnn.find("./x1").text)
                ann.x2 = float(xmlAnn.find("./x2").text)
                ann.series = series.name
                series.annotations.append(ann)
            if len(series.annotations) > 0:
                parent.annotations[series.name] = series
        else:
            for xmlSeries in xmlAnnotationParent.findall("./annotations/series"):
                series = AnnotationSeries()
                series.name = xmlSeries.get("name")
                series.color = xmlSeries.get("color")
                for xmlAnn in xmlSeries.findall("./annotation"):
                    ann = Annotation()
                    ann.text = xmlAnn.find("./text").text
                    ann.x1 = float(xmlAnn.find("./x1").text)
                    ann.x2 = float(xmlAnn.find("./x2").text)
                    if self.version > "0.1.0":
                        ann.show = xmlAnn.find("./show").text
                    ann.series = series.name
                    series.annotations.append(ann)
                if len(series.annotations) > 0:
                    parent.annotations[series.name] = series

    def writeToFile(self, path):
        xmlRoot = ET.Element("glyxXML")
        # write version
        xmlVersion = ET.SubElement(xmlRoot, "version")
        xmlVersion.text = self._version_

        xmlParameters = ET.SubElement(xmlRoot, "parameters")
        xmlSpectra = ET.SubElement(xmlRoot, "spectra")
        xmlFeatures = ET.SubElement(xmlRoot, "features")
        xmlGlycomodHits = ET.SubElement(xmlRoot, "glycomod")

        # write parameters
        self._writeParameters(xmlParameters)
        # write spectra
        self._writeSpectra(xmlSpectra)
        # write features
        self._writeFeatures(xmlFeatures)
        # write glycoModHits
        self._writeGlycoModHits(xmlGlycomodHits)
        # writing to file
        xmlTree = ET.ElementTree(xmlRoot)
        f = file(path, "w")
        f.write(ET.tostring(xmlTree, pretty_print=True))
        f.close()


    def readFromFile(self, path):
        f = file(path, "r")
        root = ET.fromstring(f.read())
        f.close()
        # check version
        version = root.find(".//version")
        if version == None:
            self.version = "0.0.1"
        else:
            self.version = version.text
        # read parameters
        parameters = self._parseParameters(root.find(".//parameters"))
        # parse spectra
        spectra = self._parseSpectra(root.findall("./spectra/spectrum"))
        # parse features
        features = self._parseFeatures(root.findall("./features/feature"))
        # parse glycomod
        glycoMod = self._parseGlycoModHits(root.findall("./glycomod/hit"))
        
        #Link all data
        specIDs = {}
        featureIDs = {}
        for spec in spectra:
            specIDs[spec.getNativeId()] = spec
            
        for feature in features:
            featureIDs[feature.id] = feature
            feature.spectra = []
            for specID in feature.spectraIds:
                spectrum = specIDs[specID]
                feature.spectra.append(spectrum)
                spectrum.features.add(feature)
        for hit in glycoMod:
            hit.feature = featureIDs[hit.featureID]
            hit.feature.hits.add(hit)
        
        # assign data to object
        self.parameters = parameters
        self.spectra = spectra
        self.features = features
        self.glycoModHits = glycoMod

    def setParameters(self, parameters):
        self.parameters = parameters

    def getParameters(self):
        return self.parameters

    def addSpectrum(self, glyxXMLSpectrum):
        self.spectra.append(glyxXMLSpectrum)

    def addFeature(self, glyxXMLFeature):
        self.features.append(glyxXMLFeature)


class XMLPeptide(object):

    def __init__(self):
        self.proteinID = ""
        self.sequence = ""
        self.start = -1
        self.end = -1
        self.mass = 0.0
        self.modifications = []
        self.glycosylationSites = []

    def copy(self):
        new = XMLPeptide()
        new.proteinID = self.proteinID
        new.sequence = self.sequence
        new.start = self.start
        new.end = self.end
        new.mass = self.mass
        new.modifications = self.modifications
        new.glycosylationSites = self.glycosylationSites
        return new

    def toString(self):
        s = self.sequence
        modi = {}
        for mod, pos in sorted(self.modifications, key=lambda x:x[1], reverse=True):
            if pos == -1:
                modi[mod] = modi.get(mod, 0) + 1
            else:
                s = s[:pos+1] + "("+mod+")"+ s[pos+1:]
        for mod in modi:
            s += " ("+mod+")"+str(modi[mod])
        return s
        
    def fromString(self, string):
        """ Peptide sequence: EE(Cys_CAM)QFNS(+CHO)TF(-OH)R Cys_CAM(-1) MSO(-1)  """
        string = string.strip()
        sp = string.split(" ")
        
        rawsequence = sp[0]
        self.modifications = []

        # extract modifications from sequence
        currentlyInMod = False
        e = -1
        self.sequence = ""
        for i in range(0, len(rawsequence)):
            letter = rawsequence[i]
            if letter == "(":
                currentlyInMod = True
                mod = ""
                pos = e
                continue
            elif letter == ")":
                currentlyInMod = False
                self.modifications.append((mod, pos))
                continue
            if currentlyInMod == False:
                assert letter in glyxtoolms.masses.AMINOACID
                self.sequence += letter
                e += 1
            else:
                mod += letter

        for modstring in sp[1:]:
            # check if modification is properly separated
             # check if mod is like CAM(-1,-1) or (CAM)1
            for match in re.findall(".+?\([,\d\W]+\)", modstring):
                mod = re.search("[A-z]+\(", match).group()[:-1].upper()
                assert mod in glyxtoolms.masses.PROTEINMODIFICATION
                for posstring in re.search("\(.+\)", match).group()[1:-1].split(","):
                        pos = int(posstring)
                        self.modifications.append((mod, pos))
            for match in re.findall("\(.+?\)\d+", modstring):
                mod = re.search("\(.+?\)", match).group()[1:-1].upper()
                amount =  int(re.search("\d+$", match).group())
                for i in range(0, amount):
                    self.modifications.append((mod,  -1))
        
        self.mass = glyxtoolms.masses.calcPeptideMass(self)
        
    def testModificationValidity(self):
        """ Checks validity of the supplied modifications """
        if len(self.modifications) == 0:
            return True
        X = []
        for mod,pos in self.modifications:
            line = [0]*len(self.sequence)
            if pos > -1:
                line[pos] = 1
            else:
                targets = glyxtoolms.masses.getModificationTargets(mod)
                if "NTERM" in targets:
                    line[0] = 1
                if "CTERM" in targets:
                    line[-1] = 1   
                for pos,amino in enumerate(self.sequence):
                    if amino in targets:
                        line[pos] = 1
            X.append(line)

        matrix = np.array(X)

        for row in range(0, matrix.shape[0]):
            #find all rows with 1s, get the one with the lowest sum
            hits = []
            for col in range(0, matrix.shape[1]):
                if matrix[row,col] == 1:
                    hits.append((col,sum(matrix[:,col])))
            # get minimum sum
            if len(hits) == 0:
                return False
            col = min(hits,key=lambda x:x[1])[0]
            # set column and row to zero
            matrix[row,:] = 0
            matrix[:,col] = 0
            matrix[row,col] = 1

        # check validity
        for row in range(0, matrix.shape[0]):
            if sum(matrix[row,:]) != 1:
                return False

        for col in range(0, matrix.shape[1]):
            if sum(matrix[:,col]) > 1:
                return False
        return True

    def _parse(self, xmlPeptide):
        self.proteinID = xmlPeptide.find("./proteinId").text
        self.sequence = xmlPeptide.find("./sequence").text
        self.start = int(xmlPeptide.find("./start").text)
        self.end = int(xmlPeptide.find("./end").text)
        self.mass = float(xmlPeptide.find("./mass").text)


        for xmlMod in xmlPeptide.findall("./modifications/modification"):
            name = xmlMod.find("./name").text
            pos = int(xmlMod.find("./position").text)
            self.modifications.append((name, pos))

        for xmlSite in xmlPeptide.findall("./glycosylationsites/glycosylationsite"):
            typ = xmlSite.find("./type").text
            pos = int(xmlSite.find("./position").text)
            self.glycosylationSites.append((pos, typ))
        return

    def _write(self, xmlPeptide):
        xmlSequence = ET.SubElement(xmlPeptide, "sequence")
        xmlSequence.text = self.sequence

        xmlProteinId = ET.SubElement(xmlPeptide, "proteinId")
        xmlProteinId.text = self.proteinID

        xmlStart = ET.SubElement(xmlPeptide, "start")
        xmlStart.text = str(self.start)

        xmlEnd = ET.SubElement(xmlPeptide, "end")
        xmlEnd.text = str(self.end)

        xmlMass = ET.SubElement(xmlPeptide, "mass")
        xmlMass.text = str(self.mass)

        xmlModifications = ET.SubElement(xmlPeptide, "modifications")
        for mod, pos in self.modifications:
            xmlMod = ET.SubElement(xmlModifications, "modification")

            xmlModName = ET.SubElement(xmlMod, "name")
            xmlModName.text = mod

            xmlModPos = ET.SubElement(xmlMod, "position")
            xmlModPos.text = str(pos)

        xmlSites = ET.SubElement(xmlPeptide, "glycosylationsites")
        for pos, typ in self.glycosylationSites:
            xmlSite = ET.SubElement(xmlSites, "glycosylationsite")
            xmlSitePos = ET.SubElement(xmlSite, "position")
            xmlSitePos.text = str(pos)
            xmlSiteTyp = ET.SubElement(xmlSite, "type")
            xmlSiteTyp.text = typ
        return

class XMLPeptideParameters(object):

    def __init__(self):
        self.proteins = []
        #self.data = []
        self.digestionEnzymes = []
        self.NGlycosylation = False
        self.OGlycosylation = False
        self.modifications = []
        self.missedCleavages = 0



class XMLPeptideFile(object):

    def __init__(self):
        self.peptides = []
        self.parameters = XMLPeptideParameters()


    def _writeParameters(self, xml):
        parameters = self.parameters
        xmlProteins = ET.SubElement(xml, "proteins")
        for protein in parameters.proteins:
            xmlProtein = ET.SubElement(xmlProteins, "proteinIdentifier")
            xmlProtein.text = str(protein.identifier)
        xmlEnzymes = ET.SubElement(xml, "enzymes")
        xmlEnzymes.text = ", ".join(parameters.digestionEnzymes)
        glycosylations = []
        if parameters.NGlycosylation == True:
            glycosylations.append("N")
        if parameters.OGlycosylation == True:
            glycosylations.append("O")
        xmlGlycosylations = ET.SubElement(xml, "glycosylations")
        xmlGlycosylations.text = ", ".join(glycosylations)

        xmlModifications = ET.SubElement(xml, "modifications")
        xmlModifications.text = ", ".join(parameters.modifications)
        xmlmissedCleaveage = ET.SubElement(xml, "missedCleaveage")
        xmlmissedCleaveage.text = str(parameters.missedCleavages)

        return

    def _writePeptides(self, xmlPeptides):
        for peptide in self.peptides:
            xmlPeptide = ET.SubElement(xmlPeptides, "peptide")
            peptide._write(xmlPeptide)
        return

    def _parsePeptides(self, xmlPeptides):
        peptides = []

        for xmlPeptide in xmlPeptides:
            peptide = XMLPeptide()
            peptide._parse(xmlPeptide)
            peptides.append(peptide)

        return peptides

    def _parseParameters(self, xmlParameters):
        parameters = XMLPeptideParameters()
        return parameters

    def writeToFile(self, path):
        xmlRoot = ET.Element("xmlPeptides")
        xmlParameters = ET.SubElement(xmlRoot, "parameters")
        xmlPeptides = ET.SubElement(xmlRoot, "peptides")
        # write parameters
        self._writeParameters(xmlParameters)
        # write peptide
        self._writePeptides(xmlPeptides)
        # writing to file
        xmlTree = ET.ElementTree(xmlRoot)
        f = file(path, "w")
        f.write(ET.tostring(xmlTree, pretty_print=True))
        f.close()
        return

    def loadFromFile(self, path):
        f = file(path, "r")
        root = ET.fromstring(f.read())
        f.close()
        # read parameters
        parameters = self._parseParameters(root.find(".//parameters"))
        # parse spectra
        peptides = self._parsePeptides(root.findall("./peptides/peptide"))
        # assign data to object
        self.parameters = parameters
        self.peptides = peptides
        return

class GlycanCompositionFile(object):
    
    def __init__(self):
        self.glycans = []
        self.version = "1.0"
        
    def read(self, path):
        f = file(path,"r")
        self.glycans = []
        self.version = "1.0"
        for line in f:
            line = line.strip()
            if line.startswith("#"): # comment
                if line.startswith("#version:"):
                    self.version = line.split(":")[1]
                continue
            elif "," in line:
                typ,glycanstring = line.split(",")
                assert typ in ["?", "N", "O"]
                glycan = glyxtoolms.lib.Glycan(glycanstring.strip(),typ=typ.strip())
            else:
                glycan = glyxtoolms.lib.Glycan(line)
            self.glycans.append(glycan)
        f.close()
    
    def write(self,path):
        f = file(path,"w")
        f.write("#version:"+self.version+"\n")
        for glycan in self.glycans:
            f.write(glycan.typ + "," + glycan.toString() + "\n")
        f.close()
