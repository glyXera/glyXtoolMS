import ttk
import Tkinter

from glyxtoolms.gui import FramePlot
from glyxtoolms.gui import Appearance

class ChromatogramView(FramePlot.FramePlot):

    def __init__(self, master, model):
        FramePlot.FramePlot.__init__(self, master, model, xTitle="rt [s]", yTitle="Intensity [counts]")

        self.master = master
        self.NrXScales = 3.0
        self.rt = None

        # Events
        #self.canvas.bind("<Left>", self.sayHi)
        #self.canvas.bind("<Right>", self.sayHi)
        #self.canvas.bind("<Button-1>", self.setSpectrumPointer)

        self.spectrumPointer = None



    def setSpectrumPointer(self, event):
        if self.model.exp == None:
            return
        if self.allowZoom == False:
            return
        rt = self.convXtoA(event.x)

        # get selected MSLevel
        if self.model.currentAnalysis.selectedChromatogram == None:
            return
        msLevel = self.model.currentAnalysis.selectedChromatogram.msLevel
        nearest = None
        diff = -1
        for spec in self.model.exp:
            if spec.getMSLevel() != msLevel: # fix, needs Level from chromatogram
                continue
            diffNew = abs(spec.getRT()-rt)
            if diff == -1 or diffNew < diff:
                nearest = spec
                diff = diffNew
        if diff != -1:
            self.model.funcPaintSpectrum(nearest)



    def setMaxValues(self):
        self.aMax = -1
        self.bMax = -1
        for treeId in self.model.currentAnalysis.chromatograms:
            chrom = self.model.currentAnalysis.chromatograms[treeId]
            if chrom.plot == False:
                continue
            for rt in chrom.rt:
                if self.aMax == -1 or rt > self.aMax:
                    self.aMax = rt
            for intensity in chrom.intensity:
                if self.bMax == -1 or intensity > self.bMax:
                    self.bMax = intensity


    def paintObject(self):
        if self.model.currentAnalysis == None:
            return
        self.allowZoom = False
        for treeId in self.model.currentAnalysis.chromatograms:
            chrom = self.model.currentAnalysis.chromatograms[treeId]
            if chrom.plot == False:
                continue
            if chrom.selected == True:
                linewidth = 2
            else:
                linewidth = 1
            if len(chrom.rt) != len(chrom.intensity):
                raise Exception("Different length of chromatogram parameters!")
            xy = []
            for i in range(0, len(chrom.rt)):
                rt = chrom.rt[i]
                intens = chrom.intensity[i]
                xy.append(self.convAtoX(rt))
                xy.append(self.convBtoY(intens))
            if len(xy) == 0:
                continue
            self.canvas.create_line(xy, fill=chrom.color, width=linewidth)

        if self.rt != None:
            intZero = self.convBtoY(0)
            intMax = self.convBtoY(self.viewYMax)
            self.canvas.create_line(
                self.convAtoX(self.rt),
                intZero,
                self.convAtoX(self.rt),
                intMax,
                fill='blue')
            self.allowZoom = True

    def initChromatogram(self, low, high, rt):
        if self.model.currentAnalysis == None:
            return
        self.viewXMin = low
        self.viewXMax = high
        self.viewYMin = 0
        self.viewYMax = -1
        self.rt = rt
        self.initCanvas(keepZoom=True)

    def identifier(self):
        return "ChromatogramView"


