import ttk
import Tkinter
import tkMessageBox
import random

import numpy as np

import glyxtoolms
from glyxtoolms.gui import AddIdentificationFrame


class NotebookFeature(ttk.Frame):

    def __init__(self, master, model):
        ttk.Frame.__init__(self, master=master)
        self.master = master
        self.model = model
        
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=0)
        self.rowconfigure(0,weight=0)
        self.rowconfigure(1,weight=1)

        self.aMenu = Tkinter.Menu(self, tearoff=0)


        # show treeview of mzML file MS/MS and MS
        # ------------------- Feature Tree ----------------------------#

        scrollbar = Tkinter.Scrollbar(self)
        self.featureTree = ttk.Treeview(self, yscrollcommand=scrollbar.set)
        
        self.columns = ("RT", "MZ", "Charge", "Best Score", "Nr Spectra", "Status", "Nr. Idents")
        self.columnsWidth = {"RT":60, "MZ":80, "Charge":80, "Best Score":80, "Nr Spectra":80, "Status":80, "Nr. Idents":80}
        self.columnNames = {"RT":"RT", "MZ":"MZ [Da]", "Charge":"Charge", "Best Score":"Best Score", "Nr Spectra":"Nr Spectra", "Status": "Status", "Nr. Idents":"Nr. Idents"}
        self.showColumns = {}
        for name in self.columns:
            self.showColumns[name] = Tkinter.BooleanVar()
            self.showColumns[name].set(True)
            self.showColumns[name].trace("w", self.columnVisibilityChanged)
        
        self.featureTree["columns"] = self.columns
        self.featureTree.column("#0", width=60)
        self.featureTree.heading("#0", text="Feature Nr",
                                 command=lambda col='#0': self.sortFeatureColumn(col))
        for col in self.columns:
            self.featureTree.column(col, width=self.columnsWidth[col])
            self.featureTree.heading(col,
                                     text=col,
                                     command=lambda col=col: self.sortFeatureColumn(col))

        self.setHeadingNames()

        button = Tkinter.Button(self,image=self.model.resources["filter"])
        button.grid(row=0, column=1)
        self.featureTree.grid(row=0, column=0, rowspan=2, sticky=("N", "W", "E", "S"))
        scrollbar.grid(row=1, column=1, sticky=("N", "W", "E", "S"))
        
        scrollbar.config(command=self.featureTree.yview)

        self.featureTreeIds = {}
        self.featureItems = {}

        # treeview style
        self.featureTree.tag_configure('oddUnknown', background='Moccasin')
        self.featureTree.tag_configure('evenUnknown', background='PeachPuff')
        
        self.featureTree.tag_configure('oddDeleted', background='LightSalmon')
        self.featureTree.tag_configure('evenDeleted', background='Salmon')
        
        self.featureTree.tag_configure('oddAccepted', background='PaleGreen')
        self.featureTree.tag_configure('evenAccepted', background='YellowGreen')
        
        self.featureTree.tag_configure('oddRejected', background='LightBlue')
        self.featureTree.tag_configure('evenRejected', background='SkyBlue')
        
        self.featureTree.bind("<<TreeviewSelect>>", self.clickedFeatureTree)
        self.featureTree.bind("a", lambda e: self.setStatus("Accepted"))
        self.featureTree.bind("u", lambda e: self.setStatus("Unknown"))
        self.featureTree.bind("r", lambda e: self.setStatus("Rejected"))
        self.featureTree.bind("z", self.zoomToFeature)
        self.featureTree.bind("<Control-Key-a>", self.selectAllFeatures)
        self.featureTree.bind("<Button-3>", self.popup)
        # Bindings influencing FeatureChromatogramView
        self.featureTree.bind("<Left>", self.goLeft)
        self.featureTree.bind("<Right>", self.goRight)
        
        self.model.registerClass("NotebookFeature",self)
        
    def setHeadingNames(self):
        
        if self.model.timescale == "minutes":
            self.columnNames["RT"] = "RT [min]"
        else:
            self.columnNames["RT"] = "RT [s]"

        for col in self.columnNames:
            self.featureTree.heading(col, text=self.columnNames.get(col, col))

    def columnVisibilityChanged(self, *arg, **args):
        header = []
        for columnname in self.columns:
            if self.showColumns[columnname].get() == True:
                header.append(columnname)
        self.featureTree["displaycolumns"] = tuple(header)
        space = self.grid_bbox(column=0, row=0, col2=0, row2=0)[2]
        width = space/(len(header)+1)
        rest = space%(len(header)+1)
        for column in ["#0"] + header:
            self.featureTree.column(column, width=width+rest)
            rest = 0

    def selectAllFeatures(self, event):
        items = self.featureTree.get_children()
        if len(items) == 0:
            return
        self.featureTree.selection_set(items)
        self.clickedFeatureTree(None)
    
    def popup(self, event):
        area = self.featureTree.identify_region(event.x, event.y)
        self.aMenu.delete(0,"end")
        if area == "nothing":
            return
        elif area == "heading" or area == "separator":
            for name in self.columns:
                self.aMenu.insert_checkbutton("end", label=name, onvalue=1, offvalue=0, variable=self.showColumns[name])
        else:
            self.aMenu.add_command(label="Set to Accepted", 
                                   command=lambda x="Accepted": self.setStatus(x))
            self.aMenu.add_command(label="Set to  Rejected",
                                   command=lambda x="Rejected": self.setStatus(x))
            self.aMenu.add_command(label="Set to Unknown",
                                   command=lambda x="Unknown": self.setStatus(x))
            self.aMenu.add_separator()
            self.aMenu.add_command(label="Change Feature",
                                   command=self.changeFeature)
            self.aMenu.add_command(label="Copy Feature",
                                   command=self.copyFeature)
            self.aMenu.add_command(label="Add Identification",
                                   command=self.addIdentification)
            self.aMenu.add_separator()
            self.aMenu.add_command(label="Copy to Clipboard",
                                   command=self.copyToClipboard)
        self.aMenu.post(event.x_root, event.y_root)
        self.aMenu.focus_set()
        self.aMenu.bind("<FocusOut>", self.removePopup)
        
    def removePopup(self,event):
        try: # catch bug in Tkinter with tkMessageBox. TODO: workaround
            if self.focus_get() != self.aMenu:
                self.aMenu.unpost()
        except:
            pass
            
    def copyToClipboard(self, *arg, **args):
        # get active columns
        header = ["Feature Nr"]
        active = []
        for columnname in self.columns:
            isActive = self.showColumns[columnname].get()
            active.append(isActive)
            if isActive == True:
                header.append(self.columnNames.get(columnname,columnname))
        
        # add header
        text = "\t".join(header) + "\n"
        for item in self.featureTree.selection():
            content = self.featureTree.item(item)
            line = []
            line.append(content["text"])
            for isActive,value in zip(active,content["values"]):
                if isActive:
                    line.append(str(value))
            text += "\t".join(line) + "\n"
        try:
            self.model.saveToClipboard(text)
            tkMessageBox.showinfo("Saved Table to Clipboard", "Table Data are saved to the Clipboard")
        except:
            tkMessageBox.showerror("Clipboard Error", "Cannot save Data to Clipboard.\nPlease select another clipboard method under Options!")
            raise
            
    def goLeft(self, event):
        self.model.classes["FeatureChromatogramView"].goLeft(event)
        return "break" # Stop default event propagation
        
    def goRight(self, event):
        self.model.classes["FeatureChromatogramView"].goRight(event)
        return "break" # Stop default event propagation
        
    def zoomToFeature(self, event):
        selection = self.featureTree.selection()
        if len(selection) != 1:
            return
        feature = self.featureTreeIds[selection[0]]
        minRT, maxRT, minMZ, maxMZ = feature.getBoundingBox()
        rtdiff = (maxRT-minRT)
        minRT = minRT-rtdiff
        maxRT = maxRT+rtdiff
        mzdiff = maxMZ-minMZ
        minMZ = minMZ-mzdiff*3
        maxMZ = maxMZ+mzdiff*3
        self.model.classes["TwoDView"].zoomToCoordinates(minRT, minMZ, maxRT, maxMZ)
            
    def setStatus(self, status):
        # get currently active hit
        selection = self.featureTree.selection()
        if len(selection) == 0:
            return
        for item in selection:
            feature = self.featureTreeIds[item]
            
            if status == "Accepted":
                feature.status = glyxtoolms.io.ConfirmationStatus.Accepted
            elif status == "Rejected":
                feature.status = glyxtoolms.io.ConfirmationStatus.Rejected
            elif status == "Unknown":
                feature.status = glyxtoolms.io.ConfirmationStatus.Unknown
            # Update on Treeview
            values = self.featureTree.item(item)["values"]
            values[5] = feature.status
            self.featureTree.item(item, values=values)
            
            taglist = list(self.featureTree.item(item, "tags"))
            taglist = self.setHighlightingTag(taglist, feature.status)
            self.featureTree.item(item, tags=taglist)
    
    def changeFeature(self):
        selection = self.featureTree.selection()
        if len(selection) != 1:
            return
        feature = self.featureTreeIds[selection[0]]
        ChangeFeatureFrame(self.master, self.model, feature)
        
    def copyFeature(self):
        analysis = self.model.currentAnalysis
        if analysis == None:
            return
        selection = self.featureTree.selection()
        if len(selection) != 1:
            return
        feature = self.featureTreeIds[selection[0]]
        new = feature.copy()
        # generate new feature id, check that id is unique
        while True:
            newid = "".join([str(random.randint(0,9)) for i in range(0,20)])
            found = False
            for feat in analysis.analysis.features:
                if newid == feat.id:
                    found = True
                    break
            if found == False:
                break
        new.id = newid
        new.annotations = []
        new.hits = []
        new.passesFilter = feature.passesFilter
        new.status = glyxtoolms.io.ConfirmationStatus.Unknown
        analysis.analysis.features.append(new)
        # update internal ids
        analysis.createFeatureIds()
        # collect specta within features
        analysis.collectFeatureSpectra()
        self.updateFeatureTree()
        self.model.classes["NotebookScoring"].updateTree([feature])
        tkMessageBox.showinfo("Feature Copied", "The feature has been copied!")
        
        
    def addIdentification(self):
        selection = self.featureTree.selection()
        if len(selection) != 1:
            return
        feature = self.featureTreeIds[selection[0]]
        AddIdentificationFrame.AddIdentificationFrame(self.master, self.model, feature)

    def sortFeatureColumn(self, col):

        if self.model == None or self.model.currentAnalysis == None:
            return
        sortingColumn, reverse = self.model.currentAnalysis.sorting["NotebookFeature"]
        if col == sortingColumn:
            reverse = not reverse
        else:
            sortingColumn = col
            reverse = False
        self.model.currentAnalysis.sorting["NotebookFeature"] = (sortingColumn, reverse)

        children = self.featureTree.get_children('')
        if col == "isGlycopeptide" or col == "Status":
            l = [(self.featureTree.set(k, col), k) for k in children]
        elif col == "Nr. Idents":
            l = [(int(self.featureTree.set(k, col)), k) for k in children]
        elif col == "#0":
            l = [(int(self.featureTree.item(k, "text")), k) for k in children]
        else:
            l = [(float(self.featureTree.set(k, col)), k) for k in children]

        l.sort(reverse=reverse)


        # rearrange items in sorted positions
        for index, (val, k) in enumerate(l):
            self.featureTree.move(k, '', index)
            status = self.featureTree.item(k)["values"][5]
            # adjust tags
            taglist = list(self.featureTree.item(k, "tags"))
            if "odd" in taglist:
                taglist.remove("odd")
            if "even" in taglist:
                taglist.remove("even")
            if index%2 == 0:
                taglist.append("even")
                taglist = self.setHighlightingTag(taglist, status)
            else:
                taglist.append("odd")
                taglist = self.setHighlightingTag(taglist, status)
            self.featureTree.item(k, tags=taglist)

    def setHighlightingTag(self, taglist, status):
        assert status in glyxtoolms.io.ConfirmationStatus._types
        for statustype in glyxtoolms.io.ConfirmationStatus._types:
            if "even"+statustype in taglist:
                taglist.remove("even"+statustype)
            if "odd"+statustype in taglist:
                taglist.remove("odd"+statustype)
        if "even" in taglist:
            taglist.append("even"+status)
        elif "odd" in taglist:
            taglist.append("odd"+status)
        else:
            raise Exception("Cannot find 'even' or 'odd' tag in taglist!")
        return taglist

    def updateFeatureTree(self):

        # clear tree
        self.featureTree.delete(*self.featureTree.get_children())
        self.featureTreeIds = {}
        self.setHeadingNames()
        project = self.model.currentProject

        if project == None:
            return

        if project.mzMLFile.exp == None:
            return

        analysis = self.model.currentAnalysis

        if analysis == None:
            return
            
        self.featureItems = {}

        # insert all ms2 spectra
        #("RT", "MZ", "Charge", "Best Score", "Nr Spectra")
        index = 0
        for feature in analysis.analysis.features:
            # check if hit passes filters
            if feature.passesFilter == False:
                continue

            if index%2 == 0:
                taglist = ("even" + feature.status, "even", )
            else:
                taglist = ("odd" + feature.status, "odd", )
            index += 1
            name = str(feature.index)
            bestScore = 10.0
            for specId in feature.getSpectraIds():
                spectrum = analysis.spectraIds[specId]
                if spectrum.logScore < bestScore:
                    bestScore = spectrum.logScore 

            if self.model.timescale == "minutes":
                rt = round(feature.getRT()/60.0, 2)
            else:
                rt = round(feature.getRT(), 1)

            item = self.featureTree.insert("", "end", text=name,
                                           values=(rt,
                                                   round(feature.getMZ(), 4),
                                                   feature.getCharge(),
                                                   round(bestScore, 2),
                                                   len(feature.getSpectraIds()),
                                                   feature.status,
                                                   len(feature.hits)),
                                           tags=taglist)
            self.featureTreeIds[item] = feature
            self.featureItems[feature.getId()] = item

        # apply possible sorting
        if not "NotebookFeature" in analysis.sorting:
            analysis.sorting["NotebookFeature"] = ("#0", False)
        
        sortingColumn, reverse = analysis.sorting["NotebookFeature"]
        analysis.sorting["NotebookFeature"] = (sortingColumn, not reverse)
        self.sortFeatureColumn(sortingColumn)

    def selectFeature(self, feature):
        item = self.featureItems.get(feature.getId(), False)
        if item == False:
            return
        self.featureTree.selection_set(item)
        self.featureTree.see(item)
        self.clickedFeatureTree(None)
        
    def updateFeature(self, feature):
        item = self.featureItems.get(feature.getId(), False)
        if item == False:
            return
        analysis = self.model.currentAnalysis
        if analysis == None:
            return
            
        if self.model.timescale == "minutes":
            rt = round(feature.getRT()/60.0, 2)
        else:
            rt = round(feature.getRT(), 1)
                
        bestScore = 10.0
        for specId in feature.getSpectraIds():
            spectrum = analysis.spectraIds[specId]
            if spectrum.logScore < bestScore:
                bestScore = spectrum.logScore
        self.featureTree.item(item,values=(rt,
                                           round(feature.getMZ(), 4),
                                           feature.getCharge(),
                                           round(bestScore, 2),
                                           len(feature.getSpectraIds()),
                                           feature.status,
                                           len(feature.hits)))
    
    def getSelectedFeatures(self):
        selection = self.featureTree.selection()
        features = []
        for item in selection:
            feature = self.featureTreeIds[item]
            features.append(feature)
        return features

    def clickedFeatureTree(self, event):
        # collect features and update IdentificationFrame
        features = self.getSelectedFeatures()
        self.model.classes["PeptideCoverageFrame"].init(None)
        self.model.classes["NotebookIdentification"].updateTree(features)
        self.model.classes["NotebookScoring"].updateTree(features)
        if "OxoniumIonPlot" in self.model.classes:
            self.model.classes["OxoniumIonPlot"].init(features=features)
        self.plotSelectedFeatures(features)
        
    def plotSelectedFeatures(self, features, hit=None):
        self.model.classes["TwoDView"].init(features, keepZoom=True)
        if len(features) != 1:
            self.model.classes["FeatureChromatogramView"].init(None, None, 0, 0, 0)
            self.model.classes["ConsensusSpectrumFrame"].init(None, hit)
            return
        feature = features[0]
        # calculate spectrum and chromatogram
        exp = self.model.currentProject.mzMLFile.exp
        minRT, maxRT, minMZ, maxMZ = feature.getBoundingBox()
        minMZView = minMZ -2
        maxMZView = maxMZ +2
        minRTView = minRT - 60
        maxRTView = maxRT - 60

        number = 10000
        base = np.linspace(minMZView, maxMZView, num=number)
        sumSpectra = np.zeros_like(base)
        bestSpectra = np.zeros_like(base)
        highestIntensity = 0
        c = glyxtoolms.gui.DataModel.Chromatogram()
        c.rt = []
        c.intensity = []
        highest = []

        for spec in self.model.currentAnalysis.featureSpectra[feature.getId()]:
            if spec.getMSLevel() != 1:
                continue
            rt = spec.getRT()
            c.rt.append(rt)
            
            peaks = spec.get_peaks()
            if hasattr(peaks, "shape"):
                mzArray = peaks[:, 0]
                intensArray = peaks[:, 1]
            else:
                mzArray, intensArray = peaks
                
            # get intensity in range
            choice_Chrom = np.logical_and(np.greater(mzArray, minMZ), np.less(mzArray, maxMZ))
            #choice_Chrom = np.logical_and(np.greater(mzArray, minMZ-0.1), np.less(mzArray, minMZ+0.1))
            arr_intens_Chrom = np.extract(choice_Chrom, intensArray)
            sumIntensity = arr_intens_Chrom.sum()
            c.intensity.append(sumIntensity)
            highest.append((sumIntensity, spec.getNativeID()))

        # find ms1 spectrum nearest to feature rt
        index = -1
        minDiff = None
        for spec in self.model.currentAnalysis.project.mzMLFile.exp:
            index += 1
            if spec.getMSLevel() != 1:
                continue
            diff = spec.getRT() - feature.rt
            if diff > 0:
                break
            if minDiff == None or abs(diff) < minDiff:
                minDiff = abs(diff)
            

        c.plot = True
        c.name = "test"
        c.rangeLow = minMZ
        c.rangeHigh = maxMZ
        c.msLevel = 1
        c.selected = True

        
        self.model.classes["FeatureChromatogramView"].init(c, feature, minMZView, maxMZView, index)
        self.model.classes["ConsensusSpectrumFrame"].init(feature, hit)

    def sortSpectrumColumn(self, col):
        if self.model == None or self.model.currentAnalysis == None:
            return
        sortingColumn, reverse = self.model.currentAnalysis.sorting["NotebookFeatureSpectra"]
        if col == sortingColumn:
            reverse = not reverse
        else:
            sortingColumn = col
            reverse = False
        self.model.currentAnalysis.sorting["NotebookFeatureSpectra"] = (sortingColumn, reverse)
        
        children = self.spectrumTree.get_children('')
        if col == "Is Glyco":
            l = [(self.spectrumTree.set(k, col), k) for k in children]
        elif col == "#0":
            l = [(int(self.spectrumTree.item(k, "text")), k) for k in children]
        else:
            l = [(float(self.spectrumTree.set(k, col)), k) for k in children]

        l.sort(reverse=reverse)


        # rearrange items in sorted positions
        for index, (val, k) in enumerate(l):
            self.spectrumTree.move(k, '', index)

            # adjust tags
            taglist = list(self.spectrumTree.item(k, "tags"))
            if "oddrowFeature" in taglist:
                taglist.remove("oddrowFeature")
            if "evenrowFeature" in taglist:
                taglist.remove("evenrowFeature")

            if index%2 == 0:
                taglist.append("evenrowFeature")
            else:
                taglist.append("oddrowFeature")
            self.spectrumTree.item(k, tags=taglist)


    def setSelectedFeature(self, index):
        for item in self.featureTreeIds:
            if index == self.featureTreeIds[item].index:
                self.featureTree.selection_set(item)
                self.featureTree.see(item)
                break

    def deleteFeature(self, event):

        #updateFeatureTree
        selection = self.featureTree.selection()
        if len(selection) == 0:
            return
        for item in selection:

            feature = self.featureTreeIds[item]
            nextItem = self.featureTree.next(item)
            self.featureTree.delete(item)
            self.featureTreeIds.pop(item)
            self.featureItems.pop(feature.getId())
            
            if nextItem != {}:
                self.featureTree.selection_set(nextItem)
                self.featureTree.see(nextItem)
            elif len(self.featureTree.get_children('')) > 0:
                nextItem = self.featureTree.get_children('')[-1]
                self.featureTree.selection_set(nextItem)
                self.featureTree.see(nextItem)

            # remove feature from analysis file
            analysis = self.model.currentAnalysis
            analysis.removeFeature(feature)
        
        self.model.classes["NotebookIdentification"].updateTree()

        # adjust tags
        for index, k in enumerate(self.featureTree.get_children('')):            
            taglist = list(self.featureTree.item(k, "tags"))
            status = self.featureTree.item(k)["values"][5]
            if "odd" in taglist:
                taglist.remove("odd")
            if "even" in taglist:
                taglist.remove("even")
            if index%2 == 0:
                taglist.append("even")
                taglist = self.setHighlightingTag(taglist, status)
            else:
                taglist.append("odd")
                taglist = self.setHighlightingTag(taglist, status)
            self.featureTree.item(k, tags=taglist)


