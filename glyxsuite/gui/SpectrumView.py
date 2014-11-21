import ttk 
from Tkinter import * 

class PeakTMP:
    
    def __init__(self,mass,intensity):
        self.mass = mass
        self.intensity = intensity
        
    def getMZ(self):
        return self.mass
        
    def getIntensity(self):
        return self.intensity
        
        
class ActionZoom:
    
    def __init__(self,master,canvas,x,y):
        self.master = master
        self.canvas = canvas
        self.rectangle = canvas.create_rectangle(x, y, x, y)
        self.x = x
        self.y = y
        
    def onMotion(self,event):
        # change coordinates of rectangle
        self.canvas.coords(self.rectangle,(self.x,self.y,event.x,event.y))
        
    def onButtonRelease(self,event):
        x1,y1,x2,y2 = self.canvas.coords(self.rectangle)
        self.canvas.delete(self.rectangle)
        self.master.zoom(x1,y1,x2,y2)

class SpectrumView(ttk.Frame):
    
    def __init__(self,master,model):
        ttk.Frame.__init__(self,master=master)
        self.master = master
        self.model = model
        self.action = None
        
        # add canvas
        # (left, top, right, bottom)
        # (minMZ,maxInt,maxMZ,minInt)
        self.spectrumMaxMZ = -1
        self.spectrumMaxInt = -1
        
        self.viewXMin = 0
        self.viewXMax = 1000
        self.viewYMin = 0
        self.viewYMax = -1
        self.dimensionScrollregion = (0,0,600,300) # Pixel dimensions of the spectrum
       
        self.slopeX = 1
        self.slopeY = 1
        
        self.height = 300
        self.width = 600
        self.border = 50
        
        xscrollbar = Scrollbar(self, orient=HORIZONTAL)
        xscrollbar.grid(row=1, column=0, sticky=E+W)

        yscrollbar = Scrollbar(self)
        yscrollbar.grid(row=0, column=1, sticky=N+S)
        
        self.spectrum = Canvas(self, width=600, height=300, scrollregion=(0, 0, 600, 300),xscrollcommand=xscrollbar.set,
                yscrollcommand=yscrollbar.set) # check screen resolution
        self.spectrum.grid(row=0, column=0, sticky=N+S+E+W)
        
        b1 = Button(self, text="save",command=self.save)
        b1.grid(row=2, column=0, sticky=N+S)
        
        b2 = Button(self, text="load",command=self.read)
        b2.grid(row=2, column=1, sticky=N+S)
        
        self.coord = StringVar()
        l = Label( self,textvariable=self.coord)
        l.grid(row=3, column=1, sticky=N+S)
                
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        

        
        xscrollbar.config(command=self.spectrum.xview)
        yscrollbar.config(command=self.spectrum.yview)
        
        
        # add events for spectrum canvas
        #self.spectrum.bind("<Button-1>", lambda event: self.hi("button1"))
        #self.spectrum.bind("<FocusIn>", lambda event: self.hi("FucusIn")) # focus fuer das komplette programm
        #self.spectrum.bind("<FocusOut>", lambda event: self.hi("FocusOut")) # geht nicht
        self.spectrum.bind("<Motion>", self.eventMouseMotion)
        #self.model.root.bind("<Control-Shift-KeyPress-H>", lambda event: self.hi("KEY"))
        self.model.root.bind("<Control-Button-1>", self.eventStartZoom)
        self.model.root.bind("<ButtonRelease>", self.eventButtonRelease)
        
        
        # link function
        self.model.funcPaintSpectrum = self.makeSpectrum
     
    def eventMouseMotion(self,event):
        self.coord.set(str(round(self.convert_X_to_MZ(event.x),2))+"/"+str(round(self.convert_Y_to_Int(event.y),0)))
        if self.action == None:
            return
        if not hasattr(self.action,"onMotion"):
            return
        self.action.onMotion(event)
    
    def eventStartZoom(self,event):
        # ToDo: Cancel previous action?
        self.action = ActionZoom(self,self.spectrum,event.x,event.y)
        return
    
    def eventButtonRelease(self,event):
        if self.action == None:
            return
        if not hasattr(self.action,"onButtonRelease"):
            return
        self.action.onButtonRelease(event)
        self.action = None
        return


    def setSpectrumRange(self,spec):
        self.spectrumMaxMZ = -1
        self.spectrumMaxInt = -1
        
        for peak in spec:
            mz = peak.getMZ()
            intens = peak.getIntensity()
            if self.spectrumMaxMZ == -1 or mz > self.spectrumMaxMZ :
                self.spectrumMaxMZ = mz
            if self.spectrumMaxInt == -1  or intens > self.spectrumMaxInt:
                self.spectrumMaxInt = intens
                
            
        
    def calcScales(self):
        
        # check dimensionSpectrumView
        
        if self.viewXMin == -1:
            self.viewXMin = 0
        if self.viewYMin == -1:
            self.viewYMin = 0
            
        if self.viewXMax == -1:
            self.viewXMax = self.spectrumMaxMZ
        if self.viewYMax == -1:
            self.viewYMax = self.spectrumMaxInt
        
        # calc slopes
        print "foo",self.viewXMax,self.viewYMax
        self.slopeMZ = (self.width-2*self.border)/float(self.viewXMax-self.viewXMin)
        self.slopeInt = (self.height-2*self.border)/float(self.viewYMax-self.viewYMin)
        
        
        # calculate dimensionScrollregion
        self.dimensionScrollregion = [0,0]
        self.dimensionScrollregion.append(int(self.slopeMZ*self.spectrumMaxMZ))
        self.dimensionScrollregion.append(int(self.slopeInt*self.spectrumMaxInt))
        print self.dimensionScrollregion
        self.spectrum.config(scrollregion=self.dimensionScrollregion)
        
        
    def convert_MZ_to_X(self,MZ):
        return self.border+self.slopeMZ*MZ

    def convert_Int_to_Y(self,Int):
        return self.height-self.border-self.slopeInt*Int

    def convert_X_to_MZ(self,X):
        if self.model.spec == None:
            return X
        return (X-self.border)/self.slopeMZ

    def convert_Y_to_Int(self,Y):
        if self.model.spec == None:
            return Y
        return (self.height-self.border-Y)/self.slopeInt

        
    def makeSpectrum(self,spec):
        if spec == None:
            return
        self.model.spec = spec
        self.setSpectrumRange(spec)
        self.calcScales()
        self.spectrum.delete(ALL)
        for peak in spec:
            pMZ = self.convert_MZ_to_X(peak.getMZ())
            pInt = self.convert_Int_to_Y(peak.getIntensity())
            pInt0 = self.convert_Int_to_Y(0) # fix, zoom

            item = self.spectrum.create_line(pMZ,pInt0,pMZ,pInt,tags=("scale",))
            

    def zoom(self,x1,y1,x2,y2):
        if self.model.spec == None:
            return
        if x1 < x2:
            self.viewXMin = self.convert_X_to_MZ(x1)
            self.viewXMax = self.convert_X_to_MZ(x2)
        else:
            self.viewXMin = self.convert_X_to_MZ(x2)
            self.viewXMax = self.convert_X_to_MZ(x1)
        if y1 < y2:
            self.viewYMin = self.convert_Y_to_Int(y2)
            self.viewYMax = self.convert_Y_to_Int(y1)
        else:
            self.viewYMin = self.convert_Y_to_Int(y1)
            self.viewYMax = self.convert_Y_to_Int(y2)
        self.makeSpectrum(self.model.spec)
        
        # scroll to new area
        self.spectrum.xview_moveto(self.viewXMin/self.spectrumMaxMZ) 
        self.spectrum.yview_moveto(self.viewYMin/self.spectrumMaxInt) 
        print "zoomed"
        
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
        self.makeSpectrum(spec)
                
