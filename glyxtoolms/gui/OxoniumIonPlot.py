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
        
    def setMaxValues(self):
        self.aMax = -1
        self.bMax = -1
        #for feature in self.model.currentAnalysis.analysis.features:
        #    rt = feature.getRT()
        #    mz = feature.getMZ()
        #    if self.aMax < rt:
        #        self.aMax = rt
        #    if self.bMax < mz:
        #        self.bMax = mz
        self.aMax *= 1.1
        self.bMax *= 1.1

    def paintObject(self):
        return
        
        
    def init(self, features = [], spectra=[], keepZoom=False):
        print features
        self.data = []
        for feature in features:
            avg = {}
            for spectrum in feature.spectra:
                collect = []
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
        print self.data
            
                
        
        self.initCanvas(keepZoom=keepZoom)
