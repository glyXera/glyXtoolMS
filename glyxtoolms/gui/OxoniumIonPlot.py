import ttk
import Tkinter
import math
import os
import tkFileDialog
from glyxtoolms.gui import FramePlot


class OxoniumIonPlot(FramePlot.FramePlot):
    


    def __init__(self, master, model, xTitle="", yTitle=""):
        FramePlot.FramePlot.__init__(self, master, model, xTitle="Oxonium Ions",
                                     yTitle="Normalized Intensity")
        self.model.classes["OxoniumIonPlot"] = self
        self.data = []
        self.names = []
        self.colorindex = 0
        self.colors = ["red", "blue", "green", "orange"]
        self.allowZoom = True
        #self.borderBottom = 150
    
    """
    def _paintXAxis(self):
        # create axis
        self.canvas.create_line(self.convAtoX(self.viewXMin),
                                self.convBtoY(self.viewYMin),
                                self.convAtoX(self.viewXMax)+10,
                                self.convBtoY(self.viewYMin),
                                tags=("axis", ), arrow="last")
        # search scale X
        
        start, end, diff, exp = findScale(self.viewXMin, self.viewXMax,
                                          self.NrXScales)
        while start < end:
            if start > self.viewXMin and start < self.viewXMax:
                x = self.convAtoX(start)
                y = self.convBtoY(self.viewYMin)
                if self.xTypeTime == True and self.model.timescale == "minutes":
                    self.canvas.create_text((x, y+5),
                                            text=shortNr(start/60.0, exp-2),
                                            anchor="n")
                else:
                    self.canvas.create_text((x, y+5),
                                            text=shortNr(start, exp),
                                            anchor="n")
                self.canvas.create_line(x, y, x, y+4)
            start += diff
    """

    def getNewColor(self):
        self.colorindex += 1
        if self.colorindex >= len(self.colors):            
            self.colorindex = 0
        return self.colors[self.colorindex]
        
        
    def setMaxValues(self):
        if len(self.data) == 0:
            self.aMax = -1
            self.bMax = -1
            return
        self.names = set()
        self.aMax = len(self.data)

        
        for ions in self.data:
            for ionname in ions:
                self.names.add(ionname)
                intensity = ions[ionname]
                if self.bMax < intensity:
                    self.bMax = intensity
        self.names = sorted(list(self.names))
        self.aMax = len(self.names)*2
        self.aMax *= 1.1
        self.bMax *= 1.1

    def paintObject(self):
        if len(self.data) == 0:
            return
        width = 1/float(len(self.data))
        self.colorindex = 0
        i = 0
        y0 = self.convBtoY(0)
        for ions in self.data:
            color = self.getNewColor()
            x = 0
            for ionname in self.names:
                x0 = self.convAtoX(x+width*i)
                x1 = self.convAtoX(x+width*(i+1))
                y1 = self.convBtoY(ions.get(ionname, 0))
                self.canvas.create_rectangle(x0, y0, x1, y1, fill=color)
                x += 2
            i += 1
        
        
    def init(self, features = [], spectra=[], keepZoom=False):
        self.data = []
        for feature in features:
            avg = {}
            for spectrum in feature.spectra:
                collect = []
                total = 0
                for group in spectrum.ions:
                    for name in spectrum.ions[group]:
                        if name.startswith("Loss"):
                            continue
                        mass = spectrum.ions[group][name]["mass"]
                        intensity = spectrum.ions[group][name]["intensity"]
                        collect.append((mass, name, intensity))
                        total += intensity
                for mass, name, intensity in collect:
                    avg[name] = avg.get(name, 0) + intensity/float(total)*100
            avg[name] = avg[name]/len(feature.spectra)
            self.data.append(avg)
        self.initCanvas(keepZoom=keepZoom)
