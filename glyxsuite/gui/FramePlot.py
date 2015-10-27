import ttk
import Tkinter
import math


class ActionZoom(object):

    def __init__(self, master, canvas, x, y):
        self.master = master
        self.canvas = canvas
        self.rectangle = canvas.create_rectangle(x, y, x, y)
        self.x = x
        self.y = y

    def onMotion(self, event):
        # change coordinates of rectangle
        self.canvas.coords(self.rectangle, (self.x, self.y, event.x, event.y))

    def onButtonRelease(self, event):
        x1, y1, x2, y2 = self.canvas.coords(self.rectangle)
        self.canvas.delete(self.rectangle)
        self.master.zoom(x1, y1, x2, y2)

class FramePlot(ttk.Frame):

    def __init__(self, master, model, height=300, width=800, xTitle="", yTitle=""):
        ttk.Frame.__init__(self, master=master)
        self.model = model
        self.master = master
        self.action = None
        self.zoomHistory = []
        self.allowZoom = False

        self.xTitle = xTitle
        self.yTitle = yTitle

        self.NrXScales = 5.0
        self.NrYScales = 5.0

        # add canvas
        self.aMax = -1
        self.bMax = -1
        self.aMin = 0
        self.bMin = 0

        self.viewXMin = 0
        self.viewXMax = 1
        self.viewYMin = 0
        self.viewYMax = 1

        self.slopeA = 1
        self.slopeB = 1

        self.height = height
        self.width = width

        self.borderLeft = 100
        self.borderRight = 50
        self.borderTop = 50
        self.borderBottom = 50

        self.canvas = Tkinter.Canvas(self, width=self.width, height=self.height) # check screen resolution
        self.canvas.config(bg="white")
        self.canvas.grid(row=0, column=0, sticky="NSEW")

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)


        self.canvas.bind("<Button-1>", self.eventTakeFokus)
        self.canvas.bind("<Motion>", self.eventMouseMotion)
        self.canvas.bind("<Control-Button-1>", self.eventStartZoom)
        self.canvas.bind("<ButtonRelease>", self.eventButtonRelease)
        self.canvas.bind("<BackSpace>", self.zoomBack)
        self.canvas.bind("<Control-Left>", self.keyLeft)
        self.canvas.bind("<Control-Right>", self.keyRight)
        self.canvas.bind("<Control-BackSpace>", self.resetZoom)

        self.calcScales()
        self._paintAxis()

    def keyLeft(self, event):
        if self.allowZoom == False:
            return
        add = abs(self.viewXMax-self.viewXMin)*0.1
        if self.viewXMin-add <= 0:
            add = self.viewXMin
        self.viewXMin = self.viewXMin-add
        self.viewXMax = self.viewXMax-add
        self._paintCanvas(addToHistory=False)

    def keyRight(self, event):
        if self.allowZoom == False:
            return
        add = abs(self.viewXMax-self.viewXMin)*0.1
        if self.viewXMax+add >= self.aMax:
            add = self.aMax-self.viewXMax
        self.viewXMin = self.viewXMin+add
        self.viewXMax = self.viewXMax+add
        self._paintCanvas(addToHistory=False)

    def identifier(self):
        return "Frameplot"

    def setMaxValues(self):
        raise Exception("Replace function!")

    def paintObject(self):
        raise Exception("Replace function!")

    def eventTakeFokus(self, event):
        self.canvas.focus_set()

    def eventMouseMotion(self, event):
        self.coord.set(self.identifier()+"/"+str(round(self.convXtoA(event.x), 2))+"/"+str(round(self.convYtoB(event.y), 0)))
        if self.action == None:
            return
        if not hasattr(self.action, "onMotion"):
            return
        self.action.onMotion(event)


    def eventStartZoom(self, event):
        self.canvas.focus_set()
        # ToDo: Cancel previous action?
        self.action = ActionZoom(self, self.canvas, event.x, event.y)
        return


    def eventButtonRelease(self, event):
        if self.action == None:
            return
        if not hasattr(self.action, "onButtonRelease"):
            return
        self.action.onButtonRelease(event)
        self.action = None
        return

    def calcScales(self):
        if self.viewXMin == -1:
            self.viewXMin = self.aMin
        if self.viewYMin == -1:
            self.viewYMin = self.bMin

        if self.viewXMax == -1:
            self.viewXMax = self.aMax
        if self.viewYMax == -1:
            self.viewYMax = self.bMax

        # calc slopes
        baseX = float(self.viewXMax-self.viewXMin)
        if baseX == 0.0:
            baseY = 1.0
            self.viewXMax = self.viewXMin+1
        baseY = float(self.viewYMax-self.viewYMin)
        if baseY == 0.0:
            baseY = 1.0
            self.viewYMax = self.viewYMin+1
        self.slopeA = (self.width-self.borderLeft-self.borderRight)/baseX
        self.slopeB = (self.height-self.borderTop-self.borderBottom)/baseY

    def convAtoX(self, A):
        return self.borderLeft+self.slopeA*(A-self.viewXMin)

    def convBtoY(self, B):
        return self.height-self.borderBottom-self.slopeB*(B-self.viewYMin)

    def convXtoA(self, X):
        if self.allowZoom == False:
            return X
        return (X-self.borderLeft)/self.slopeA+self.viewXMin

    def convYtoB(self, Y):
        if self.allowZoom == False:
            return Y
        return (self.height-self.borderBottom-Y)/self.slopeB+self.viewYMin

    def initCanvas(self, keepZoom=False):
        self.setMaxValues()
        if self.keepZoom.get() == 0 and keepZoom == False:
            self.viewXMin = -1
            self.viewXMax = -1
            self.viewYMin = -1
            self.viewYMax = -1
            self.zoomHistory = []
        self._paintCanvas()

    def _paintCanvas(self, addToHistory=True):
        if addToHistory == True:
            self.zoomHistory.append((self.viewXMin, self.viewXMax, self.viewYMin, self.viewYMax))

        self.calcScales()
        self.canvas.delete(Tkinter.ALL)

        self.paintObject()
        self._paintAxis()

    def _paintAxis(self):

        # overpaint possible overflows
        self.canvas.create_rectangle(0, 0,
                                     self.borderLeft, self.height,
                                     fill=self.canvas["background"], width=0)
        self.canvas.create_rectangle(self.width-self.borderRight,
                                     0, self.width, self.height,
                                     fill=self.canvas["background"], width=0)
        self.canvas.create_rectangle(0, 0,
                                     self.width, self.borderTop,
                                     fill=self.canvas["background"], width=0)
        self.canvas.create_rectangle(0, self.height-self.borderBottom,
                                     self.width, self.height+1,
                                     fill=self.canvas["background"], width=0)

        # create axis
        self.canvas.create_line(self.convAtoX(self.viewXMin),
                                self.convBtoY(self.viewYMin),
                                self.convAtoX(self.viewXMax)+10,
                                self.convBtoY(self.viewYMin),
                                tags=("axis", ), arrow="last")
        self.canvas.create_line(self.convAtoX(self.viewXMin),
                                self.convBtoY(self.viewYMin),
                                self.convAtoX(self.viewXMin),
                                self.convBtoY(self.viewYMax)-10,
                                tags=("axis", ), arrow="last")

        # search scale X
        start, end, diff, exp = findScale(self.viewXMin, self.viewXMax,
                                          self.NrXScales)
        while start < end:
            if start > self.viewXMin and start < self.viewXMax:
                x = self.convAtoX(start)
                y = self.convBtoY(self.viewYMin)
                self.canvas.create_text((x, y+5),
                                        text = shortNr(start, exp),
                                        anchor="n")
                self.canvas.create_line(x, y, x, y+4)
            start += diff

        # search scale Y
        start, end, diff, exp = findScale(self.viewYMin, self.viewYMax,
                                          self.NrYScales)
        while start < end:
            if start > self.viewYMin and start < self.viewYMax:
                x = self.convAtoX(self.viewXMin)
                y = self.convBtoY(start)
                self.canvas.create_text((x-5, y),
                                        text=shortNr(start, exp),
                                        anchor="e")
                self.canvas.create_line(x-4, y, x, y)
            start += diff

        # write axis description
        item = self.canvas.create_text(self.convAtoX((self.viewXMin+self.viewXMax)/2.0),
                                       self.height-self.borderBottom/3.0,
                                       text=self.xTitle)

        item = self.canvas.create_text(self.borderLeft,
                                       self.borderTop/2.0,
                                       text = self.yTitle)


    def resetZoom(self, event):
        if self.allowZoom == False:
            return
        self.viewXMin = -1
        self.viewXMax = -1
        self.viewYMin = -1
        self.viewYMax = -1
        self._paintCanvas()

    def zoom(self, x1, y1, x2, y2):
        if self.allowZoom == False:
            return
        if x1 == x2 or y1 == y2:
            return
        xa = self.convXtoA(x1)
        xb = self.convXtoA(x2)
        # check if zoom is outside of canvas
        def testBorder(x, xmin, xmax):
            if x < xmin:
                x = xmin
            if x > xmax:
                x = xmax
            return x
        xa = testBorder(xa, self.viewXMin, self.viewXMax)
        xb = testBorder(xb, self.viewXMin, self.viewXMax)
        if xa == xb:
            return

        if xa < xb:
            self.viewXMin = xa
            self.viewXMax = xb
        else:
            self.viewXMin = xb
            self.viewXMax = xa

        ya = self.convYtoB(y1)
        yb = self.convYtoB(y2)

        ya = testBorder(ya, self.viewYMin, self.viewYMax)
        yb = testBorder(yb, self.viewYMin, self.viewYMax)
        if ya == yb:
            return

        if ya < yb:
            self.viewYMin = ya
            self.viewYMax = yb
        else:
            self.viewYMin = yb
            self.viewYMax = ya

        # check maximal parameters
        if self.viewXMax > self.aMax:
            self.viewXMax = self.aMax
        if self.viewXMin < self.aMin:
            self.viewXMin = self.aMin
        if self.viewYMax > self.bMax:
            self.viewYMax = self.bMax
        if self.viewYMin < self.bMin:
            self.viewYMin = self.bMin

        self._paintCanvas()

    def zoomBack(self, event):
        if len(self.zoomHistory) == 0:
            print "no history"
            return
        a, b, c, d = self.zoomHistory.pop(-1)
        if (a, b, c, d) == (self.viewXMin, self.viewXMax, self.viewYMin, self.viewYMax):
            self.zoomBack(event)
            return
        self.viewXMin, self.viewXMax, self.viewYMin, self.viewYMax = a, b, c, d
        self._paintCanvas()

def shortNr(nr, exp):
    # shorten nr if precision is necessary
    if exp <= 0:
        return round (nr, int(-exp+1))
    if exp > 4:
        e = int(math.floor(math.log(nr)/math.log(10)))
        b = round(nr/float(10**e), 4)
        return str(b)+"E"+str(e)
    return int(nr)

def findScale(start, end, NrScales):
    diff = abs(end-start)/NrScales
    exp = math.floor(math.log(diff)/math.log(10))
    base = 10**exp
    nr = diff/base
    if nr < 0 or nr >= 10:
        raise Exception("error in scaling")
    # choose nearest scale of [1, 2, 2.5, 5]
    scales = [1, 2, 2.5, 5]
    sortNr = [(abs(s-nr), s) for s in scales]
    sortNr.sort()
    diff = sortNr[0][1]*base

    startAxis = math.floor(start/diff)*diff
    endAxis = math.ceil(end/diff)*diff
    return startAxis, endAxis, diff, exp
