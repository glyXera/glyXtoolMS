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

    def __init__(self, master, model, xTitle="", yTitle=""):
        FramePlot.FramePlot.__init__(self, master, model, xTitle=xTitle,
                                     yTitle=yTitle)

        self.master = master
        self.peaksByItem = {}
        self.annotations = {}
        self.series = {}
        self.annotationItems = {}
        self.selectedAnnotation = None
        self.mouseOverAnnotation = None

        # create popup menu
        self.aMenu = Tkinter.Menu(self, tearoff=0)

        self.canvas.bind("<Button-1>", self.button1Pressed, "+")
        self.canvas.bind("<ButtonRelease-1>", self.button1Released, "+")
        self.canvas.bind("<B1-Motion>", self.button1Motion, "+")
        self.canvas.bind("<Motion>", self.mouseMoveEvent, "+")
        self.canvas.bind("<Button-3>", self.button3Pressed, "+")
        self.canvas.bind("<Control-p>", self.getPattern, "+")

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

    def getPattern(self, event):
        if self.model.currentAnalysis == None:
            return
        if self.action is not None:
            return

        # search after pattern
        pattern = {}
        pattern["pep"] = 0.0
        pattern["-NH3"] = -glyxtoolms.masses.MASS["N"] - 3*glyxtoolms.masses.MASS["H"]
        pattern["+N83"] = glyxtoolms.masses.calcMassFromElements({"C":4, "H":5, "N":1, "O":1})
        pattern["+HEXNAC"] = glyxtoolms.masses.GLYCAN["HEXNAC"]

        tolerance = 0.1
        all_patterns = []
        for i1 in self.peaksByItem:
            this_pattern = {}
            start = self.peaksByItem[i1]
            for i2 in self.peaksByItem:
                peak = self.peaksByItem[i2]
                diff = peak.x - start.x
                for key in pattern:
                    error = pattern[key] - diff
                    if abs(error) <= tolerance:
                        if not key in this_pattern or peak.y > this_pattern[key]:
                            this_pattern[key] = peak
            if len(this_pattern) > 1:
                intensity = sum([this_pattern[key].y for key in this_pattern])
                all_patterns.append((len(this_pattern),intensity,this_pattern))
        all_patterns = sorted(all_patterns, key=lambda x: (x[0],x[1]), reverse=True)
        # sort pattern after intensity
        if len(all_patterns) > 5:
            all_patterns = all_patterns[:5]
        print all_patterns

        i = 0
        for length, intensity, pattern in all_patterns:
            i += 1
            seriesname = "pattern"+str(i)
            for key in pattern:
                if key == "pep":
                    continue
                x1 = pattern["pep"].x
                x2 = pattern[key].x
                if x2 < x1:
                    x1,x2 = x2,x1

                # create new annotation
                a = glyxtoolms.io.Annotation()
                a.x1 = x1
                a.x2 = x2
                a.text = key
                a.y = 0
                self.addAnnotation(a, seriesname)
        self._paintCanvas(False)

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

    def initCanvas(self, keepZoom=False):
        super(AnnotatedPlot, self).initCanvas(keepZoom)
        if self.rulerbutton.active.get() == True:
            #self.sidepanel.panels["ruler"].currentAnnotation = None
            self.sidepanel.panels["ruler"].update()

    def rulerToggled(self, *arg, **args):
        if self.rulerbutton.active.get() == False:
            self.setSelectedAnnotation(None)
            self._paintCanvas()
        else:
            self.sidepanel.panels["ruler"].update()

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

    def removePopup(self,event):
        try: # catch bug in Tkinter with tkMessageBox. TODO: workaround
            if self.focus_get() != self.aMenu:
                self.aMenu.unpost()
        except:
            pass # Brrrr

    def button3Pressed(self, event):

        def defineNewAnnotation(x1, x2, annotation=None):
            # create new annotation
            a = glyxtoolms.io.Annotation()
            if x1 > x2:
                x1,x2 = x2,x1
            a.x1 = x1
            a.x2 = x2
            a.text = ""
            a.y = 0
            if annotation == None:
                # choose a default name series1, series2, etc
                i = 1
                while True:
                    seriesName = "series"+str(i)
                    if not seriesName in self.annotations:
                        break
                    i += 1
            else:
                seriesName = annotation.series
            self.addAnnotation(a, seriesName)
            self.setSelectedAnnotation(a)
            self._paintCanvas()

        def searchMassDifference(mass, tolerance, annotation): # TODO get tolerance from user/analysis
            # get series charge
            if annotation == None:
                chargeGoal = 0
            else:
                chargeGoal = self.annotations[annotation.series].charge
            hits = {}
            for peak in self.peaksByItem.values():
                diff = peak.x - mass
                for goal, name, charge,typ in self.model.massdifferences:
                    if chargeGoal != 0 and chargeGoal != charge:
                        continue
                    error = abs(abs(diff)-goal)
                    if error < tolerance:
                        if diff < 0:
                            sign = "-"
                        else:
                            sign = "+"
                        hits[sign] = hits.get(sign, []) + [(error, charge, peak, name)]
            for sign in hits:
                hits[sign] = sorted(hits[sign], key=lambda x: (x[0],x[1]))
            if len(hits) == 0:
                return
            self.aMenu.delete(0,"end")

            for error, charge, peak, name in hits.get("-",[]):
                self.aMenu.add_command(label="-"+name + " :" + str(round(error,4))+" Da ("+str(charge) + "+)",
                                       command=lambda x1=mass,x2=peak.x: defineNewAnnotation(x1,x2,annotation))
            self.aMenu.add_separator()
            for error, charge, peak, name in hits.get("+",[]):
                self.aMenu.add_command(label="+"+name + " :" + str(round(error,4))+" Da ("+str(charge) + "+)",
                                       command=lambda x1=mass,x2=peak.x: defineNewAnnotation(x1,x2,annotation))

            # post menu above cursor
            self.aMenu.post(event.x_root, event.y_root - self.aMenu.yposition("end"))
            self.aMenu.focus_set()
            self.aMenu.bind("<FocusOut>", self.removePopup)

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
            annotation = None
            if "selected_x1" in text:
                annotation = text["selected_x1"]
                mass = annotation.x1
            elif "selected_x2" in text:
                annotation = text["selected_x2"]
                mass = annotation.x2
            if annotation != None:
                searchMassDifference(mass, 0.1, annotation)

        if len(annotatableItems) > 0:
            # select nearest annotatable
            nearest = []
            for item in annotatableItems:
                annotatable = self.peaksByItem[item]
                dist = abs(self.convAtoX(annotatable.x)-event.x)
                nearest.append((dist, annotatable))
            nearest = nearest[0][1]
            searchMassDifference(nearest.x, 0.1, None)


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

        # get annotation text
        if annotation.show == "text":
            annotationText = annotation.text
        elif annotation.show == "lookup":
            #annotationText = annotation.lookup
            string = self.doMassDifferenceLookup(annotation)
            annotationText = string
        elif annotation.show == "mass":
            mass = round(abs(annotation.x1-annotation.x2),4)
            annotationText = str(mass)
        else:
            annotationText = ""

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
                               text=annotationText,
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

    def doMassDifferenceLookup(self, annotation):
        tolerance = 0.1 # Todo: Fix tolerance
        massdifference = abs(annotation.x1-annotation.x2)
        charge = self.annotations[annotation.series].charge
        string = []
        for mass, key, charge2, typ in self.model.massdifferences:
            if charge != 0 and charge != charge2:
                continue
            error = abs(mass-massdifference)
            if abs(mass-massdifference) <= tolerance:
                string.append((error, key))
        string = sorted(string)
        return "; ".join([s for e,s in string])

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

    def __init__(self, master, annotationspanel, framePlot):
        Tkinter.Frame.__init__(self, master=master)
        self.columnconfigure(0,weight=1)
        self.rowconfigure(0,weight=1)
        # Header:
        # Action, Name, Color, Show Series
        self.frame = Tkinter.LabelFrame(self,text="Edit Series")
        self.frame.grid(row=0, column=0, sticky="NSEW")
        self.framePlot = framePlot
        self.annotationspanel = annotationspanel


        self.frame.columnconfigure(0,weight=1, minsize=100) # 121
        self.frame.columnconfigure(1,weight=0, minsize=22) # 22
        self.frame.columnconfigure(2,weight=0, minsize=22) # 22
        self.frame.columnconfigure(3,weight=0, minsize=27) # 27
        self.frame.columnconfigure(4,weight=0, minsize=20) # 20
        self.frame.rowconfigure(0,weight=1)

        self.row = 0
        self.elements = {} # link to all elements of each series over series object

        eye_icon = 'R0lGODlhDAAIAIAAAAAAAAAAACH+EUNyZWF0ZWQgd2l0aCBHSU1QACH5BAEKAAEALAAAAAAMAAgA\nAAIUjIFpC9fx4JkyPhthbnlJ6nWJYhQAOw==\n'
        photo = Tkinter.PhotoImage(data=eye_icon)
        h1 = Tkinter.Label(self.frame, text="Name")
        h1.grid(row=self.row, column=0)
        h2 = Tkinter.Label(self.frame, text="z")
        h2.grid(row=self.row, column=1)
        h3 = Tkinter.Label(self.frame, text="Color")
        h3.grid(row=self.row, column=2)
        h4 = Tkinter.Label(self.frame, image=photo, width=10, height=10)
        h4.image = photo
        h4.grid(row=self.row, column=3)

    def clear(self):
        for series in self.elements:
            self.elements[series]["entryName"].destroy()
            self.elements[series]["entryCharge"].destroy()
            self.elements[series]["buttonColor"].destroy()
            self.elements[series]["checkShow"].destroy()
            self.elements[series]["buttonDelete"].destroy()
        self.elements = {}
        self.row = 0

    def addSeries(self, series):
        self.row += 1
        varName = Tkinter.StringVar()
        entryName = Tkinter.Entry(self.frame, textvariable=varName, width=10)
        entryName.config(bg="white")
        entryName.grid(row=self.row, column=0, sticky="WE")
        varName.set(series.name)
        varName.trace("w", lambda name, index, mode,x=series:self.eventNameChanged(x))

        varCharge = Tkinter.StringVar()
        entryCharge = Tkinter.Entry(self.frame, textvariable=varCharge, width=2)
        entryCharge.grid(row=self.row, column=1)
        entryCharge.config(bg="white")
        varCharge.set(series.charge)
        varCharge.trace("w", lambda name, index, mode,x=series:self.eventChargeChanged(x))

        buttonColor = Tkinter.Button(self.frame, text=" ", padx=6, pady=1)
        buttonColor.config(command=lambda b=buttonColor, s=series: self.eventSetColor(b,series))
        buttonColor.grid(row=self.row, column=2)
        buttonColor.config(bg=series.color)
        buttonColor.config(activebackground=series.color)

        varShow = Tkinter.IntVar()
        checkShow = Tkinter.Checkbutton(self.frame, variable=varShow)
        checkShow.grid(row=self.row, column=3)
        if series.hidden == True:
            varShow.set(0)
        else:
            varShow.set(1)

        varShow.trace("w", lambda name, index, mode,s=series, var=varShow:self.eventSetVisibility(s,var))

        buttonDelete = Tkinter.Button(self.frame, text="X", padx=3, pady=0)
        buttonDelete.config(command=lambda x=series: self.eventDeleteSeries(x))
        buttonDelete.grid(row=self.row, column=4)

        # add elements to list
        self.elements[series] = {}
        self.elements[series]["varName"] = varName
        self.elements[series]["entryName"] = entryName
        self.elements[series]["varCharge"] = varCharge
        self.elements[series]["entryCharge"] = entryCharge
        self.elements[series]["buttonColor"] = buttonColor
        self.elements[series]["varShow"] = varShow
        self.elements[series]["checkShow"] = checkShow
        self.elements[series]["buttonDelete"] = buttonDelete


    def eventSetVisibility(self, series, var):
        if series.hidden  == var.get():
            series.hidden = not series.hidden
            if series.hidden == True and self.annotationspanel.currentAnnotation != None:
                if self.annotationspanel.currentAnnotation.series == series.name:
                    self.annotationspanel.setAnnotation(None)
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
        self.elements[series]["entryCharge"].destroy()
        self.elements[series]["buttonColor"].destroy()
        self.elements[series]["checkShow"].destroy()
        self.elements[series]["buttonDelete"].destroy()
        self.elements.pop(series)
        self.framePlot.annotations.pop(series.name)
        if self.annotationspanel.currentAnnotation in series.annotations:
            self.annotationspanel.setAnnotation(None)
        self.annotationspanel.update()
        self.framePlot._paintCanvas()

    def eventSetColor(self, button, series):
        chooser = ColorChooser(self, button.cget("bg"))
        color = chooser.color
        if color != None and series.color != color:
            button.config(bg=color)
            button.config(activebackground=color)
            series.color=color
            self.annotationspanel.update()
            self.framePlot._paintCanvas()

    def eventChargeChanged(self,changedSeries):
        varCharge = self.elements[changedSeries]["varCharge"]
        entryCharge = self.elements[changedSeries]["entryCharge"]
        try:
            value = int(varCharge.get())
            changedSeries.charge = value
            entryCharge.config(bg="white")
            self.annotationspanel.updateAnnotationMasses()
            self.framePlot._paintCanvas()
        except:
            entryCharge.config(bg="red")


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
                self.annotationspanel.setAnnotation(self.annotationspanel.currentAnnotation)



