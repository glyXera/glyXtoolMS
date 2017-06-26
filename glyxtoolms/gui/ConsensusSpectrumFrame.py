import ttk
import Tkinter
from glyxtoolms.gui import AnnotatedPlot
from glyxtoolms.gui import Appearance
import tkFont
from tkColorChooser import askcolor


class ConsensusSpectrumFrame(AnnotatedPlot.AnnotatedPlot):

    def __init__(self, master, model):
        AnnotatedPlot.AnnotatedPlot.__init__(self, master, model, xTitle="m/z",
                                     yTitle="Intensity [counts]")
        self.master = master
        self.hit = None
        self.feature = None
        self.consensus = None
        self.selectedFragments = []
        self.NrXScales = 5.0
        
        self.referenceMass = 0
        
        self.annotationItems = {}
        self.annotations = {}
        self.currentAnnotation = None
        self.peaksByItem = {}
        
        # register additional button bindings
        self.canvas.bind("<Button-2>", self.button2, "+")
        self.canvas.bind("<Button-3>", self.button3, "+")
        
        
    def getDefaultOptions(self):
        options = super(ConsensusSpectrumFrame, self).getDefaultOptions()
        options["annotations"] = {}
        options["annotations"]["font"] = tkFont.Font(family="Arial",size=10)
        options["annotations"]["labelcolor"] = "blue violet"
        options["annotations"]["oxcolor"] = "red"
        options["annotations"]["pepcolor"] = "blue"
        options["annotations"]["shownames"] = True
        options["annotations"]["showmasses"] = True
        options["annotations"]["showox"] = True
        options["annotations"]["showpep"] = True
        return options
    
    def createOptions(self, optionsFrame):
        def toggleVisbility(a,b,c,varname, var):
            self.options["annotations"][varname] = var.get()
            self._paintCanvas(False)
            
        super(ConsensusSpectrumFrame, self).createOptions(optionsFrame)
        frame = optionsFrame.addLabelFrame("Annotations")
        optionsFrame.addFont(frame, "annotations", "Size: ")
        
        nameVar = Tkinter.BooleanVar()
        nameVar.set(self.options["annotations"]["shownames"])
        optionsFrame.addVariable("annotations", "shownames", nameVar)
        c = Appearance.Checkbutton(frame, text="Show Names", variable=nameVar)
        c.grid(row=frame.row, column=0, columnspan=2, sticky="NWS")
        frame.row += 1
        nameVar.trace("w", lambda a,b,c,d="shownames",e=nameVar: toggleVisbility(a,b,c,d,e))
        
        massVar = Tkinter.BooleanVar()
        massVar.set(self.options["annotations"]["showmasses"])
        optionsFrame.addVariable("annotations", "showmasses", massVar)
        c = Appearance.Checkbutton(frame, text="Show Mass Labels", variable=massVar)
        c.grid(row=frame.row, column=0, columnspan=2, sticky="NWS")
        frame.row += 1
        massVar.trace("w", lambda a,b,c,d="showmasses",e=massVar: toggleVisbility(a,b,c,d,e))
        
        oxVar = Tkinter.BooleanVar()
        oxVar.set(self.options["annotations"]["showox"])
        optionsFrame.addVariable("annotations", "showox", oxVar)
        c = Appearance.Checkbutton(frame, text="Highlight Oxonium Ions and Losses", variable=oxVar)
        c.grid(row=frame.row, column=0, columnspan=2, sticky="NWS")
        frame.row += 1
        oxVar.trace("w", lambda a,b,c,d="showox",e=oxVar: toggleVisbility(a,b,c,d,e))
        
        pepVar = Tkinter.BooleanVar()
        pepVar.set(self.options["annotations"]["showpep"])
        optionsFrame.addVariable("annotations", "showpep", pepVar)
        c = Appearance.Checkbutton(frame, text="Highlight Peptide Fragments", variable=pepVar)
        c.grid(row=frame.row, column=0, columnspan=2, sticky="NWS")
        frame.row += 1
        pepVar.trace("w", lambda a,b,c,d="showpep",e=pepVar: toggleVisbility(a,b,c,d,e))
        
        buttonColorLabel = Tkinter.Button(frame, text="Set Color")
        buttonColorLabel.grid(row=1, column=2,rowspan=2, sticky="NW")
        buttonColorLabel.config(fg=self.options["annotations"]["labelcolor"])
        buttonColorLabel.config(activeforeground=self.options["annotations"]["labelcolor"])
        buttonColorLabel.config(command=lambda a="labelcolor", b=buttonColorLabel: self.setColor(a,b))
        #frame.row += 1
        
        buttonColorOx = Tkinter.Button(frame, text="Set Color")
        buttonColorOx.grid(row=3, column=2, sticky="NW")
        buttonColorOx.config(fg=self.options["annotations"]["oxcolor"])
        buttonColorOx.config(activeforeground=self.options["annotations"]["oxcolor"])
        buttonColorOx.config(command=lambda a="oxcolor", b=buttonColorOx: self.setColor(a,b))
        #frame.row += 1
        
        buttonColorPep = Tkinter.Button(frame, text="Set Color")
        buttonColorPep.grid(row=4, column=2, sticky="NW")
        buttonColorPep.config(fg=self.options["annotations"]["pepcolor"])
        buttonColorPep.config(activeforeground=self.options["annotations"]["pepcolor"])
        buttonColorPep.config(command=lambda a="pepcolor", b=buttonColorPep: self.setColor(a,b))
        #frame.row += 1
        
    def setColor(self, name, button):
        color = askcolor(self.options["annotations"][name])[1]
        
        if color == None:
            return
        self.options["annotations"][name] = color
        button.config(fg=color)
        button.config(activeforeground=color)
        self._paintCanvas(False)
        
    def button2(self, event):
        overlap = set(self.canvas.find_overlapping(event.x-10,
                                                   0,
                                                   event.x+10,
                                                   self.height))
        hits = []
        for item in overlap:
            if item in self.peaksByItem:
                hits.append(self.peaksByItem[item])
        if len(hits) == 0:
            self.referenceMass = 0
            self.initCanvas(keepZoom=True)
            return
        peak = max(hits, key=lambda p: p.y)
        self.referenceMass = peak.x
        self.initCanvas(keepZoom=True)

    def button3(self,*args):
        return

    def setMaxValues(self):
        if self.consensus == None:
            return
        self.aMax = -1
        self.bMax = -1

        for peak in self.consensus:
            mz = peak.x
            intens = peak.y
            if self.aMax == -1 or mz > self.aMax:
                self.aMax = mz
            if self.bMax == -1  or intens > self.bMax:
                self.bMax = intens
        self.aMax *= 1.1
        self.bMax *= 1.2

    def paintObject(self):
        if self.consensus == None:
            return
        if self.feature == None:
            return
        pInt0 = self.convBtoY(self.viewYMin)
        # compile list of found oxonium-ions within the MS2 Spectra
        analysis = self.model.currentAnalysis
        glycanFragments = {}
        for spectrum in self.feature.spectra:
            for glycanname in spectrum.ions:
                for ionname in spectrum.ions[glycanname]:
                    ion = spectrum.ions[glycanname][ionname]
                    glycanFragments[ionname] = ion["mass"]
        annotationText = []
        annotationMass = []
        self.peaksByItem = {}
        for peak in self.consensus:
            pMZ = self.convAtoX(peak.x)
            pInt = self.convBtoY(peak.y)

            masstext = str(round(peak.x - self.referenceMass, 4))
            # check if a fragment exists for the peak
            foundGlycan = None
            if self.options["annotations"]["showox"] == True:
                for ionname in glycanFragments:
                    if abs(glycanFragments[ionname]-peak.x) < 0.1:
                        foundGlycan = ionname
                        break

            foundPep = None
            if self.options["annotations"]["showpep"] == True:
                if self.hit != None:
                    for key in self.hit.fragments:
                        if foundGlycan != None:
                            break
                        if abs(self.hit.fragments[key]["mass"]-peak.x) < 0.1:
                            foundPep = key
                            break
            if foundGlycan != None and foundPep != None:
                color = self.options["annotations"]["oxcolor"]
                annotationText.append((pMZ, pInt, foundGlycan+"\n"+foundPep, masstext))
            elif foundGlycan != None:
                color = self.options["annotations"]["oxcolor"]
                annotationText.append((pMZ, pInt, foundGlycan, masstext))
            elif foundPep != None:
                color = self.options["annotations"]["pepcolor"]
                annotationText.append((pMZ, pInt, foundPep, masstext))
            else:
                annotationMass.append((pMZ, pInt, "", masstext))
                color = "black"
            item = self.canvas.create_line(pMZ, pInt0, pMZ, pInt, tags=("peak", ), fill=color)
            self.peaksByItem[item] = peak
        items = self.plotText(annotationText, set(), 0)
        items = self.plotText(annotationMass, items, 5)

        self.plotSelectedFragments()
        
        # paint all available annotations
        self.paintAllAnnotations()
        
        self.allowZoom = True

    def init(self, feature, hit):
        self.hit = hit
        self.feature = feature
        if self.feature != None:
            self.consensus = sorted(feature.consensus, key=lambda e: e.y, reverse=True)
            self.annotations = feature.annotations
        self.selectedFragments = []
        self.viewXMin = 0
        self.viewXMax = -1
        self.viewYMin = -1
        self.viewYMax = -1
        self.referenceMass = 0
        self.annotationItems = {}
        self.currentAnnotation = None
        self.peaksByItem = {}
        
        self.initCanvas(keepZoom=True)

    def identifier(self):
        return "ConsensusSpectrumFrame"


    def plotText(self, collectedText, items=set(), N=0):
        # remove text which is outside of view
        ymax = self.convBtoY(self.viewYMin)
        ymin = self.convBtoY(self.viewYMax)

        xmin = self.convAtoX(self.viewXMin)
        xmax = self.convAtoX(self.viewXMax)
        viewable = []
        for textinfo in collectedText:
            x, y, namedText, massText = textinfo
            if xmin < x < xmax and ymin < y < ymax:
                viewable.append(textinfo)
        # sort textinfo
        viewable = sorted(viewable, key=lambda t: t[1])
        # plot items
        for textinfo in viewable:
            if N > 0 and len(items) >= N:
                break
            x, y, namedText, massText = textinfo
            text = []
            if self.options["annotations"]["shownames"] == True:
                text.append(namedText)
            if self.options["annotations"]["showmasses"] == True:
                text.append(massText)
            text = "\n".join(text)
            splitText = text.split("\n")[::-1]
            tempItems = set()
            hasOverlap = False
            for part in splitText:
                item = self.canvas.create_text((x, y), text=part,
                                               fill=self.options["annotations"]["labelcolor"],
                                               font = self.options["annotations"]["font"],
                                               anchor="s", justify="center")
                tempItems.add(item)
                
                # check bounds of other items
                bbox = self.canvas.bbox(item)
                y = bbox[1] # set new y value based on now drawn string
                overlap = set(self.canvas.find_overlapping(*bbox))
                if len(overlap.intersection(items)) != 0:
                    hasOverlap = True
                    break
            if hasOverlap == False:
                items = items.union(tempItems)
            else:
                for item in tempItems:
                    self.canvas.delete(item)
        return items

    def plotSelectedFragments(self, fragments=None, zoomIn=False):
        # remove previous fragment selections
        self.canvas.delete("fragmentSelection")
        if fragments != None:
            self.selectedFragments = fragments
        if self.hit == None:
            return
        pIntMin = self.convBtoY(self.viewYMin)
        pIntMax = self.convBtoY(self.viewYMax)
        plotting = []
        for ionname in self.selectedFragments:
            mz = self.hit.fragments[ionname]["mass"]
            pMZ = self.convAtoX(mz)
            plotting.append(mz)
            self.canvas.create_line(pMZ, pIntMin, pMZ, pIntMax,
                                    tags=("fragmentSelection", ),
                                    fill="cyan")
        self.canvas.tag_lower("fragmentSelection", "peak")
        # set zoom
        if zoomIn == False:
            return
        if len(plotting) == 0:
            return
        minPlot = min(plotting)
        maxPlot = max(plotting)
        if self.viewXMin <= minPlot and maxPlot <= self.viewXMax:
            return
        # find minimal zoom
        widthNow = abs(self.viewXMax-self.viewXMin) 
        widthFrag = abs(minPlot-minPlot)
        diff = (widthNow - widthFrag)/2.0
        if diff < widthFrag/20.0:
            diff = widthFrag/20.0
        self.viewXMin = minPlot-diff
        self.viewXMax = maxPlot+diff
        self._paintCanvas()

