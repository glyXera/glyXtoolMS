import ttk
import tkFont
import Tkinter
import math
import os
import tkFileDialog
from glyxtoolms.gui import FramePlot
import glyxtoolms
import re
from glyxtoolms.gui import Appearance

class OxoniumIonPlot(FramePlot.FramePlot):

    def __init__(self, master, model, xTitle="", yTitle=""):
        FramePlot.FramePlot.__init__(self, master, model, xTitle="Normalized Intensity",
                                     yTitle="Oxonium Ions")

        self.data = []
        self.sdev = []
        self.names = []
        self.colorindex = 0
        self.colors = ["red", "blue", "green", "orange"]
        self.allowZoom = True
        self.visible = {}
        self.legend = {}

        # create popup menu
        self.aMenu = Tkinter.Menu(self, tearoff=0)
        self.canvas.bind("<Button-3>", self.popup)

        # add sidepanel for selection
        self.sidePanelSelection = SelectionSidePanel(self.sidepanel, self)
        self.sidepanel.addContextPanel("oxonium", self.sidePanelSelection)

        # add selection panel toggle
        self.selectionButton = self.toolbar.addButton("oxonium","selection", "default")
        # add trace to ruler button toggles
        self.selectionButton.active.trace("w", self.selectionPanelToggled)
        self.plotOrder = ["HexNAc","N" "Hex","H","dHex","F", "NeuAc","Sa" "NeuGc","Sg"]

    def identifier(self):
        return "OxoniumIonPlot"


    def getDefaultOptions(self):
        options = super(OxoniumIonPlot, self).getDefaultOptions()
        options["axislabel"]["showpicto"] = True
        return options



    def createOptions(self, optionsFrame):
        def togglePictogram(a,b,c, var):
            self.options["axislabel"]["showpicto"] = var.get()
            self._paintCanvas(False)

        super(OxoniumIonPlot, self).createOptions(optionsFrame)
        frameAxis = optionsFrame.getLabelFrame("Axis")

        pictogramVar = Tkinter.BooleanVar()
        pictogramVar.set(self.options["axislabel"]["showpicto"])
        optionsFrame.addVariable("axislabel", "showPicto", pictogramVar)
        c = Appearance.Checkbutton(frameAxis, text="Use Glycan Pictograms", variable=pictogramVar)
        c.grid(row=frameAxis.row, column=0, columnspan=2, sticky="NWS")
        frameAxis.row += 1
        pictogramVar.trace("w", lambda a,b,c,d=pictogramVar: togglePictogram(a,b,c,d))

    def parseOxoniumion(self, name):
        # check type
        units = {}
        if name.endswith("(+)"):
            name = name.replace("(+)","")
            sp = name.split("-")
            glycanpart = sp[0]
            for part in re.findall(".\d+",glycanpart):
                amount = int(re.sub("\D+","",part))
                glycan = re.sub("\d+","",part)
                units[glycan] = amount
            if sp == 2:
                loss = sp[1]
                units[loss[1:]] = -1
        else:

            for unit in re.findall("\(.+?\)-?\d+",name):
                glycan, amount = unit.split(")")
                glycan = glycan[1:]
                amount = int(amount)
                if amount == 0:
                    continue
                units[glycan] = amount
            if "H+" in units:
                units.pop("H+")
        print name, units
        return units

    def paintOxoniumion(self, x, y, name):
        x = x -10
        text = name
        self.canvas.create_text((x, y),
                                    text=text,
                                    anchor="e",
                                    font=self.options["axisnumbering"]["font"])
        x = x - self.options["axisnumbering"]["font"].measure(text)-2
        return x

    def paintOxoniumionOld(self, x, y, name):
        units = self.parseOxoniumion(name)
        # use size of font to assume shape sizes
        size = self.options["axisnumbering"]["font"].config()["size"]
        h = size/2.0
        x = x -10
        rest = []
        for unit in units:
            if unit not in self.plotOrder:
                rest.append(unit)
        for unit in self.plotOrder[::-1]:
            if unit not in units:
                continue
            amount = units[unit]
            #if unit == "H2O":
            #
            #    text = "H2O"
            #    if amount < -1:
            #       text = str(amount)+text
            #    elif amount == -1:
            #        text = "-"+text
            #    elif amount == 1:
            #        text = "+"+text
            #    else:
            #        text = "+" +str(amount)+text
            #    self.canvas.create_text((x, y),
            #                            text=text,
            #                            anchor="e",
            #                            font=self.options["axisnumbering"]["font"])
            #    # measure new x
            #    x = x - self.options["axisnumbering"]["font"].measure(text)-2
            #else:
            for i in range(0, amount):
                if unit == "HexNAc" or unit == "N":
                    self.canvas.create_rectangle(x,y-h,x-size, y+h)
                elif unit == "Hex"or unit == "H":
                    self.canvas.create_oval(x,y-h,x-size, y+h)
                elif unit == "dHex"or unit == "F":
                    self.canvas.create_polygon(x,y+h,x-size,y+h,x-h,y-h, fill="red", outline="black")
                elif unit == "NeuAc"or unit == "Sa":
                    self.canvas.create_polygon(x,y,x-h,y-h,x-size,y,x-h,y+h, fill="violet", outline="black")
                elif unit == "NeuGc"or unit == "Sg":
                    self.canvas.create_polygon(x,y,x-h,y-h,x-size,y,x-h,y+h, fill="azure", outline="black")
                x = x - size -2
        for unit in rest:
            text = unit
            amount = units[unit]
            if amount < -1:
               text = str(amount)+text
            elif amount == -1:
                text = "-"+text
            elif amount == 1:
                text = "+"+text
            else:
                text = "+" +str(amount)+text
            self.canvas.create_text((x, y),
                                    text=text,
                                    anchor="e",
                                    font=self.options["axisnumbering"]["font"])
            # measure new x
            x = x - self.options["axisnumbering"]["font"].measure(text)-2
        return x


    def selectionPanelToggled(self, *arg, **args):
        if self.selectionButton.active.get() == False:
            self._paintCanvas()
        else:
            self.sidePanelSelection.update()

    def visbilityChanged(self, *arg, **args):
        self.initCanvas(keepZoom=False)

    def popup(self, event):

        self.aMenu.delete(0,"end")
        for name in self.names:
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
                                tags=("axis", ))

        index = 0
        for name in self.names:
            if self.visible[name].get() == False:
                continue
            start = index*2+0.5
            if start > self.viewYMin and start < self.viewYMax:
                x = self.convAtoX(self.viewXMin)
                y = self.convBtoY(start)
                y2 = self.convBtoY(start+1)
                if self.options["axislabel"]["showpicto"] == True:
                    self.paintOxoniumion(x,y, name)
                else:
                    self.canvas.create_text((x-5, y),
                                            text=name,
                                            anchor="e",
                                            font=self.options["axisnumbering"]["font"])
                self.canvas.create_line(x-4, y, x, y)
            index += 1

        item = self.canvas.create_text(self.options["margins"]["left"],
                                       self.options["margins"]["top"]/2.0,
                                       text=self.yTitle,
                                       font=self.options["axislabel"]["font"])
        # write legend
        y_legend = self.convBtoY(self.viewYMax)-10
        i = 0
        x0 = self.convAtoX(self.viewXMax)+15
        for legend in self.legend:
            i += 1
            if i == 6:
                legend = "..."
            item = self.canvas.create_text(x0+20,
                                           y_legend,
                                           text=legend,
                                           font=self.options["legend"]["font"],
                                           anchor="nw")
            if i == 6:
                break
            bbox = self.canvas.bbox(item)
            y = (bbox[1]+bbox[3])/2.0
            self.canvas.create_rectangle(x0, y-5, x0+10, y+5, fill=self.legend[legend])
            y_legend = bbox[3]

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


    def _getOxoniumionsIdentification(self, hits):
        names = {}
        values = {}

        for hit in hits:
            collect = []
            total = 0
            for fragment in hit.fragments.values():
                if fragment.typ == glyxtoolms.fragmentation.FragmentType.OXONIUMION:
                    mass = fragment.mass
                    intensity = fragment.peak.y
                    name = fragment.name
                    collect.append((mass, name, intensity))
                    names[name] = mass
                    total += intensity

            for mass, name, intensity in collect:
                values[name] = values.get(name, []) + [intensity/float(total)*100]

            # calculate average
            avg = {}
            sdev = {}
            for name in values:
                length = float(len(hits))
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
            avg, sdev, names  = self._getOxoniumionsIdentification([hit])
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

        if self.selectionButton.active.get() == True:
            self.sidePanelSelection.update()
        self.initCanvas(keepZoom=keepZoom)


    def _paintCanvas(self, addToHistory=True):
        """ Overwrite method to include margin calculation """
        if addToHistory == True:
            self.zoomHistory.append((self.viewXMin, self.viewXMax, self.viewYMin, self.viewYMax))


        self.calculateMargins()
        self.calcScales()
        self.canvas.delete(Tkinter.ALL)
        self.paintObject()
        self._paintAxis()

    def calculateMargins(self):
        # calculate space for oxonium names
        self.options["margins"]["left"] = 100
        if len(self.names) > 0:
            sizes = []
            if self.options["axislabel"]["showpicto"] == True:
                for name in self.names:
                    sizes.append(abs(self.paintOxoniumion(0,0,name)))
            else:
                for name in self.names:
                    sizes.append(self.options["axisnumbering"]["font"].measure(name))
            size = max(sizes)+10
            if size > 80:
                self.options["margins"]["left"] = size+20

        # calculate space for legend
        self.options["margins"]["right"] = 50
        if len(self.legend) > 0:
            sizes = []
            for text in self.legend:
                sizes.append(self.options["legend"]["font"].measure(text))
            size = max(sizes)
            self.options["margins"]["right"] = size+50

