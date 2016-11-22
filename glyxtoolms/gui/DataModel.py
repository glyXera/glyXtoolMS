import glyxtoolms
import os
import configparser
import tkFont
from pkg_resources import resource_stream
import pickle
import base64
import Tkinter

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
        
        self.resources = {}

        # read settings
        self.readSettings()
        
        # read resources
        self.loadResources()
        
    def runFilters(self): # check filters
        hasActiveFilter = False
        for key in self.filters:
            if len(self.filters[key]) > 0:
                hasActiveFilter = True
                break
  
        self.classes["main"].setActiveFilterHint(hasActiveFilter)
        if self.currentAnalysis == None:
            return

        for spectrum in self.currentAnalysis.analysis.spectra:
            spectrum.passesFilter = True
            for f in self.filters["Scoring"]:
                try:
                    if not f.evaluate(spectrum):
                        spectrum.passesFilter = False
                        break
                except:
                    raise Exception("Cannot evaluate Filter", f)

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
                try:
                    if not f.evaluate(feature, timescale=self.timescale):
                        feature.passesFilter = False
                        break
                except:
                    raise Exception("Cannot evaluate Filter", f)
        for hit in self.currentAnalysis.analysis.glycoModHits:
            hit.passesFilter = True
            if hit.feature.passesFilter == False:
                hit.passesFilter = False
                continue
            for f in self.filters["Identification"]:
                try:
                    if not f.evaluate(hit):
                        hit.passesFilter = False
                        break
                except:
                    raise Exception("Cannot evaluate Filter", f)

    def readSettings(self):
        home = os.path.expanduser("~")
        settingspath = os.path.join(home, '.glyxtoolms.ini')
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
        settingspath = os.path.join(home, '.glyxtoolms.ini')
        config = configparser.ConfigParser()
        config["DEFAULT"] = {}
        config["DEFAULT"]["workingdir"] = self.workingdir
        config["DEFAULT"]["timescale"] = self.timescale
        with open(settingspath, 'w') as configfile:
            config.write(configfile)
            
    def loadResources(self):
        
        # load table with isotope distibution confidence intervals
        # get pickled res
        pickle_obj = resource_stream('glyxtoolms', 'gui/resources/isotope_confidence.pickle')
        self.resources["isotopes"] = pickle.load(pickle_obj)
        stream = resource_stream('glyxtoolms', 'gui/resources/drag.gif')
        self.resources["drag"] = Tkinter.PhotoImage(data = base64.encodestring(stream.read()))
        stream = resource_stream('glyxtoolms', 'gui/resources/zoom_in.gif')
        self.resources["zoom_in"] = Tkinter.PhotoImage(data = base64.encodestring(stream.read()))
        stream = resource_stream('glyxtoolms', 'gui/resources/zoom_out.gif')
        self.resources["zoom_out"] = Tkinter.PhotoImage(data = base64.encodestring(stream.read()))
        stream = resource_stream('glyxtoolms', 'gui/resources/zoom_auto.gif')
        self.resources["zoom_auto"] = Tkinter.PhotoImage(data = base64.encodestring(stream.read()))
        stream = resource_stream('glyxtoolms', 'gui/resources/ruler.gif')
        self.resources["ruler"] = Tkinter.PhotoImage(data = base64.encodestring(stream.read()))
        stream = resource_stream('glyxtoolms', 'gui/resources/eye.gif')
        self.resources["eye"] = Tkinter.PhotoImage(data = base64.encodestring(stream.read()))


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

    def __init__(self,model, project, path):
        self.model = model
        self.path = path
        self.project = project
        self.name = os.path.basename(path)
        self.analysis = None
        self.projectItem = None
        self.spectraIds = {}
        self.featureIds = {}
        self.data = []
        self.sorting = {}
        self.chromatograms = {}
        self.selectedChromatogram = None
        self.currentFeature = None
        self.featureSpectra = {} # Container for MS1 spectra within the feature, for faster chromatogram / Sum spectra generation

    def createIds(self):
        self.createSpectraIds()
        self.createFeatureIds()

    def createSpectraIds(self):
        self.spectraIds = {}
        i = 0
        for spectrum in self.analysis.spectra:
            i += 1
            spectrum.chromatogramSpectra = []
            spectrum.index = str(i)
            self.spectraIds[spectrum.nativeId] = spectrum

    def createFeatureIds(self):
        self.featureIds = {}
        i = 0
        for feature in self.analysis.features:
            i += 1
            feature.index = str(i) # TODO: Warp feature
            self.featureIds[feature.getId()] = feature

    def collectFeatureSpectra(self):
        # collect spectra within feature
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


    def removeFeature(self, feature):
        if feature in self.analysis.features:
            self.analysis.features.remove(feature)
        if feature.getId() in self.featureSpectra:
            self.featureSpectra.pop(feature.getId())
        if feature.getId() in self.featureIds:
            self.featureIds.pop(feature.getId())
        #remove from spectra
        for spectrum in feature.spectra:
            spectrum.remove(feature)
        # remove corresponding hits
        for hit in feature.hits:
            self.analysis.glycoModHits.remove(hit)

    def removeIdentification(self, hit):
        if hit in self.analysis.glycoModHits:
            self.analysis.glycoModHits.remove(hit)

    def featureEdited(self, feature):
        if self.analysis == None:
            return
        minRT, maxRT, minMZ, maxMZ = feature.getBoundingBox()
        
        # check if new spectra fall within feature bounds
        for spectrum in self.analysis.spectra:
            if (minRT <= spectrum.rt <= maxRT and 
                minMZ <= spectrum.precursorMass <= maxMZ):
                feature.addSpectrum(spectrum)    
            else:
                feature.removeSpectrum(spectrum)
        # delete features that fall within bounds
        
        # update identifications
        for hit in feature.hits:
            mass = hit.peptide.mass+hit.glycan.mass+glyxtoolms.masses.MASS["H+"]
            precursormass = (feature.mz*feature.charge-
                              glyxtoolms.masses.MASS["H+"]*(feature.charge-1))
            diff = mass- precursormass
            hit.error = diff
        
        # remove possible identifications
        
        # update views
        #self.model.classes["TwoDView"].paintObject()
        self.model.classes["NotebookFeature"].updateFeature(feature)
        self.model.classes["NotebookFeature"].updateSpectrumTree()
        self.model.classes["NotebookFeature"].clickedFeatureTree(None)

