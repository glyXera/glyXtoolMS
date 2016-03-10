import ttk
import Tkinter
import tkMessageBox
import random

import numpy as np

import glyxsuite


class NotebookFeature(ttk.Frame):

    def __init__(self, master, model):
        ttk.Frame.__init__(self, master=master)
        self.master = master
        self.model = model
        
        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=0)
        self.columnconfigure(0, weight=1)
        
        frameFeature = ttk.Labelframe(self, text="Features")
        frameFeature.grid(row=0, column=0, sticky=("N", "W", "E", "S"))
        frameFeature.rowconfigure(0, weight=1)
        frameFeature.columnconfigure(0, weight=1)
        frameFeature.columnconfigure(1, weight=0)

        frameSpectrum = ttk.Labelframe(self, text="Featurespectra")
        frameSpectrum.grid(row=1, column=0, sticky=("N", "W", "E", "S"))
        frameSpectrum.columnconfigure(0, weight=1)
        frameSpectrum.columnconfigure(1, weight=0)
        
        self.aMenu = Tkinter.Menu(self, tearoff=0)
        self.aMenu.add_command(label="Accepted", 
                               command=lambda x="Accepted": self.setStatus(x))
        self.aMenu.add_command(label="Rejected",
                               command=lambda x="Rejected": self.setStatus(x))
        self.aMenu.add_command(label="Unknown",
                               command=lambda x="Unknown": self.setStatus(x))
        self.aMenu.add_command(label="Change Feature",
                               command=self.changeFeature)
        self.aMenu.add_command(label="Copy Feature",
                               command=self.copyFeature)
        self.aMenu.add_command(label="Add Identification",
                               command=self.addIdentification)
                                                      
                               
                               

        # show treeview of mzML file MS/MS and MS
        # ------------------- Feature Tree ----------------------------#

        scrollbar = Tkinter.Scrollbar(frameFeature)
        self.featureTree = ttk.Treeview(frameFeature, yscrollcommand=scrollbar.set)

        columns = ("RT", "MZ", "Charge", "Best Score", "Nr Spectra", "Status", "Nr. Idents")
        self.featureTree["columns"] = columns
        self.featureTree.column("#0", width=60)
        self.featureTree.heading("#0", text="Feature",
                                 command=lambda col='#0': self.sortFeatureColumn(col))
        for col in columns:
            self.featureTree.column(col, width=80)
            self.featureTree.heading(col,
                                     text=col,
                                     command=lambda col=col: self.sortFeatureColumn(col))

        self.featureTree.grid(row=0, column=0, sticky=("N", "W", "E", "S"))

        scrollbar.grid(row=0, column=1, sticky=("N", "W", "E", "S"))
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
        self.featureTree.bind("<Button-3>", self.popup)
        # Bindings influencing FeatureChromatogramView
        self.featureTree.bind("<Left>", self.goLeft)
        self.featureTree.bind("<Right>", self.goRight)

        self.model.classes["NotebookFeature"] = self

        # ------------------- Spectrum Tree ---------------------------#
        self.spectrumTreeIds = {}

        scrollbar = Tkinter.Scrollbar(frameSpectrum)
        self.spectrumTree = ttk.Treeview(frameSpectrum, yscrollcommand=scrollbar.set)
        columns = ("RT", "Mass", "Charge", "Score", "Is Glyco")
        self.spectrumTree["columns"] = columns
        self.spectrumTree.column("#0", width=100)
        self.spectrumTree.heading("#0",
                                  text="Spectrum Nr.",
                                  command=lambda col='#0': self.sortSpectrumColumn(col))
        for col in columns:
            self.spectrumTree.column(col, width=80)
            self.spectrumTree.heading(col, text=col,
                                      command=lambda col=col: self.sortSpectrumColumn(col))

        self.spectrumTree.grid(row=0, column=0, sticky=("N", "W", "E", "S"))
        scrollbar.grid(row=0, column=1, sticky=("N", "W", "E", "S"))

        scrollbar.config(command=self.spectrumTree.yview)
        self.spectrumTree.bind("<<TreeviewSelect>>", self.clickedSpectrumTree)
    
    def popup(self, event):
        self.aMenu.post(event.x_root, event.y_root)
        self.aMenu.focus_set()
        self.aMenu.bind("<FocusOut>", self.removePopup)
        
    def removePopup(self,event):
        try: # catch bug in Tkinter with tkMessageBox. TODO: workaround
            if self.focus_get() != self.aMenu:
                self.aMenu.unpost()
        except:
            pass
            
    def goLeft(self, event):
        self.model.classes["FeatureChromatogramView"].goLeft(event)
        return "break" # Stop default event propagation
        
    def goRight(self, event):
        self.model.classes["FeatureChromatogramView"].goRight(event)
        return "break" # Stop default event propagation
            
    def setStatus(self, status):
        # get currently active hit
        selection = self.featureTree.selection()
        if len(selection) == 0:
            return
        for item in selection:
            feature = self.featureTreeIds[item]
            
            if status == "Accepted":
                feature.status = glyxsuite.io.ConfirmationStatus.Accepted
            elif status == "Rejected":
                feature.status = glyxsuite.io.ConfirmationStatus.Rejected
            elif status == "Unknown":
                feature.status = glyxsuite.io.ConfirmationStatus.Unknown
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
        new.status = glyxsuite.io.ConfirmationStatus.Unknown
        analysis.analysis.features.append(new)
        # update internal ids
        analysis.createFeatureIds()
        # collect specta within features
        analysis.collectFeatureSpectra()
        self.updateFeatureTree()
        self.model.classes["NotebookScoring"].updateTree()
        tkMessageBox.showinfo("Feature Copied", "The feature has been copied!")
        
        
    def addIdentification(self):
        selection = self.featureTree.selection()
        if len(selection) != 1:
            return
        feature = self.featureTreeIds[selection[0]]
        AddIdentificationFrame(self.master, self.model, feature)

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
        assert status in glyxsuite.io.ConfirmationStatus._types
        for statustype in glyxsuite.io.ConfirmationStatus._types:
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
        

    def clickedFeatureTree(self, event):
        selection = self.featureTree.selection()
        if len(selection) == 0:
            return
        item = selection[0]
        feature = self.featureTreeIds[item]
        self.model.currentAnalysis.currentFeature = feature

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
        c = glyxsuite.gui.DataModel.Chromatogram()
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
            #choice_Chrom = np.logical_and(np.greater(mzArray, minMZ), np.less(mzArray, maxMZ))
            choice_Chrom = np.logical_and(np.greater(mzArray, minMZ-0.1), np.less(mzArray, minMZ+0.1))
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

        self.model.classes["TwoDView"].init(keepZoom=True)
        self.updateSpectrumTree()
        self.model.classes["FeatureChromatogramView"].init(c, feature, minMZView, maxMZView, index)

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
            

    def updateSpectrumTree(self):
        # clear tree
        self.spectrumTree.delete(*self.spectrumTree.get_children())

        analysis = self.model.currentAnalysis

        if analysis == None:
            return

        feature = analysis.currentFeature
        if feature == None:
            return
        # insert all ms2 spectra
        minRT, maxRT, minMZ, maxMZ = feature.getBoundingBox()
        index = 0
        self.spectrumTreeIds = {}
        for spec, spectrum in analysis.data:

            # check if spectrum is linked to feature
            if not spectrum.nativeId in feature.getSpectraIds():
                if spectrum.rt < minRT:
                    continue
                if spectrum.rt > maxRT:
                    continue
                if spectrum.precursorMass < minMZ:
                    continue
                if spectrum.precursorMass > maxMZ:
                    continue

            index += 1
            if index%2 == 0:
                tag = ("oddrowFeature", )
            else:
                tag = ("evenrowFeature", )

            isGlycopeptide = "no"
            if spectrum.isGlycopeptide:
                isGlycopeptide = "yes"
            name = spectrum.index
            if self.model.timescale == "minutes":
                rt = round(spectrum.rt/60.0, 2)
            else:
                rt = round(spectrum.rt, 1)
            itemSpectra = self.spectrumTree.insert("", "end", text=name,
                                                   values=(rt,
                                                           round(spectrum.precursorMass, 4),
                                                           spectrum.precursorCharge,
                                                           round(spectrum.logScore, 2),
                                                           isGlycopeptide),
                                                   tags=tag)
            self.spectrumTreeIds[itemSpectra] = (spec, spectrum)

        # apply possible sorting
        if not "NotebookFeatureSpectra" in analysis.sorting:
            analysis.sorting["NotebookFeatureSpectra"] = ("#0", False)
        sortingColumn, reverse = analysis.sorting["NotebookFeatureSpectra"]
        analysis.sorting["NotebookFeatureSpectra"] = (sortingColumn, not reverse)
        self.sortSpectrumColumn(sortingColumn)
        
        children = self.spectrumTree.get_children('')
        if len(children) > 0:
            item = children[0]
            self.spectrumTree.selection_set(item)
            self.spectrumTree.see(item)

    def clickedSpectrumTree(self, event):
        selection = self.spectrumTree.selection()
        if len(selection) == 0:
            return
        item = selection[0]
        spec, spectrum = self.spectrumTreeIds[item]
        self.model.classes["FeatureSpectrumView"].initSpectrum(spec)
        self.model.classes["NotebookScoring"].setSelectedSpectrum(spectrum.index)

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


