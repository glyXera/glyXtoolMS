import ttk
import Tkinter
import math
import FramePlot
import glyxsuite
import Appearance


class IdentificationStatsFrame(FramePlot.FramePlot):

    def __init__(self, master, model, height=300, width=800):
        FramePlot.FramePlot.__init__(self, master, model, height=height, width=width, xTitle= "FeatureNr", yTitle="Error")

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
        #self.model.funcScoringMSSpectrum = self.initSpectrum
        self.model.funcUpdateExtentionIdentification = self.init

    def setMaxValues(self):
        self.aMax = -1
        self.bMax = -1
        self.bMin = -1
        analysis = self.model.currentAnalysis

        if analysis == None:
            return

        # insert all glycomod hits
        for hit in analysis.analysis.glycoModHits:
            feature = analysis.featureIds[hit.featureID]
            #featureNr = (feature.getMZ()-glyxsuite.masses.MASS["H+"])*feature.getCharge()
            featureNr = int(feature.index)
            error = hit.error
            if self.aMax == -1 or featureNr > self.aMax:
                self.aMax = featureNr
            if self.bMax == -1 or error > self.bMax:
                self.bMax = error
            if self.bMin == -1 or error < self.bMin:
                self.bMin = error
        self.aMax = self.aMax*1.1
        self.bMax = self.bMax+0.1
        self.bMin = self.bMin-0.1

        #self.bMax = 2
        #self.bMin = -2

    def paintObject(self):

        analysis = self.model.currentAnalysis

        if analysis == None:
            return

        # insert all glycomod hits

        # paint zero line
        xMin = self.convAtoX(self.aMin)
        xMax = self.convAtoX(self.aMax)
        zero = self.convBtoY(0)
        self.canvas.create_line(xMin, zero, xMax, zero, fill="blue")

        for hit in analysis.analysis.glycoModHits:
            feature = analysis.featureIds[hit.featureID]
            featureNr = int(feature.index)
            #featureNr = (feature.getMZ()-glyxsuite.masses.MASS["H+"])*feature.getCharge()
            error = hit.error

            diam = 3
            x = self.convAtoX(featureNr)
            y = self.convBtoY(error)
            item = self.canvas.create_oval(x-diam, y-diam, x+diam, y+diam, fill="green")
        self.allowZoom = True

    def init(self):
        self.viewXMin = 0
        self.viewXMax = -1
        self.viewYMin = -1
        self.viewYMax = -1
        self.initCanvas(keepZoom = True)

    def identifier(self):
        return "IdentificationErrorView"

