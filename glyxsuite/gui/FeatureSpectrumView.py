import ttk
import Tkinter

from glyxsuite.gui import FramePlot
from glyxsuite.gui import Appearance

class SpectrumView(FramePlot.FramePlot):

    def __init__(self, master, model, height=300, width=800):
        FramePlot.FramePlot.__init__(self, master, model, height=height,
                                     width=width, xTitle="mz [Th]",
                                     yTitle="Intensity [counts]")

        self.master = master
        self.spec = None

        self.coord = Tkinter.StringVar()
        l = ttk.Label(self, textvariable=self.coord)
        l.grid(row=4, column=0, sticky="NS")

        self.keepZoom = Tkinter.IntVar()
        c = Appearance.Checkbutton(self, text="keep zoom fixed", variable=self.keepZoom)
        c.grid(row=5, column=0, sticky="NS")


        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # link function
        self.model.funcUpdateFeatureMSMSSpectrum = self.initSpectrum

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
            peaks.append((intens, mz))

        # sort peaks after highest intensity
        peaks.sort(reverse=True)

        # get scored peaks
        scored = {}
        if specId in self.model.currentAnalysis.spectraIds:
            ions = self.model.currentAnalysis.spectraIds[specId].ions
            for sugar in ions:
                for fragment in ions[sugar]:
                    mass = ions[sugar][fragment]["mass"]
                    l = []
                    for intens, mz in peaks:
                        if abs(mz-mass) < 1.0:
                            l.append((abs(mz-mass), mz, sugar, fragment))

                    l.sort()
                    if len(l) > 0:
                        err, mz, sugar, fragment = l[0]
                        scored[mz] = (sugar, fragment)

        scoredPeaks = []
        annotationText = []
        annotationMass = []
        for intens, mz in peaks:
            # check if peak is a scored peak
            pMZ = self.convAtoX(mz)
            pInt = self.convBtoY(intens)
            masstext = str(round(mz, 4))
            if mz in scored:
                scoredPeaks.append((intens, mz))
                sugar, fragment = scored[mz]
                annotationText.append((pMZ, pInt, fragment+"\n"+masstext))
            else:
                item = self.canvas.create_line(pMZ, pInt0, pMZ, pInt, tags=("peak", ), fill="black")
                annotationMass.append((pMZ, pInt, masstext))

            self.allowZoom = True

        # plot scored peaks last
        scoredPeaks.sort(reverse=True)
        for intens, mz in scoredPeaks:
            pMZ = self.convAtoX(mz)
            pInt = self.convBtoY(intens)
            item = self.canvas.create_line(pMZ, pInt0, pMZ, pInt, tags=("peak", ), fill="red")

        items = self.plotText(annotationText, set(), 0)
        items = self.plotText(annotationMass, items, 5)

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

    def initSpectrum(self, spec):
        if spec == None:
            return
        self.spec = spec
        self.initCanvas()

    def identifier(self):
        return "FeatureSpectrumView"
