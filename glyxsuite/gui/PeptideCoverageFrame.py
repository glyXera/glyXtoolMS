import ttk
import Tkinter
import math
import FramePlot
import glyxsuite
import Appearance


class PeptideCoverageFrame(FramePlot.FramePlot):

    def __init__(self, master, model, height=300, width=800):
        FramePlot.FramePlot.__init__(self, master, model, height=height, width=width, xTitle= "Peptide", yTitle="Peptide")

        self.master = master
        self.logScore = 0.0
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
        #self.model.funcUpdateExtentionIdentification = self.init

    def setMaxValues(self):
        self.aMax = -1
        self.bMax = -1
        self.bMin = -1
        analysis = self.model.currentAnalysis

        if analysis == None:
            return

    def paintObject(self):

        analysis = self.model.currentAnalysis

        if analysis == None:
            return
        self.allowZoom = True

    def init(self):
        self.viewXMin = 0
        self.viewXMax = -1
        self.viewYMin = -1
        self.viewYMax = -1
        self.initCanvas(keepZoom = True)

    def identifier(self):
        return "PeptideCoverageFrame"

