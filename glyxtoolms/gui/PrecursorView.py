import ttk
import Tkinter

from glyxtoolms.gui import FramePlot
from glyxtoolms.gui import Appearance

class PrecursorView(FramePlot.FramePlot):

    def __init__(self, master, model):
        FramePlot.FramePlot.__init__(self, master, model, xTitle="m/z",
                                     yTitle="Intensity [counts]")

        self.master = master
        self.spec = None
        self.charge = 0
        self.precursormass = 0.0
        self.NrXScales = 3.0

    def setMaxValues(self):
        self.aMax = -1
        self.bMax = -1

        for peak in self.spec:
            mz = peak.getMZ()
            intens = peak.getIntensity()
            if self.aMax == -1 or mz > self.aMax:
                self.aMax = mz
            if self.bMax == -1  or intens > self.bMax:
                self.bMax = intens


    def paintObject(self):
        if self.spec == None:
            self.charge = 0
            self.precursormass = 0.0
            return

        # continuous spectrum
        xy = []
        for peak in self.spec:
            mz = peak.getMZ()

            intens = peak.getIntensity()
            if mz < self.viewXMin or mz > self.viewXMax:
                continue
            pMZ = self.convAtoX(mz)
            pInt = self.convBtoY(intens)
            xy.append(pMZ)
            xy.append(pInt)
        if len(xy) > 0:
            self.canvas.create_line(xy, tags=("peak", ))

        # plot precursor line
        intZero = self.convBtoY(0)
        intMax = self.convBtoY(self.viewYMax)
        if self.precursormass != 0:
            for i in range(0, 4):
                if self.charge == 0:
                    mass = self.precursormass
                else:
                    mass = self.precursormass+1/abs(float(self.charge))*i
                self.canvas.create_line(self.convAtoX(mass),
                                        intZero,
                                        self.convAtoX(mass),
                                        intMax,
                                        fill='green')

        # plot rt line
        c = self.model.currentAnalysis.selectedChromatogram
        if  c != None:
            self.canvas.create_line(self.convAtoX(c.rangeLow),
                                    intZero,
                                    self.convAtoX(c.rangeLow),
                                    intMax,
                                    fill='blue')
            self.canvas.create_line(self.convAtoX(c.rangeHigh),
                                    intZero,
                                    self.convAtoX(c.rangeHigh),
                                    intMax,
                                    fill='blue')
        self.allowZoom = True

    def initSpectrum(self, spec, mass, charge, low, high):
        if spec == None:
            self.charge = 0
            self.precursormass = 0.0
            return
        self.spec = spec
        self.precursormass = mass
        self.charge = charge
        self.viewXMin = low
        self.viewXMax = high
        self.viewYMin = 0
        self.viewYMax = -1
         # set self.viewYMax
        for peak in self.spec:
            mz = peak.getMZ()
            intens = peak.getIntensity()
            if mz < self.viewXMin or mz > self.viewXMax:
                continue
            if intens > self.viewYMax:
                self.viewYMax = intens

        self.initCanvas(keepZoom=True)

    def identifier(self):
        return "PrecursorView"
