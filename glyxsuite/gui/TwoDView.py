import ttk 
from Tkinter import * 
import math
import FramePlot
import DataModel

        
class TwoDView(FramePlot.FramePlot):
    
    def __init__(self,master,model,height=300,width=300):
        FramePlot.FramePlot.__init__(self,master,model,height=height,width=width)
        
        self.master = master

        self.coord = StringVar()
        l = Label( self,textvariable=self.coord)
        l.grid(row=4, column=0, sticky=N+S)
        
        self.keepZoom = IntVar()
        c = Checkbutton(self, text="keep zoom fixed", variable=self.keepZoom)
        c.grid(row=5, column=0, sticky=N+S)
                
                
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # link function
        self.model.funcFeatureTwoDView = self.init
        
        # Events
        #self.canvas.bind("<Left>", self.sayHi)
        #self.canvas.bind("<Right>", self.sayHi)
        #self.canvas.bind("<Button-1>", self.setSpectrumPointer)
        
        
    
        
    def setMaxValues(self):
        self.aMax = -1
        self.bMax = -1
        for feature in self.model.currentAnalysis.analysis.features:
            rt = feature.getRT()
            mz = feature.getMZ()
            if self.aMax < rt:
                self.aMax = rt
            if self.bMax < mz:
                self.bMax = mz


    def paintObject(self):
        print "paintObject"
        self.allowZoom = False
        
        # calculate circle diameter
        diam = int(min(self.slopeA,self.slopeB)*2)
        print "diameter",diam
        for feature in self.model.currentAnalysis.analysis.features:
            rt1,rt2,mz1,mz2 = feature.getBoundingBox()
            rt1 = self.convAtoX(rt1)
            rt2 = self.convAtoX(rt2)
            mz1 = self.convBtoY(mz1)
            mz2 = self.convBtoY(mz2)

            linewidth = 1
            #if chrom.selected == True:
            #    linewidth = 2
            xy = []
            xy += [rt1,mz1]
            xy += [rt2,mz1]
            xy += [rt2,mz2]
            xy += [rt1,mz2]
            xy += [rt1,mz1]
            if self.model.currentAnalysis.currentFeature == feature:
                color = "red"
                colorSpec = "green"
            else:
                color = "black"
                colorSpec = "white"
            item = self.canvas.create_line(xy,fill=color, width = linewidth)
            
        # plot msms spectra
        for specId in self.model.currentAnalysis.spectraInFeatures:
            features = self.model.currentAnalysis.spectraInFeatures[specId]
            currentFeature = self.model.currentAnalysis.currentFeature
            if currentFeature is None:
                color = "white"
            elif currentFeature.getId() in features:
                color = "green"
            else:
                color = "white"
            spectrum = self.model.currentAnalysis.spectraIds[specId]
            x = self.convAtoX(spectrum.rt)
            y = self.convBtoY(spectrum.precursorMass)
            item = self.canvas.create_oval(x-diam, y-diam, x+diam, y+diam, fill=color)
        self.allowZoom = True
        # paint current selected feature borders
        #feature = self.model.currentAnalysis.currentFeature
        #if feature == None:
        #    return
        
    
    def init(self,keepZoom = False):
        print "init 2D View"
        self.initCanvas(keepZoom = keepZoom)

    def identifier(self):
        return "2DView"

        
    
