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
        self.destroy()
        self.color = color
        
        
    def pressedCancel(self):
        self.color = None
        self.destroy()
        

class AnnotationContextPanel(Tkinter.Frame):
    def __init__(self, master, framePlot):
        Tkinter.Frame.__init__(self, master=master)
        self.master = master
        self.framePlot = framePlot
        self.currentAnnotation = None
        
        self.editPanel = ttk.Frame(self)
        self.editPanel.pack(side="left")
        
        self.hideEditPanel()
        
        self.seriesPanel = Tkinter.Frame(self.editPanel)
        self.seriesPanel.pack(side="left")
        editButton = Tkinter.Button(self.seriesPanel, text="Edit Series", command=self.editSeries)
        editButton.pack(side="left", fill="y")
        
        self.annotationPanel = Tkinter.Frame(self.editPanel)
        self.annotationPanel.pack(side="left")
        
        frameText = Tkinter.LabelFrame(self.annotationPanel,text="Annotation Text")
        frameText.pack(side="left")
        
        font = tkFont.Font(font=frameText['font'])
        font["size"] = 8
        frameText.config(font=font)

        self.varText = Tkinter.StringVar()
        entryText = Tkinter.Entry(frameText, textvariable=self.varText)
        entryText.config(bg="white")
        entryText.pack(side="left")
        self.varText.trace("w", self.eventTextChanged)
        
        frameSeries = Tkinter.LabelFrame(self.annotationPanel,text="Select Series")
        frameSeries.pack(side="left", fill="y")
        frameSeries.config(font=font)
        frameSeries.columnconfigure(0,weight=1)
        frameSeries.rowconfigure(0,weight=1)
        
        self.mb = Tkinter.Menubutton(frameSeries, text='', pady=0,
                             relief="raised")
        self.mb.grid(sticky="NWSE")
        
        
        self.mb.menu = Tkinter.Menu(self.mb, tearoff=0)
        self.mb['menu'] = self.mb.menu

        self.varSeries  = Tkinter.StringVar()
        self.varSeries.trace("w", self.eventSeriesChanged)
        
        frameMasses = Tkinter.Frame(self.annotationPanel)
        frameMasses.pack(side="left")
        self.varMasses1 = Tkinter.StringVar()
        labelMasses1 = Tkinter.Label(frameMasses, textvariable=self.varMasses1)
        labelMasses1.pack(side="top", anchor="w")
        self.varMasses2 = Tkinter.StringVar()
        labelMasses2 = Tkinter.Label(frameMasses, textvariable=self.varMasses2)
        labelMasses2.pack(side="top", anchor="w")
        
        self.setAnnotation(None)

    def eventSeriesChanged(self,*arg, **args):
        newSeries = self.framePlot.annotations[self.varSeries.get()]
        self.mb.config(text=newSeries.name)
        self.mb.config(foreground=newSeries.color)
        self.mb.config(activeforeground=newSeries.color)
        # check if annotation needs to be updated
        if self.currentAnnotation == None:
            return
        if self.currentAnnotation.series == newSeries.name:
            return
        oldSeries = self.framePlot.annotations[self.currentAnnotation.series]
        oldSeries.annotations.remove(self.currentAnnotation)
        newSeries.annotations.append(self.currentAnnotation)
        self.currentAnnotation.series = newSeries.name
        self.framePlot._paintCanvas()
        
    def buildMenu(self):
        if self.currentAnnotation == None:
            return
        series = self.framePlot.annotations[self.currentAnnotation.series]
        self.mb.menu.delete(0,"end")
        for name in sorted(self.framePlot.annotations.keys()):
            s = self.framePlot.annotations[name]
            self.mb.menu.add_radiobutton(label=name, 
                                         variable=self.varSeries,
                                         value=name)
            self.mb.menu.entryconfig("end", foreground=s.color)
            self.mb.menu.entryconfig("end", activeforeground=s.color)
        self.mb.menu.add_separator()
        self.mb.menu.add_command(label="Edit Series", command=self.editSeries)
        self.varSeries.set(series.name)
        self.mb.config(text=series.name)
        self.mb.config(foreground=series.color)
        self.mb.config(activeforeground=series.color)
        
    def showEditPanel(self):
        self.editPanel.pack(side="left")
    
    def hideEditPanel(self):
        self.editPanel.pack_forget()
        
    def setAnnotation(self, annotation):
        # show or hide annotation panel, make annotation editable
        if (annotation == None or 
        annotation.series not in self.framePlot.annotations or
        self.framePlot.annotations[annotation.series].hidden == True):
                
            self.annotationPanel.pack_forget()
            self.seriesPanel.pack(side="left")
            self.currentAnnotation = None
        else:
            self.currentAnnotation = annotation
            self.annotationPanel.pack(side="left")
            self.seriesPanel.pack_forget()
            # get series
            series = self.framePlot.annotations[annotation.series]
            self.varText.set(annotation.text)
            
            # build menu for series chooser
            self.buildMenu()
            self.varMasses1.set(str(round(annotation.x1,4)) + " -> " + str(round(annotation.x2,4)))
            self.varMasses2.set("= " + str(round(annotation.x2-annotation.x1,4)))
            #print annotation.__dict__
            
    def eventTextChanged(self, *arg, **args):
        self.currentAnnotation.text = self.varText.get()
        self.framePlot._paintCanvas()
        
    def editSeries(self):
        EditSeriesFrame(self, self.framePlot)
        
    def eventSeriesEdited(self):
        # rebuild menu to represent changes to series properties
        self.setAnnotation(self.currentAnnotation)
        

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

        #self.canvas.bind("<Button-2>", self.button2, "+")
        
        self.canvas.bind("<Button-1>", self.button1Pressed, "+")
        self.canvas.bind("<ButtonRelease-1>", self.button1Released, "+")
        self.canvas.bind("<B1-Motion>", self.button1Motion, "+")
        self.canvas.bind("<Motion>", self.mouseMoveEvent, "+")
        #self.canvas.bind("<Button-3>", self.showContextMenu)
        #self.canvas.bind("<Double-Button-1>", self.showAnnotationEdit)
        

        #self.canvas.bind("<Button-3>", self.button3Pressed, "+")
        #self.canvas.bind("<ButtonRelease-3>", self.button3Released, "+")
        #self.canvas.bind("<B3-Motion>", self.button3Motion, "+")
        
        self.canvas.bind("<Delete>", self.deleteAnnotation, "+")
        
        
        # add annotation context panel
        self.contextPanel = AnnotationContextPanel(self.toolbar, self)
        self.toolbar.addPanel("annotation", panel=self.contextPanel, side="left")
        
        # add ruler toggle
        self.rulerbutton = self.toolbar.addButton("ruler","toggle", "annotation")
        # add trace to ruler button toggles
        self.rulerbutton.active.trace("w", self.rulerToggled)

        
    def rulerToggled(self, *arg, **args):
        if self.rulerbutton.active.get() == True:
            self.contextPanel.showEditPanel()
        else:
            self.contextPanel.hideEditPanel()
            self.setSelectedAnnotation(None)
            self._paintCanvas()
        
    def button1Motion(self, event):
        if self.rulerbutton.active.get() == False:
            return
        if self.action == None:
            return
        objects = self.findItemsAt(pixelX=event.x)

        #print "b1-motion", self.action
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
                    continue
                break
            if x != None and x < annotation.x2:
                annotation.x1 = x
            self._paintCanvas(False)
        elif self.action.get("name","") == 'move_x2':
            annotation = self.action.get("annotation")
            x = None
            for x,other in xx:
                if other == annotation:
                    continue
                break
            if x != None and x > annotation.x1:
                annotation.x2 = x
            self._paintCanvas(False)
        elif self.action.get("name","") == 'selected_x1' or self.action.get("name","") == 'selected_x2':
            annotation = self.action.get("annotation")
            x = None
            for x,other in xx:
                if other == annotation:
                    continue
                break
            if x != None:
                xo = self.action.get("originx")
                if x < xo:
                    annotation.x1 = x
                    annotation.x2 = xo
                else:
                    annotation.x1 = xo
                    annotation.x2 = x
                self._paintCanvas(False)

    def button1Released(self, event):
        if self.rulerbutton.active.get() == False:
            return
        if self.action is None:
            return
        if self.action.get("name","") == 'selected_x1' or self.action.get("name","") == 'selected_x1':
            annotation = self.action.get("annotation")
            if annotation.x1 == annotation.x2:
                self.removeAnnotation(annotation)
                self._paintCanvas(False)
        else:
            self.action = None
        

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
        if len(self.annotations[seriesName].annotations) == 0:
            self.annotations.pop(seriesName)
            repaint = True
        if self.selectedAnnotation == annotation:
            self.setSelectedAnnotation(None)
            repaint = True
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
        self.contextPanel.setAnnotation(annotation)
           
        
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
            #print [(key,text[key].text) for key in text]
            setTo = None
            self.action = None
            if "move_x1" in text:
                setTo = text["move_x1"]
                self.action = {"name":"move_x1", "annotation":setTo}
            elif "move_x2" in text:
                print "action move x2"
                setTo = text["move_x2"]
                self.action = {"name":"move_x2", "annotation":setTo}
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
                a.text = "new"
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
            #series = self.selectedAnnotation.series
            #self.annotations[series] = self.annotations.get(series,[]) + [self.selectedAnnotation]
        self.selectedAnnotation = None
        self.paintCanvas()

    def deleteAnnotation(self, event):
        if self.selectedAnnotation is None:
            return
        seriesName = self.selectedAnnotation.series
        if not seriesName in self.annotations:
            return
        if not self.selectedAnnotation in self.annotations[seriesName].annotations:
            return
        self.annotations[seriesName].annotations.remove(self.selectedAnnotation)
        self.setSelectedAnnotation(None)
        self._paintCanvas()
        
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
        item3 = self.canvas.create_line(px1, py, px2, py, tags=tags, fill=color,arrow="both", width=width)
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
    
    def __init__(self, master):
        Tkinter.Frame.__init__(self, master=master)
        # Header:
        # Action, Name, Color, Show Series
        self.frame = ttk.Labelframe(self,text="Edit Series")
        self.frame.grid(row=0, column=0, sticky="NSEW")
        self.columnconfigure(0,weight=1)
        self.rowconfigure(0,weight=1)
        self.row = 0
        self.elements = {} # link to all elements of each series over series object
        for column, text in enumerate(["Name", "Color", "Show Series", "Action"]):
            h = ttk.Label(self.frame, text=text)
            h.grid(row=self.row, column=column)

        
    def addSeries(self, series):
        self.row += 1
        
        self.frame.columnconfigure(0,weight=1)
        self.frame.columnconfigure(1,weight=0)
        self.frame.columnconfigure(2,weight=0)
        self.frame.columnconfigure(3,weight=0)
        self.frame.rowconfigure(0,weight=1)
        
        varName = Tkinter.StringVar()
        entryName = Tkinter.Entry(self.frame, textvariable=varName)
        entryName.config(bg="white")
        entryName.grid(row=self.row, column=0, sticky="WE")
        varName.set(series.name)
        varName.trace("w", self.eventNameChanged)
        
        buttonColor = Tkinter.Button(self.frame, height=1, width=1)
        buttonColor.config(command=lambda x=buttonColor: self.getColor(x))
        buttonColor.grid(row=self.row, column=1)
        buttonColor.config(bg=series.color)
        buttonColor.config(activebackground=series.color)
        
        
        varShow = Tkinter.IntVar()
        checkShow = ttk.Checkbutton(self.frame, variable=varShow)
        checkShow.grid(row=self.row, column=2)
        if series.hidden == True:
            varShow.set(0)
        else:
            varShow.set(1)
            
        buttonDelete = Tkinter.Button(self.frame, text="Delete")
        buttonDelete.config(command=lambda x=series: self.deleteSeries(x))
        buttonDelete.grid(row=self.row, column=3)
                
        # add elements to list
        self.elements[series] = {}
        self.elements[series]["varName"] = varName
        self.elements[series]["entryName"] = entryName
        self.elements[series]["buttonColor"] = buttonColor
        self.elements[series]["varShow"] = varShow
        self.elements[series]["checkShow"] = checkShow
        self.elements[series]["buttonDelete"] = buttonDelete
        
        
    def deleteSeries(self, series):
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
        
    def getColor(self, button):
        #rgb, color = tkColorChooser.askcolor(button.cget("bg"))
        chooser = ColorChooser(self, button.cget("bg"))
        color = chooser.color
        if color != None:
            button.config(bg=color)
            button.config(activebackground=color)
        
    def eventNameChanged(self,*arg, **args):
        # check all entries for names which are not unique or empty
        # disable OK button if not unqiue
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
            self.master.bOk.config(state="normal")
        else:
            self.master.bOk.config(state="disabled")
    
