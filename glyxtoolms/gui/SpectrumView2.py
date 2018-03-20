import ttk
import Tkinter

from glyxtoolms.gui import AnnotatedPlot
from glyxtoolms.gui import Appearance
import glyxtoolms

"""
class Annotation(object):

    def __init__(self):
        self.x1 = 0
        self.x2 = 0
        self.y = 0
        self.text = ""
        self.items = {}
        self.selected = ""
"""

class SpectrumView(AnnotatedPlot.AnnotatedPlot):

    def __init__(self, master, model):
        AnnotatedPlot.AnnotatedPlot.__init__(self, master, model, xTitle="m/z",
                                     yTitle="Intensity [counts]")

        self.master = master
        self.spec = None # Link to raw spectrum
        self.spectrum = None # Link to current spectrum score

        #self.peaksByItem = {}
        self.clearAnnotatableList()

        self.annotationItems = {}
        self.annotations = {}
        self.currentAnnotation = None
        self.referenceMass = 0

        self.canvas.bind("<Button-2>", self.button2, "+")

        #self.canvas.bind("<Button-1>", self.button1Pressed, "+")
        #self.canvas.bind("<ButtonRelease-1>", self.button1Released, "+")
        #self.canvas.bind("<B1-Motion>", self.button3Motion, "+")


        #self.canvas.bind("<Button-3>", self.button3Pressed, "+")
        #self.canvas.bind("<ButtonRelease-3>", self.button3Released, "+")
        #self.canvas.bind("<B3-Motion>", self.button3Motion, "+")

        #self.canvas.bind("<Delete>", self.deleteAnnotation, "+")

    def identifier(self):
        return "SpectrumView"

    def initSpectrum(self, spec):
        if spec == None:
            return
        if spec.getNativeID() in self.model.currentAnalysis.spectraIds:
             self.annotations = self.model.currentAnalysis.spectraIds[spec.getNativeID()].annotations
        self.spec = spec
        self.referenceMass = 0
        #self.peaksByItem = {}
        self.clearAnnotatableList()
        self.annotationItems = {}
        self.currentAnnotation = None
        self.initCanvas()

    def setMaxValues(self):
        self.aMax = -1
        self.bMax = -1

        for peak in self.spec:
            mz = peak.getMZ()
            intens = peak.getIntensity()
            if self.aMax == -1 or mz > self.aMax:
                self.aMax = mz
            if self.bMax == -1  or intens > self.bMax:
                self.bMax = intens
        self.aMax *= 1.1
        self.bMax *= 1.2

    def paintObject(self):
        if self.spec == None:
            return
        specId = self.spec.getNativeID()
        pInt0 = self.convBtoY(self.viewYMin)

        # create peaklist
        peaks = []
        for peak in self.spec:
            mz = peak.getMZ()
            intens = peak.getIntensity()
            if mz < self.viewXMin or mz > self.viewXMax:
                continue
            if intens < self.viewYMin:
                continue
            peaks.append(AnnotatedPlot.Annotatable(mz,intens))

        # sort peaks after highest intensity
        peaks.sort(reverse=True, key=lambda p: p.y)

        # get scored peaks
        scored = {}
        if specId in self.model.currentAnalysis.spectraIds:
            ions = self.model.currentAnalysis.spectraIds[specId].ions
            for sugar in ions:
                for fragment in ions[sugar]:
                    mass = ions[sugar][fragment]["mass"]
                    l = []
                    for p in peaks:
                        if abs(p.x-mass) < 1.0:
                            l.append((abs(p.x-mass), p.x, sugar, fragment))

                    l.sort()
                    if len(l) > 0:
                        err, mz, sugar, fragment = l[0]
                        scored[mz] = (sugar, fragment)

        scoredPeaks = []
        annotationText = []
        annotationMass = []
        self.clearAnnotatableList()

        for p in peaks:
            # check if peak is a scored peak
            pMZ = self.convAtoX(p.x)
            pInt = self.convBtoY(p.y)
            masstext = str(round(p.x - self.referenceMass, 4))
            if p.x in scored:
                scoredPeaks.append(p)
                sugar, fragment = scored[p.x]
                annotationText.append((pMZ, pInt, fragment+"\n"+masstext))
            else:
                item = self.canvas.create_line(pMZ, pInt0, pMZ, pInt, tags=("peak", ), fill="black")
                self.addAnnotatableItem(item, p)
                annotationMass.append((pMZ, pInt, masstext))

            self.allowZoom = True

        # plot scored peaks last
        scoredPeaks.sort(reverse=True)
        for p in scoredPeaks:
            pMZ = self.convAtoX(p.x)
            pInt = self.convBtoY(p.y)
            item = self.canvas.create_line(pMZ, pInt0, pMZ, pInt, tags=("peak", ), fill="red")
            self.addAnnotatableItem(item, p)

        items = self.plotText(annotationText, set(), 0)
        items = self.plotText(annotationMass, items, 5)

        # paint all available annotations
        self.paintAllAnnotations()

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
            item = self.canvas.create_text((x, y, ),
                                           text=text,
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

    def button2(self, event):
        if self.spec == None:
            return
        peak = self.findPeakAt(event.x)
        if peak == None:
            self.referenceMass = 0
            self.initCanvas(keepZoom=True)
            return
        self.referenceMass = peak.x
        self.initCanvas(keepZoom=True)
