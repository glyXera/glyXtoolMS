import ttk
import Tkinter

from glyxtoolms.gui import FramePlot
from glyxtoolms.gui import Appearance

class TwoDView(FramePlot.FramePlot):

    def __init__(self, master, model):
        FramePlot.FramePlot.__init__(self, master, model, xTitle="rt [s]",
                                     yTitle="m/z")

        self.master = master
        self.xTypeTime = True
        self.featureItems = {}
        self.currentFeatures = []

        s = ttk.Style()

        s.map('TCheckbutton',
              foreground=[('disabled', 'black'),
                          ('pressed', 'black'),
                          ('active', 'black')],
              background=[('disabled', '#d9d9d9'),
                          ('pressed', '!focus', '#d9d9d9'),
                          ('active', '#d9d9d9')])

        self.visible = {}
        for name in ["Glycopeptide spectra",
                      "Non-Glycopeptide spectra",
                      "Glycopeptide features",
                      "Non-Glycopeptide features"]:
            self.visible[name] = Tkinter.BooleanVar()
            self.visible[name].set(True)
            self.visible[name].trace("w", self.visbilityChanged)

        self.canvas.bind("<Button-1>", self.eventMouseClick, "+")
        # Events
        #self.canvas.bind("<Left>", self.setButtonValue)
        #self.canvas.bind("<Right>", self.setButtonValue)
        #self.canvas.bind("<Button-1>", self.setSpectrumPointer)
        """
        optionsFrame = ttk.Labelframe(master, text="Plot Options")
        optionsFrame.grid(row=0, column=1, sticky="NS")

        self.ov1 = Tkinter.IntVar()
        oc1 = Appearance.Checkbutton(optionsFrame,
                                     text="Right Charge",
                                     variable=self.ov1,
                                     command=lambda: self.setButtonValue(1))
        oc1.grid(row=3, column=0, sticky="WS")
        #print "class", oc1.winfo_class()

        self.ov2 = Tkinter.IntVar() # Switch all Features and Wrong Charge
        oc2 = Appearance.Checkbutton(optionsFrame,
                                     text="Wrong Charge",
                                     variable=self.ov2,
                                     command=lambda: self.setButtonValue(2))
        oc2.grid(row=4, column=0, sticky="WS")

        self.ov3 = Tkinter.IntVar() # Switch all Outside Features
        oc3 = Appearance.Checkbutton(optionsFrame, text="Outside Feature",
                                     variable=self.ov3,
                                     command=lambda: self.setButtonValue(3))
        oc3.grid(row=6, column=0, sticky="WS")

        self.ov4 = Tkinter.IntVar() # Switch all Glycopeptide
        ol4 = ttk.Label(optionsFrame, text="Glycopeptide")
        ol4.grid(row=0, column=2, sticky="S")
        oc4 = Appearance.Checkbutton(optionsFrame,
                                     variable=self.ov4,
                                     command=lambda: self.setButtonValue(4))
        oc4.grid(row=1, column=2, sticky="S")

        self.ov5 = Tkinter.IntVar() # Switch all No Glycopeptide
        ol5 = ttk.Label(optionsFrame, text="No Glycopeptide")
        ol5.grid(row=0, column=4, sticky="S")
        oc5 = Appearance.Checkbutton(optionsFrame,
                                     variable=self.ov5,
                                     command=lambda: self.setButtonValue(5))
        oc5.grid(row=1, column=4, sticky="S")

        self.ov6 = Tkinter.IntVar() # In Feature / Glyco / Right Charge
        oc6 = Appearance.Checkbutton(optionsFrame,
                                     variable=self.ov6,
                                     command=lambda: self.setButtonValue(6))
        oc6.grid(row=3, column=2, sticky="NS")

        self.ov7 = Tkinter.IntVar() # In Feature / Glyco / Wrong Charge
        oc7 = Appearance.Checkbutton(optionsFrame,
                                     variable=self.ov7,
                                     command=lambda: self.setButtonValue(7))
        oc7.grid(row=4, column=2, sticky="NS")

        self.ov8 = Tkinter.IntVar() # In Feature / No Glyco / Right Charge
        oc8 = Appearance.Checkbutton(optionsFrame,
                                     variable=self.ov8,
                                     command=lambda: self.setButtonValue(8))
        oc8.grid(row=3, column=4, sticky="NS")

        self.ov9 = Tkinter.IntVar() # In Feature / No Glyco / Wrong Charge
        oc9 = Appearance.Checkbutton(optionsFrame,
                                     variable=self.ov9,
                                     command=lambda: self.setButtonValue(9))
        oc9.grid(row=4, column=4, sticky="NS")

        self.ov10 = Tkinter.IntVar() # Glyco / Outside feature
        oc10 = Appearance.Checkbutton(optionsFrame,
                                      variable=self.ov10,
                                      command=lambda: self.setButtonValue(10))
        oc10.grid(row=6, column=2, sticky="NS")

        self.ov11 = Tkinter.IntVar() # No Glyco / Outside feature
        oc11 = Appearance.Checkbutton(optionsFrame,
                                      variable=self.ov11,
                                      command=lambda: self.setButtonValue(11))
        oc11.grid(row=6, column=4, sticky="NS")

        s1 = ttk.Separator(optionsFrame)
        s1.grid(row=2, column=0, columnspan=5, sticky="NSEW")
        s2 = ttk.Separator(optionsFrame)
        s2.grid(row=5, column=0, columnspan=5, sticky="NSEW")

        s3 = ttk.Separator(optionsFrame, orient="vertical")
        s3.grid(row=0, column=1, rowspan=7, sticky="NSEW")
        s4 = ttk.Separator(optionsFrame, orient="vertical")
        s4.grid(row=0, column=3, rowspan=7, sticky="NSEW")

        # set default states
        self.ov1.set(0)
        self.ov2.set(0)
        self.ov3.set(0)
        self.ov4.set(0)
        self.ov5.set(0)
        self.ov6.set(1)
        self.ov7.set(1)
        self.ov8.set(1)
        self.ov9.set(1)
        self.ov10.set(1)
        self.ov11.set(0)
        """

        # create popup menu
        self.aMenu = Tkinter.Menu(self, tearoff=0)
        self.canvas.bind("<Button-3>", self.popup)

    def visbilityChanged(self, *arg, **args):
        self.paintObject()

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

    def setButtonValue(self, i):
        state = getattr(self, "ov"+str(i)).get()
        if i == 1:
            self.ov6.set(state)
            self.ov8.set(state)
        elif i == 2:
            self.ov7.set(state)
            self.ov9.set(state)
        elif i == 3:
            self.ov10.set(state)
            self.ov11.set(state)
        elif i == 4:
            self.ov6.set(state)
            self.ov7.set(state)
            self.ov10.set(state)
        elif i == 5:
            self.ov8.set(state)
            self.ov9.set(state)
            self.ov11.set(state)
        # plot feature
        if self.model.currentAnalysis == None:
            return
        if self.model.currentAnalysis.analysis == None:
            return
        self.init(keepZoom=True)

    def setMaxValues(self):
        self.aMax = -1
        self.bMax = -1
        for feature in self.model.currentAnalysis.analysis.features:
            rt = feature.getRT()
            mz = feature.getMZ()
            if self.aMax < rt:
                self.aMax = rt
            if self.bMax < mz:
                self.bMax = mz
        self.aMax *= 1.1
        self.bMax *= 1.1

    def plotFeatureLine(self, feature):
        if feature.passesFilter == False:
                return
        rt1, rt2, mz1, mz2 = feature.getBoundingBox()
        rt1 = self.convAtoX(rt1)
        rt2 = self.convAtoX(rt2)
        mz1 = self.convBtoY(mz1)
        mz2 = self.convBtoY(mz2)
        rt0 = self.convAtoX(self.viewXMin)
        rtMax = self.convAtoX(self.viewXMax)
        mz0 = self.convBtoY(self.viewYMin)
        mzMax = self.convBtoY(self.viewYMax)
        color = "grey"
        self.canvas.create_line(rt0, mz1, rtMax, mz1, fill=color)
        self.canvas.create_line(rt0, mz2, rtMax, mz2, fill=color)
        self.canvas.create_line(rt1, mz0, rt1, mzMax, fill=color)
        self.canvas.create_line(rt2, mz0, rt2, mzMax, fill=color)

    def paintFeatures(self):
        if self.model.currentAnalysis == None:
            return
        if self.model.currentAnalysis.analysis == None:
            return
        self.featureItems = {}
        for feature in self.currentFeatures:
            self.plotFeatureLine(feature)

        for feature in self.model.currentAnalysis.analysis.features:
            if feature.passesFilter == False:
                continue

            rt1, rt2, mz1, mz2 = feature.getBoundingBox()
            rt1 = self.convAtoX(rt1)
            rt2 = self.convAtoX(rt2)
            mz1 = self.convBtoY(mz1)
            mz2 = self.convBtoY(mz2)

            linewidth = 2
            #if chrom.selected == True:
            #    linewidth = 2
            xy = []
            xy += [rt1, mz1]
            xy += [rt2, mz1]
            xy += [rt2, mz2]
            xy += [rt1, mz2]
            xy += [rt1, mz1]
            if feature in self.currentFeatures:
                color = "purple"
            elif feature.getId().startswith("own"):
                color = "orange"
            else:
                color = "black"
            item = self.canvas.create_line(xy, fill=color, width=linewidth)
            self.featureItems[item] = feature


    def paintSpectra(self):
        if self.model.currentAnalysis == None:
            return
        if self.model.currentAnalysis.analysis == None:
            return
        # calculate circle diameter
        #diam = int(min(self.slopeA, self.slopeB)*2)
        diam = int(min(self.slopeA, self.slopeB)*2)+1.5
        # plot msms spectra
        #colorGlyco = "olive"
        colorGlycoNoHit = "dark khaki"
        colorGlycoOneHit = "green"
        colorGlycoMultipleHits = "cyan"
        colorNonGlyco = "blue"
        for spectrum in self.model.currentAnalysis.analysis.spectra:
            if spectrum.passesFilter == False:
                continue
            # get charge state
            hasCharge = False
            nrFeatureHits = {0} # find out how many hits the spectrum belongs to
            for feature in spectrum.features:
                if feature.passesFilter == False:
                    continue
                nrFeatureHits.add(len(feature.hits))

                if feature.charge == spectrum.precursorCharge:
                    hasCharge = True
                    break
            nrFeatureHits = max(nrFeatureHits)

            if spectrum.isGlycopeptide:
                if self.visible["Glycopeptide spectra"].get() == False:
                    continue
                color = colorGlycoOneHit
            else:
                if self.visible["Non-Glycopeptide spectra"].get() == False:
                    continue
                color = colorNonGlyco
            """
            nr = 1
            if spectrum.isGlycopeptide:
                nr *= 1
            else:
                nr *= 2

            if len(spectrum.features) == 0:
                nr *= 3
            elif hasCharge == True:
                nr *= 5
            else:
                nr *= 7
            if nr == 5:
                #if self.ov6.get() == 0:
                #    continue
                if nrFeatureHits == 0:
                    color = colorGlycoNoHit
                elif nrFeatureHits == 1:
                    color = colorGlycoOneHit
                else:
                    color = colorGlycoMultipleHits
            elif nr == 7:
                #if self.ov7.get() == 0:
                #    continue
                if nrFeatureHits == 0:
                    color = colorGlycoNoHit
                elif nrFeatureHits == 1:
                    color = colorGlycoOneHit
                else:
                    color = colorGlycoMultipleHits
            elif nr == 3:
                #if self.ov10.get() == 0:
                #    continue
                if nrFeatureHits == 0:
                    color = colorGlycoNoHit
                elif nrFeatureHits == 1:
                    color = colorGlycoOneHit
                else:
                    color = colorGlycoMultipleHits
            elif nr == 10:
                #if self.ov8.get() == 0:
                #    continue
                color = colorNonGlyco
            elif nr == 14:
                #if self.ov9.get() == 0:
                #    continue
                color = colorNonGlyco
            else:
                #if self.ov11.get() == 0:
                #    continue
                color = colorNonGlyco
            """
            x = self.convAtoX(spectrum.rt)
            y = self.convBtoY(spectrum.precursorMass)
            #color = "red"
            item = self.canvas.create_oval(x-diam, y-diam, x+diam, y+diam, fill=color)

    def paintObject(self):
        if self.model.currentAnalysis == None:
            return
        if self.model.currentAnalysis.analysis == None:
            return
        self.allowZoom = False

        self.paintFeatures()
        self.paintSpectra()

        self.allowZoom = True

    def init(self, features=[], keepZoom=False):
        if self.model.currentAnalysis == None:
            return
        if self.model.currentAnalysis.analysis == None:
            return
        self.currentFeatures = features
        self.initCanvas(keepZoom=keepZoom)

    def eventMouseClick(self, event):
        if self.toolbar.active.get("toggle", "") != "": # TODO create real action
            return
        # clear color from all items
        self.canvas.itemconfigure("site", fill="black")

        overlap = set(self.canvas.find_overlapping(event.x-10,
                                                   event.y-10,
                                                   event.x+10,
                                                   event.y+10))
        nearest, distn = None, 0

        for item in overlap:
            if item in self.featureItems:
                # find nearest
                coords = self.canvas.coords(item)
                x = sum(coords[0:8:4])/2.0
                y = sum(coords[1:8:4])/2.0
                dist = (x-event.x)**2 + (y-event.y)**2
                if nearest == None or dist < distn:
                    nearest = self.featureItems[item]
                    distn = dist
        if nearest != None:
            self.model.currentAnalysis.currentFeature = nearest
            self.currentFeatures = [nearest]
            self.model.classes["NotebookFeature"].selectFeature(nearest)

    def identifier(self):
        return "TwoDView"