class EditSeriesFrame(Tkinter.Toplevel):

    def __init__(self, master, framePlot):
        Tkinter.Toplevel.__init__(self, master=master)
        self.master = master
        self.framePlot = framePlot
        self.title("Edit Series")
        self.config(bg="#d9d9d9")
        self.columnconfigure(0,weight=1)
        self.columnconfigure(1,weight=0)
        self.columnconfigure(2,weight=0)
        self.rowconfigure(0,weight=0)
        self.rowconfigure(1,weight=1)

        self.lb = CheckboxList(self)
        self.lb.grid(row=0, column=0, columnspan=3, sticky="EW")
        
        for seriesName in self.framePlot.annotations:
            series = self.framePlot.annotations[seriesName]
            self.lb.addSeries(series)
            
        
        bAddSeries = Tkinter.Button(self, text="New Series", command=self.addEmptySeries)
        bAddSeries.grid(row=1, column=0, sticky="NW")
        
        bCancel = Tkinter.Button(self, text="Cancel", command=self.pressedCancel)
        bCancel.grid(row=1, column=2, sticky="NE")
        
        self.bOk = Tkinter.Button(self, text="OK", command=self.pressedOK)
        self.bOk.grid(row=1, column=1, sticky="NE")
        
        # lift window on top
        self.lift(master)
        self.transient(master)
        self.grab_set()
        
    def addEmptySeries(self):
        series = glyxtoolms.io.AnnotationSeries()
        series.name = ""
        series.color = "grey"
        self.lb.addSeries(series)
        self.lb.eventNameChanged()
        
    def pressedCancel(self):
        self.destroy()
        
    def pressedOK(self):
        # collect all series from lb
        #annotations = self.master.annotations.values()
        # generate new annotations dict
        newAnnotations = {}
        for series in self.lb.elements:
            content = self.lb.elements[series]
            series.name = content["varName"].get()
            for annotation in series.annotations:
                annotation.series = series.name
            series.color = content["buttonColor"].cget("bg")
            if content["varShow"].get() == True:
                series.hidden = False
            else:
                series.hidden = True
            newAnnotations[series.name] = series
            
        # replace annotations
        self.framePlot.annotations = newAnnotations
        self.destroy()
        self.framePlot._paintCanvas()
        self.master.eventSeriesEdited()
