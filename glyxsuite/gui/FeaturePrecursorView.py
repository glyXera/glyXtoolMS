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

        self.coord = Tkinter.StringVar()
        l = ttk.Label(self, textvariable=self.coord)
        l.grid(row=4, column=0, sticky="NS")

        self.keepZoom = Tkinter.IntVar()
        c = Appearance.Checkbutton(self, text="keep zoom fixed", variable=self.keepZoom)
        c.grid(row=5, column=0, sticky="NS")


        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # link function
        self.model.funcUpdateFeaturePrecursorSpectrum = self.initSpectrum

    def setMaxValues(self):
        self.aMax = -1
        self.bMax = -1

        for mz, intensity in self.specArray:
            if self.aMax == -1 or mz > self.aMax:
                self.aMax = mz
            if self.bMax == -1  or intensity > self.bMax:
                self.bMax = intensity


    def paintObject(self):
        if self.specArray == None:
            return
        # continuous spectrum
        xy = []
        for mz, intensity in self.specArray:
            if mz < self.viewXMin or mz > self.viewXMax:
                continue
            pMZ = self.convAtoX(mz)
            pInt = self.convBtoY(intensity)
            xy.append(pMZ)
            xy.append(pInt)
        if len(xy) > 0:
            self.canvas.create_line(xy, tags=("peak", ))
        
        pMZ = self.convAtoX(self.monoisotope)
        pIntMin = self.convBtoY(self.viewYMin)
        pIntMax = self.convBtoY(self.viewYMax)
        
        self.canvas.create_line(pMZ, pIntMin, pMZ, pIntMax, tags=("monoisotope", ),fill="red")

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

    def identifier(self):
        return "FeaturePrecursorView"
