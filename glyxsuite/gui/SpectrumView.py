import ttk 
import Tkinter
import math
import FramePlot
import Appearance

class PeakTMP:
    
    def __init__(self,mass,intensity):
        self.mass = mass
        self.intensity = intensity
        
    def getMZ(self):
        return self.mass
        
    def getIntensity(self):
        return self.intensity
        
        
class SpectrumView(FramePlot.FramePlot):
    
    def __init__(self,master,model,height=300,width=800):
        FramePlot.FramePlot.__init__(self,master,model,height=height,width=width,xTitle="mz [Th]",yTitle="Intensity [counts]")
        
        self.master = master
        self.spec = None

        self.coord = Tkinter.StringVar()
        l = ttk.Label( self,textvariable=self.coord)
        l.grid(row=4, column=0, sticky="NS")
        
        self.keepZoom = Tkinter.IntVar()
        c = Appearance.Checkbutton(self, text="keep zoom fixed", variable=self.keepZoom)
        c.grid(row=5, column=0, sticky="NS")
                
                
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # link function
        self.model.funcScoringMSMSSpectrum = self.initSpectrum

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
            peaks.append((intens,mz))
            
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
                    for intens,mz in peaks:
                        if abs(mz-mass) < 1.0:
                            l.append((abs(mz-mass),mz,sugar,fragment))
                            
                    l.sort()
                    if len(l) > 0:
                        err,mz,sugar,fragment = l[0]
                        scored[mz] = (sugar,fragment)
        
        scoredPeaks = []
        i = 0
        e = 0
        for intens,mz in peaks:
            i += 1
            # check if peak is a scored peak
            pMZ = self.convAtoX(mz)
            pInt = self.convBtoY(intens)
            text = []
            if mz in scored:
                scoredPeaks.append((intens,mz))
                sugar,fragment = scored[mz]
                if e < 5:
                    text.append(fragment)
                    e += 1
            else:
                item = self.canvas.create_line(pMZ,pInt0,pMZ,pInt,tags=("peak",),fill="black")    
            # plot only masses for 5 highest peaks
            if i < 5:
                text.append(str(round(mz,3)))
            if len(text):
                self.canvas.create_text((pMZ,pInt,),text="\n".join(text),anchor="s",justify="center")
            
            self.allowZoom = True
        
        # plot scored peaks last
        scoredPeaks.sort(reverse=True)
        for intens,mz in scoredPeaks:
            pMZ = self.convAtoX(mz)
            pInt = self.convBtoY(intens)
            item = self.canvas.create_line(pMZ,pInt0,pMZ,pInt,tags=("peak",),fill="red")
                
        # make text
        
        """
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
                    self.canvas.create_text((pMZ,pInt,),text=fragment,anchor="s")
                    self.canvas.create_line(pMZ,pInt0,pMZ,pInt,tags=("score",),fill="red")            
        """
    def initSpectrum(self,spec):
        if spec == None:
            return
        self.spec = spec
        self.initCanvas()
        
    def identifier(self):
        return "SpectrumView"
