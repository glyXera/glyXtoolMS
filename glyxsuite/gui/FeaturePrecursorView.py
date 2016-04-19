import ttk
import Tkinter
import tkMessageBox

from glyxsuite.gui import FramePlot
from glyxsuite.gui import Appearance

class PrecursorView(FramePlot.FramePlot):

    def __init__(self, master, model, height=300, width=800):
        FramePlot.FramePlot.__init__(self, master, model, height=height, width=width, xTitle="m/z", yTitle="Intensity [counts]")

        self.master = master
        self.specArray = None
        self.NrXScales = 3.0
        self.spectrum = None
        self.feature = None
        self.base = None

        self.coord = Tkinter.StringVar()
        l = ttk.Label(self, textvariable=self.coord)
        l.grid(row=4, column=0, sticky="NS")

        self.keepZoom = Tkinter.IntVar()
        c = Appearance.Checkbutton(self, text="keep zoom fixed", variable=self.keepZoom)
        c.grid(row=5, column=0, sticky="NS")


        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
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

        # link function
        self.model.classes["FeaturePrecursorView"] = self

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
        try:
            self.bMax = max(self.spectrum)
        except:
            self.bMax = 1
        try:
            self.aMax = max(self.base)
        except:
            self.aMax = 1

    def paintObject(self):
        if self.spectrum == None:
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
        # paint monoisotopic mass
        pMZ = self.convAtoX(minMZ)
        self.canvas.create_line(pMZ, pIntMin, pMZ, pIntMax, tags=("leftborder", ),fill="red")
        
        pMZ = self.convAtoX(maxMZ)
        self.canvas.create_line(pMZ, pIntMin, pMZ, pIntMax, tags=("rightborder", ),fill="red")

        self.allowZoom = True
        
    def init(self, spectrumXArray, spectrumYArray, feature, minMZ, maxMZ):
        self.spectrum = spectrumYArray
        self.base = spectrumXArray
        self.feature = feature
        self.viewXMin = minMZ
        self.viewXMax = maxMZ
        self.viewYMin = 0
        if sum(spectrumYArray) > 0:
            self.viewYMax = max(spectrumYArray)
        self.initCanvas(keepZoom=True)

    def identifier(self):
        return "FeaturePrecursorView"
