import ttk
import Tkinter

from glyxsuite.gui import FramePlot
from glyxsuite.gui import Appearance

class PrecursorView(FramePlot.FramePlot):

    def __init__(self, master, model, height=300, width=800):
        FramePlot.FramePlot.__init__(self, master, model, height=height, width=width, xTitle="mz [Th]", yTitle="Intensity [counts]")

        self.master = master
        self.specArray = None
        self.NrXScales = 3.0
        self.monoisotope = 0
        self.spectrum = None
        self.base = None

        self.coord = Tkinter.StringVar()
        l = ttk.Label(self, textvariable=self.coord)
        l.grid(row=4, column=0, sticky="NS")

        self.keepZoom = Tkinter.IntVar()
        c = Appearance.Checkbutton(self, text="keep zoom fixed", variable=self.keepZoom)
        c.grid(row=5, column=0, sticky="NS")


        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # link function
        self.model.classes["FeaturePrecursorView"] = self

    def setMaxValues(self):
        try:
            self.bMax = max(self.spectrum)
        except:
            self.bMax = 1
        try:
            self.aMax = max(self.base)
        except:
            self.aMax = 1

    def paintObject(self):
        if self.spectrum == None:
            return
        if self.feature == None:
            return

        # continuous spectrum
        xy = []
        for mz, intensity in zip(self.base,self.spectrum):
            if mz < self.viewXMin or mz > self.viewXMax:
                continue
            pMZ = self.convAtoX(mz)
            pInt = self.convBtoY(intensity)
            xy.append(pMZ)
            xy.append(pInt)
        if len(xy) > 0:
            self.canvas.create_line(xy, tags=("peak", ))
        
        
        pIntMin = self.convBtoY(self.viewYMin)
        pIntMax = self.convBtoY(self.viewYMax)
        
        # paint monoisotopic mass
        pMZ = self.convAtoX(self.monoisotope)
        self.canvas.create_line(pMZ, pIntMin, pMZ, pIntMax, tags=("monoisotope", ),fill="blue")
        
        minRT, maxRT, minMZ, maxMZ = self.feature.getBoundingBox()
        # paint monoisotopic mass
        pMZ = self.convAtoX(minMZ)
        self.canvas.create_line(pMZ, pIntMin, pMZ, pIntMax, tags=("featureborder", ),fill="red")
        
        pMZ = self.convAtoX(maxMZ)
        self.canvas.create_line(pMZ, pIntMin, pMZ, pIntMax, tags=("featureborder", ),fill="red")
        #self.canvas.create_line(pMZ, pIntMin, pMZ, pIntMax, tags=("monoisotope", ),fill="blue")

        self.allowZoom = True
        
    def initSpectrum(self, specArray, monoisotope, minMZ, maxMZ):
        if specArray == None:
            return
        self.specArray = specArray
        self.viewXMin = minMZ
        self.viewXMax = maxMZ
        self.viewYMin = 0
        self.viewYMax = max(specArray[:, 1])
        self.monoisotope = monoisotope
        self.initCanvas(keepZoom=True)
        
        
    def init(self, spectrumXArray, spectrumYArray, feature, minMZ, maxMZ):
        self.spectrum = spectrumYArray
        self.base = spectrumXArray
        self.feature = feature
        self.monoisotope = feature.getMZ()
        self.viewXMin = minMZ
        self.viewXMax = maxMZ
        self.viewYMin = 0
        #self.viewYMax = 1
        if sum(spectrumYArray) > 0:
            self.viewYMax = max(spectrumYArray)
        self.initCanvas(keepZoom=True)

    def identifier(self):
        return "FeaturePrecursorView"
