from glyxtoolms.gui import FramePlot
import glyxtoolms

class Annotatable(object):
    
    def __init__(self,x=0,y=0):
        """  Annotatable object, has to provide a x and y coordinate """
        self.x = x
        self.y = y

class AnnotatedPlot(FramePlot.FramePlot):

    def __init__(self, master, model, height=300, width=800, xTitle="", yTitle=""):
        FramePlot.FramePlot.__init__(self, master, model, height=height,
                                     width=width, xTitle=xTitle,
                                     yTitle=yTitle)

        self.master = master
        self.peaksByItem = {}
        self.annotations = {}
        self.series = {}
        self.annotationItems = {}
        self.currentAnnotation = None

        #self.canvas.bind("<Button-2>", self.button2, "+")
        
        self.canvas.bind("<Button-1>", self.button1Pressed, "+")
        self.canvas.bind("<ButtonRelease-1>", self.button1Released, "+")
        #self.canvas.bind("<B1-Motion>", self.button3Motion, "+")
        self.canvas.bind("<Motion>", self.mouseMoveEvent, "+")

        self.canvas.bind("<Button-3>", self.button3Pressed, "+")
        self.canvas.bind("<ButtonRelease-3>", self.button3Released, "+")
        self.canvas.bind("<B3-Motion>", self.button3Motion, "+")
        
        self.canvas.bind("<Delete>", self.deleteAnnotation, "+")
        
        
        
        # add ruler toggle
        self.rulerbutton = self.toolbar.addButton("ruler","toggle")
        
    def _paintCanvas(self, addToHistory=True):
        """ Method override to inject annotation painting """
        super(AnnotatedPlot, self)._paintCanvas(addToHistory)
        self.paintAllAnnotations()

    def clearAnnotatableList(self):
        self.peaksByItem = {}

    def addAnnotatableItem(self, item, annotatableObject):
        self.peaksByItem[item] = annotatableObject
        
    def addSeries(self, series, color):
        self.series[series] = {"locked":True, "hidden":False, "color":color}
        self.annotations[series] = []

    def addAnnotation(self, annotation, series):
        annotation.series = series
        if not series in self.annotations:
            return
        if len(self.annotations[series]) == 0:
            annotation.nr = 0
        else:
            maxnr = max([a.nr for a in self.annotations[series]])
            annotation.nr = maxnr+1
        #self.annotations[series] = self.annotations.get(series,[]) + [annotation]
        self.annotations[series].append(annotation)

    def findItemAt(self, pixelX=None, pixelY=None):
        if pixelX == None and pixelY == None:
            return
        if pixelX == None:
            xmin = 0
            xmax = self.height
        else:
            xmin = pixelX - 10
            xmax = pixelX + 10
        if pixelY == None:
            ymin = 0
            ymax = self.height
        else:
            ymin = pixelY - 10
            ymax = pixelY + 10
        overlap = set(self.canvas.find_overlapping(xmin, ymin,
                                                   xmax, ymax))
        peaks = []
        annotations = []
        for item in overlap:
            minlist = []
            if pixelX != None:
                minlist.append(abs(self.canvas.coords(item)[0] - pixelX))
            if pixelY != None:
                minlist.append(abs(self.canvas.coords(item)[1] - pixelY))
            mini = min(minlist)
                
            if item in self.peaksByItem:
                peaks.append((mini, item))
            if item in self.annotationItems:
                annotations.append((mini, item))
        if len(peaks) == 0:
            peak = None
        else:
            peak = min(peaks)[1]
        if len(annotations) == 0:
            annotation = None
        else:
            annotation = min(annotations)[1]
        return {"annotatable":peak, "annotation":annotation}

    def findObjectAt(self, pixelX=None, pixelY=None):
        items = self.findItemAt(pixelX, pixelY)
        annotatableItem = items["annotatable"]
        annotationItem = items["annotation"]
        if annotatableItem == None:
            peak = None
        else:
            peak = self.peaksByItem[annotatableItem]
        if annotationItem == None:
            annotation = None
        else:
            annotation = self.annotationItems[annotationItem]
        return {"annotatable":peak, "annotation":annotation}

#    def findPeakAt(self, pixelX):
#        overlap = set(self.canvas.find_overlapping(pixelX-10,
#                                                   0,
#                                                   pixelX+10,
#                                                   self.height))
#        peaks = []
#        for item in overlap:
#            if item in self.peaksByItem:
#                peaks.append((abs(self.canvas.coords(item)[0] - pixelX), self.peaksByItem[item]))
#        if len(peaks) == 0:
#            peak = None
#        else:
#            peak = min(peaks)[1]
#        return peak
    
