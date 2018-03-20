import ttk
import Tkinter

import numpy as np

import glyxtoolms

class NotebookScoring(ttk.Frame):

    def __init__(self, master, model):
        ttk.Frame.__init__(self, master=master)
        self.master = master
        self.model = model

        # create popup menu
        self.aMenu = Tkinter.Menu(self, tearoff=0)

        # layout self
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=0)
        self.rowconfigure(0,weight=0)
        self.rowconfigure(1,weight=1)

        # show treeview of mzML file MS/MS and MS
        scrollbar = ttk.Scrollbar(self)
        self.tree = ttk.Treeview(self, yscrollcommand=scrollbar.set)

        self.columns = ("Spectrum", "RT", "Mass", "Charge", "Score", "Is Glyco", "Status")
        self.columnsWidth =  {"Spectrum":80, "RT":80, "Mass":80, "Charge":80, "Score":80, "Is Glyco":80, "Status":80}
        self.tree["columns"] = self.columns
        self.tree.column("#0", width=100)
        self.tree.heading("#0", text="Feature", command=lambda col='#0': self.sortColumn(col))
        self.showColumns = {}
        for name in self.columns:
            self.showColumns[name] = Tkinter.BooleanVar()
            self.showColumns[name].set(True)
            self.showColumns[name].trace("w", self.columnVisibilityChanged)

        for col in self.columns:
            self.tree.column(col, width=self.columnsWidth[col])
            self.tree.heading(col, text=col, command=lambda col=col: self.sortColumn(col))

        button = Tkinter.Button(self,image=self.model.resources["filter"])

        button.grid(row=0, column=1)
        self.tree.grid(row=0, column=0, rowspan=2, sticky=("N", "W", "E", "S"))
        scrollbar.grid(row=1, column=1, sticky="NWES")

        scrollbar.config(command=self.tree.yview)

        self.treeIds = {}
        self.specToId = {}
        self.notify = True

        # treeview style
        self.tree.tag_configure('oddUnknown', background='Moccasin')
        self.tree.tag_configure('evenUnknown', background='PeachPuff')


        self.tree.tag_configure('oddGlycopeptide', background='PaleGreen')
        self.tree.tag_configure('evenGlycopeptide', background='YellowGreen')

        self.tree.tag_configure('oddNonGlycopeptide', background='LightBlue')
        self.tree.tag_configure('evenNonGlycopeptide', background='SkyBlue')

        self.tree.tag_configure('oddPoorGlycopeptide', background='LightSalmon')
        self.tree.tag_configure('evenPoorGlycopeptide', background='Salmon')

        self.tree.tag_configure('oddPoorNonGlycopeptide', background='Plum1')
        self.tree.tag_configure('evenPoorNonGlycopeptide', background='Plum2')

        self.tree.bind("<<TreeviewSelect>>", self.clickedTree)
        self.tree.bind("<Button-3>", self.popup)

        #self.tree.bind("a", lambda e: self.setStatus("Accepted"))
        #self.tree.bind("u", lambda e: self.setStatus("Unknown"))
        #self.tree.bind("r", lambda e: self.setStatus("Rejected"))
        self.tree.bind("g", lambda e: self.setStatus("Glycopeptide"))
        self.tree.bind("n", lambda e: self.setStatus("NonGlycopeptide"))
        self.tree.bind("h", lambda e: self.setStatus("PoorGlycopeptide"))
        self.tree.bind("m", lambda e: self.setStatus("PoorNonGlycopeptide"))
        self.tree.bind("u", lambda e: self.setStatus("Unknown"))

        self.model.registerClass("NotebookScoring", self)

    def seeItem(self, feature):
        spectra = feature.spectra
        self.notify = False
        itemIds = []
        for spectrum in spectra:
            spectrumId = self.specToId[str(spectrum.index) + "-" + str(feature.index)]
            self.tree.see(spectrumId)
            itemIds.append(spectrumId)
        #self.update()
        self.tree.selection_set(tuple(itemIds))
        self.update()
        self.notify = True




    def setStatus(self,status):
        # get currently active hit
        selection = self.tree.selection()
        if len(selection) == 0:
            return
        for item in selection:
            spec, spectrum = self.treeIds[item]

            #if status == "Accepted":
            #    spectrum.status = glyxtoolms.io.ConfirmationStatus.Accepted
            #elif status == "Rejected":
             #   spectrum.status = glyxtoolms.io.ConfirmationStatus.Rejected
            #elif status == "Unknown":
            #    spectrum.status = glyxtoolms.io.ConfirmationStatus.Unknown
            if status == "Glycopeptide":
                spectrum.status = glyxtoolms.io.ConfirmationStatus.Glycopeptide
            elif status == "NonGlycopeptide":
                spectrum.status = glyxtoolms.io.ConfirmationStatus.NonGlycopeptide
            elif status == "PoorGlycopeptide":
                spectrum.status = glyxtoolms.io.ConfirmationStatus.PoorGlycopeptide
            elif status == "PoorNonGlycopeptide":
                spectrum.status = glyxtoolms.io.ConfirmationStatus.PoorNonGlycopeptide
            elif status == "Unknown":
                spectrum.status = glyxtoolms.io.ConfirmationStatus.Unknown

            # Update on Treeview
            values = self.tree.item(item)["values"]
            values[5] = spectrum.status
            self.tree.item(item, values=values)

            taglist = list(self.tree.item(item, "tags"))
            taglist = self.setHighlightingTag(taglist, spectrum.status)
            self.tree.item(item, tags=taglist)

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

    def popup(self, event):
        area = self.tree.identify_region(event.x, event.y)
        self.aMenu.delete(0,"end")
        if area == "nothing":
            return
        elif area == "heading" or area == "separator":
            for name in self.columns:
                self.aMenu.insert_checkbutton("end", label=name, onvalue=1, offvalue=0, variable=self.showColumns[name])
        else:
            self.aMenu.add_command(label="Set to Glycopeptide",
                                   command=lambda x="Glycopeptide": self.setStatus(x))
            self.aMenu.add_command(label="Set to NonGlycopeptide",
                                   command=lambda x="NonGlycopeptide": self.setStatus(x))
            self.aMenu.add_command(label="Set to PoorGlycopeptide",
                                   command=lambda x="PoorGlycopeptide": self.setStatus(x))
            self.aMenu.add_command(label="Set to PoorNonGlycopeptide",
                                   command=lambda x="PoorNonGlycopeptide": self.setStatus(x))
            self.aMenu.add_command(label="Set to Unknown",
                                   command=lambda x="Unknown": self.setStatus(x))
            #self.aMenu.add_command(label="Copy to Clipboard",
            #                       command=self.copyToClipboard)
        self.aMenu.post(event.x_root, event.y_root)
        self.aMenu.focus_set()
        self.aMenu.bind("<FocusOut>", self.removePopup)

    def removePopup(self,event):
        if self.focus_get() != self.aMenu:
            self.aMenu.unpost()

    def setHighlightingTag(self, taglist, status):
        if not status in glyxtoolms.io.ConfirmationStatus._types:
            raise Exception("Status "+status+" not defined!")
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

    def sortColumn(self, col):

        if self.model == None or self.model.currentAnalysis == None:
            return
        sortingColumn, reverse = self.model.currentAnalysis.sorting["NotebookScoring"]

        if col == sortingColumn:
            reverse = not reverse
        else:
            sortingColumn = col
            reverse = False
        self.model.currentAnalysis.sorting["NotebookScoring"] = (sortingColumn, reverse)

        if col == "Is Glyco" or col == "Status":
            l = [(self.tree.set(k, col), k) for k in self.tree.get_children('')]
        elif col == "#0":
            l = [(int(self.tree.item(k, "text")), k) for k in self.tree.get_children('')]
        else:
            l = [(float(self.tree.set(k, col)), k) for k in self.tree.get_children('')]

        l.sort(reverse=reverse)


        # rearrange items in sorted positions
        for index, (val, k) in enumerate(l):
            self.tree.move(k, '', index)
            status = self.tree.item(k)["values"][6]

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


    def updateTree(self, features):
        # clear tree
        self.tree.delete(*self.tree.get_children())
        self.treeIds = {}
        self.specToId = {}

        project = self.model.currentProject

        if project == None:
            return

        if project.mzMLFile.exp == None:
            return

        analysis = self.model.currentAnalysis

        if analysis == None:
            return

        # insert all ms2 spectra

        index = 0
        for spec, spectrum in analysis.data:
            # check if
            contains = False
            for feature in spectrum.features:
                if not feature in features:
                    continue
                if index%2 == 0:
                    taglist = ("even" + spectrum.status, "even")
                else:
                    taglist = ("odd" + spectrum.status, "odd")
                index += 1
                isGlycopeptide = "no"
                if spectrum.isGlycopeptide:
                    isGlycopeptide = "yes"
                name = spectrum.nativeId
                if self.model.timescale == "minutes":
                    rt = round(spectrum.rt/60.0, 2)
                else:
                    rt = round(spectrum.rt, 1)
                #itemSpectra = self.tree.insert("" , "end", text=name,
                itemSpectra = self.tree.insert("", "end", text=feature.index,
                                               values=(spectrum.index,
                                                       rt,
                                                       round(spectrum.precursorMass, 4),
                                                       spectrum.precursorCharge,
                                                       round(spectrum.logScore, 2),
                                                       isGlycopeptide,
                                                       spectrum.status),
                                               tags=taglist)
                self.treeIds[itemSpectra] = (spec, spectrum)
                self.specToId[str(spectrum.index) + "-" + str(feature.index)] = itemSpectra
        # apply possible sorting
        if not "NotebookScoring" in analysis.sorting:
            analysis.sorting["NotebookScoring"] = ("#0", False)

        sortingColumn, reverse = analysis.sorting["NotebookScoring"]
        analysis.sorting["NotebookScoring"] = (sortingColumn, not reverse)
        self.sortColumn(sortingColumn)

    def clickedTree(self, event):
        if self.notify == False:
            return
        selection = self.tree.selection()
        if len(selection) == 0:
            return
        item = selection[0]

        # init Oxonium Plot
        spectra = []
        for item in selection:
            spec, spectrum = self.treeIds[item]
            spectra.append(spectrum)
        if "OxoniumIonPlot" in self.model.classes:
            self.model.classes["OxoniumIonPlot"].init(spectra=spectra)
        spec, spectrum = self.treeIds[item]

        # make calculations
        ms2, ms1 = self.model.currentProject.mzMLFile.experimentIds[spectrum.nativeId]

        # init spectrum view
        self.model.classes["SpectrumView"].initSpectrum(ms2)



    def setSelectedSpectrum(self, index):
        for itemSpectra in self.treeIds:
            if index == self.treeIds[itemSpectra][1].index:
                self.tree.selection_set(itemSpectra)
                self.tree.see(itemSpectra)
                break
