import ttk 
import Tkinter
import math
import FramePlot
        
class SpectrumView(FramePlot.FramePlot):
    
    def __init__(self,master,model,height=300,width=800):
        FramePlot.FramePlot.__init__(self,master,model,height=height,width=width,xTitle="mz [Th]",yTitle="Intensity [counts]")
        
        self.master = master
        self.spec = None

        self.coord = Tkinter.StringVar()
        l = ttk.Label( self,textvariable=self.coord)
        l.grid(row=4, column=0, sticky="NS")
        
        self.keepZoom = Tkinter.IntVar()
        c = ttk.Checkbutton(self, text="keep zoom fixed", variable=self.keepZoom)
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
            if self.aMax == -1 or mz > self.aMax :
                self.aMax = mz
            if self.bMax == -1  or intens > self.bMax:
                self.bMax = intens
        

    def paintObject(self):
        specId = self.spec.getNativeID()
        
        pInt0 = self.convBtoY(self.viewYMin)

        for peak in self.spec:
            mz = peak.getMZ()
            
            intens = peak.getIntensity()
            if mz < self.viewXMin or mz > self.viewXMax:
                continue
            if intens < self.viewYMin:
                continue
            if intens > self.viewYMax:
                intens = self.viewYMax
            pMZ = self.convAtoX(mz)
            pInt = self.convBtoY(intens)
            item = self.canvas.create_line(pMZ,pInt0,pMZ,pInt,tags=("peak",))
            self.allowZoom = True
            
            
        if specId in self.model.currentAnalysis.spectraIds:
            spectrum = self.model.currentAnalysis.spectraIds[specId]
            # paint ions from logscore
            ions = spectrum.ions
            for sugar in ions:
                for fragment in ions[sugar]:
                    intensity = ions[sugar][fragment]["intensity"]
                    mass = ions[sugar][fragment]["mass"]
                    pMZ = self.convAtoX(mass)
                    pInt = self.convBtoY(intensity)
                    self.canvas.create_line(pMZ,pInt0,pMZ,pInt,tags=("score",),fill="red")            
        
    def initSpectrum(self,spec):
        if spec == None:
            return
        self.spec = spec
        self.initCanvas()
        
    def identifier(self):
        return "SpectrumView"
