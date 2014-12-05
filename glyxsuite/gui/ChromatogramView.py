import ttk 
from Tkinter import * 
import math
import FramePlot
import DataModel

        
class ChromatogramView(FramePlot.FramePlot):
    
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
        self.model.funcPaintChromatograms = self.initChromatogram
        
        # Events
        self.canvas.bind("<Left>", self.sayHi)
        self.canvas.bind("<Right>", self.sayHi)
        self.canvas.bind("<Button-1>", self.setSpectrumPointer)
        
        self.spectrumPointer = None
        
        

    def setSpectrumPointer(self,event):
        if self.model.exp == None:
            return
        if self.allowZoom == False:
            return
        rt = self.convXtoA(event.x)
        
        # get selected MSLevel
        if self.model.selectedChromatogram == None:
            return
        msLevel = self.model.selectedChromatogram.msLevel
        nearest = None
        diff = -1
        for spec in self.model.exp:
            if spec.getMSLevel() != msLevel: # fix, needs Level from chromatogram
                continue
            diffNew = abs(spec.getRT()-rt)
            if diff == -1 or diffNew < diff:
                nearest = spec
                diff = diffNew
        print nearest,msLevel,nearest == None,diff 
        if diff != -1:
            print "do spectrum"
            self.model.funcPaintSpectrum(nearest)
        
        
        
    def setMaxValues(self):
        self.aMax = -1
        self.bMax = -1
        for treeId in self.model.chromatograms:
            chrom = self.model.chromatograms[treeId]
            if chrom.plot == False:
                continue
            for rt in chrom.rt:
                if self.aMax == -1 or rt > self.aMax :
                    self.aMax = rt
            for intensity in chrom.intensity:
                if self.bMax == -1 or intensity > self.bMax :
                    self.bMax = intensity


    def paintObject(self):
        self.allowZoom = False
        for treeId in self.model.chromatograms:
            chrom = self.model.chromatograms[treeId]
            if chrom.plot == False:
                continue
            if chrom.selected == True:
                linewidth = 2
            else:
                linewidth = 1
            if len(chrom.rt) != len(chrom.intensity):
                raise Exception("Different length of chromatogram parameters!")
            xy = []
            for i in range(0,len(chrom.rt)):
                rt = chrom.rt[i]
                intens = chrom.intensity[i]       
                xy.append(self.convAtoX(rt))
                xy.append(self.convBtoY(intens))
            if len(xy) == 0:
                continue
            item = self.canvas.create_line(xy,fill=chrom.color, width = linewidth)
            self.allowZoom = True
    
    def initChromatogram(self,keepZoom = False):
        print "init chromatogram"
        self.initCanvas(keepZoom = keepZoom)

    def identifier(self):
        return "ChromatogramView"
    
    def save(self):
        f = file("chromout.txt","w")
        for treeId in self.model.chromatograms:
            chrom = self.model.chromatograms[treeId]
            f.write("name:"+chrom.name+"\n")
            f.write("rt:"+reduce(lambda x,y:str(x)+";"+str(y),chrom.rt)+"\n")
            f.write("int:"+reduce(lambda x,y:str(x)+";"+str(y),chrom.intensity)+"\n")
            f.write("color:"+str(chrom.color)+"\n")
            f.write("low:"+str(chrom.rangeLow)+"\n")
            f.write("high:"+str(chrom.rangeHigh)+"\n")
            f.write("plot:"+str(chrom.plot)+"\n")
        f.close()
        print "saved"
        
    def read(self):
        f = file("chromout.txt","r")
        chroms = {}
        c = DataModel.Chromatogram()
        for line in f:
            key,content = line[:-1].split(":")
            if key == "name":
                c = DataModel.Chromatogram()
                c.plot = True
                c.name = content
                chroms[content] = c
            if key == "rt":
                c.rt = map(float,content.split(";"))
            if key == "int":
                c.intensity = map(float,content.split(";"))
            if key == "color":
                c.color = content
            if key == "low":
                c.rangeLow = float(content)
            if key == "high":
                c.rangeHigh = float(content)
            if key == "plot":
                if content == "True":
                    c.plot = True
                else:
                    c.plot = False
        
                
        f.close()
        self.model.chromatograms = chroms
        self.initChromatogram()
        print "loaded", len(chroms), " chromatograms"
        
    
