import ttk 
from Tkinter import * 
import math
import FramePlot

class PrecursorView(FramePlot.FramePlot):
    
    def __init__(self,master,model,height=300,width=800):
        FramePlot.FramePlot.__init__(self,master,model,height=height,width=width,xTitle="mz [Th]",yTitle="Intensity [counts]")
        
        self.master = master
        self.specArray = None
        self.NrXScales = 3.0

        self.coord = StringVar()
        l = Label( self,textvariable=self.coord)
        l.grid(row=4, column=0, sticky=N+S)
        
        self.keepZoom = IntVar()
        c = Checkbutton(self, text="keep zoom fixed", variable=self.keepZoom)
        c.grid(row=5, column=0, sticky=N+S)
                
                
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # link function
        self.model.funcUpdateFeaturePrecursorSpectrum = self.initSpectrum

    def setMaxValues(self):
        self.aMax = -1
        self.bMax = -1
        
        for mz,intensity in self.specArray:
            if self.aMax == -1 or mz > self.aMax :
                self.aMax = mz
            if self.bMax == -1  or intensity > self.bMax:
                self.bMax = intensity
        

    def paintObject(self):
        if self.specArray == None:
            return
        # continuous spectrum
        xy = []
        for mz,intensity in self.specArray:
            if mz < self.viewXMin or mz > self.viewXMax:
                continue
            pMZ = self.convAtoX(mz)
            pInt = self.convBtoY(intensity)
            xy.append(pMZ)
            xy.append(pInt)
        if len(xy) > 0:
            item = self.canvas.create_line(xy,tags=("peak",))
        
        
        self.allowZoom = True
            
    def initSpectrum(self,specArray,minMZ,maxMZ):
        print "init feature spectrum"
        self.specArray = specArray
        self.viewXMin = minMZ
        self.viewXMax = maxMZ
        self.viewYMin = 0
        self.viewYMax = max(specArray[:,1])
        self.initCanvas(keepZoom = True)
        """
        feature = self.model.currentAnalysis.currentFeature
        exp = self.model.currentProject.mzMLFile
        minRT,maxRT,minMZ,maxMZ = feature.getBoundingBox()
        
        for spec in exp:
            if spec.getMSLevel() != 1:
                continue
            
        
        if spec == None:
            self.charge = 0
            self.precursormass = 0.0
            return
        self.spec = spec
        self.precursormass = mass
        self.charge = charge
        self.viewXMin = low
        self.viewXMax = high
        self.viewYMin = 0
        self.viewYMax = -1
         # set self.viewYMax
        for peak in self.spec:
            mz = peak.getMZ()
            intens = peak.getIntensity()
            if mz < self.viewXMin or mz > self.viewXMax:
                continue
            if intens > self.viewYMax:
                self.viewYMax = intens
        
        self.initCanvas(keepZoom = True)
        """
        
    def identifier(self):
        return "SpectrumView"
