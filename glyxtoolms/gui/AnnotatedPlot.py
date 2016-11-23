from glyxtoolms.gui import FramePlot
import glyxtoolms
import ttk
import Tkinter
import tkColorChooser
import tkMessageBox
import tkFont
import random

class Annotatable(object):
    
    def __init__(self,x=0,y=0):
        """  Annotatable object, has to provide a x and y coordinate """
        self.x = x
        self.y = y

COLORS = ["#c00000", "#ff0000", "#7030a0", "#b83098", "#0070c0", "#00b0f0", "#00aa50", "#92d050", "#ff8b00", "#ffc000"]
ACOLORS = ["#c05000", "#ff5300", "#8c30a0", "#b85698", "#00a1c0", "#00c9f0", "#00c950", "#92f150", "#ff9900", "#ffe400"]
        
class ColorChooser(Tkinter.Toplevel):

    def __init__(self, master, startColor=None):
        Tkinter.Toplevel.__init__(self, master=master)
        self.master = master
        self.title("Edit Series Color")
        self.config(bg="#d9d9d9")
        self.color = None
        
        self.buttons = []
        for index, color in enumerate(COLORS):
            b = Tkinter.Button(self, width=1, height=1)
            b.config(bg=color)
            b.config(activebackground=ACOLORS[index])
            b.config(command=lambda x=b: self.setColor(x))
            b.grid(row=index%2,column=int(index/2))
            self.buttons.append(b)
            if startColor == color:
                b.config(relief="sunken")
        
        col = int(index/2)
        self.current = Tkinter.Label(self, text="Currently chosen")
        self.current.grid(row=0, column=col+1, columnspan=2)
        if startColor != None:
            self.current.config(bg=startColor)
        bOK = Tkinter.Button(self, text="Ok", command=self.pressedOK)
        bOK.grid(row=1,column=col+1)
        bCancel = Tkinter.Button(self, text="Cancel", command=self.pressedCancel)
        bCancel.grid(row=1,column=col+2)

        # lift window on top
        self.lift(master)
        self.transient(master)
        self.grab_set()
        self.wait_window(self)
        
    def setColor(self, button):
        # untoggle all buttons
        for b in self.buttons:
            b.config(relief="raised")
        button.config(relief="sunken")
        self.current.config(bg=button.cget("bg"))
        
    def pressedOK(self):
        color = self.current.cget("bg")
        self.color = color
        self.destroy()

    def pressedCancel(self):
        self.color = None
        self.destroy()

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
        self.selectedAnnotation = None
        self.mouseOverAnnotation = None
        
        self.canvas.bind("<Button-1>", self.button1Pressed, "+")
        self.canvas.bind("<ButtonRelease-1>", self.button1Released, "+")
        self.canvas.bind("<B1-Motion>", self.button1Motion, "+")
        self.canvas.bind("<Motion>", self.mouseMoveEvent, "+")
        #self.canvas.bind("<Button-3>", self.showContextMenu)
        #self.canvas.bind("<Double-Button-1>", self.showAnnotationEdit)
        #self.canvas.bind("<Button-3>", self.button3Pressed, "+")
        #self.canvas.bind("<ButtonRelease-3>", self.button3Released, "+")
        #self.canvas.bind("<B3-Motion>", self.button3Motion, "+")
        
        self.canvas.bind("<Delete>", self.eventDeleteAnnotation, "+")
        
        # add sidepanel for annotations
        sidePanelAnnotations = AnnotationSidePanel(self.sidepanel, self)
        self.sidepanel.addContextPanel("ruler", sidePanelAnnotations)
        
        # add ruler toggle
        self.rulerbutton = self.toolbar.addButton("ruler","toggle", "default")
        # add trace to ruler button toggles
        self.rulerbutton.active.trace("w", self.rulerToggled)

        
    def rulerToggled(self, *arg, **args):
        if self.rulerbutton.active.get() == False:
            self.setSelectedAnnotation(None)
            self._paintCanvas()
        
    def button1Motion(self, event):
        if self.rulerbutton.active.get() == False:
            return
        if self.action == None:
            return
        objects = self.findItemsAt(pixelX=event.x)
        # find annotations and peaks
        xx = []
        for item in objects["annotation"]:
            other = self.annotationItems[item]
            key = other.items[item]
            if key == "x1":
                xx.append((other.x1,other))
            elif key == "x2":
                xx.append((other.x2,other))
        for item in objects["annotatable"]:
            peak = self.peaksByItem[item]
            xx.append((peak.x, peak))
        
        if self.action.get("name","") == 'move_x1':
            annotation = self.action.get("annotation")
            # select new x position
            x = None
            for x,other in xx:
                if other == annotation:
                    x = None
                    continue
                break
            cursor="sb_h_double_arrow"
            if x != None and x < annotation.x2:
                annotation.x1 = x
                annotation.valid = True
            else:
                annotation.valid = False
                x = self.convXtoA(event.x)
                if x < annotation.x2:
                    annotation.x1 = x
                    self.canvas.config(cursor=cursor)
                else:
                    cursor="X_cursor"
            self.canvas.config(cursor=cursor)
            self.sidepanel.panels["ruler"].updateAnnotationMasses()
            self._paintCanvas(False)
        elif self.action.get("name","") == 'move_x2':
            annotation = self.action.get("annotation")
            x = None
            for x,other in xx:
                if other == annotation:
                    x = None
                    continue
                break
            cursor="sb_h_double_arrow"
            if x != None and x > annotation.x1:
                annotation.x2 = x
                annotation.valid = True
            else:
                annotation.valid = False
                x = self.convXtoA(event.x)
                if x > annotation.x1:
                    annotation.x2 = x
                    self.canvas.config(cursor=cursor)
                else:
                    cursor="X_cursor"
            self.canvas.config(cursor=cursor)
            self.sidepanel.panels["ruler"].updateAnnotationMasses()
            self._paintCanvas(False)
        elif self.action.get("name","") == 'selected_x1' or self.action.get("name","") == 'selected_x2':
            annotation = self.action.get("annotation")
            x = None
            for x,other in xx:
                if other == annotation:
                    x = None
                    continue
                break
            if x != None:
                annotation.valid = True
            else:
                x = self.convXtoA(event.x)
                annotation.valid = False
            xo = self.action.get("originx")
            if x < xo:
                annotation.x1 = x
                annotation.x2 = xo
            else:
                annotation.x1 = xo
                annotation.x2 = x
            self.sidepanel.panels["ruler"].updateAnnotationMasses()
            self._paintCanvas(False)

    def button1Released(self, event):
        if self.rulerbutton.active.get() == False:
            return
        if self.action is None:
            return
        repaint = False
        if self.action.get("name","") == 'move_x1':
            annotation = self.action.get("annotation")
            if annotation.valid == False:
                annotation.valid = True
                annotation.x1 = self.action.get("originx")
                repaint = True
                self.sidepanel.panels["ruler"].updateAnnotationMasses()
        if self.action.get("name","") == 'move_x2':
            annotation = self.action.get("annotation")
            if annotation.valid == False:
                annotation.valid = True
                annotation.x2 = self.action.get("originx")
                repaint = True
                self.sidepanel.panels["ruler"].updateAnnotationMasses()
        if self.action.get("name","") == 'selected_x1' or self.action.get("name","") == 'selected_x1':
            annotation = self.action.get("annotation")
            if annotation.valid == False or annotation.x1 == annotation.x2:
                self.removeAnnotation(annotation)
                repaint = True
        else:
            self.action = None
        if repaint == True:
            self._paintCanvas(False)
        

    def _paintCanvas(self, addToHistory=True):
        """ Method override to inject annotation painting """
        super(AnnotatedPlot, self)._paintCanvas(addToHistory)
        self.paintAllAnnotations()

    def clearAnnotatableList(self):
        self.peaksByItem = {}

    def addAnnotatableItem(self, item, annotatableObject):
        self.peaksByItem[item] = annotatableObject
        
    def addSeries(self, seriesName, color):
        series = glyxtoolms.io.AnnotationSeries()
        series.name = seriesName
        series.color = color
        self.annotations[seriesName] = series
        self.sidepanel.panels["ruler"].update()

    def addAnnotation(self, annotation, seriesName):
        annotation.series = seriesName
        annotation.items = {}
        if not seriesName in self.annotations:
            # choose a new color, preferably not used yet
            colors = set(COLORS)
            usedColors = set([s.color for s in self.annotations.values()])
            remaining = colors.difference(usedColors)
            if len(remaining) == 0:
                color = random.choice(list(remaining))
            else:
                color = remaining.pop()
            self.addSeries(seriesName, color) # TODO: set color
        self.annotations[seriesName].annotations.append(annotation)
        
    def removeAnnotation(self, annotation):
        seriesName = annotation.series
        if not seriesName in self.annotations:
            return
        if not annotation in  self.annotations[seriesName].annotations:
            return
        self.annotations[seriesName].annotations.remove(annotation)
        # check if series is empty, if yes remove too
        repaint = False
        if self.selectedAnnotation == annotation:
            self.setSelectedAnnotation(None)
            repaint = True
        if len(self.annotations[seriesName].annotations) == 0:
            self.annotations.pop(seriesName)
            repaint = True
            self.sidepanel.panels["ruler"].update()
        if repaint == True:
            self._paintCanvas()
            
    def findItemsAt(self, pixelX=None, pixelY=None, delta=10):
        if pixelX == None and pixelY == None:
            return {"annotatable":[], "annotation":[]} 
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
        return {"annotatable":[p[1] for p in peaks], 
                 "annotation":[a[1] for a in annotations]}        

    def findItemAt(self, pixelX=None, pixelY=None):
        if pixelX == None and pixelY == None:
            return
        objects = self.findItemsAt(pixelX,pixelY)
        peaks = objects["annotatable"]
        annotations = objects["annotation"]
        if len(peaks) == 0:
            peak = None
        else:
            peak = peaks[0]
        if len(annotations) == 0:
            annotation = None
        else:
            annotation = annotations[0]
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

    def setSelectedAnnotation(self, annotation):
        if self.selectedAnnotation != None:
            self.selectedAnnotation.selected = ""
        self.selectedAnnotation = annotation
        self.sidepanel.panels["ruler"].setAnnotation(annotation)
        
    def setMouseOverAnnotation(self, annotations, selected):
        if self.mouseOverAnnotation != None:
            self.mouseOverAnnotation.selected = ""
        if selected == "":
            annotation = None
        else:
            annotation = annotations[selected]
            annotation.selected = selected
        self.mouseOverAnnotation = annotation
        self._paintCanvas()
                
    def mouseMoveEvent(self, event):
        if self.rulerbutton.active.get() == False:
            return
        objects = self.findItemsAt(pixelX=event.x, pixelY=event.y,delta=10)
        annotationItems = objects["annotation"]
        peakItems = objects["annotatable"]
        cursor = ""
        if len(annotationItems) > 0:
            # collect text
            text = {}
            for item in annotationItems:
                annotation = self.annotationItems[item]
                key = annotation.items[item]
                if not key in text:
                    text[key] = annotation
            if "move_x1" in text:
                cursor="sb_h_double_arrow"
                self.setMouseOverAnnotation(text, "move_x1")
            elif "move_x2" in text:
                cursor="sb_h_double_arrow"
                self.setMouseOverAnnotation(text, "move_x2")
            elif "selected_x1" in text:
                cursor="plus"
                self.setMouseOverAnnotation(text, "selected_x1")
            elif "selected_x2" in text:
                cursor="plus"
                self.setMouseOverAnnotation(text, "selected_x2")
            elif "selected_body" in text:
                #cursor="pencil"
                self.setMouseOverAnnotation(text, "selected_body")
            elif "line" in text:
                self.setMouseOverAnnotation(text, "line")
            elif "text" in text:
                self.setMouseOverAnnotation(text, "text")
        else:
            self.setMouseOverAnnotation(None, "")
        if cursor == "" and len(peakItems) > 0:
            cursor = "bottom_side"
        self.canvas.config(cursor=cursor)

    def button1Pressed(self, event):
        if self.rulerbutton.active.get() == False:
            return
        objects = self.findItemsAt(pixelX=event.x, pixelY=event.y,delta=10)
        annotationItems = objects["annotation"]
        annotatableItems = objects["annotatable"]
        
        if len(annotationItems) > 0:
            # collect text
            text = {}
            for item in annotationItems:
                annotation = self.annotationItems[item]
                key = annotation.items[item]
                if not key in text or annotation == self.selectedAnnotation:
                    text[key] = annotation
            setTo = None
            self.action = None
            if "move_x1" in text:
                setTo = text["move_x1"]
                self.action = {"name":"move_x1", "annotation":setTo, "originx":setTo.x1}
            elif "move_x2" in text:
                setTo = text["move_x2"]
                self.action = {"name":"move_x2", "annotation":setTo, "originx":setTo.x2}
            elif "selected_x1" in text:
                setTo = text["selected_x1"]
                # create new annotation
                a = glyxtoolms.io.Annotation()
                a.x1 = setTo.x1
                a.x2 = setTo.x1
                a.text = ""
                a.y = 0
                self.addAnnotation(a, setTo.series)
                self.action = {"name":"selected_x1", "annotation":a, "originx":setTo.x1}
                setTo = a
            elif "selected_x2" in text:
                setTo = text["selected_x2"]
                # create new annotation
                a = glyxtoolms.io.Annotation()
                a.x1 = setTo.x2
                a.x2 = setTo.x2
                a.text = ""
                a.y = 0
                self.addAnnotation(a, setTo.series)
                self.action = {"name":"selected_x2", "annotation":a, "originx":setTo.x2}
                setTo = a
            elif "selected_body" in text:
                setTo = text["selected_body"]
            elif "text" in text:
                setTo = text["text"]
            elif "line" in text:
                setTo = text["line"]
            if self.selectedAnnotation != setTo:
                self.setSelectedAnnotation(setTo)
                self._paintCanvas()
                return
            elif setTo != None:
                self._paintCanvas()
                return
        if len(annotatableItems) > 0:
            self.setSelectedAnnotation(None)
            # select nearest annotatable
            nearest = []
            for item in annotatableItems:
                annotatable = self.peaksByItem[item]
                dist = abs(self.convAtoX(annotatable.x)-event.x)
                nearest.append((dist, annotatable))
            nearest = nearest[0][1]
            # create new annotation
            a = glyxtoolms.io.Annotation()
            a.x1 = nearest.x
            a.x2 = nearest.x
            a.text = ""
            a.y = 0
            # choose a default name series1, series2, etc
            i = 1
            while True:
                newName = "series"+str(i)
                if not newName in self.annotations:
                    break
                i += 1
            self.addAnnotation(a, newName)
            self.action = {"name":"selected_x1", "annotation":a, "originx":a.x1}
            self.setSelectedAnnotation(a)
            self._paintCanvas()
        else:
            self.setSelectedAnnotation(None)
            self._paintCanvas()

    def button3Pressed(self, event):
        if self.rulerbutton.active.get() == False:
            return
        peak = self.findObjectAt(pixelX=event.x)["annotatable"]
        y = self.convYtoB(event.y)
        
        if peak is not None:
            self.selectedAnnotation = glyxtoolms.io.Annotation()
            self.selectedAnnotation.x1 = peak.x
            self.selectedAnnotation.x2 = peak.x
            self.selectedAnnotation.selected = "x2"
            self.selectedAnnotation.y = y
        else:
            self.selectedAnnotation = None
        self.paintCurrentAnnotation()

    
    def button3Motion(self, event):
        if self.rulerbutton.active.get() == False:
            return
        if self.selectedAnnotation is None:
            return
        peak = self.findObjectAt(pixelX=event.x)["annotatable"]

        if peak is  None:
            return
        
        x = peak.x

        if self.selectedAnnotation.selected == "x1":
            self.selectedAnnotation.x1 = x
        elif self.selectedAnnotation.selected == "x2":
            self.selectedAnnotation.x2 = x

        self.selectedAnnotation.y = event.y
        self.selectedAnnotation.text = str(round(abs(self.selectedAnnotation.x1-self.selectedAnnotation.x2),4))
        self.paintCurrentAnnotation()
    
    def button3Released(self, event):
        if self.rulerbutton.active.get() == False:
            return
        if self.selectedAnnotation is None:
            return
        self.selectedAnnotation.y = event.y
        peak = self.findObjectAt(pixelX=event.x)["annotatable"]
        if peak is not None:
            if self.selectedAnnotation.selected == "x1":
                self.selectedAnnotation.x1 = peak.x
            elif self.selectedAnnotation.selected == "x2":
                self.selectedAnnotation.x2 = peak.x
            self.selectedAnnotation.text = str(round(abs(self.selectedAnnotation.x1-self.selectedAnnotation.x2),4))
            self.addAnnotation(self.selectedAnnotation, "test")
        self.selectedAnnotation = None
        self.paintCanvas()

    def eventDeleteAnnotation(self, event):
        if self.selectedAnnotation is None:
            return
        self.removeAnnotation(self.selectedAnnotation)
        
    def paintCurrentAnnotation(self):
        self.canvas.delete("currentAnnotation")
        # draw annotation lines
        if self.selectedAnnotation is None:
            return
        self.paintAnnotation(self.selectedAnnotation)
        self.canvas.tag_lower("currentAnnotation")
        
    def paintAllAnnotations(self):
        self.canvas.delete("annotation")
        self.annotationItems = {}
        dimensions = {}
        # calculate dimensions of each series
        for seriesName in self.annotations:
            series = self.annotations[seriesName]
            if series.hidden == True:
                continue
            if len(series.annotations) == 0:
                continue
            dimensions[seriesName] = {}
            
            for annotation in sorted(series.annotations, key=lambda a: (a.x1,-abs(a.x2-a.x1))):
                x1 = annotation.x1
                x2 = annotation.x2
                level = 0
                while True:
                    if level not in dimensions[seriesName]:
                         dimensions[seriesName][level] = (x1,x2)
                         annotation.level = level
                         break
                    else:
                        l1,l2 = dimensions[seriesName][level]
                        if not (x1 < l2 and l1 < x2): # ranges dont overlap
                            ranges = (x1,x2,l1,l2)
                            dimensions[seriesName][level] = (min(ranges),max(ranges))
                            annotation.level = level
                            break
                    level += 1
        # group series
        noOverlap = {}
        offsets = {}
        for seriesName in dimensions:
            y1 = min(dimensions[seriesName].keys())
            y2 = max(dimensions[seriesName].keys())
            x1= min([min(dimensions[seriesName][level]) for level in dimensions[seriesName]])
            x2= max([max(dimensions[seriesName][level]) for level in dimensions[seriesName]])
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
            offsets[seriesName] = offset
            noOverlap[seriesName] = (x1,x2,y1+offset,y2+offset)
        
        # recalculate annotation level based on offset
        for seriesName in sorted(offsets, key=lambda s: offsets[s]):
            for annotation in self.annotations[seriesName].annotations:
                annotation.level += offsets[seriesName]
                self.paintAnnotation(annotation)
        self.canvas.tag_lower("annotation")
        
    def paintAnnotation(self, annotation):
        # remove annotation items from canvas if exiting
        for item in annotation.items:
            if item in self.annotationItems:
                self.annotationItems.pop(item)
                self.canvas.delete(item)
        pIntMin = self.convBtoY(self.viewYMin)
        pIntMax = self.convBtoY(self.viewYMax)
        px1 = self.convAtoX(annotation.x1)
        px2 = self.convAtoX(annotation.x2)
        pXText = self.convAtoX((annotation.x1+annotation.x2)/2.0)
        py = annotation.level*20 + self.convBtoY(self.viewYMax)+20
        
        dash = None
        color = self.annotations[annotation.series].color
        width = 1
        
        tags = ("annotation", )
        if annotation == self.selectedAnnotation:
            tags = ("currentAnnotation", "annotation")
            #color = "orange"
        if annotation == self.mouseOverAnnotation:
            tags = ("annotation", )
            width = 4
        
        #item1 = self.canvas.create_line(px1, pIntMin, px1, pIntMax, tags=tags, fill=color)
        item1 = self.canvas.create_line(px1, pIntMin, px1, py-10, tags=tags, fill=color)
        item2 = self.canvas.create_line(px2, pIntMin, px2, py-10, tags=tags, fill=color)
        #item2 = self.canvas.create_line(px2, pIntMin, px2, pIntMax, tags=tags, fill=color)
        if annotation.valid == True:
            item3 = self.canvas.create_line(px1, py, px2, py, tags=tags, fill=color,arrow="both", width=width)
        else:
            item3 = self.canvas.create_line(px1, py, px2, py, tags=tags, fill=color,arrow="both", width=width, dash=(3,5))
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
    
        if annotation == self.selectedAnnotation:
            #item5 = self.canvas.create_rectangle(px1+5, py-16, px2-5, py+6, tags=tags, outline='', fill="grey", stipple="gray25",activestipple="gray75")
            item5 = self.canvas.create_rectangle(px1+5, py-16, px2-5, py+6, tags=tags, outline='', fill="grey", stipple="gray25")
            annotation.items[item5] = "selected_body"
            self.canvas.tag_lower(item5,item1)
            self.annotationItems[item5] = annotation
            
            item6 = self.canvas.create_rectangle(px1-5, pIntMin, px1+5, py+6, tags=tags, outline='', fill="black", stipple="gray25",activestipple="gray75")
            annotation.items[item6] = "selected_x1"
            self.canvas.tag_lower(item6,item1)
            self.annotationItems[item6] = annotation
            
            item7 = self.canvas.create_rectangle(px1-5, py-16, px1+5, py+6, tags=tags, outline='', fill="green", stipple="gray25",activestipple="gray75")
            annotation.items[item7] = "move_x1"
            self.canvas.tag_lower(item7,item1)
            self.annotationItems[item7] = annotation
            
            item8 = self.canvas.create_rectangle(px2-5, pIntMin, px2+5, py+6, tags=tags, outline='', fill="black", stipple="gray25",activestipple="gray75")
            annotation.items[item8] = "selected_x2"
            self.canvas.tag_lower(item8,item1)
            self.annotationItems[item8] = annotation
            
            item9 = self.canvas.create_rectangle(px2-5, py-16, px2+5, py+6, tags=tags, outline='', fill="green", stipple="gray25",activestipple="gray75")
            annotation.items[item9] = "move_x2"
            self.canvas.tag_lower(item9,item1)
            self.annotationItems[item9] = annotation
        
        self.annotationItems[item1] = annotation
        self.annotationItems[item2] = annotation
        self.annotationItems[item3] = annotation
        self.annotationItems[item4] = annotation




        
