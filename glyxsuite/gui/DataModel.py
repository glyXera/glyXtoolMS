import glyxsuite
import os


class DataModel:
    
    def __init__(self):
        self.workingdir = "/afs/mpi-magdeburg.mpg.de/data/bpt/bptglycan/DATA_EXCHANGE/Terry/GlyxMSuite/AMAZON/CID"
        self.debug = None
        self.root = None
        self.projects= {}
        self.currentProject = None
        self.currentAnalysis = None
        
        # call function to paint Frameplots
        # PrecursorView
        # NotebookScoring
        self.funcScoringMSSpectrum = None
        # SpectrumView
        # NotebookScoring
        self.funcScoringMSMSSpectrum = None
        # ChromatogramView
        # NotebookScoring
        self.funcScoringChromatogram = None
        
        #TwoDView
        # ExtentionFeature
        # NotebookFeature
        self.funcFeatureTwoDView = None
        
        self.funcUpdateNotebookScoring = None
        self.funcUpdateNotebookIdentification = None
        self.funcUpdateNotebookFeature = None
        
class Chromatogram:
    
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
                
class ContainerSpectrum(object):
    
    def __init__(self,spectrum):
        self._spectrum = spectrum
        self.chromatogramSpectra = []
        
    @property
    def nativeId(self):
        return self._spectrum.nativeId

    @nativeId.setter
    def nativeId(self, value):
        self._spectrum.nativeId = value

    @property
    def rt(self):
        return self._spectrum.rt

    @rt.setter
    def rt(self, value):
        self._spectrum.rt = value

    @property
    def precursorMass(self):
        return self._spectrum.precursorMass

    @precursorMass.setter
    def precursorMass(self, value):
        self._spectrum.precursorMass = value
        
    @property
    def precursorCharge(self):
        return self._spectrum.precursorCharge

    @precursorCharge.setter
    def precursorCharge(self, value):
        self._spectrum.precursorCharge = value

    @property
    def logScore(self):
        return self._spectrum.logScore

    @logScore.setter
    def logScore(self, value):
        self._spectrum.logScore = value

    @property
    def ions(self):
        return self._spectrum.ions

    @property
    def isGlycopeptide(self):
        return self._spectrum.isGlycopeptide

    @isGlycopeptide.setter
    def isGlycopeptide(self, value):
        self._spectrum.isGlycopeptide = value

class Project:
    
    def __init__(self,name,path):
        self.name = name
        self.path = path
        self.mzMLFile = None
        self.analysisFiles = {}    
      
class ContainerMZMLFile:
    
    def __init__(self,project,path):
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
                self.experimentIds[nativeId] = (spec,ms1)           

class ContainerAnalysisFile:
    
    def __init__(self,project,path):
        self.path = path
        self.project = project
        self.name = os.path.basename(path)
        self.analysis = None
        self.projectItem = None
        self.spectraIds = {}
        self.featureIds = {}
        self.spectraInFeatures = {}
        self.data = []
        self.sortedColumn = ""
        self.reverse = False
        self.chromatograms = {}
        self.selectedChromatogram = None
        self.currentFeature = None
        
        
        
    def createIds(self):
        self.spectraIds = {}
        self.spectraInFeatures = {}
        for spectrum in self.analysis.spectra:
            self.spectraIds[spectrum.nativeId] = ContainerSpectrum(spectrum)
            self.spectraInFeatures[spectrum.nativeId] = []
        
        # create featureIds
        # create feature - spectra link
        self.featureIds = {}
        for feature in self.analysis.features:
            self.featureIds[feature.getId()] = feature
            for specId in feature.getSpectraIds():
                self.spectraInFeatures[specId].append(feature.getId())
                

        
        
            
    def addNewSpectrum(self,nativeID):
        spectrum = glyxsuite.io.GlyxXMLSpectrum()
        spectrum.setNativeId(nativeID)
        self.spectraIds[nativeID] = spectrum
        self.analysis.spectra.append(spectrum)
        return spectrum
        