class AddIdentificationFrame(Tkinter.Toplevel):

    def __init__(self, master, model, feature):
        Tkinter.Toplevel.__init__(self, master=master)
        #self.minsize(600, 300)
        self.master = master
        self.feature = feature 
        self.title("Add Identification")
        self.config(bg="#d9d9d9")
        self.model = model
        self.glycan = None
        self.peptide = None

        self.precursorMass = (self.feature.getMZ()*self.feature.getCharge()-
                              glyxsuite.masses.MASS["H+"]*(self.feature.getCharge()-1))
        
        labelMass = Tkinter.Label(self, text="Feature Mass")
        labelMassValue = Tkinter.Label(self, text=str(round(self.precursorMass,4))+ " Da")
        labelMass.grid(row=0, column=0, sticky="NWES")
        labelMassValue.grid(row=0, column=1, columnspan=2, sticky="NWES")
        
        labelError = Tkinter.Label(self, text="Feature Error")
        self.labelErrorValue = Tkinter.Label(self, text="- Da")
        labelError.grid(row=1, column=0, sticky="NWES")
        self.labelErrorValue.grid(row=1, column=1, columnspan=2, sticky="NWES")

        labelGlycan = Tkinter.Label(self, text="Glycan")
        self.glycanVar = Tkinter.StringVar()
        self.glycanVar.trace("w", self.valuesChanged)
        self.entryGlycan = Tkinter.Entry(self, textvariable=self.glycanVar)
        labelGlycanMassLabel = Tkinter.Label(self, text="Glycan Mass")
        self.labelGlycanMass = Tkinter.Label(self, text="")
        
        labelGlycan.grid(row=2, column=0, sticky="NWES")
        self.entryGlycan.grid(row=2, column=1, columnspan=2, sticky="NWES")
        labelGlycanMassLabel.grid(row=3, column=0, sticky="NWES")
        self.labelGlycanMass.grid(row=3, column=1, columnspan=2, sticky="NWES")
        
        
        labelPeptide = Tkinter.Label(self, text="Peptide")
        self.peptideVar = Tkinter.StringVar()
        self.peptideVar.trace("w", self.valuesChanged)
        self.entryPeptide = Tkinter.Entry(self, textvariable=self.peptideVar)
        labelPeptideMassLabel = Tkinter.Label(self, text="Peptide Mass")
        self.labelPeptideMass = Tkinter.Label(self, text="")
        
        labelPeptide.grid(row=4, column=0, sticky="NWES")
        self.entryPeptide.grid(row=4, column=1, columnspan=2, sticky="NWES")
        labelPeptideMassLabel.grid(row=5, column=0, sticky="NWES")
        self.labelPeptideMass.grid(row=5, column=1, columnspan=2, sticky="NWES")
        
        
        cancelButton = Tkinter.Button(self, text="Cancel", command=self.cancel)        
        saveButton = Tkinter.Button(self, text="Add Identification", command=self.addIdentification)

        cancelButton.grid(row=10, column=0, sticky="NWES")
        saveButton.grid(row=10, column=1, sticky="NWES")
        
        # set values
        #self.chargeVar.set(feature.getCharge())
        #self.massVar.set(feature.getMZ())
        
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
            self.glycan = glyxsuite.lib.Glycan(self.glycanVar.get())
            self.labelGlycanMass.config(text=str(self.glycan.mass) +" Da")
            self.glycanVar.set(self.glycan.toString())
            self.entryGlycan.config(bg="grey")
            
        except:
            self.valid = False
            self.glycan = None
            self.labelGlycanMass.config(text=" - Da")
            self.entryGlycan.config(bg="red")

        try:
            self.peptide = glyxsuite.io.XMLPeptide()
            self.peptide.fromString(self.peptideVar.get())
            self.labelPeptideMass.config(text=str(self.peptide.mass) +" Da")
            self.entryPeptide.config(bg="grey")
        except:
            self.valid = False
            self.peptide = None
            self.labelPeptideMass.config(text=" - Da")
            self.entryPeptide.config(bg="red")
        
        # calculate Identification error
        if self.valid == True:
            mass = self.peptide.mass+self.glycan.mass+glyxsuite.masses.MASS["H+"]
            diff = mass-self.precursorMass
            self.labelErrorValue.config(text=str(round(diff,4)) + " Da")
        else:
            self.labelErrorValue.config(text="- Da")
    
    def addIdentification(self):
        if self.valid == False:
            return
            
        mass = self.peptide.mass+self.glycan.mass+glyxsuite.masses.MASS["H+"]
        diff = mass-self.precursorMass
        hit = glyxsuite.io.GlyxXMLGlycoModHit()
        hit.featureID = self.feature.getId()
        hit.glycan = self.glycan
        hit.peptide = self.peptide
        hit.error = diff
        hit.feature = self.feature
            
        self.model.currentAnalysis.analysis.glycoModHits.append(hit)
        
        self.destroy()
        self.model.runFilters()
        self.model.classes["NotebookFeature"].updateFeatureTree()
        self.model.classes["NotebookIdentification"].updateTree()

    def cancel(self):
        self.destroy()
