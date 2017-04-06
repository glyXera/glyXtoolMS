import glyxtoolms
import os
import configparser
import tkFont
from pkg_resources import resource_stream
import pickle
import base64
import Tkinter
import pyperclip

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

    def __init__(self, root=None):

        #for s in range(10,100):
        #    font = tkFont.Font(family="Courier",size=s)
        #    print s, font.measure(" ")

        self.workingdir = ""
        self.timescale = "seconds"
        # possible clipboards: ('Tkinter','osx','gtk','qt','xclip','xsel','klipper','windows')
        self.clipboard = "Tkinter" # Switch indicating clipboard to use
        self.errorType = "Da"
        self.debug = None
        self.root = root
        self.projects = {}
        self.options = {}
        self.optionsConverter = {}
        self.currentProject = None
        self.currentAnalysis = None
        self.filters = {"Identification":[], "Features":[], "Scoring":[]} # stores filter used to filter data
        self.classes = {} # Functionhandler - each class should register itself here
        #self.textsize = {"default":{"axis:12, }} #container for textsizes of various canvases
        self.resources = {}
        self.toplevel = {} # store references to other toplevel windows
        self.configfile = None
        
        # register converter functions for settings
        self.registerOptionsConverterFunctions()
        
        # read settings
        self.readSettings()
        
        # read resources
        self.loadResources()
        
    def registerClass(self, name, theClass):
        #if name in self.classes:
        #    raise Exception("A class with the name "+name+" is already registered!")
        self.classes[name] = theClass

    def registerOptionsConverterFunctions(self):
        
        def registerFunction(model, name, to_String, fromString):
            if name in model.optionsConverter:
                return
            model.optionsConverter[name] = {}
            model.optionsConverter[name]["toString"] = to_String
            model.optionsConverter[name]["fromString"] = fromString
            
        def fontToString(font):
            return font["family"] + ","+str(font["size"])
            
        def stringToFont(string):
            family,size  = string.split(",")
            return tkFont.Font(family=family,size=int(size))
            
        # register converters for options
        registerFunction(self, "font", fontToString, stringToFont)
        registerFunction(self, "show", str, bool)
        registerFunction(self, "left", str, int)
        registerFunction(self, "right", str, int)
        registerFunction(self, "bottom", str, int)
        registerFunction(self, "top", str, int)
        registerFunction(self, "labelcolor", str, str)
        registerFunction(self, "oxcolor", str, str)
        registerFunction(self, "pepcolor", str, str)
        registerFunction(self, "shownames", str, bool)
        registerFunction(self, "showmasses", str, bool)
        registerFunction(self, "showox", str, bool)
        registerFunction(self, "showpep", str, bool)
        registerFunction(self, "showpicto", str, bool)
        
        
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
        self.configfile = configparser.ConfigParser()
        self.configfile.read(os.path.join(settingspath))
        
        if "GENERAL" in self.configfile.sections():
            section = self.configfile["GENERAL"]
            self.workingdir = section["workingdir"]
            if "timescale" in section:
                self.timescale = section["timescale"]
            if "clipboard" in section:
                self.clipboard = section["clipboard"]
            if "errorType" in section:
                self.errorType = section["errorType"]
                
        if "PLOTOPTIONS" in self.configfile.sections():
            section = self.configfile["PLOTOPTIONS"]
            for key in section:
                plotname, propty, typ = key.split(".")
                if typ in self.optionsConverter:
                    converter = self.optionsConverter[typ]["fromString"]
                    value = section[key]
                    self.options[plotname] = self.options.get(plotname, {})
                    self.options[plotname][propty] = self.options[plotname].get(propty, {})
                    self.options[plotname][propty][typ] = converter(value)
                else:
                    print "cannot load option", key
   
    def setLayout(self):
        if self.configfile == None:
            return
        if "LAYOUT" not in self.configfile.sections():
            return
        if not "main" in self.classes:
            return
        geometry = self.configfile["LAYOUT"]["geometry"]
        self.root.geometry(geometry)
        coords = {}
        for key in self.configfile["LAYOUT"]:
            if key.startswith("sashposition."):
                name = key.replace("sashposition.", "")
                value = self.configfile["LAYOUT"][key]
                x,y = value.split(",")
                coords[name] = (int(x), int(y))
        
        self.classes["main"].setSashCoords(coords)

    def saveSettings(self):
        if self.configfile == None:
            self.configfile = configparser.ConfigParser()
        self.configfile["GENERAL"] = {}
        self.configfile["GENERAL"]["workingdir"] = self.workingdir
        self.configfile["GENERAL"]["timescale"] = self.timescale
        self.configfile["GENERAL"]["clipboard"] = self.clipboard
        self.configfile["GENERAL"]["errorType"] = self.errorType

        # write plotting setting 
        self.configfile["PLOTOPTIONS"] = {}
        for plotname in self.options:
            for propty in self.options[plotname]:
                for typ in self.options[plotname][propty]:
                    value = self.options[plotname][propty][typ]
                    optionname = plotname+"."+propty+"."+typ
                    # convert value to string, based on the provided typ
                    if typ in self.optionsConverter:
                        converter = self.optionsConverter[typ]["toString"]
                        self.configfile["PLOTOPTIONS"][optionname] = converter(value)
                    else:
                        print "cannot save option", optionname
                        
        # write sash coordinates
        self.configfile["LAYOUT"] = {}
        self.configfile["LAYOUT"]["geometry"] = self.root.geometry()
        if "main" in self.classes:
            coords = self.classes["main"].getSashCoords()
            for key in coords:
                x,y = coords[key]
                self.configfile["LAYOUT"]["sashposition."+key] = str(x)+","+str(y)

        home = os.path.expanduser("~")
        settingspath = os.path.join(home, '.glyxtoolms.ini')
        with open(settingspath, 'w') as configfile:
            self.configfile.write(configfile)
            
        print "Settings saved to:", settingspath
            

            
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
        stream = resource_stream('glyxtoolms', 'gui/resources/drop_down.gif')
        self.resources["drop_down"] = Tkinter.PhotoImage(data = base64.encodestring(stream.read()))
        stream = resource_stream('glyxtoolms', 'gui/resources/filter.gif')
        self.resources["filter"] = Tkinter.PhotoImage(data = base64.encodestring(stream.read()))
        stream = resource_stream('glyxtoolms', 'gui/resources/ox.gif')
        self.resources["oxonium"] = Tkinter.PhotoImage(data = base64.encodestring(stream.read()))
        stream = resource_stream('glyxtoolms', 'gui/resources/options.gif')
        self.resources["options"] = Tkinter.PhotoImage(data = base64.encodestring(stream.read()))
        
    def saveToClipboard(self, text):
        # ('Tkinter','osx','gtk','qt','xclip','xsel','klipper','windows')
        if self.clipboard == "Tkinter":
            print "saving to clipboard using Tkinter method"
            self.root.clipboard_clear()
            self.root.clipboard_append(text)
        else:
            print "saving to clipboard using xsel"
            pyperclip.set_clipboard(self.clipboard)
            pyperclip.copy(text)
            


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

        # update views
        #self.model.classes["TwoDView"].paintObject()
        self.model.classes["NotebookFeature"].updateFeature(feature)
        self.model.classes["NotebookFeature"].clickedFeatureTree(None)

