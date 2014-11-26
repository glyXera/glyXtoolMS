import ttk 
from Tkinter import * 
import math

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
        self.zoomHistory = []
        
        # add canvas
        self.spectrumMaxMZ = -1
        self.spectrumMaxInt = -1
        
        self.viewXMin = 0
        self.viewXMax = -1
        self.viewYMin = 0
        self.viewYMax = -1
       
        self.slopeX = 1
        self.slopeY = 1
        
        self.height = 400
        self.width = 800

        self.borderLeft = 100
        self.borderRight = 50
        self.borderTop = 50
        self.borderBottom = 50

        self.spectrum = Canvas(self, width=self.width, height=self.height) # check screen resolution          
        self.spectrum.grid(row=0, column=0, sticky=N+S+E+W)
        
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
        
        
        # add events for spectrum canvas
        #self.spectrum.bind("<Button-1>", lambda event: self.hi("button1"))
        #self.spectrum.bind("<FocusIn>", lambda event: self.hi("FucusIn")) # focus fuer das komplette programm
        #self.spectrum.bind("<FocusOut>", lambda event: self.hi("FocusOut")) # geht nicht
        self.spectrum.bind("<Motion>", self.eventMouseMotion)
        #self.model.root.bind("<Control-Shift-KeyPress-H>", lambda event: self.hi("KEY"))
        self.model.root.bind("<Control-Button-1>", self.eventStartZoom)
        self.model.root.bind("<ButtonRelease>", self.eventButtonRelease)
        self.model.root.bind("<BackSpace>", self.zoomBack)
        
        
        
        # link function
        self.model.funcPaintSpectrum = self.initSpectrum
        
    def scrollX(self,event,args):
        self.xscrollbar.set(event,args)
        #self.spectrum.xview
     
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
            self.viewXMax = self.spectrumMaxMZ*1.1
        if self.viewYMax == -1:
            self.viewYMax = self.spectrumMaxInt*1.1
        
        # calc slopes
        self.slopeMZ = (self.width-self.borderLeft-self.borderRight)/float(self.viewXMax-self.viewXMin)
        self.slopeInt = (self.height-self.borderTop-self.borderBottom)/float(self.viewYMax-self.viewYMin)

    def convert_MZ_to_X(self,MZ):
        return self.borderLeft+self.slopeMZ*(MZ-self.viewXMin)

    def convert_Int_to_Y(self,Int):
        return self.height-self.borderBottom-self.slopeInt*(Int-self.viewYMin)

    def convert_X_to_MZ(self,X):
        if self.model.spec == None:
            return X
        return (X-self.borderLeft)/self.slopeMZ+self.viewXMin

    def convert_Y_to_Int(self,Y):
        if self.model.spec == None:
            return Y
        return (self.height-self.borderBottom-Y)/self.slopeInt+self.viewYMin

    def initSpectrum(self,spec):
        print "init spectrum"
        if spec == None:
            return
        self.model.spec = spec
        self.setSpectrumRange(spec)
        if self.keepZoom.get() == 0:
            self.viewXMin = 0
            self.viewXMax = -1
            self.viewYMin = 0
            self.viewYMax = -1
        self.zoomHistory = []
        self.makeSpectrum()
        
        
    def makeSpectrum(self):
        self.zoomHistory.append((self.viewXMin,self.viewXMax,self.viewYMin,self.viewYMax))
        
        self.calcScales() 
        self.spectrum.delete(ALL)
        for peak in self.model.spec:
            mz = peak.getMZ()
            intens = peak.getIntensity()
            if mz < self.viewXMin or mz > self.viewXMax:
                continue
            if intens < self.viewYMin:
                continue
            if intens > self.viewYMax:
                intens = self.viewYMax
            pMZ = self.convert_MZ_to_X(mz)
            pInt = self.convert_Int_to_Y(intens)
            pInt0 = self.convert_Int_to_Y(self.viewYMin)

            item = self.spectrum.create_line(pMZ,pInt0,pMZ,pInt,tags=("peak",))
        # create axis
        self.spectrum.create_line(self.convert_MZ_to_X(self.viewXMin),
                                    self.convert_Int_to_Y(self.viewYMin),
                                    self.convert_MZ_to_X(self.viewXMax),
                                    self.convert_Int_to_Y(self.viewYMin),
                                    tags=("axis",))
        self.spectrum.create_line(self.convert_MZ_to_X(self.viewXMin),
                                    self.convert_Int_to_Y(self.viewYMin),
                                    self.convert_MZ_to_X(self.viewXMin),
                                    self.convert_Int_to_Y(self.viewYMax),
                                    tags=("axis",))
                                    
        # search scale X
        start,end,diff,exp = findScale(self.viewXMin,self.viewXMax,5.0)

        while start < end:
            if start > self.viewXMin and start < self.viewXMax:
                x = self.convert_MZ_to_X(start)
                y = self.convert_Int_to_Y(self.viewYMin)
                self.spectrum.create_text(
                    (x,y+5),text = shortNr(start,exp),anchor=N)
                self.spectrum.create_line(x,y,x,y+4)
            start += diff

        # search scale Y
        start,end,diff,exp = findScale(self.viewYMin,self.viewYMax,5.0)
        while start < end:
            if start > self.viewYMin and start < self.viewYMax:
                x = self.convert_MZ_to_X(self.viewXMin)
                y = self.convert_Int_to_Y(start)
                self.spectrum.create_text(
                    (x-5,y),text = shortNr(start,exp),anchor=E)
                self.spectrum.create_line(x-4,y,x,y)
            start += diff
            

    def zoom(self,x1,y1,x2,y2):
        if self.model.spec == None:
            return
        xa = self.convert_X_to_MZ(x1)
        xb = self.convert_X_to_MZ(x2)
        if x1 < x2:
            self.viewXMin = xa
            self.viewXMax = xb
        else:
            self.viewXMin = xb
            self.viewXMax = xa
            
        ya = self.convert_Y_to_Int(y1)
        yb = self.convert_Y_to_Int(y2)
        if y1 < y2:
            self.viewYMin = yb
            self.viewYMax = ya
        else:
            self.viewYMin = ya
            self.viewYMax = yb

        # check maximal parameters
        if self.viewXMax > self.spectrumMaxMZ:
            self.viewXMax = self.spectrumMaxMZ*1.1
        if self.viewXMin < 0:
            self.viewXMin = 0
        if self.viewYMax > self.spectrumMaxInt:
            self.viewYMax = self.spectrumMaxInt*1.1
        if self.viewYMin < 0:
            self.viewYMin = 0
        

        
        self.makeSpectrum()

    def zoomBack(self,event):
        if len(self.zoomHistory) == 0:
            print "no history"
            return
        a,b,c,d = self.zoomHistory.pop(-1)
        if (a,b,c,d) == (self.viewXMin,self.viewXMax,self.viewYMin,self.viewYMax):
            self.zoomBack(event)
            return
        self.viewXMin,self.viewXMax,self.viewYMin,self.viewYMax = a,b,c,d
        self.makeSpectrum()
        
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

def shortNr(nr,exp):
    # shorten nr if precision is necessary
    if exp <= 0:
        return round (nr,int(-exp+1))
    if exp > 4:
        e = int(math.floor(math.log(nr)/math.log(10)))
        b = round(nr/float(10**e),4)
        return str(b)+"E"+str(e)
    return int(nr)
                
def findScale(start,end,NrScales):
    diff = abs(end-start)/NrScales
    exp = math.floor(math.log(diff)/math.log(10))
    base = 10**exp
    nr = diff/base
    if nr < 0 or nr >= 10:
        raise Exception("error in scaling")
    # choose nearest scale of [1,2,2.5,5]
    scales = [1,2,2.5,5]
    sortNr = [(abs(s-nr),s) for s in scales]
    sortNr.sort()
    diff = sortNr[0][1]*base
    
    startAxis = math.floor(start/diff)*diff
    endAxis = math.ceil(end/diff)*diff
    return startAxis,endAxis,diff,exp