#    def findAnnotationAt(self.pixelX, pixelY):
#        overlap = set(self.canvas.find_overlapping(pixelX-10,
#                                           0,
#                                           pixelX+10,
#                                           self.height))
#        for item in overlap:
#            if item in self.annotationItems:
                
    def mouseMoveEvent(self, event):
        if self.rulerbutton.active == False:
            return
        nearest = self.findItemAt(pixelX=event.x, pixelY=event.y)
        annotationItem = nearest["annotation"]
        annotatableItem = nearest["annotatable"]
        if annotationItem != None:
            annotation = self.annotationItems[annotationItem]
            if annotation.items[annotationItem] == "line":
                self.canvas.config(cursor="pencil")
            else:
                self.canvas.config(cursor="plus")
            #if self.canvas.coords(annotationItem)[0] - event.x < 0:
            #    self.canvas.config(cursor="left_side")
            #else:
            #    self.canvas.config(cursor="right_side")
        elif annotatableItem != None:
            self.canvas.config(cursor="bottom_side")
        else:
            self.canvas.config(cursor="")
        

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
        peak = self.findObjectAt(pixelX=event.x)["annotatable"]

        if peak is not None:
            if self.currentAnnotation.selected == "x1":
                self.currentAnnotation.x1 = peak.x
            elif self.currentAnnotation.selected == "x2":
                self.currentAnnotation.x2 = peak.x
            self.currentAnnotation.text = str(round(abs(self.currentAnnotation.x1-self.currentAnnotation.x2),4))
        self.paintAllAnnotations()

    def button3Pressed(self, event):
        if self.rulerbutton.active == False:
            return
        peak = self.findObjectAt(pixelX=event.x)["annotatable"]
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
        if self.rulerbutton.active == False:
            return
        if self.currentAnnotation is None:
            return
        peak = self.findObjectAt(pixelX=event.x)["annotatable"]

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
        if self.rulerbutton.active == False:
            return
        if self.currentAnnotation is None:
            return
        self.currentAnnotation.y = event.y
        peak = self.findObjectAt(pixelX=event.x)["annotatable"]
        if peak is not None:
            if self.currentAnnotation.selected == "x1":
                self.currentAnnotation.x1 = peak.x
            elif self.currentAnnotation.selected == "x2":
                self.currentAnnotation.x2 = peak.x
            self.currentAnnotation.text = str(round(abs(self.currentAnnotation.x1-self.currentAnnotation.x2),4))
            self.addAnnotation(self.currentAnnotation, "test")
            #series = self.currentAnnotation.series
            #self.annotations[series] = self.annotations.get(series,[]) + [self.currentAnnotation]
        self.currentAnnotation = None
        self.paintAllAnnotations()

    def deleteAnnotation(self, event):
        if self.currentAnnotation is None:
            return
        series = self.currentAnnotation.series
        if not series in self.annotations:
            return
        if not self.currentAnnotation in self.annotations[series]:
            return
        self.annotations[series].remove(self.currentAnnotation)
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
        dimensions = {}
        # caculate dimensions of each series
        for series in self.annotations:
            dimensions[series] = {}
            
            #for annotation in sorted(self.annotations[series], key=lambda a: abs(a.x2-a.x1), reverse=True):
            for annotation in sorted(self.annotations[series], key=lambda a: (a.x1,-abs(a.x2-a.x1))):
                #x1 = int(self.convAtoX(annotation.x1))
                #x2 = int(self.convAtoX(annotation.x2))
                x1 = annotation.x1
                x2 = annotation.x2
                level = 0
                while True:
                    if level not in dimensions[series]:
                         dimensions[series][level] = (x1,x2)
                         annotation.level = level
                         break
                    else:
                        l1,l2 = dimensions[series][level]
                        if not (x1 < l2 and l1 < x2): # ranges dont overlap
                            ranges = (x1,x2,l1,l2)
                            dimensions[series][level] = (min(ranges),max(ranges))
                            annotation.level = level
                            break
                    level += 1
        # group series
        noOverlap = {}
        offsets = {}
        for series in dimensions:
            y1 = min(dimensions[series].keys())
            y2 = max(dimensions[series].keys())
            x1= min([min(dimensions[series][level]) for level in dimensions[series]])
            x2= max([max(dimensions[series][level]) for level in dimensions[series]])
            offset = 0
            while True:
                if len(noOverlap) == 0:
                    break
                overlaps = False
                for s in noOverlap:
                    a1,a2,b1,b2 = noOverlap[s]
                    # check overlap
                    if (x1 < a2 and a1 < x2) and (y1+offset <= b2 and b1 <= y2+offset):
                        overlaps = True
                        break
                if overlaps == False:
                    break
                offset += 1
            offsets[series] = offset
            noOverlap[series] = (x1,x2,y1+offset,y2+offset)
        
        # recalculate annotation level based on offset
        for series in sorted(offsets, key=lambda s: offsets[s]):
            for annotation in self.annotations[series]:
                annotation.level += offsets[series]
                self.paintAnnotation(annotation)
        self.canvas.tag_lower("annotation")
        
    def paintAnnotation(self, annotation):
        pIntMin = self.convBtoY(self.viewYMin)
        pIntMax = self.convBtoY(self.viewYMax)
        #if annotation.x1 == 0:
        #    return
        #    
        #if annotation.x2 == 0:
        #    return
        #    
        #if annotation.y == 0:
        #    return
        
        px1 = self.convAtoX(annotation.x1)
        px2 = self.convAtoX(annotation.x2)
        pXText = self.convAtoX((annotation.x1+annotation.x2)/2.0)
        py = annotation.level*20 + self.convBtoY(self.viewYMax)+20
        
        if annotation == self.currentAnnotation:
            tags = ("currentAnnotation", "annotation")
            color = "orange"
        else:
            tags = ("annotation", )
            color = self.series[annotation.series]["color"]
        
        #item1 = self.canvas.create_line(px1, pIntMin, px1, pIntMax, tags=tags, fill=color)
        item1 = self.canvas.create_line(px1, pIntMin, px1, py-10, tags=tags, fill=color)
        item2 = self.canvas.create_line(px2, pIntMin, px2, py-10, tags=tags, fill=color)
        #item2 = self.canvas.create_line(px2, pIntMin, px2, pIntMax, tags=tags, fill=color)
        item3 = self.canvas.create_line(px1, py, px2, py, tags=tags, fill=color,arrow="both")
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

