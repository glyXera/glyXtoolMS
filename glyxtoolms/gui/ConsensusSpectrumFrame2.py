import ttk
import Tkinter
from glyxtoolms.gui import AnnotatedPlot
from glyxtoolms.gui import Appearance


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
        pInt0 = self.convBtoY(self.viewYMin)
        # compile list of found oxonium-ions within the MS2 Spectra
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
            for ionname in glycanFragments:
                if abs(glycanFragments[ionname]-peak.x) < 0.1:
                    foundGlycan = ionname
                    break

            foundPep = None
            if foundGlycan != None and foundPep != None:
                color = "green"
                annotationText.append((pMZ, pInt, foundGlycan+"\n"+foundPep+"\n"+masstext))
            if foundGlycan != None:
                color = "red"
                annotationText.append((pMZ, pInt, foundGlycan+"\n"+masstext))
            elif foundPep != None:
                color = "blue"
                annotationText.append((pMZ, pInt, foundPep+"\n"+masstext))
            else:
                annotationMass.append((pMZ, pInt, masstext))
                color = "black"
            item = self.canvas.create_line(pMZ, pInt0, pMZ, pInt, tags=("peak", ), fill=color)
            self.peaksByItem[item] = peak
        items = self.plotText(annotationText, set(), 0)
        items = self.plotText(annotationMass, items, 5)

        # paint all available annotations
        self.paintAllAnnotations()

        self.allowZoom = True

    def init(self, feature):
        if feature.consensus == None:
            return
        self.feature = feature
        self.consensus = sorted(feature.consensus, key=lambda e: e.y, reverse=True)
        self.selectedFragments = []
        self.viewXMin = 0
        self.viewXMax = -1
        self.viewYMin = -1
        self.viewYMax = -1
        self.referenceMass = 0
        self.annotationItems = {}
        self.currentAnnotation = None
        self.peaksByItem = {}
        self.annotations = feature.annotations
        self.initCanvas(keepZoom=True)

    def identifier(self):
        return "ConsensusSpectrumFrame2"


    def plotText(self, collectedText, items=set(), N=0):
        # remove text which is outside of view
        ymax = self.convBtoY(self.viewYMin)
        ymin = self.convBtoY(self.viewYMax)

        xmin = self.convAtoX(self.viewXMin)
        xmax = self.convAtoX(self.viewXMax)
        viewable = []
        for textinfo in collectedText:
            x, y, text = textinfo
            if xmin < x < xmax and ymin < y < ymax:
                viewable.append(textinfo)
        # sort textinfo
        viewable = sorted(viewable, key=lambda t: t[1])
        # plot items

        for textinfo in viewable:
            if N > 0 and len(items) >= N:
                break
            x, y, text = textinfo
            item = self.canvas.create_text((x, y,), text=text,
                                           fill="blue violet",
                                           anchor="s", justify="center")
            # check bounds of other items
            bbox = self.canvas.bbox(item)
            overlap = set(self.canvas.find_overlapping(*bbox))
            if len(overlap.intersection(items)) == 0:
                items.add(item)
            else:
                self.canvas.delete(item)
        return items


