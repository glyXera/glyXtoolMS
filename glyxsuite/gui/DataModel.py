class DataModel:
    
    def __init__(self):
        self.workingdir = "/afs/mpi-magdeburg.mpg.de/data/bpt/bptglycan/DATA_EXCHANGE/Terry/GlyxMSuite/AMAZON/CID"
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
        self.funcPaintSpectrum = None # SpectrumView.initSpectrum(spec)
        self.funcPaintChromatograms = None # ChromatogramView.initChromatogram()
        self.funcPaintTwo2View = None # TwoDView.init()
        
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
                
