import ttk
import Tkinter

from glyxtoolms.gui import FramePlot
from glyxtoolms.gui import Appearance
import glyxtoolms

class IdentificationStatsFrame(FramePlot.FramePlot):

    def __init__(self, master, model):
        FramePlot.FramePlot.__init__(self, master, model, xTitle="FeatureNr",
                                     yTitle="Error")

        self.master = master
        self.logScore = 0.0
        self.NrXScales = 5.0

    def setMaxValues(self):
        self.aMax = -1
        #self.aMin = -1
        self.bMax = -1
        self.bMin = -1
        analysis = self.model.currentAnalysis

        if analysis == None:
            return

        # insert all glycomod hits
        for hit in analysis.analysis.glycoModHits:
            feature = analysis.featureIds[hit.featureID]
            featureNr = int(feature.index)
            #mass = (feature.mz-glyxtoolms.masses.MASS["H+"])*feature.charge
            error = hit.error
            if self.aMax == -1 or featureNr > self.aMax:
                self.aMax = featureNr
            #if self.aMax == -1 or mass > self.aMax:
            #    self.aMax = mass
            #if self.aMin == -1 or mass < self.aMin:
            #    self.aMin = mass
            if self.bMax == -1 or error > self.bMax:
                self.bMax = error
            if self.bMin == -1 or error < self.bMin:
                self.bMin = error
        #self.aMin = self.aMin-self.aMax*0.1
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
            #mass = (feature.mz-glyxtoolms.masses.MASS["H+"])*feature.charge
            error = hit.error

            diam = 3
            x = self.convAtoX(featureNr)
            #x = self.convAtoX(mass)
            y = self.convBtoY(error)
            self.canvas.create_oval(x-diam, y-diam, x+diam, y+diam, fill="green")
        self.allowZoom = True

    def init(self):
        self.viewXMin = 0
        self.viewXMax = -1
        self.viewYMin = -1
        self.viewYMax = -1
        self.initCanvas(keepZoom=True)

    def identifier(self):
        return "IdentificationStatsFrame"