class EditAnnotationFrame(Tkinter.Toplevel):

    def __init__(self, master):
        Tkinter.Toplevel.__init__(self, master=master)
        self.master = master
        self.title("Edit Annotation")
        self.config(bg="#d9d9d9")
        
        l1 = ttk.Label(self, text="Text: ")
        l1.grid(row=1, column=0, sticky="NE")
        
        self.varText = Tkinter.StringVar()
        e2 = ttk.Entry(self, textvariable=self.varText)
        e2.grid(row=1, column=1, columnspan=2)
        self.varText.set(master.selectedAnnotation.text)
        
        l2 = ttk.Label(self, text="Series: ")
        l2.grid(row=2, column=0, sticky="NE")
        
        #f2 = ttk.Labelframe(self,text="Series")
        #f2.grid(row=2, column=0, columnspan=3, sticky="NE")
        self.lb = Tkinter.Listbox(self, selectmode="SINGLE")
        self.lb.config(bg="white")
        self.lb.grid(row=2, column=1, columnspan=2, sticky="NE")
        #self.lb.pack()
        
        bAdd = Tkinter.Button(self, text="Edit available Series")
        bAdd.grid(row=3, column=1, columnspan=2, sticky="NE")
        
        bCancel = Tkinter.Button(self, text="Cancel",command=self.pressedCancel)
        bCancel.grid(row=4, column=1, sticky="NE")
        
        bOk = Tkinter.Button(self, text="OK",command=self.pressedOK)
        bOk.grid(row=4, column=2, sticky="NE")
        
        # lift window on top
        self.lift(master)
        self.transient(master)
        self.grab_set()
        
        self.updateListbox()
        
    def updateListbox(self):
        self.lb.delete(0, "end")
        
        for seriesName in self.master.annotations:
            series = self.master.annotations[seriesName]
            self.lb.insert("end", series.name)
            self.lb.itemconfig("end", {'fg':series.color,"selectforeground":series.color})
            # set selected
            if seriesName == self.master.selectedAnnotation.series:
                self.lb.selection_set("end")
        return
        
    def pressedOK(self):
        # check name
        newName = self.varText.get()
        if newName != self.master.selectedAnnotation.text:
            self.master.selectedAnnotation.text = newName
        self.destroy()
        self.master._paintCanvas()
        
    def pressedCancel(self):
        self.destroy()
        
