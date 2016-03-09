import ttk
import Tkinter
import tkMessageBox

import numpy as np

from glyxsuite.gui import FramePlot
from glyxsuite.gui import Appearance
import glyxsuite


class FeatureChromatogramView(FramePlot.FramePlot):

    def __init__(self, master, model, height=300, width=800):
        FramePlot.FramePlot.__init__(self, master, model, height=height, width=width, xTitle="rt [s]", yTitle="Intensity [counts]")

        self.master = master
        self.NrXScales = 3.0
        self.chrom = None
        self.rt = 0
        self.featureLow = 0
        self.featureHigh = 0
        self.minMZView = 0
        self.maxMZView = 0
        self.index = 0
        self.feature = None
        
        self.xTypeTime = True
        

        self.coord = Tkinter.StringVar()
        l = ttk.Label(self, textvariable=self.coord)
        l.grid(row=4, column=0, sticky="NS")

        self.keepZoom = Tkinter.IntVar()
        c = Appearance.Checkbutton(self, text="keep zoom fixed", variable=self.keepZoom)
        c.grid(row=5, column=0, sticky="NS")


        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # link function
        self.model.classes["FeatureChromatogramView"] = self
        

        # Events
        self.canvas.bind("<Left>", self.goLeft)
        self.canvas.bind("<Right>", self.goRight)
        self.canvas.bind("<ButtonRelease-3>", self.popup)
        
        self.aMenu = Tkinter.Menu(self.canvas, tearoff=0)
        self.aMenu.add_command(label="Set Left Retention Border", 
                               command=lambda x="leftborder": self.setBorder(x))
        self.aMenu.add_command(label="Set Right Retention Border",
                               command=lambda x="rightborder": self.setBorder(x))
        self.aMenu.add_command(label="Cancel",
                               command=lambda x="Cancel": self.setBorder(x))
        #self.canvas.bind("<Button-1>", self.setSpectrumPointer)

        self.spectrumPointer = None

    def setBorder(self,status):
        self.aMenu.unpost()
        self.aMenu.grab_release()
        if self.feature == None:
            return
        self.canvas.delete("tempborder")
        if status == "Cancel":
            return
        minRT, maxRT, minMZ, maxMZ = self.feature.getBoundingBox()
        pMZ = self.convAtoX(self.currentX)
        pIntMin = self.convBtoY(self.viewYMin)
        pIntMax = self.convBtoY(self.viewYMax)
        if status == "leftborder":
            if self.currentX >= maxRT:
                return
            self.canvas.create_line(pMZ, pIntMin, pMZ, pIntMax, tags=("tempborder", ),fill="red", dash=(2, 4))
            if tkMessageBox.askyesno('Keep new Retention Border?',
                                     'Do you want to keep the new retention border?'):
                self.feature.minRT = self.currentX
        if status == "rightborder":
            if self.currentX <= minRT:
                return
            self.canvas.create_line(pMZ, pIntMin, pMZ, pIntMax, tags=("tempborder", ),fill="red", dash=(2, 4))
            if tkMessageBox.askyesno('Keep new Retention Border?',
                                     'Do you want to keep the new retention border?'):
                self.feature.maxRT = self.currentX
        self.canvas.delete("tempborder")
    
    
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

    def setSpectrumPointer(self, event):
        if self.model.exp == None:
            return
        if self.allowZoom == False:
            return
        rt = self.convXtoA(event.x)

        # get selected MSLevel
        if self.model.currentAnalysis.selectedChromatogram == None:
            return
        msLevel = self.model.currentAnalysis.selectedChromatogram.msLevel
        nearest = None
        diff = -1
        for spec in self.model.exp:
            if spec.getMSLevel() != msLevel: # fix, needs Level from chromatogram
                continue
            diffNew = abs(spec.getRT()-rt)
            if diff == -1 or diffNew < diff:
                nearest = spec
                diff = diffNew
        if diff != -1:
            self.model.funcPaintSpectrum(nearest)



    def setMaxValues(self):
        self.aMax = -1
        self.bMax = -1

        for rt in self.chrom.rt:
            if self.aMax == -1 or rt > self.aMax:
                self.aMax = rt
        for intensity in self.chrom.intensity:
            if self.bMax == -1 or intensity > self.bMax:
                self.bMax = intensity


    def paintObject(self):
        self.allowZoom = False
        if self.chrom == None:
            return
        if len(self.chrom.rt) != len(self.chrom.intensity):
            raise Exception("Different length of chromatogram parameters!")
        xy = []
        for i in range(0, len(self.chrom.rt)):
            rt = self.chrom.rt[i]
            intens = self.chrom.intensity[i]
            xy.append(self.convAtoX(rt))
            xy.append(self.convBtoY(intens))
        if len(xy) == 0:
            return
        self.canvas.create_line(xy, fill=self.chrom.color, width=1)
        lowMZ = self.convAtoX(self.featureLow)
        highMZ = self.convAtoX(self.featureHigh)
        pIntMin = self.convBtoY(self.viewYMin)
        pIntMax = self.convBtoY(self.viewYMax)
        
        self.canvas.create_line(lowMZ, pIntMin, lowMZ, pIntMax, tags=("leftborder", ),fill="red")
        self.canvas.create_line(highMZ, pIntMin, highMZ, pIntMax, tags=("rightborder", ),fill="red")
        
        self.allowZoom = True
        
    def init(self,chrom, feature, minMZView, maxMZView, index):
        
        self.chrom = chrom
        self.feature = feature
        minRT, maxRT, minMZ, maxMZ = feature.getBoundingBox()
        self.viewXMin = chrom.rt[0]
        self.viewXMax =  chrom.rt[-1]
        self.viewYMin = 0
        self.viewYMax = -1
        self.featureLow = minRT
        self.featureHigh = maxRT
        self.minMZView = minMZView
        self.maxMZView = maxMZView
        
        self.initCanvas(keepZoom=True)
        self.plotPrecursorSpectrum(index)

    def identifier(self):
        return "FeatureChromatogramView"
        
    def plotPositionMarker(self):
        
        pRT = self.convAtoX(self.rt)
        pIntMin = self.convBtoY(self.viewYMin)
        pIntMax = self.convBtoY(self.viewYMax)
        self.canvas.delete("positionmarker")
        item = self.canvas.create_line(pRT, pIntMin, pRT, pIntMax, tags=("positionmarker", ),fill="blue")
        
    def plotPrecursorSpectrum(self, index):
        spec = self.model.currentAnalysis.project.mzMLFile.exp[index]
        if spec.getMSLevel() != 1:
            return
        peaks = spec.get_peaks()
        if hasattr(peaks, "shape"):
            mzArray = peaks[:, 0]
            intensArray = peaks[:, 1]
        else:
            mzArray, intensArray = peaks

        choice_MZ = np.logical_and(np.greater(mzArray, self.minMZView),
                                   np.less(mzArray, self.maxMZView))
        mz_array = np.extract(choice_MZ, mzArray)
        
        intens_array = np.extract(choice_MZ, intensArray)
        self.index = index
        self.rt = spec.getRT()
        self.plotPositionMarker()

        self.model.classes["FeaturePrecursorView"].init(mz_array,
                                                        intens_array,
                                                        self.feature,
                                                        self.minMZView,
                                                        self.maxMZView)
        #return rt, arr_mz_MZ, arr_intens_MZ

    def goLeft(self, event):
        exp = self.model.currentAnalysis.project.mzMLFile.exp
        spec = None
        index = self.index
        while index > 0:
            index -= 1
            spec = exp[index]
            if spec.getRT() < self.chrom.rt[0]:
                return
            if spec.getMSLevel() == 1:
                break
        if spec == None:
            return
        self.plotPrecursorSpectrum(index)


    def goRight(self, event):
        exp = self.model.currentAnalysis.project.mzMLFile.exp
        spec = None
        index = self.index
        while index < exp.size():
            index += 1
            spec = exp[index]
            if spec.getRT() > self.chrom.rt[-1]:
                return
            if spec.getMSLevel() == 1:
                break
        if spec == None:
            return
        self.plotPrecursorSpectrum(index)
            
