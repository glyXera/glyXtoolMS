import ttk
import Tkinter
import math
import FramePlot
import glyxsuite
import Appearance


class ConsensusSpectrumFrame(FramePlot.FramePlot):

    def __init__(self, master, model, height=300, width=800):
        FramePlot.FramePlot.__init__(self, master, model, height=height, width=width, xTitle= "Peptide", yTitle="Peptide")

        self.master = master
        self.hit = None
        self.consensus = None
        self.NrXScales = 5.0

        self.coord = Tkinter.StringVar()
        l = ttk.Label( self, textvariable=self.coord)
        l.grid(row=4, column=0, sticky="NS")

        self.keepZoom = Tkinter.IntVar()
        c = Appearance.Checkbutton(self, text="keep zoom fixed", variable=self.keepZoom)
        c.grid(row=5, column=0, sticky="NS")


        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # link function
        self.model.funcUpdateConsensusSpectrum = self.init

    def setMaxValues(self):
        if self.consensus == None:
            return
        self.aMax = -1
        self.bMax = -1

        for peak in self.consensus:
            mz = peak.x
            intens = peak.y
            if self.aMax == -1 or mz > self.aMax :
                self.aMax = mz
            if self.bMax == -1  or intens > self.bMax:
                self.bMax = intens
        self.aMax *= 1.1
        self.bMax *= 1.2

    def paintObject(self):
        if self.consensus == None:
            return
        pInt0 = self.convBtoY(self.viewYMin)
        for peak in self.consensus:
            pMZ = self.convAtoX(peak.x)
            pInt = self.convBtoY(peak.y)
            # check if a fragment exists for the peak
            found = None
            for key in self.hit.fragments:
                if abs(self.hit.fragments[key]["mass"]-peak.x) < 0.1:
                    found = key
                    break
            if found != None:
                color = "blue"
                self.canvas.create_text((pMZ, pInt, ), text=found, anchor="s", justify="center")
            else:
                color= "black"
            item = self.canvas.create_line(pMZ, pInt0, pMZ, pInt, tags=("peak", ), fill=color)
            
        self.allowZoom = True

    def init(self,hit):
        analysis = self.model.currentAnalysis
        if analysis == None:
            return
        if hit.featureID not in analysis.featureIds:
            return
        self.hit = hit
        feature = analysis.featureIds[hit.featureID]
        self.consensus = feature.consensus
        if self.consensus == None:
            return

        self.viewXMin = 0
        self.viewXMax = -1
        self.viewYMin = -1
        self.viewYMax = -1
        self.hit = hit
        self.initCanvas(keepZoom = True)

    def identifier(self):
        return "ConsensusSpectrumFrame"

