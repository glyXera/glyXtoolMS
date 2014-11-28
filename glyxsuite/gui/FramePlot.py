import ttk 
from Tkinter import * 
import math
       
        
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

class FramePlot(ttk.Frame):
    
    def __init__(self,master,model):
        ttk.Frame.__init__(self,master=master)
        self.model = model
        self.master = master
        self.action = None
        self.zoomHistory = []
        self.allowZoom = False
        
        # add canvas
        self.aMax = -1
        self.bMax = -1
        self.aMax = -1
        self.bMax = -1
        
        self.viewXMin = 0
        self.viewXMax = -1
        self.viewYMin = 0
        self.viewYMax = -1
       
        self.slopeA = 1
        self.slopeB = 1
        
        self.height = 300
        self.width = 800

        self.borderLeft = 100
        self.borderRight = 50
        self.borderTop = 50
        self.borderBottom = 50

        self.canvas = Canvas(self, width=self.width, height=self.height) # check screen resolution          
        self.canvas.grid(row=0, column=0, sticky=N+S+E+W)
        
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        
        self.canvas.bind("<Motion>", self.eventMouseMotion)
        self.canvas.bind("<Control-Button-1>", self.eventStartZoom)
        self.canvas.bind("<ButtonRelease>", self.eventButtonRelease)
        self.canvas.bind("<BackSpace>", self.zoomBack)
        self.canvas.bind("<Left>", self.keyLeft)
        self.canvas.bind("<Right>", self.keyRight)

    def keyLeft(self,event):
        if self.allowZoom == False:
            return
        add = abs(self.viewXMax-self.viewXMin)*0.1
        if self.viewXMin-add <= 0:
            add = self.viewXMin
        self.viewXMin = self.viewXMin-add
        self.viewXMax = self.viewXMax-add
        self._paintCanvas()
        
    def keyRight(self,event):
        if self.allowZoom == False:
            return
        add = abs(self.viewXMax-self.viewXMin)*0.1
        if self.viewXMax+add >= self.aMax:
            add = self.aMax-self.viewXMax
        self.viewXMin = self.viewXMin+add
        self.viewXMax = self.viewXMax+add
        self._paintCanvas()

    def identifier(self):
        return "Frameplot"
            
    def setMaxValues(self):
        raise Exception("Replace function!")
        
    def paintObject(self):
        raise Exception("Replace function!")
        
    def eventMouseMotion(self,event):
        self.canvas.focus_set()
        self.coord.set(self.identifier()+"/"+str(round(self.convXtoA(event.x),2))+"/"+str(round(self.convYtoB(event.y),0)))
        if self.action == None:
            return
        if not hasattr(self.action,"onMotion"):
            return
        self.action.onMotion(event)
    
    def eventStartZoom(self,event):
        print "start zoom", self.identifier()
        # ToDo: Cancel previous action?
        self.action = ActionZoom(self,self.canvas,event.x,event.y)
        return
    

    def eventButtonRelease(self,event):
        if self.action == None:
            return
        if not hasattr(self.action,"onButtonRelease"):
            return
        self.action.onButtonRelease(event)
        self.action = None
        return

    def calcScales(self):
        if self.viewXMin == -1:
            self.viewXMin = 0
        if self.viewYMin == -1:
            self.viewYMin = 0
            
        if self.viewXMax == -1:
            self.viewXMax = self.aMax
        if self.viewYMax == -1:
            self.viewYMax = self.bMax
        
        # calc slopes
        self.slopeA = (self.width-self.borderLeft-self.borderRight)/float(self.viewXMax-self.viewXMin)
        self.slopeB = (self.height-self.borderTop-self.borderBottom)/float(self.viewYMax-self.viewYMin)

    def convAtoX(self,A):
        return self.borderLeft+self.slopeA*(A-self.viewXMin)

    def convBtoY(self,B):
        return self.height-self.borderBottom-self.slopeB*(B-self.viewYMin)

    def convXtoA(self,X):
        if self.allowZoom == False:
            return X
        return (X-self.borderLeft)/self.slopeA+self.viewXMin

    def convYtoB(self,Y):
        if self.allowZoom == False:
            return Y
        return (self.height-self.borderBottom-Y)/self.slopeB+self.viewYMin

    def initCanvas(self):
        self.setMaxValues()
        if self.keepZoom.get() == 0:
            self.viewXMin = 0
            self.viewXMax = -1
            self.viewYMin = 0
            self.viewYMax = -1
        self.zoomHistory = []
        self._paintCanvas()

    def _paintCanvas(self):
        self.zoomHistory.append((self.viewXMin,self.viewXMax,self.viewYMin,self.viewYMax))
        
        self.calcScales() 
        self.canvas.delete(ALL)
        
        self.paintObject()
                            
        # overpaint possible overflows                    
        self.canvas.create_rectangle(0,0,
                                self.borderLeft,self.height,
                                fill= self.canvas["background"],width=0)
        self.canvas.create_rectangle(self.width-self.borderRight,
                                0,self.width,self.height,
                                fill= self.canvas["background"],width=0)
        self.canvas.create_rectangle(0,0,
                                self.width,self.borderTop,
                                fill= self.canvas["background"],width=0)
        self.canvas.create_rectangle(0,self.height-self.borderBottom,
                                self.width,self.height+1,
                                fill= self.canvas["background"],width=0)
                                    
        # create axis
        self.canvas.create_line(self.convAtoX(self.viewXMin),
                                    self.convBtoY(self.viewYMin),
                                    self.convAtoX(self.viewXMax)+10,
                                    self.convBtoY(self.viewYMin),
                                    tags=("axis",),arrow="last")
        self.canvas.create_line(self.convAtoX(self.viewXMin),
                                    self.convBtoY(self.viewYMin),
                                    self.convAtoX(self.viewXMin),
                                    self.convBtoY(self.viewYMax)-10,
                                    tags=("axis",),arrow="last")                            
                                    
        # search scale X
        start,end,diff,exp = findScale(self.viewXMin,self.viewXMax,5.0)
        while start < end:
            if start > self.viewXMin and start < self.viewXMax:
                x = self.convAtoX(start)
                y = self.convBtoY(self.viewYMin)
                self.canvas.create_text(
                    (x,y+5),text = shortNr(start,exp),anchor=N)
                self.canvas.create_line(x,y,x,y+4)
            start += diff

        # search scale Y
        start,end,diff,exp = findScale(self.viewYMin,self.viewYMax,5.0)
        while start < end:
            if start > self.viewYMin and start < self.viewYMax:
                x = self.convAtoX(self.viewXMin)
                y = self.convBtoY(start)
                self.canvas.create_text(
                    (x-5,y),text = shortNr(start,exp),anchor=E)
                self.canvas.create_line(x-4,y,x,y)
            start += diff
            

    def zoom(self,x1,y1,x2,y2):
        if self.allowZoom == False:
            return
        if x1 == x2 or y1 == y2:
            return
        xa = self.convXtoA(x1)
        xb = self.convXtoA(x2)
        if x1 < x2:
            self.viewXMin = xa
            self.viewXMax = xb
        else:
            self.viewXMin = xb
            self.viewXMax = xa
            
        ya = self.convYtoB(y1)
        yb = self.convYtoB(y2)
        if y1 < y2:
            self.viewYMin = yb
            self.viewYMax = ya
        else:
            self.viewYMin = ya
            self.viewYMax = yb

        # check maximal parameters
        if self.viewXMax > self.aMax:
            self.viewXMax = self.aMax
        if self.viewXMin < 0:
            self.viewXMin = 0
        if self.viewYMax > self.bMax:
            self.viewYMax = self.bMax
        if self.viewYMin < 0:
            self.viewYMin = 0

        self._paintCanvas()

    def zoomBack(self,event):
        if len(self.zoomHistory) == 0:
            print "no history"
            return
        a,b,c,d = self.zoomHistory.pop(-1)
        if (a,b,c,d) == (self.viewXMin,self.viewXMax,self.viewYMin,self.viewYMax):
            self.zoomBack(event)
            return
        self.viewXMin,self.viewXMax,self.viewYMin,self.viewYMax = a,b,c,d
        self._paintCanvas()

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