class ChangeFeatureFrame(Tkinter.Toplevel):

    def __init__(self, master, model, feature):
        Tkinter.Toplevel.__init__(self, master=master)
        #self.minsize(600, 300)
        self.master = master
        self.feature = feature
        self.title("Change Feature")
        self.config(bg="#d9d9d9")
        self.model = model
        self.mass = 0
        self.charge = 0
        
        labelCharge = Tkinter.Label(self, text="Charge")
        self.chargeVar = Tkinter.StringVar()
        self.chargeVar.trace("w", self.valuesChanged)
        self.entryCharge = Tkinter.Entry(self, textvariable=self.chargeVar)
        labelCharge.grid(row=0, column=0, sticky="NWES")
        self.entryCharge.grid(row=0, column=1, columnspan=2, sticky="NWES")
        
        labelMass = Tkinter.Label(self, text="Mass")
        self.massVar = Tkinter.StringVar()
        self.massVar.trace("w", self.valuesChanged)
        self.entryMass = Tkinter.Entry(self, textvariable=self.massVar)
        labelMass.grid(row=1, column=0, sticky="NWES")
        self.entryMass.grid(row=1, column=1, columnspan=2, sticky="NWES")
        
        cancelButton = Tkinter.Button(self, text="Cancel", command=self.cancel)        
        saveButton = Tkinter.Button(self, text="Save", command=self.save)

        cancelButton.grid(row=10, column=0, sticky="NWES")
        saveButton.grid(row=10, column=1, sticky="NWES")
        
        # set values
        self.chargeVar.set(feature.getCharge())
        self.massVar.set(feature.getMZ())
        
        # get window size
        self.update()
        h = self.winfo_height()
        w = self.winfo_width()

        # get screen width and height
        ws = master.winfo_screenwidth() # width of the screen
        hs = master.winfo_screenheight() # height of the screen

        # calculate x and y coordinates for the Tk window
        x = (ws/2) - (w/2)
        y = (hs/2) - (h/2)
        # set the dimensions of the screen 
        # and where it is placed
        self.geometry('%dx%d+%d+%d' % (w, h, x, y))
                                                   
        
    def valuesChanged(self, *args):
        # check entries for validity
        self.valid = True
        try:
            self.charge = int(self.chargeVar.get())
            self.entryCharge.config(bg="grey")
        except:
            self.valid = False
            self.entryCharge.config(bg="red")
            
        try:
            self.mass = float(self.massVar.get())
            self.entryMass.config(bg="grey")
        except:
            self.valid = False
            self.entryMass.config(bg="red")
    
    def save(self):
        if self.valid == False:
            return
        self.feature.setCharge(self.charge)
        self.feature.setMZ(self.mass)
        self.destroy()
        self.model.currentAnalysis.featureEdited(self.feature)
        #self.model.classes["NotebookFeature"].updateFeatureTree()

    def cancel(self):
        self.destroy()
 
