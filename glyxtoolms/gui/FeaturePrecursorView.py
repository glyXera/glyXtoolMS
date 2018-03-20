import ttk
import Tkinter
import tkMessageBox
import glyxtoolms
import numpy as np
from glyxtoolms.gui import FramePlot
from glyxtoolms.gui import Appearance

class PrecursorView(FramePlot.FramePlot):

    def __init__(self, master, model):
        FramePlot.FramePlot.__init__(self, master, model, xTitle="m/z", yTitle="Intensity [counts]")

        self.master = master
        self.specArray = None
        self.NrXScales = 3.0
        self.spectrum = []
        self.feature = None
        self.base = []

        # Events
        self.canvas.bind("<ButtonRelease-3>", self.popup)

        # Popup
        self.aMenu = Tkinter.Menu(self.canvas, tearoff=0)
        self.aMenu.add_command(label="Set monoisotopic peak",
                               command=lambda x="mono": self.setBorder(x))
        self.aMenu.add_command(label="Set Left Feature Border",
                               command=lambda x="leftborder": self.setBorder(x))
        self.aMenu.add_command(label="Set Right Feature Border",
                               command=lambda x="rightborder": self.setBorder(x))
        self.aMenu.add_command(label="Cancel",
                               command=lambda x="Cancel": self.setBorder(x))

    def setBorder(self,status):
        self.aMenu.unpost()
        self.aMenu.grab_release()
        if self.feature == None:
            return
        self.canvas.delete("tempborder")
        self.canvas.delete("tempmono")
        if status == "Cancel":
            return
        minRT, maxRT, minMZ, maxMZ = self.feature.getBoundingBox()
        pMZ = self.convAtoX(self.currentX)
        pIntMin = self.convBtoY(self.viewYMin)
        pIntMax = self.convBtoY(self.viewYMax)
        if status == "mono":
            if self.currentX <= minMZ or self.currentX >= maxMZ:
                return
            self.canvas.create_line(pMZ, pIntMin, pMZ, pIntMax, tags=("tempmono", ),fill="blue", dash=(2, 4))
            if tkMessageBox.askyesno('Keep new monoisotopic peak?',
                                     'Do you want to keep the new monoisotopic peak?'):
                self.feature.mz = self.currentX
                self.model.currentAnalysis.featureEdited(self.feature)

        if status == "leftborder":
            if self.currentX >= maxMZ:
                return
            self.canvas.create_line(pMZ, pIntMin, pMZ, pIntMax, tags=("tempborder", ),fill="red", dash=(2, 4))
            if tkMessageBox.askyesno('Keep new border?',
                                     'Do you want to keep the new feature border?'):
                self.feature.minMZ = self.currentX
                self.model.currentAnalysis.featureEdited(self.feature)

        if status == "rightborder":
            if self.currentX <= minMZ:
                return
            self.canvas.create_line(pMZ, pIntMin, pMZ, pIntMax, tags=("tempborder", ),fill="red", dash=(2, 4))
            if tkMessageBox.askyesno('Keep new border?',
                                     'Do you want to keep the new feature border?'):
                self.feature.maxMZ = self.currentX
                self.model.currentAnalysis.featureEdited(self.feature)

        self.canvas.delete("tempborder")
        self.canvas.delete("tempmono")

    def popup(self, event):
        self.aMenu.post(event.x_root, event.y_root)
        self.mouse_position = event.x_root
        self.aMenu.grab_set()
        self.aMenu.focus_set()
        self.aMenu.bind("<FocusOut>", self.removePopup)


    def removePopup(self,event):
        try: # catch bug in Tkinter with tkMessageBox. TODO: workaround
            if self.focus_get() != self.aMenu:
                self.aMenu.unpost()
                self.aMenu.grab_release()
        except:
            pass

    def setMaxValues(self):
        if len(self.spectrum) == 0:
            return
        try:
            self.bMax = max(self.spectrum)
        except:
            self.bMax = 1
        try:
            self.aMax = max(self.base)
        except:
            self.aMax = 1

    def paintObject(self):
        if len(self.spectrum) == 0:
            return
        if self.feature == None:
            return

        # continuous spectrum
        xy = []
        for mz, intensity in zip(self.base,self.spectrum):
            if mz < self.viewXMin or mz > self.viewXMax:
                continue
            pMZ = self.convAtoX(mz)
            pInt = self.convBtoY(intensity)
            xy.append(pMZ)
            xy.append(pInt)
        if len(xy) > 0:
            self.canvas.create_line(xy, tags=("peak", ))

        pIntMin = self.convBtoY(self.viewYMin)
        pIntMax = self.convBtoY(self.viewYMax)

        # paint monoisotopic mass
        pMZ = self.convAtoX(self.feature.getMZ())
        self.canvas.create_line(pMZ, pIntMin, pMZ, pIntMax, tags=("monoisotope", ),fill="blue")

        minRT, maxRT, minMZ, maxMZ = self.feature.getBoundingBox()

        # paint border
        pMZ = self.convAtoX(minMZ)
        self.canvas.create_line(pMZ, pIntMin, pMZ, pIntMax, tags=("leftborder", ),fill="red")

        pMZ = self.convAtoX(maxMZ)
        self.canvas.create_line(pMZ, pIntMin, pMZ, pIntMax, tags=("rightborder", ),fill="red")

        # paint confidence interval
        self.plotConfidenceBoxes()


        self.allowZoom = True

    def plotConfidenceBoxes(self):

        def countStuff(x, l5, l95):
            N = 0
            for a,b in zip(l5, l95):
                if b <= x <= a:
                    N += 1
            return N

        xp = []
        for i in range(0,5):
            xp.append(self.feature.getMZ()+i/float(self.feature.getCharge())*glyxtoolms.masses.MASS["H+"])

        yp = np.interp(xp, self.base, self.spectrum)


        # get convidence range
        key = int(self.feature.getMZ()*self.feature.getCharge()/50)*50
        conv = self.model.resources["isotopes"][key]

        z5 = np.array([conv[i]["5%"] for i in range(0,5)])
        z50 = np.array([conv[i]["50%"] for i in range(0,5)])
        z95 = np.array([conv[i]["95%"] for i in range(0,5)])

        # find best fit
        l5 = [yp[i]/z5[i] for i in range(0,5)]
        l95 = [yp[i]/z95[i] for i in range(0,5)]

        ky = sorted(l5+l95)
        kx = [countStuff(value, l5,l95) for value in ky]

        # split stretches
        stretches = {}
        current = -1
        stretch = []
        for a,b in zip(kx,ky):
            if a != current:
                stretches[current] = stretches.get(current, []) + [stretch]
                current = a
                stretch = []
            stretch.append(b)

        # get longest strecht
        strecht = max(stretches[max(stretches.keys())], key=lambda x:len(x))
        if len(strecht) > 0:
            fa = (min(strecht)+max(strecht))/2.0
        else:
            fa = yp[0]/z50[0]
        #fa = np.polyfit(zp,yp,1)[0]

        # plot boxes
        for i in range(0,5):

            pMZlow = self.convAtoX(xp[i]-0.05)
            pMZhigh = self.convAtoX(xp[i]+0.05)
            pIntLow = self.convBtoY(conv[i]["5%"]*fa)
            pInthigh = self.convBtoY(conv[i]["95%"]*fa)
            b =  [pMZlow,  pIntLow]
            b += [pMZhigh, pIntLow]
            b += [pMZhigh, pInthigh]
            b += [pMZlow,  pInthigh]
            b += [pMZlow,  pIntLow]
            self.canvas.create_line(b, tags=("box", ), fill="red")


    def init(self, spectrumXArray, spectrumYArray, feature, minMZ, maxMZ):
        self.spectrum = spectrumYArray
        self.base = spectrumXArray
        self.feature = feature
        self.viewXMin = minMZ
        self.viewXMax = maxMZ
        self.viewYMin = 0
        if len(self.spectrum) > 0 and sum(spectrumYArray) > 0:
            self.viewYMax = max(spectrumYArray)
        self.initCanvas(keepZoom=True)

    def identifier(self):
        return "FeaturePrecursorView"
