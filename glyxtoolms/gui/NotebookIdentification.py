import ttk
import Tkinter
import tkFileDialog
import tkMessageBox
import os
import pyperclip

import glyxtoolms


class NotebookIdentification(ttk.Frame):

    def __init__(self, master, model):
        ttk.Frame.__init__(self, master=master)
        self.master = master
        self.model = model
        
        self.features = []
        
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=0)
        self.rowconfigure(0,weight=0)
        self.rowconfigure(1,weight=1)
        
        # create popup menu
        self.aMenu = Tkinter.Menu(self, tearoff=0)

        # show treeview of mzML file MS/MS and MS
        button = Tkinter.Button(self,image=self.model.resources["filter"])
        scrollbar = Tkinter.Scrollbar(self)
        self.tree = ttk.Treeview(self, yscrollcommand=scrollbar.set, selectmode='extended')
        self.columns = ("Mass", "error", "Peptide", "Glycan", "Status")
        self.columnNames = {"Mass":"Mass [Da]", "error":"Error", "Peptide":"Peptide", "Glycan":"Glycan", "Status":"Status"}
        self.columnsWidth = {"Mass":70, "error":80, "Peptide":150, "Glycan":160, "Status":80}
        self.showColumns = {}
        for name in self.columns:
            self.showColumns[name] = Tkinter.BooleanVar()
            self.showColumns[name].set(True)
            self.showColumns[name].trace("w", self.columnVisibilityChanged)

        self.tree.column("#0", width=80)
        self.tree.heading("#0", text="Feature Nr", command=lambda col='#0': self.sortColumn(col))
        
        
        self.tree["columns"] = self.columns
        for col in self.columns:
            self.tree.column(col, width=self.columnsWidth[col])
            self.tree.heading(col, text=col, command=lambda col=col: self.sortColumn(col))
            
        self.setHeadingNames()

        self.tree.grid(row=0, column=0, rowspan=2, sticky=("N", "W", "E", "S"))

        scrollbar.grid(row=1, column=1, sticky="NWES")
        scrollbar.config(command=self.tree.yview)
        button.grid(row=0, column=1)

        self.treeIds = {}

        # treeview style
        self.tree.tag_configure('oddUnknown', background='Moccasin')
        self.tree.tag_configure('evenUnknown', background='PeachPuff')
        
        self.tree.tag_configure('oddDeleted', background='LightSalmon')
        self.tree.tag_configure('evenDeleted', background='Salmon')
        
        self.tree.tag_configure('oddAccepted', background='PaleGreen')
        self.tree.tag_configure('evenAccepted', background='YellowGreen')
        
        self.tree.tag_configure('oddRejected', background='LightBlue')
        self.tree.tag_configure('evenRejected', background='SkyBlue')

        self.tree.bind("<<TreeviewSelect>>", self.clickedTree)
        self.tree.bind("<Button-3>", self.popup)
        
        self.tree.bind("a", lambda e: self.setStatus("Accepted"))
        self.tree.bind("u", lambda e: self.setStatus("Unknown"))
        self.tree.bind("r", lambda e: self.setStatus("Rejected"))

        self.model.registerClass("NotebookIdentification", self)
        
    def setHeadingNames(self):
        if self.model.errorType == "Da":
            self.columnNames["error"] = "Error [Da]"
        else:
            self.columnNames["error"] = "Error [ppm]"
        for col in self.columnNames:
            self.tree.heading(col, text=self.columnNames.get(col, col))
        
    def columnVisibilityChanged(self, *arg, **args):
        header = []
        for columnname in self.columns:
            if self.showColumns[columnname].get() == True:
                header.append(columnname)
        self.tree["displaycolumns"] = tuple(header)
        space = self.grid_bbox(column=0, row=0, col2=0, row2=0)[2]
        width = space/(len(header)+1)
        rest = space%(len(header)+1)
        for column in ["#0"] + header:
            self.tree.column(column, width=width+rest)
            rest = 0

    def selectAllIdentifications(self, event):
        items = self.tree.get_children()
        if len(items) == 0:
            return
        self.tree.selection_set(items)
        self.clickedTree(None)
        
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
        for item in self.tree.selection():
            content = self.tree.item(item)
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
        
        
        

    def setStatus(self,status):
        # get currently active hit
        selection = self.tree.selection()
        if len(selection) == 0:
            return
        for item in selection:
            hit = self.treeIds[item]
            
            if status == "Accepted":
                hit.status = glyxtoolms.io.ConfirmationStatus.Accepted
            elif status == "Rejected":
                hit.status = glyxtoolms.io.ConfirmationStatus.Rejected
            elif status == "Unknown":
                hit.status = glyxtoolms.io.ConfirmationStatus.Unknown
            # Update on Treeview
            values = self.tree.item(item)["values"]
            values[4] = hit.status
            self.tree.item(item, values=values)
            
            taglist = list(self.tree.item(item, "tags"))
            taglist = self.setHighlightingTag(taglist, hit.status)
            self.tree.item(item, tags=taglist)
        
    def popup(self, event):
        area = self.tree.identify_region(event.x, event.y)
        self.aMenu.delete(0,"end")
        if area == "nothing":
            return
        elif area == "heading" or area == "separator":
            for name in self.columns:
                self.aMenu.insert_checkbutton("end", label=name, onvalue=1, offvalue=0, variable=self.showColumns[name])
        else:
            self.aMenu.add_command(label="Set to Accepted", 
                                   command=lambda x="Accepted": self.setStatus(x))
            self.aMenu.add_command(label="Set to Rejected",
                                   command=lambda x="Rejected": self.setStatus(x))
            self.aMenu.add_command(label="Set to Unknown",
                                   command=lambda x="Unknown": self.setStatus(x))
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
            pass # Brrrr

    def sortColumn(self, col):
        if self.model == None or self.model.currentAnalysis == None:
            return

        sortingColumn, reverse = self.model.currentAnalysis.sorting["NotebookIdentification"]
        if col == sortingColumn:
            reverse = not reverse
        else:
            sortingColumn = col
            reverse = False
        self.model.currentAnalysis.sorting["NotebookIdentification"] = (sortingColumn, reverse)

        if col == "Peptide" or col == "Glycan" or col == "Status":
            l = [(self.tree.set(k, col), k) for k in self.tree.get_children('')]
        elif col == "Mass":
            l = [(float(self.tree.set(k, col)), k) for k in self.tree.get_children('')]
        elif col == "error":
            l = [(abs(float(self.tree.set(k, col))), k) for k in self.tree.get_children('')]
        elif col == "#0":
            l = [(int(self.tree.item(k, "text")), k) for k in self.tree.get_children('')]
        else:
            return
        l.sort(reverse=reverse)


        # rearrange items in sorted positions
        for index, (val, k) in enumerate(l):
            self.tree.move(k, '', index)
            status = self.tree.item(k)["values"][4]
            
            # adjust tags
            taglist = list(self.tree.item(k, "tags"))
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
            self.tree.item(k, tags=taglist)
            
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


    def updateTree(self, features=None):
        """ Supply list of features that should be shown. 
        If 'None' is supplied, the currently shown features are updated """
        # clear tree
        self.tree.delete(*self.tree.get_children())
        self.treeIds = {}
        
        self.setHeadingNames()

        project = self.model.currentProject

        if project == None:
            return

        if project.mzMLFile.exp == None:
            return

        analysis = self.model.currentAnalysis

        if analysis == None:
            return
            
        # check supplied features
        if features is not None:
            self.features = features
            

        # insert all glycomod hits
        index = 0
        for hit in analysis.analysis.glycoModHits:
            
            # select hits only present in given features
            if hit.feature not in self.features:
                continue
            
            # check if hit passes filters
            if hit.passesFilter == False:
                continue
                        
            feature = hit.feature
            name = feature.index
            # mass
            mass = (feature.getMZ()-glyxtoolms.masses.MASS["H+"])*feature.getCharge()
            peptide = hit.peptide.toString()
            # clean up glycan
            glycan = glyxtoolms.lib.Glycan(hit.glycan.composition)

            if index%2 == 0:
                taglist = ("even" + hit.status, "even")
            else:
                taglist = ("odd" + hit.status, "odd")
            index += 1
            # error
            if self.model.errorType == "Da":
                error = round(hit.error, 4)
            else:
                error = round(hit.error/float(feature.getMZ())*1E6, 1)
            itemSpectra = self.tree.insert("", "end", text=name,
                                           values=(round(mass, 4),
                                                   error,
                                                   peptide,
                                                   glycan.toString(),
                                                   hit.status),
                                           tags=taglist)
            self.treeIds[itemSpectra] = hit

        # apply possible sorting
        if not "NotebookIdentification" in analysis.sorting:
            analysis.sorting["NotebookIdentification"] = ("#0", False)
        
        sortingColumn, reverse = analysis.sorting["NotebookIdentification"]
        analysis.sorting["NotebookIdentification"] = (sortingColumn, not reverse)
        self.sortColumn(sortingColumn)

    def clickedTree(self, event):
        selection = self.tree.selection()

        if len(selection) == 1:
            item = selection[0]
            hit = self.treeIds[item]
            self.model.classes["NotebookFeature"].plotSelectedFeatures([hit.feature], hit)
            self.model.classes["PeptideCoverageFrame"].init(hit)
            if "OxoniumIonPlot" in self.model.classes:
                self.model.classes["OxoniumIonPlot"].init(identifications=[hit])
        else:
            features = set()
            hits = []
            for item in selection:
                hit = self.treeIds[item]
                hits.append(hit)
                features.add(hit.feature)
            features = list(features)
            self.model.classes["NotebookFeature"].plotSelectedFeatures(features, None)
            self.model.classes["PeptideCoverageFrame"].init(None)
            if "OxoniumIonPlot" in self.model.classes:
                self.model.classes["OxoniumIonPlot"].init(identifications=hits)
            

    def deleteIdentification(self, event):
        selection = self.tree.selection()
        if len(selection) == 0:
            return
        for item in selection:
            hit = self.treeIds[item]

            nextItem = self.tree.next(item)
            self.tree.delete(item)
            self.treeIds.pop(item)
            if nextItem != {}:
                self.tree.selection_set(nextItem)
            elif len(self.tree.get_children('')) > 0:
                nextItem = self.tree.get_children('')[-1]
                self.tree.selection_set(nextItem)

            analysis = self.model.currentAnalysis
            analysis.removeIdentification(hit)
        
        # update NotebookFeature
        self.model.classes["NotebookFeature"].updateFeatureTree()
