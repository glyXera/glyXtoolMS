import ttk 
from Tkinter import * 
import math
import FramePlot

class PeakTMP:
    
    def __init__(self,mass,intensity):
        self.mass = mass
        self.intensity = intensity
        
    def getMZ(self):
        return self.mass
        
    def getIntensity(self):
        return self.intensity
        
        
class SpectrumView(FramePlot.FramePlot):
    
    def __init__(self,master,model):
        FramePlot.FramePlot.__init__(self,master,model)
        
        self.master = master
        
        b1 = Button(self, text="save",command=self.save)
        b1.grid(row=2, column=0, sticky=N+S)
        
        b2 = Button(self, text="load",command=self.read)
        b2.grid(row=3, column=0, sticky=N+S)
        

        self.coord = StringVar()
        l = Label( self,textvariable=self.coord)
        l.grid(row=4, column=0, sticky=N+S)
        
        self.keepZoom = IntVar()
        c = Checkbutton(self, text="keep zoom fixed", variable=self.keepZoom)
        c.grid(row=5, column=0, sticky=N+S)
                
                
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # link function
        self.model.funcPaintSpectrum = self.initSpectrum

    def setMaxValues(self):
        self.aMax = -1
        self.bMax = -1
        
        for peak in self.model.spec:
            mz = peak.getMZ()
            intens = peak.getIntensity()
            if self.aMax == -1 or mz > self.aMax :
                self.aMax = mz
            if self.bMax == -1  or intens > self.bMax:
                self.bMax = intens
        

    def paintObject(self):
        for peak in self.model.spec:
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
            pInt0 = self.convBtoY(self.viewYMin)
            item = self.canvas.create_line(pMZ,pInt0,pMZ,pInt,tags=("peak",))
            self.allowZoom = True
    
    def initSpectrum(self,spec):
        print "init spectrum"
        if spec == None:
            return
        self.model.spec = spec
        self.initCanvas()
        
    def identifier(self):
        return "SpectrumView"
        
    def save(self):
        f = file("out.txt","w")
        for peak in self.model.spec:
            f.write(str(peak.getMZ())+"\t"+str(peak.getIntensity())+"\n")
        f.close()
        print "saved"
        
    def read(self):
        f = file("out.txt","r")
        spec = []
        for line in f:
            mass,intensity = line[:-1].split("\t")
            spec.append(PeakTMP(float(mass),float(intensity)))
        f.close()
                
        print "loaded"
        print len(spec)      
        self.initSpectrum(spec)