class AnnotationSidePanel(Tkinter.Frame, object):
    def __init__(self, master, framePlot):
        Tkinter.Frame.__init__(self, master=master)
        self.master = master
        self.framePlot = framePlot

        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)

        self.scrollbar = Tkinter.Scrollbar(self)
        self.scrollbar.grid(row=0, column=1, sticky="WNS")
        self.canvas = Tkinter.Canvas(self, yscrollcommand=self.scrollbar.set)
        self.canvas.config(highlightthickness=0)
        #self.canvas.grid(row=0, column=0, sticky="NSWE")
        self.canvas.grid(row=0, column=0, rowspan=2, sticky="NSWE")

        self.frame = Tkinter.Frame(self.canvas)
        self.canvas.create_window(0, 0, anchor="nw", window=self.frame)

        self.scrollbar.config(command=self.canvas.yview)

        self.empty = Tkinter.Canvas(self, width=10, height=0)
        self.empty.grid(row=1, column=1, sticky="WNS")
        self.empty.config(highlightthickness=0)

        self.frame.columnconfigure(1,weight=1)
        self.frame.rowconfigure(0,weight=0)
        self.frame.rowconfigure(1,weight=1)
        self.frame.rowconfigure(2,weight=1)

        self.canvas.bind("<Configure>", self.on_resize, "+")
        self.frame.bind("<Configure>", self.on_resize, "+")

        self.frameTools = Tkinter.LabelFrame(self.frame,text="Annotation Tools")
        self.frameTools.grid(row=0,column=0, sticky="NEW", padx=2)
        self.buttonTools = Tkinter.Button(self.frameTools, text="Tools", command=self.openTools)
        self.buttonTools.grid(row=0,column=0, padx=4, sticky="NESW")

        self.frameAnnotation = Tkinter.LabelFrame(self.frame,text="Current Annotation")
        self.frameAnnotation.grid(row=1,column=0, sticky="NEW", padx=2)

        self.annotationContent = Tkinter.Frame(self.frameAnnotation)
        self.annotationContent.grid(row=0,column=0, sticky="NSEW")
        self.annotationContent.columnconfigure(0,weight=0)
        self.annotationContent.columnconfigure(1,weight=1)
        self.annotationContent.rowconfigure(0,weight=0)
        self.annotationContent.rowconfigure(1,weight=0)
        self.annotationContent.rowconfigure(2,weight=0)
        self.annotationContent.rowconfigure(3,weight=1)

        self.buttonDelete = Tkinter.Button(self.annotationContent, text="Delete  Annotation",command=self.deleteAnnotation)
        self.buttonDelete.grid(row=0,column=0,columnspan=2, padx=4, sticky="NESW")

        labelMassText1 = Tkinter.Label(self.annotationContent, text="m1")
        labelMassText1.grid(row=1,column=0, sticky="NSEW")
        self.labelMass1 = Tkinter.Label(self.annotationContent, text=" - Da", anchor="e")
        self.labelMass1.grid(row=1,column=1, padx=4, sticky="NSEW")

        labelMassText2 = Tkinter.Label(self.annotationContent, text="m2")
        labelMassText2.grid(row=2,column=0, sticky="NSEW")
        self.labelMass2 = Tkinter.Label(self.annotationContent, text=" - Da", anchor="e")
        self.labelMass2.grid(row=2,column=1, padx=4, sticky="NSEW")

        radioFrame = Tkinter.LabelFrame(self.annotationContent, text="Annotate with")
        radioFrame.grid(row=3,column=0, columnspan=2, padx=2)

        self.varRadio = Tkinter.StringVar()
        self.varRadio.trace("w", self.radioGroupChanged)

        self.buttonShowDiff = Tkinter.Radiobutton(radioFrame, text="Diff", variable=self.varRadio, value="mass")
        self.buttonShowDiff.grid(row=0,column=0, sticky="NWS")

        self.varMass = Tkinter.StringVar()
        self.entryMass= Tkinter.Entry(radioFrame, textvariable=self.varMass, width=14)
        self.entryMass.grid(row=0,column=1, padx=4, sticky="NSEW")
        self.entryMass.config(justify="right")

        self.buttonShowLookup = Tkinter.Radiobutton(radioFrame, text="Lookup", variable=self.varRadio, value="lookup")
        self.buttonShowLookup.grid(row=1,column=0, sticky="NWS")

        self.varLookup = Tkinter.StringVar()
        self.entryLookup= Tkinter.Entry(radioFrame, textvariable=self.varLookup ,width=14)
        self.entryLookup.grid(row=1,column=1, padx=4, sticky="NWES")

        self.buttonShowText = Tkinter.Radiobutton(radioFrame, text="Text", variable=self.varRadio, value="text")
        self.buttonShowText.grid(row=2,column=0, sticky="NWS")

        self.buttonShowNone = Tkinter.Radiobutton(radioFrame, text="None", variable=self.varRadio, value="none")
        self.buttonShowNone.grid(row=3,column=0, sticky="NWS")

        self.varText = Tkinter.StringVar()
        self.entryText = Tkinter.Entry(radioFrame, textvariable=self.varText ,width=14)
        self.entryText.config(bg="white")
        self.entryText.grid(row=2,column=1, padx=4, sticky="NWES")

        self.entryLookup.config(state="readonly")
        self.entryMass.config(state="readonly")

        labelSeries = Tkinter.Label(self.annotationContent, text="Series")
        labelSeries.grid(row=8,column=0, padx=2)

        self.varSeries = Tkinter.StringVar()
        self.mb = Tkinter.Menubutton(self.annotationContent, text=u" \u25BC",
                             relief="raised", anchor="e")
        self.mb.menu = Tkinter.Menu(self.mb, tearoff=0)
        self.mb['menu'] = self.mb.menu
        self.mb.grid(row=8,column=1, padx=4, pady=4, sticky="NESW")

        self.varText.trace("w", self.eventTextChanged)
        self.varSeries.trace("w", self.eventSeriesChanged)

        self.frameSeries = CheckboxList(self.frame, self, self.framePlot)
        self.frameSeries.grid(row=2,column=0, sticky="SEW", padx=2)
        self.setAnnotation(None)

    def openTools(self):
        frame = AnnotationToolsFrame(self.master)

    def radioGroupChanged(self, *arg, **args):
        if self.currentAnnotation == None:
            self.entryText.config(state="disabled")
            self.entryLookup.config(state="disabled")
            self.entryMass.config(state="disabled")
            return

        self.entryLookup.config(state="readonly")
        self.entryMass.config(state="readonly")
        self.currentAnnotation.show = self.varRadio.get()
        if self.currentAnnotation.show == "text":
            self.entryText.config(state="normal")
        else:
            self.entryText.config(state="disabled")
        self.framePlot._paintCanvas()

    def on_resize(self,event):
        self.frame.update_idletasks()
        size = self.canvas.bbox("all")
        self.empty.config(height=event.height -size[3])
        self.canvas.config(height=size[3], width=size[2])
        self.canvas.config(scrollregion=size)

    def deleteAnnotation(self):
        if self.currentAnnotation == None:
            return
        self.framePlot.removeAnnotation(self.currentAnnotation)

    def update(self):
        self.currentAnnotation = None
        self.frameSeries.clear()
        for seriesName in self.framePlot.annotations:
            series = self.framePlot.annotations[seriesName]
            self.frameSeries.addSeries(series)
        self.buildMenu()

    def updateAnnotationMasses(self):
        if self.currentAnnotation == None:
            self.labelMass1.config(text=" - Da")
            self.labelMass2.config(text=" - Da")
            self.varMass.set("- Da")
            self.varLookup.set("")
        else:
            m1 = str(round(self.currentAnnotation.x1,4))
            m2 = str(round(self.currentAnnotation.x2,4))
            m3 = str(round(self.currentAnnotation.x2-self.currentAnnotation.x1,4))
            self.labelMass1.config(text= m1 + " Da")
            self.labelMass2.config(text= m2 + " Da")
            self.varMass.set(m3 + " Da")
            string = self.framePlot.doMassDifferenceLookup(self.currentAnnotation)
            self.currentAnnotation.lookup = string
            self.varLookup.set(string)
            if self.currentAnnotation.valid == True:
                self.entryMass.config(fg="black")
            else:
                self.entryMass.config(fg="red")

    def setAnnotation(self, annotation):
        self.currentAnnotation = annotation

        if annotation == None:
            self.mb.config(text="Series"+u" \u25BC")
            self.mb.config(state="disabled")
            self.buttonDelete.config(state="disabled")

            self.buttonShowDiff.config(state="disabled")
            self.buttonShowLookup.config(state="disabled")
            self.buttonShowText.config(state="disabled")
            self.buttonShowNone.config(state="disabled")

            self.entryMass.config(state="disabled")
            self.varText.set("")
            self.varMass.set("- Da")
            self.varLookup.set("")
            self.entryText.config(state="disabled")
            self.entryLookup.config(state="disabled")

        else:
            self.mb.config(state="normal")
            self.buttonDelete.config(state="normal")

            self.buttonShowDiff.config(state="normal")
            self.buttonShowLookup.config(state="normal")
            self.buttonShowText.config(state="normal")
            self.buttonShowNone.config(state="normal")

            self.varRadio.set(annotation.show)
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
        #if self.currentAnnotation.series not in self.framePlot.annotations:
        #    self.currentAnnotation = None
        #    return
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


class AnnotationToolsFrame(Tkinter.Toplevel):

    def __init__(self, master):
        Tkinter.Toplevel.__init__(self, master=master)
        self.master = master
        self.title("Annotation tools")
        self.config(bg="#d9d9d9")