class CheckboxList(Tkinter.Frame):
    
    def __init__(self, master, framePlot):
        Tkinter.Frame.__init__(self, master=master)
        # Header:
        # Action, Name, Color, Show Series
        self.frame = Tkinter.LabelFrame(self,text="Edit Series")
        self.frame.grid(row=0, column=0, sticky="NSEW")
        self.framePlot = framePlot
        self.columnconfigure(0,weight=1)
        self.rowconfigure(0,weight=1)
        self.row = 0
        self.elements = {} # link to all elements of each series over series object
        eye_icon = 'R0lGODlhDAAIAIAAAAAAAAAAACH+EUNyZWF0ZWQgd2l0aCBHSU1QACH5BAEKAAEALAAAAAAMAAgA\nAAIUjIFpC9fx4JkyPhthbnlJ6nWJYhQAOw==\n'
        photo = Tkinter.PhotoImage(data=eye_icon)
        h1 = Tkinter.Label(self.frame, text="Name")
        h1.grid(row=self.row, column=0)
        h2 = Tkinter.Label(self.frame, text="Color")
        h2.grid(row=self.row, column=1)
        h3 = Tkinter.Label(self.frame, image=photo, width=10, height=10)
        h3.image = photo
        h3.grid(row=self.row, column=2)
        
    def clear(self):
        for series in self.elements:
            self.elements[series]["entryName"].destroy()
            self.elements[series]["buttonColor"].destroy()
            self.elements[series]["checkShow"].destroy()
            self.elements[series]["buttonDelete"].destroy()
        self.elements = {}
        self.row = 0
        
    def addSeries(self, series):
        self.row += 1
        
        self.frame.columnconfigure(0,weight=1)
        self.frame.columnconfigure(1,weight=0)
        self.frame.columnconfigure(2,weight=0)
        self.frame.columnconfigure(3,weight=0)
        self.frame.rowconfigure(0,weight=1)
        
        varName = Tkinter.StringVar()
        entryName = Tkinter.Entry(self.frame, textvariable=varName, width=10)
        entryName.config(bg="white")
        entryName.grid(row=self.row, column=0, sticky="WE")
        varName.set(series.name)
        varName.trace("w", lambda name, index, mode,x=series:self.eventNameChanged(x))
        
        buttonColor = Tkinter.Button(self.frame, text=" ", padx=6, pady=1)
        buttonColor.config(command=lambda b=buttonColor, s=series: self.eventSetColor(b,series))
        buttonColor.grid(row=self.row, column=1)
        buttonColor.config(bg=series.color)
        buttonColor.config(activebackground=series.color)
        
        
        varShow = Tkinter.IntVar()
        checkShow = Tkinter.Checkbutton(self.frame, variable=varShow)
        checkShow.grid(row=self.row, column=2)
        if series.hidden == True:
            varShow.set(0)
        else:
            varShow.set(1)
            
        varShow.trace("w", lambda name, index, mode,s=series, var=varShow:self.eventSetVisibility(s,var))
            
        buttonDelete = Tkinter.Button(self.frame, text="X", padx=3, pady=0)
        buttonDelete.config(command=lambda x=series: self.eventDeleteSeries(x))
        buttonDelete.grid(row=self.row, column=3)
                
        # add elements to list
        self.elements[series] = {}
        self.elements[series]["varName"] = varName
        self.elements[series]["entryName"] = entryName
        self.elements[series]["buttonColor"] = buttonColor
        self.elements[series]["varShow"] = varShow
        self.elements[series]["checkShow"] = checkShow
        self.elements[series]["buttonDelete"] = buttonDelete
        
    def eventSetVisibility(self, series, var):
        if series.hidden  == var.get():
            series.hidden = not series.hidden
            if series.hidden == True and self.master.currentAnnotation != None:
                if self.master.currentAnnotation.series == series.name:
                    self.master.setAnnotation(None)
            self.framePlot._paintCanvas()

    def eventDeleteSeries(self, series):
        if series not in self.elements:
            return
        ask = tkMessageBox.askyesno("Delete Series", 
                                    "Do you want to delete the series '"+
                                    self.elements[series]["entryName"].get()+
                                    "'?",
                                    default=tkMessageBox.NO)
        if ask == False:
            return
        self.elements[series]["entryName"].destroy()
        self.elements[series]["buttonColor"].destroy()
        self.elements[series]["checkShow"].destroy()
        self.elements[series]["buttonDelete"].destroy()
        self.elements.pop(series)
        self.framePlot.annotations.pop(series.name)
        if self.master.currentAnnotation in series.annotations:
            self.master.setAnnotation(None)
        self.master.update()
        self.framePlot._paintCanvas()
        
    def eventSetColor(self, button, series):
        chooser = ColorChooser(self, button.cget("bg"))
        color = chooser.color
        if color != None and series.color != color:
            button.config(bg=color)
            button.config(activebackground=color)
            series.color=color
            self.master.update()
            self.framePlot._paintCanvas()
        
    def eventNameChanged(self,changedSeries):
        # check all entries for names which are not unique or empty
        names = {}
        valid = True
        for series in self.elements:
            varName = self.elements[series]["varName"]
            entryName = self.elements[series]["entryName"]
            
            name = varName.get()
            names[name] = names.get(name, []) + [entryName]
        for name in names:
            if len(names[name]) > 1 or name == "":
                color = "red"
                valid = False
            else:
                color = "white"
            for entry in names[name]:
                entry.config(bg=color)
        if valid == True:
            varName = self.elements[changedSeries]["varName"]
            newName = varName.get()
            oldName = changedSeries.name
            if newName == oldName:
                return
            if oldName in self.framePlot.annotations:
                self.framePlot.annotations.pop(oldName)
                self.framePlot.annotations[newName] = changedSeries
                for annotation in changedSeries.annotations:
                    annotation.series = newName
                changedSeries.name = newName
                self.master.setAnnotation(self.master.currentAnnotation)
    
