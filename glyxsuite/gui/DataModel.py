import glyxsuite
import os

class DataModel:
    
    def __init__(self):
        self.workingdir = "/afs/mpi-magdeburg.mpg.de/data/bpt/bptglycan/DATA_EXCHANGE/Terry/GlyxMSuite/AMAZON/CID"
        #self.mzMLFilename = ""
        #self.fileMzMLFile = None
        #self.exp = None
        #self.analyis = None
        #self.test = None
        self.debug = None
        #self.combination = {}
        #self.spectra = {}
        #self.treeIds = {}
        #self.spec = None
        self.root = None
        #self.chromatograms = {}
        #self.selectedChromatogram = None
        
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
        

        
        self.funcUpdateNotebookScoring = None
        

        
        # model
        # Project
        #  mzml file
        #    chromatograms
        #    spectra
        #  analysisfile
        #    parameters
        #    spectra
        #    features
        #    identifications
        # Results
        #   protein
        #     glycosite
        #       glycopeptide
        #        feature
        #         spectrum
        
class AnalysisSet:
    
    def __init__(self):
        self.mzMLFile = None
        self.analysis = {}
        self.spectra = {}
        
class Analysis:
    
    def __init__(self):
        self.analysisFile = None
        
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
        print "creating ids"
        self.experimentIds = {}
        ms1 = None
        for spec in self.exp:
            level = spec.getMSLevel()
            if level == 1:
                ms1 = spec
            if level == 2:
                self.experimentIds[spec.getNativeID()] = (spec,ms1)

class ContainerAnalysisFile:
    
    def __init__(self,project,path):
        self.path = path
        self.project = project
        self.name = os.path.basename(path)
        self.analysis = None
        self.projectItem = None
        self.spectraIds = {}
        self.data = {}
        self.sortedColumn = ""
        self.reverse = False
        self.chromatograms = {}
        self.selectedChromatogram = None
        
        
        
    def createIds(self):
        self.spectraIds = {}
        for spectrum in self.analysis.spectra:
            self.spectraIds[spectrum.getNativeId()] = spectrum
        
            
    def addNewSpectrum(self,nativeID):
        spectrum = glyxsuite.io.GlyxXMLSpectrum()
        spectrum.setNativeId(nativeID)
        self.spectraIds[nativeID] = spectrum
        self.analysis.spectra.append(spectrum)
        return spectrum
        
