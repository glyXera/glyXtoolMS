import ttk
import Tkinter
from glyxtoolms.gui import AnnotatedPlot
from glyxtoolms.gui import Appearance
import glyxtoolms
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
        options["annotations"]["immcolor"] = "yellow"
        options["annotations"]["acolor"] = "blue"
        options["annotations"]["bcolor"] = "blue"
        options["annotations"]["ccolor"] = "blue"
        options["annotations"]["xcolor"] = "blue"
        options["annotations"]["ycolor"] = "blue"
        options["annotations"]["zcolor"] = "blue"
        options["annotations"]["bycolor"] = "blue"
        options["annotations"]["pepcolor"] = "blue"
        options["annotations"]["glycopepcolor"] = "green"


        options["annotations"]["shownames"] = True
        options["annotations"]["showisotopes"] = True
        options["annotations"]["showmasses"] = True
        options["annotations"]["showox"] = True
        options["annotations"]["showimmonium"] = True
        options["annotations"]["showa"] = True
        options["annotations"]["showb"] = True
        options["annotations"]["showc"] = True
        options["annotations"]["showx"] = True
        options["annotations"]["showy"] = True
        options["annotations"]["showz"] = True
        options["annotations"]["showby"] = True
        options["annotations"]["showpep"] = True
        options["annotations"]["showglycopep"] = True


        return options

    def createOptions(self, optionsFrame):
        def toggleVisbility(a,b,c,varname, var):
            self.options["annotations"][varname] = var.get()
            self._paintCanvas(False)

        def addFragmentHighlight(showName=None, text=None, colorName=None):
            if showName != None and text != None:
                var = Tkinter.BooleanVar()
                var.set(self.options["annotations"][showName])
                optionsFrame.addVariable("annotations", showName, var)
                c = Appearance.Checkbutton(frame, text=text, variable=var)
                c.grid(row=frame.row, column=0, columnspan=2, sticky="NWS")
                var.trace("w", lambda a,b,c,d=showName,e=var: toggleVisbility(a,b,c,d,e))
            if colorName != None:
                botton = Tkinter.Button(frame, text="Set Color")
                botton.grid(row=frame.row, column=2, sticky="NW")
                botton.config(fg=self.options["annotations"][colorName])
                botton.config(activeforeground=self.options["annotations"][colorName])
                botton.config(command=lambda a=colorName, b=botton: self.setColor(a,b))
            frame.row += 1



        super(ConsensusSpectrumFrame, self).createOptions(optionsFrame)
        frame = optionsFrame.addLabelFrame("Annotations")
        optionsFrame.addFont(frame, "annotations", "Size: ")

        addFragmentHighlight(showName="showmasses", text="Show Mass Labels")
        addFragmentHighlight(showName="shownames", text="Show Names", colorName = "labelcolor")
        addFragmentHighlight(showName="showisotopes", text="Show Isotopes")

        addFragmentHighlight(showName="showox", text="Highlight oxonium ions", colorName = "oxcolor")
        addFragmentHighlight(showName="showimmonium", text="Highlight immmonium ions", colorName = "immcolor")
        addFragmentHighlight(showName="showa", text="Highlight a-ions", colorName = "acolor")
        addFragmentHighlight(showName="showb", text="Highlight b-ions", colorName = "bcolor")
        addFragmentHighlight(showName="showc", text="Highlight c-ions", colorName = "ccolor")
        addFragmentHighlight(showName="showx", text="Highlight x-ions", colorName = "xcolor")
        addFragmentHighlight(showName="showy", text="Highlight y-ions", colorName = "ycolor")
        addFragmentHighlight(showName="showz", text="Highlight z-ions", colorName = "zcolor")
        addFragmentHighlight(showName="showby", text="Highlight by-ions", colorName = "bycolor")

        addFragmentHighlight(showName="showpep", text="Highlight peptide ions", colorName = "pepcolor")
        addFragmentHighlight(showName="showglycopep", text="Highlight B/Y ions", colorName = "glycopepcolor")


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

        TYPE = glyxtoolms.fragmentation.FragmentType
        paintHierachary = []
        paintHierachary.append((TYPE.OXONIUMION, "showox", "oxcolor",1))
        paintHierachary.append((TYPE.IMMONIUMION, "showimmonium", "immcolor",2))
        paintHierachary.append((TYPE.PEPTIDEION, "showpep", "pepcolor",3))
        paintHierachary.append((TYPE.GLYCOPEPTIDEION, "showglycopep", "glycopepcolor",4))
        paintHierachary.append((TYPE.YION, "showy", "ycolor",5))
        paintHierachary.append((TYPE.BION, "showb", "bcolor",6))
        paintHierachary.append((TYPE.CION, "showc", "ccolor",7))
        paintHierachary.append((TYPE.XION, "showx", "xcolor",8))
        paintHierachary.append((TYPE.ZION, "showz", "zcolor",9))
        paintHierachary.append((TYPE.AION, "showa", "acolor",11))
        paintHierachary.append((TYPE.BYION, "showby", "bycolor",12))
        paintHierachary.append((TYPE.UNKNOWN, "", "",13))


        def findTypes(all_fragments, fragList):
            types = set()
            types.add(TYPE.UNKNOWN)
            for fragment in fragList:
                if fragment.typ == TYPE.ISOTOPE:
                    for name in fragment.parents:
                        if name in all_fragments:
                            types = types.union(findTypes(all_fragments, [all_fragments[name]]))
                else:
                    types.add(fragment.typ)
            return types

        def findColorAndText(all_fragments, fragList):
            # collect types
            types = findTypes(all_fragments, fragList)
            TYPE = glyxtoolms.fragmentation.FragmentType

            annotations = self.options["annotations"]
            color = "black"

            for typ, showVar, colorvar,rank in paintHierachary:
                if typ not in types:
                    continue
                if annotations.get(showVar, False) == True:
                    color = annotations.get(colorvar,"black")
                    break

            # sort fragments after hierachy
            text = []
            for fragment in fragList:
                types = findTypes(all_fragments, [fragment])

                for typ, showVar, colorvar,rank in paintHierachary:
                    if annotations.get(showVar, False) == False:
                        continue
                    if typ in types:
                        break
                if annotations.get(showVar, False) == False:
                    continue
                if typ == TYPE.UNKNOWN:
                    continue
                text.append((rank,fragment.name))

            text = [name for rank,name in sorted(text)]
            return color, text

        if self.consensus == None:
            return
        if self.feature == None:
            return
        pInt0 = self.convBtoY(self.viewYMin)
        # compile list of found oxonium-ions within the MS2 Spectra
        analysis = self.model.currentAnalysis
        if self.hit == None and self.options["annotations"]["showox"] == True:
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
            foundGlycans = set()
            foundFrag = set()
            if self.hit == None: # annotate glycans from scoring tool
                if self.options["annotations"]["showox"] == True:
                    for ionname in glycanFragments:
                        if abs(glycanFragments[ionname]-peak.x) < 0.1:
                            foundGlycans.add(ionname)
            else:
                fragments = self.annotated.get(peak, [])
                for fragment in fragments:
                    if self.options["annotations"]["showisotopes"] == True or fragment.typ != TYPE.ISOTOPE:
                        foundFrag.add(fragment)
            # sort fragment ions
            if len(foundGlycans) > 0 and len(foundFrag) > 0:

                color,text = findColorAndText(self.hit.fragments, foundFrag)
                color = self.options["annotations"]["oxcolor"]
                annotationText.append((pMZ, pInt, "\n".join(list(foundGlycans)+text), masstext))
            elif len(foundGlycans) > 0:
                color = self.options["annotations"]["oxcolor"]
                annotationText.append((pMZ, pInt, "\n".join(foundGlycans), masstext))
            elif len(foundFrag) > 0:
                # find color
                color,text = findColorAndText(self.hit.fragments, foundFrag)
                annotationText.append((pMZ, pInt, "\n".join(text), masstext))
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

        self.annotated = {}
        self.linkFragmentsToPeak()

        self.initCanvas(keepZoom=True)

    def identifier(self):
        return "ConsensusSpectrumFrame"

    def linkFragmentsToPeak(self):
        self.annotated = {}
        if self.feature == None:
            return
        if self.hit == None:
            return
        for fragment in self.hit.fragments.values():
            if fragment.peak == None:
                continue
            self.annotated[fragment.peak] = self.annotated.get(fragment.peak,[]) + [fragment]

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
            mz = self.hit.fragments[ionname].mass
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

