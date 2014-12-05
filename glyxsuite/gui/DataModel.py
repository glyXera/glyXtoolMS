class DataModel:
    
    def __init__(self):
        self.workingdir = "/afs/mpi-magdeburg.mpg.de/home/pioch/Data/Projekte/GlyxBox/glycoMod/"
        self.mzMLFilename = ""
        self.fileMzMLFile = None
        self.exp = None
        self.analyis = None
        self.test = None
        self.debug = None
        self.combination = {}
        self.spectra = {}
        self.treeIds = {}
        self.spec = None
        self.root = None
        self.chromatograms = {}
        self.selectedChromatogram = None
        self.funcPaintSpectrum = None
        self.funcPaintChromatograms = None
        
    def combineDatasets(self):
        if self.exp == None or self.analysis == None:
            return False
        
        # connect MS2 spectra
        self.combination = {}
        #for spec in exp: 
        
        
        
class Chromatogram:
    
    def __init__(self):
        self.name = ""
        self.color = ""
        self.rangeLow = 0
        self.rangeHigh = 0
        self.plot = False
        self.rt = []
        self.intensity = []
        self.msLevel = 0
        self.selected = False
                
