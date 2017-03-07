import ttk
import tkFont
import Tkinter
import math
import os
import tkFileDialog
from glyxtoolms.gui import FramePlot
import glyxtoolms


class OxoniumIonPlot(FramePlot.FramePlot):
    


    def __init__(self, master, model, xTitle="", yTitle=""):
        FramePlot.FramePlot.__init__(self, master, model, xTitle="Normalized Intensity",
                                     yTitle="Oxonium Ions")
        self.model.classes["OxoniumIonPlot"] = self
        self.data = []
        self.sdev = []
        self.names = []
        self.colorindex = 0
        self.colors = ["red", "blue", "green", "orange"]
        self.allowZoom = True
        self.borderLeft = 100
        self.visible = {}
        self.legend = {}
        
        # create popup menu
        self.aMenu = Tkinter.Menu(self, tearoff=0)
        self.canvas.bind("<Button-3>", self.popup)
    
    def visbilityChanged(self, *arg, **args):
        self.initCanvas(keepZoom=False)

    def popup(self, event):

        self.aMenu.delete(0,"end")
        for name in self.visible:
            self.aMenu.insert_checkbutton("end", label=name, onvalue=1, offvalue=0, variable=self.visible[name])

        self.aMenu.post(event.x_root, event.y_root)
        self.aMenu.focus_set()
        self.aMenu.bind("<FocusOut>", self.removePopup)
        
    def removePopup(self,event):
        if self.focus_get() != self.aMenu:
            self.aMenu.unpost()
    
    
    def _paintYAxis(self):
        self.canvas.create_line(self.convAtoX(self.viewXMin),
                                self.convBtoY(self.viewYMin),
                                self.convAtoX(self.viewXMin),
                                self.convBtoY(self.viewYMax)-10,
                                tags=("axis", ), arrow="last")
        index = 0
        for name in self.names:
            if self.visible[name].get() == False:
                continue
            start = index*2+0.5
            if start > self.viewYMin and start < self.viewYMax:
                x = self.convAtoX(self.viewXMin)
                y = self.convBtoY(start)
                self.canvas.create_text((x-5, y),
                                        text=name,
                                        anchor="e")
                self.canvas.create_line(x-4, y, x, y)
            index += 1

        item = self.canvas.create_text(self.borderLeft,
                                       self.borderTop/2.0,
                                       text=self.yTitle)
        # write legend
        y_legend = self.convBtoY(self.viewYMax)-10
        i = 0
        x0 = self.convAtoX(self.viewXMax)+15
        for legend in self.legend:
            i += 1
            if i == 6:
                legend = "..."
            self.canvas.create_text(x0+20,
                                    y_legend,
                                    text=legend,
                                    anchor="w")
            if i == 6:
                break
            self.canvas.create_rectangle(x0, y_legend-5, x0+10, y_legend+5, fill=self.legend[legend])
            y_legend += 20

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

        self.aMin = 0
        self.bMax = -1
        self.aMax = -1
        for avg, sdev in zip(self.data, self.sdev):
            for ionname in avg:
                if self.visible[ionname].get() == False:
                    continue
                intensityMax = avg[ionname]+sdev.get(ionname, 0)
                intensityMin = avg[ionname]-sdev.get(ionname, 0)
                
                if self.aMax < intensityMax:
                    self.aMax = intensityMax
                if self.aMin > intensityMin:
                    self.aMin = intensityMin
        self.bMax = len([name for name in self.names if self.visible[name].get() == True])*2
        self.aMax *= 1.1
        self.bMax *= 1.1
        self.aMin *= 1.1

    def paintObject(self):
        if len(self.data) == 0:
            return
        height = 1/float(len(self.data))
        self.colorindex = 0
        i = 0
        x0 = self.convAtoX(0)
        
        for avg, sdev, legend in zip(self.data, self.sdev, self.legend):
            color = self.getNewColor()
            self.legend[legend] = color
            y = 0
            for ionname in self.names:
                if self.visible[ionname].get() == False:
                    continue
                y0 = self.convBtoY(y+height*i)
                y1 = self.convBtoY(y+height*(i+1))
                x1 = self.convAtoX(avg.get(ionname, 0))
                # paint rectangle
                self.canvas.create_rectangle(x0, y0, x1, y1, fill=color)
                # paint standard deviation
                if ionname in sdev:
                    xdev_min = self.convAtoX(avg.get(ionname, 0) - sdev.get(ionname, 0))
                    xdev_max = self.convAtoX(avg.get(ionname, 0) + sdev.get(ionname, 0))
                    yhair1 = self.convBtoY(y+height*(i+0.25))
                    yhair2 = self.convBtoY(y+height*(i+0.75))
                    self.canvas.create_line(xdev_min,
                            (y0+y1)/2.0,
                            xdev_max,
                            (y0+y1)/2.0)
                    self.canvas.create_line(xdev_min,
                            yhair1,
                            xdev_min,
                            yhair2)
                    self.canvas.create_line(xdev_max,
                            yhair1,
                            xdev_max,
                            yhair2)
                y += 2
            i += 1
    
    def _getOxoniumions(self, spectra):
        names = {}
        values = {}
        for spectrum in spectra:
            collect = []
            total = 0
            for group in spectrum.ions:
                for name in spectrum.ions[group]:
                    if name.startswith("Loss"):
                        continue
                    mass = spectrum.ions[group][name]["mass"]
                    intensity = spectrum.ions[group][name]["intensity"]
                    collect.append((mass, name, intensity))
                    names[name] = mass
                    total += intensity
            
            for mass, name, intensity in collect:
                values[name] = values.get(name, []) + [intensity/float(total)*100]
                
            # calculate average
            avg = {}
            sdev = {}
            for name in values:
                length = float(len(spectra))
                avg[name] = sum(values[name])/length
                if length > 1:
                    sdev[name] = math.sqrt(sum([(v-avg[name])**2 for v in values[name]])/(length-1))
                #else:
                #    sdev[name] = 0.0
        return avg, sdev, names
    
    def _init_features(self, features):
        all_names = {}
        for feature in features:
            avg, sdev, names  = self._getOxoniumions(feature.spectra)
            for name in names:
                all_names[name] = names[name]
            self.data.append(avg)
            self.sdev.append(sdev)
            self.legend[str(feature.index)] = "black"
        self.names = sorted(all_names)
        
        
    def _init_identifications(self, identifications):
        all_names = {}
        for hit in identifications:
            avg, sdev, names  = self._getOxoniumions(hit.feature.spectra)
            for name in names:
                all_names[name] = names[name]
            self.data.append(avg)
            self.sdev.append(sdev)
            # generate name
            glycan = glyxtoolms.lib.Glycan(hit.glycan.composition)
            legend = str(hit.feature.index) + "-"+hit.peptide.toString() + "+" + glycan.toString()
            self.legend[legend] = "black"
        self.names = sorted(all_names)
        
    def _init_spectra(self, spectra):
        all_names = {}
        for spectrum in sorted(spectra, key=lambda s:s.rt):
            avg, sdev, names  = self._getOxoniumions([spectrum])
            for name in names:
                all_names[name] = names[name]
            self.data.append(avg)
            self.sdev.append(sdev)
            legend = str(spectrum.rt)
            self.legend[legend] = "black"
        self.names = sorted(all_names)
        
    def init(self, identifications = [], features = [], spectra=[], keepZoom=False):
        self.data = []
        self.sdev = []
        self.names = []
        self.legend = {}
        
        if len(identifications) > 0:
            self._init_identifications(identifications)
        elif len(features) > 0:
            self._init_features(features)
        elif len(spectra) > 0:
            self._init_spectra(spectra)
        
        
        # add new oxonium ions to visibility
        for name in self.names:
            if name not in self.visible:
                self.visible[name] = Tkinter.BooleanVar()
                self.visible[name].set(True)
                self.visible[name].trace("w", self.visbilityChanged)
        
        # calculate space for oxonium names
        self.borderLeft = 100
        if len(self.names) > 0:
            sizes = []
            for name in self.names:
                sizes.append(tkFont.Font(font='TkDefaultFont').measure(name))
            size = max(sizes)
            if size > 80:
                self.borderLeft = size+20
                
        # calculate space for legend
        self.borderRight = 50
        if len(self.legend) > 0:
            sizes = []
            for text in self.legend:
                sizes.append(tkFont.Font(font='TkDefaultFont').measure(text))
            size = max(sizes)
            self.borderRight = size+50
        self.initCanvas(keepZoom=keepZoom)