class AnnotationSidePanel(Tkinter.Frame, object):
    def __init__(self, master, framePlot):
        Tkinter.Frame.__init__(self, master=master)
        self.master = master
        self.framePlot = framePlot
        
        self.columnconfigure(0,weight=1)
        self.rowconfigure(0,weight=0)
        self.rowconfigure(1,weight=1)
        self.rowconfigure(2,weight=0)
        
        self.frameAnnotation = Tkinter.LabelFrame(self,text="Current Annotation")
        self.annotationContent = Tkinter.Frame(self.frameAnnotation)
        self.annotationContent.grid(row=0,column=0)
        self.annotationContent.columnconfigure(0,weight=0)
        self.annotationContent.columnconfigure(1,weight=1)
        self.annotationContent.rowconfigure(0,weight=0)
        self.annotationContent.rowconfigure(1,weight=0)
        self.annotationContent.rowconfigure(2,weight=0)
        self.annotationContent.rowconfigure(3,weight=1)
        
        self.buttonDelete = Tkinter.Button(self.annotationContent, text="Delete  Annotation",command=self.deleteAnnotation)
        self.buttonDelete.grid(row=0,column=1,columnspan=1, sticky="NESW")
        
        labelMassText1 = Tkinter.Label(self.annotationContent, text="m1:")
        labelMassText1.grid(row=1,column=0, sticky="NSEW")
        self.labelMass1 = Tkinter.Label(self.annotationContent, text=" - Da", anchor="e")
        self.labelMass1.grid(row=1,column=1, sticky="NSEW")
        
        labelMassText2 = Tkinter.Label(self.annotationContent, text="m2:")
        labelMassText2.grid(row=2,column=0, sticky="NSEW")
        self.labelMass2 = Tkinter.Label(self.annotationContent, text=" - Da", anchor="e")
        self.labelMass2.grid(row=2,column=1, sticky="NSEW")
        
        labelMassText3 = Tkinter.Label(self.annotationContent, text="diff:")
        labelMassText3.grid(row=3,column=0, sticky="NSEW")
        self.labelMass3 = Tkinter.Label(self.annotationContent, text="= - Da", anchor="e")
        self.labelMass3.grid(row=3,column=1, sticky="NSEW")
        

        labelText = Tkinter.Label(self.annotationContent, text="Text:")
        labelText.grid(row=4,column=0)
        self.varText = Tkinter.StringVar()
        self.entryText = Tkinter.Entry(self.annotationContent, textvariable=self.varText ,width=15)
        self.entryText.config(bg="white")
        self.entryText.grid(row=4,column=1, sticky="NWES")

        labelSeries = Tkinter.Label(self.annotationContent, text="Series:")
        labelSeries.grid(row=5,column=0)

        self.varSeries = Tkinter.StringVar()
        self.mb = Tkinter.Menubutton(self.annotationContent, text=u" \u25BC",
                             relief="raised", anchor="e")
        self.mb.menu = Tkinter.Menu(self.mb, tearoff=0)
        self.mb['menu'] = self.mb.menu
        self.mb.grid(row=5,column=1, sticky="NESW")

        self.varText.trace("w", self.eventTextChanged)
        self.varSeries.trace("w", self.eventSeriesChanged)
        

        
        self.frameAnnotation.grid(row=0,column=0, sticky="SEW")
        
        self.frameSeries = CheckboxList(self, self.framePlot)
        self.frameSeries.grid(row=1,column=0, sticky="SEW")
        self.setAnnotation(None)
        
    def deleteAnnotation(self):
        if self.currentAnnotation == None:
            return
        self.framePlot.removeAnnotation(self.currentAnnotation)

    def update(self):
        self.frameSeries.clear()
        for seriesName in self.framePlot.annotations:
            series = self.framePlot.annotations[seriesName]
            self.frameSeries.addSeries(series)
        self.buildMenu()
            
    def updateAnnotationMasses(self):
        if self.currentAnnotation == None:
            self.labelMass1.config(text=" - Da")
            self.labelMass2.config(text=" - Da")
            self.labelMass3.config(text="= - Da")
            self.labelMass3.config(fg="black")
        else:
            m1 = str(round(self.currentAnnotation.x1,4))
            m2 = str(round(self.currentAnnotation.x2,4))
            m3 = str(round(self.currentAnnotation.x2-self.currentAnnotation.x1,4))
            self.labelMass1.config(text= m1 + " Da")
            self.labelMass2.config(text= m2 + " Da")
            self.labelMass3.config(text="= " + m3 + " Da")
            if self.currentAnnotation.valid == True:
                self.labelMass3.config(fg="black")
            else:
                self.labelMass3.config(fg="red")
        
    def setAnnotation(self, annotation):
        self.currentAnnotation = annotation
        
        if annotation == None:
            self.mb.config(text="Series"+u" \u25BC")
            self.mb.config(state="disabled")
            self.buttonDelete.config(state="disabled")
            self.varText.set("Select Annotation")
            self.entryText.config(state="disabled")
        else:
            self.mb.config(state="normal")
            self.buttonDelete.config(state="normal")
            self.entryText.config(state="normal")
            self.varSeries.set(annotation.series)
            self.buildMenu()
            self.varText.set(annotation.text)
        self.updateAnnotationMasses()
        
    def getColorImage(self,color):
        size = 12
        image = Tkinter.PhotoImage(width=size,height=size)
        for x in range(0,size):
            for y in range(0,size):
                image.put(color,(x,y))
        return image

    def buildMenu(self):
        if self.currentAnnotation == None:
            return
        series = self.framePlot.annotations[self.currentAnnotation.series]
        self.mb.menu.delete(0,"end")
        
        #eye_icon = 'R0lGODlhDAAIAIAAAAAAAAAAACH+EUNyZWF0ZWQgd2l0aCBHSU1QACH5BAEKAAEALAAAAAAMAAgA\nAAIUjIFpC9fx4JkyPhthbnlJ6nWJYhQAOw==\n'
        #photo = Tkinter.PhotoImage(data=eye_icon)
        self.mb.menu.images = []
        for name in sorted(self.framePlot.annotations.keys()):

            s = self.framePlot.annotations[name]
            photo = self.getColorImage(s.color)
            self.mb.menu.add_radiobutton(label=name, 
                                         variable=self.varSeries,
                                         value=name, compound="left", image=photo, indicatoron=False)
            self.mb.menu.images.append(photo)

        
        self.mb.config(text=series.name+u" \u25BC")
        photo = self.getColorImage(series.color)
        self.mb.config(compound="left", image=photo)
        self.mb.image = photo
        self.varSeries.set(series.name)
        
    def eventSeriesChanged(self,*arg, **args):
        # check if annotation needs to be updated
        if self.currentAnnotation == None:
            return
        newSeries = self.framePlot.annotations[self.varSeries.get()]
        self.mb.config(text=newSeries.name+u" \u25BC")
        photo = self.getColorImage(newSeries.color)
        self.mb.config(compound="left", image=photo)
        self.mb.image = photo
        if self.currentAnnotation.series == newSeries.name:
            return
        oldSeries = self.framePlot.annotations[self.currentAnnotation.series]
        oldSeries.annotations.remove(self.currentAnnotation)
        newSeries.annotations.append(self.currentAnnotation)
        self.currentAnnotation.series = newSeries.name
        if len(oldSeries.annotations) == 0:
            self.framePlot.annotations.pop(oldSeries.name)
            self.update()
        self.framePlot._paintCanvas()
        
    def eventTextChanged(self, *arg, **args):
        if self.currentAnnotation == None:
            return
        self.currentAnnotation.text = self.varText.get()
        self.framePlot._paintCanvas()
        

