from glyxtoolms.gui import FramePlot
import glyxtoolms

class AnnotatedPlot(FramePlot.FramePlot):

    def __init__(self, master, model, height=300, width=800, xTitle="", yTitle=""):
        FramePlot.FramePlot.__init__(self, master, model, height=height,
                                     width=width, xTitle=xTitle,
                                     yTitle=yTitle)

        self.master = master
        self.annotations = None # Link to current Annotations

        self.peaksByItem = {}
        self.annotations = []
        self.annotationItems = {}
        self.currentAnnotation = None

        self.canvas.bind("<Button-2>", self.button2, "+")
        
        self.canvas.bind("<Button-1>", self.button1Pressed, "+")
        self.canvas.bind("<ButtonRelease-1>", self.button1Released, "+")
        self.canvas.bind("<B1-Motion>", self.button3Motion, "+")

        self.canvas.bind("<Button-3>", self.button3Pressed, "+")
        self.canvas.bind("<ButtonRelease-3>", self.button3Released, "+")
        self.canvas.bind("<B3-Motion>", self.button3Motion, "+")
        
        self.canvas.bind("<Delete>", self.deleteAnnotation, "+") 

    def findPeakAt(self, pixelX):
        overlap = set(self.canvas.find_overlapping(pixelX-10,
                                                   0,
                                                   pixelX+10,
                                                   self.height))
        peaks = []
        for item in overlap:
            if item in self.peaksByItem:
                peaks.append((abs(self.canvas.coords(item)[0] - pixelX), self.peaksByItem[item]))
        if len(peaks) == 0:
            peak = None
        else:
            peak = min(peaks)[1]
        return peak

    def button1Pressed(self, event):
        # search nearest annotation
        overlap = set(self.canvas.find_overlapping(event.x-10,
                                                   event.y-10,
                                                   event.x+10,
                                                   event.y+10))
        annotations = []
        for item in overlap:
            if item in self.annotationItems:
                annotations.append((abs(self.canvas.coords(item)[0] - event.x), item))
        if len(annotations) == 0:
            self.currentAnnotation = None
            self.paintAllAnnotations()
            return
        
        item = min(annotations)[1]
        annotation = self.annotationItems[item]
        annotation.selected = annotation.items[item]
        self.currentAnnotation = annotation
        self.paintAllAnnotations()

    def button1Released(self, event):
        if self.currentAnnotation is None:
            return
        if not self.currentAnnotation.selected == "text":
            self.currentAnnotation.y = event.y
        peak = self.findPeakAt(event.x)

        if peak is not None:
            if self.currentAnnotation.selected == "x1":
                self.currentAnnotation.x1 = peak.x
            elif self.currentAnnotation.selected == "x2":
                self.currentAnnotation.x2 = peak.x
            self.currentAnnotation.text = str(round(abs(self.currentAnnotation.x1-self.currentAnnotation.x2),4))
        self.paintAllAnnotations()

    def button3Pressed(self, event):
        peak = self.findPeakAt(event.x)
        y = self.convYtoB(event.y)
        
        if peak is not None:
            self.currentAnnotation = glyxtoolms.io.Annotation()
            self.currentAnnotation.x1 = peak.x
            self.currentAnnotation.x2 = peak.x
            self.currentAnnotation.selected = "x2"
            self.currentAnnotation.y = y
        else:
            self.currentAnnotation = None
        self.paintCurrentAnnotation()

    
    def button3Motion(self, event):
        if self.currentAnnotation is None:
            return
        peak = self.findPeakAt(event.x)
            
        if peak is  None:
            return
        x = peak.x

        if self.currentAnnotation.selected == "x1":
            self.currentAnnotation.x1 = x
        elif self.currentAnnotation.selected == "x2":
            self.currentAnnotation.x2 = x

        self.currentAnnotation.y = event.y
        self.currentAnnotation.text = str(round(abs(self.currentAnnotation.x1-self.currentAnnotation.x2),4))
        self.paintCurrentAnnotation()
    
    def button3Released(self, event):
        if self.currentAnnotation is None:
            return
        self.currentAnnotation.y = event.y
        peak = self.findPeakAt(event.x)
        if peak is not None:
            if self.currentAnnotation.selected == "x1":
                self.currentAnnotation.x1 = peak.x
            elif self.currentAnnotation.selected == "x2":
                self.currentAnnotation.x2 = peak.x
            self.currentAnnotation.text = str(round(abs(self.currentAnnotation.x1-self.currentAnnotation.x2),4))
            self.annotations.append(self.currentAnnotation)
        self.currentAnnotation = None
        self.paintAllAnnotations()

    def deleteAnnotation(self, event):
        if self.currentAnnotation is None:
            return
        self.annotations.remove(self.currentAnnotation)
        self.currentAnnotation = None
        self.paintAllAnnotations()
        
    def paintCurrentAnnotation(self):
        self.canvas.delete("currentAnnotation")
        # draw annotation lines
        if self.currentAnnotation is None:
            return
        self.paintAnnotation(self.currentAnnotation)
        self.canvas.tag_lower("currentAnnotation")
        
    def paintAllAnnotations(self):
        self.canvas.delete("annotation")
        self.annotationItems = {}
        for annotation in self.annotations:
            self.paintAnnotation(annotation)
        self.canvas.tag_lower("annotation")
        
    def paintAnnotation(self, annotation):
        
        pIntMin = self.convBtoY(self.viewYMin)
        pIntMax = self.convBtoY(self.viewYMax)
        if annotation.x1 == 0:
            return
            
        if annotation.x2 == 0:
            return
            
        if annotation.y == 0:
            return

        px1 = self.convAtoX(annotation.x1)
        px2 = self.convAtoX(annotation.x2)
        pXText = self.convAtoX((annotation.x1+annotation.x2)/2.0)
        py = annotation.y
        
        if annotation == self.currentAnnotation:
            tags = ("currentAnnotation", "annotation")
            color = "orange"
        else:
            tags = ("annotation", )
            color = "green"
        
        item1 = self.canvas.create_line(px1, pIntMin, px1, pIntMax, tags=tags, fill=color)
        item2 = self.canvas.create_line(px2, pIntMin, px2, pIntMax, tags=tags, fill=color)
        item3 = self.canvas.create_line(px1, py, px2, py, tags=tags, fill=color)
        item4 = self.canvas.create_text((pXText, py, ),
                               text=annotation.text,
                               fill=color,
                               anchor="s", justify="center",
                               tags=tags)
        annotation.items = {}
        annotation.items[item1] = "x1"
        annotation.items[item2] = "x2"
        annotation.items[item3] = "line"
        annotation.items[item4] = "text"
        
        self.annotationItems[item1] = annotation
        self.annotationItems[item2] = annotation
        self.annotationItems[item3] = annotation
        self.annotationItems[item4] = annotation

