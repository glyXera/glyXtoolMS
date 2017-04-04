import ttk
import Tkinter

import glyxtoolms
from glyxtoolms.gui import FramePlot
from glyxtoolms.gui import Appearance


class HistogramView(FramePlot.FramePlot, glyxtoolms.lib.Histogram):

    def __init__(self, master, model, height=300, width=800):
        FramePlot.FramePlot.__init__(self, master, model, xTitle="Glyco Score", yTitle="Counts")
        glyxtoolms.lib.Histogram.__init__(self, 0.2)
        self.canvas.config(height=height)
        self.canvas.config(width=width)

        self.master = master
        self.logScore = 0.0
        self.NrXScales = 5.0

        self.coord = Tkinter.StringVar()
        l = ttk.Label(self, textvariable=self.coord)
        l.grid(row=4, column=0, sticky="NS")

        self.keepZoom = Tkinter.IntVar()
        c = Appearance.Checkbutton(self, text="keep zoom fixed", variable=self.keepZoom)
        c.grid(row=5, column=0, sticky="NS")


        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

    def setMaxValues(self):
        self.aMax = -1
        self.bMax = -1
        height = {}
        for label in self.bins.keys():
            for b in self.bins[label]:
                va = (b+2)*self.binwidth
                if self.aMax == -1 or va > self.aMax:
                    self.aMax = va
                vb = self.bins[label][b]
                if not b in height:
                    height[b] = 0
                height[b] += vb
        for b in height:
            if self.bMax == -1 or height[b] > self.bMax:
                self.bMax = height[b]

    def paintObject(self):
        bottomStart = {}
        for label in self.bins.keys():
            if not label in self.bins:
                continue
            for b in self.bins[label]:
                if not b in bottomStart:
                    bottomStart[b] = 0
                self.canvas.create_rectangle(self.convAtoX(b*self.binwidth),
                                             self.convBtoY(bottomStart[b]),
                                             self.convAtoX(b*self.binwidth+self.binwidth),
                                             self.convBtoY(bottomStart[b]+self.bins[label][b]),
                                             fill=self.colors[label])
                bottomStart[b] += self.bins[label][b]

        # plot logScore line
        intZero = self.convBtoY(0)
        intMax = self.convBtoY(self.viewYMax)
        if self.logScore != 0:
            self.canvas.create_line(self.convAtoX(self.logScore),
                                    intZero,
                                    self.convAtoX(self.logScore),
                                    intMax,
                                    fill='red', width=4)


        self.allowZoom = True

    def initHistogram(self, logScore):
        self.viewXMin = 0
        self.viewXMax = -1
        self.viewYMin = 0
        self.viewYMax = -1
        self.logScore = logScore
        self.initCanvas(keepZoom=True)

    def identifier(self):
        return "HistogramView"

