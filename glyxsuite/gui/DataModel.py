import glyxsuite
import os
import configparser
import tkFont

class FilterMass:
    
    def __init__(self, value):
        self.value = value
    
    def evaluate(self, hit):
        # calculate glycopeptide mass
        mass = hit.glycan.mass + hit.peptide.mass
        if mass < self.value:
            return True
        return False

class DataModel(object):

    def __init__(self):

        #for s in range(10,100):
        #    font = tkFont.Font(family="Courier",size=s)
        #    print s, font.measure(" ")

        self.workingdir = ""
        self.timescale = "seconds"
        self.debug = None
        self.root = None
        self.projects = {}
        self.currentProject = None
        self.currentAnalysis = None
        self.filters = {"Identification":[], "Features":[], "Scoring":[]} # stores filter used to filter data
        self.classes = {} # Functionhandler - each class should register itself here

        # read settings
        self.readSettings()
        
    def runFilters(self): # check filters
        if self.currentAnalysis == None:
            return

        for spectrum in self.currentAnalysis.analysis.spectra:
            spectrum.passesFilter = True
            for f in self.filters["Scoring"]:
                if not f.evaluate(spectrum):
                    spectrum.passesFilter = False
                    break

        for feature in self.currentAnalysis.analysis.features:
            # remove features which have no MS2 spectra that pass the filter
            feature.passesFilter = False
            for spectrum in feature.spectra:
                if spectrum.passesFilter == True:
                    feature.passesFilter = True
                    break
                    
            if feature.passesFilter == False:
                continue

            for f in self.filters["Features"]:
                if not f.evaluate(feature, self.timescale):
                    feature.passesFilter = False
                    break

        for hit in self.currentAnalysis.analysis.glycoModHits:
            hit.passesFilter = True
            if hit.feature.passesFilter == False:
                hit.passesFilter = False
                continue
            for f in self.filters["Identification"]:
                if not f.evaluate(hit):
                    hit.passesFilter = False
                    break

    def readSettings(self):
        home = os.path.expanduser("~")
        settingspath = os.path.join(home, '.glyxsuite.ini')
        print "use settings under ", settingspath
        # Set default settings
        self.workingdir = home
        # Create settings if not exists
        if not os.path.exists(settingspath):
            self.saveSettings()
        config = configparser.ConfigParser()
        config.read(os.path.join(settingspath))
        self.workingdir = config["DEFAULT"]["workingdir"]
        if "timescale" in config["DEFAULT"]:
            self.timescale = config["DEFAULT"]["timescale"]
            

    def saveSettings(self):
        home = os.path.expanduser("~")
        settingspath = os.path.join(home, '.glyxsuite.ini')
        config = configparser.ConfigParser()
        config["DEFAULT"] = {}
        config["DEFAULT"]["workingdir"] = self.workingdir
        config["DEFAULT"]["timescale"] = self.timescale
        with open(settingspath, 'w') as configfile:
            config.write(configfile)

class Chromatogram(object):

    def __init__(self):
        self.name = ""
        self.color = "black"
        self.rangeLow = 0
        self.rangeHigh = 0
        self.plot = False
        self.rt = []
        self.intensity = []
        self.msLevel = 0
        self.selected = False

class Project(object):

    def __init__(self, name, path):
        self.name = name
        self.path = path
        self.mzMLFile = None
        self.analysisFiles = {}

class ContainerMZMLFile(object):

    def __init__(self, project, path):
        self.exp = None
        self.path = path
        self.project = project
        self.experimentIds = {}

    def createIds(self):
        self.experimentIds = {}
        ms1 = None
        for spec in self.exp:
            level = spec.getMSLevel()
            nativeId = spec.getNativeID()
            if level == 1:
                ms1 = spec
            elif level == 2:
                self.experimentIds[nativeId] = (spec, ms1)

class ContainerAnalysisFile(object):

    def __init__(self, project, path):
        self.path = path
        self.project = project
        self.name = os.path.basename(path)
        self.analysis = None
        self.projectItem = None
        self.spectraIds = {}
        self.featureIds = {}
        self.spectraInFeatures = {}
        self.data = []
        self.sorting = {}
        self.chromatograms = {}
        self.selectedChromatogram = None
        self.currentFeature = None
        self.featureSpectra = {} # Container for MS1 spectra within the feature, for faster chromatogram / Sum spectra generation
        self.featureHits = {} #feature -> hit link

    def createIds(self):
        self.spectraIds = {}
        self.spectraInFeatures = {}
        i = 0
        for spectrum in self.analysis.spectra:
            i += 1
            #c = ContainerSpectrum(spectrum)
            spectrum.chromatogramSpectra = []
            spectrum.index = str(i)
            self.spectraIds[spectrum.nativeId] = spectrum
            self.spectraInFeatures[spectrum.nativeId] = []

        # create featureIds
        # create feature - spectra link
        self.featureIds = {}
        i = 0
        for feature in self.analysis.features:
            i += 1
            feature.index = str(i) # TODO: Warp feature
            self.featureIds[feature.getId()] = feature
            for specID in feature.getSpectraIds():
                self.spectraInFeatures[specID].append(feature.getId())
        
        self.featureSpectra = {}
        for spec in self.project.mzMLFile.exp:
            if spec.getMSLevel() != 1:
                continue
            rt = spec.getRT()
            for feature in self.analysis.features:
                minRT, maxRT, minMZ, maxMZ = feature.getBoundingBox()
                if rt < minRT-60:
                    continue
                if rt > maxRT+60:
                    continue
                featureID = feature.getId()
                if not featureID in self.featureSpectra:
                    self.featureSpectra[featureID] = []
                self.featureSpectra[featureID].append(spec)
                
        # create feature -> hit link
        self.featureHits = {}
        for hit in self.analysis.glycoModHits:
            if not hit.featureID in self.featureHits:
                self.featureHits[hit.featureID] = []
            self.featureHits[hit.featureID].append(hit)

    def addNewSpectrum(self, nativeID):
        spectrum = glyxsuite.io.GlyxXMLSpectrum()
        spectrum.setNativeId(nativeID)
        self.spectraIds[nativeID] = spectrum
        self.analysis.spectra.append(spectrum)
        return spectrum

    def removeFeature(self, feature):
        if feature in self.analysis.features:
            self.analysis.features.remove(feature)
        if feature.getId() in self.featureSpectra:
            self.featureSpectra.pop(feature.getId())
        if feature.getId() in self.featureIds:
            self.featureIds.pop(feature.getId())
        for specId in  self.spectraInFeatures:
            if feature.getId() in  self.spectraInFeatures[specId]:
                self.spectraInFeatures[specId].remove(feature.getId())
        # remove corresponding hits
        for hit in self.featureHits.get(feature.getId(),[]):
            self.analysis.glycoModHits.remove(hit)
        if feature.getId() in self.featureHits:
            self.featureHits.pop(feature.getId())

    def removeIdentification(self, hit):
        if hit in self.analysis.glycoModHits:
            self.analysis.glycoModHits.remove(hit)
        self.featureHits[hit.featureID].remove(hit)