class SelectionSidePanel(Tkinter.Frame, object):
    def __init__(self, master, framePlot):
        Tkinter.Frame.__init__(self, master=master)
        self.master = master
        self.framePlot = framePlot

        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

        self.scrollbar = Tkinter.Scrollbar(self)
        self.scrollbar.grid(row=0, column=1, sticky="WNS")
        self.canvas = Tkinter.Canvas(self, yscrollcommand=self.scrollbar.set)
        self.canvas.config(highlightthickness=0)
        self.canvas.grid(row=0, column=0, rowspan=2, sticky="NSWE")

        self.frame = Tkinter.Frame(self.canvas)
        self.canvas.create_window(0, 0, anchor="nw", window=self.frame)

        self.scrollbar.config(command=self.canvas.yview)

        self.empty = Tkinter.Canvas(self, width=10, height=0)
        self.empty.grid(row=1, column=1, sticky="WNS")
        self.empty.config(highlightthickness=0)

        self.frame.columnconfigure(1,weight=1)
        self.frame.rowconfigure(0,weight=0)
        self.frame.rowconfigure(1,weight=1)

        self.canvas.bind("<Configure>", self.on_resize, "+")
        self.frame.bind("<Configure>", self.on_resize, "+")

        self.frameAnnotation = Tkinter.LabelFrame(self.frame,text="Show Oxoniumions")
        self.frameAnnotation.grid(row=0,column=0, sticky="NEW", padx=2)

        self.annotationContent = Tkinter.Frame(self.frameAnnotation)
        self.annotationContent.grid(row=0,column=0)
        b = Tkinter.Label(self.annotationContent, text="None availabe")
        b.pack(side="top", anchor="center")
        self.update()


    def radioGroupChanged(self, *arg, **args):
        if self.currentAnnotation == None:
            self.entryText.config(state="disabled")
            self.entryLookup.config(state="disabled")
            self.entryMass.config(state="disabled")
            return

        self.entryLookup.config(state="readonly")
        self.entryMass.config(state="readonly")
        self.currentAnnotation.show = self.varRadio.get()
        if self.currentAnnotation.show == "text":
            self.entryText.config(state="normal")
        else:
            self.entryText.config(state="disabled")
        self.framePlot._paintCanvas()

    def on_resize(self,event):
        self.frame.update_idletasks()
        size = self.canvas.bbox("all")
        self.empty.config(height=event.height -size[3])
        self.canvas.config(height=size[3], width=size[2])
        self.canvas.config(scrollregion=size)

    def update(self):
        self.annotationContent.destroy()

        self.annotationContent = Tkinter.Frame(self.frameAnnotation)
        self.annotationContent.grid(row=0,column=0)
        if len(self.framePlot.names) == 0:
            b = Tkinter.Label(self.annotationContent, text="None availabe")
            b.pack(side="top", anchor="center")
            return
        for name in self.framePlot.names:
            c = Tkinter.Checkbutton(self.annotationContent, text=name, variable=self.framePlot.visible[name])
            c.pack(side="top", anchor="nw")

