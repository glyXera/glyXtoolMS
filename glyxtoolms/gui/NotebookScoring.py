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
        #self.aMenu.add_command(label="Accepted",
        #                       command=lambda x="Accepted": self.setStatus(x))
        #self.aMenu.add_command(label="Rejected",
        #                       command=lambda x="Rejected": self.setStatus(x))
        #self.aMenu.add_command(label="Deleted",
        #                       command=lambda x="Unknown": self.setStatus(x))

        # layout self
        self.rowconfigure(0, weight=0) # frameSpectrum
        self.rowconfigure(1, weight=1) # frameTree
        self.columnconfigure(0, weight=1)

        frameSpectrum = ttk.Labelframe(self, text="Spectrum")
        frameSpectrum.grid(row=0, column=0, sticky=("N", "W", "E", "S"))
        frameSpectrum.columnconfigure(0, weight=1)

        frameTree = ttk.Labelframe(self, text="MS/MS Spectra")
        frameTree.grid(row=1, column=0, sticky=("N", "W", "E", "S"))
        frameTree.columnconfigure(0, weight=1)
        frameTree.columnconfigure(1, weight=0)

        l1 = ttk.Label(frameSpectrum, text="Spectrum-Id:")
        l1.grid(row=0, column=0, sticky="NE")
        self.v1 = Tkinter.StringVar()
        self.c1 = ttk.Label(frameSpectrum, textvariable=self.v1)
        self.c1.grid(row=0, column=1, sticky="NW")

        l2 = ttk.Label(frameSpectrum, text="RT:")
        l2.grid(row=1, column=0, sticky="NE")
        self.v2 = Tkinter.StringVar()
        self.c2 = ttk.Entry(frameSpectrum, textvariable=self.v2)
        self.c2.grid(row=1, column=1, sticky="NW")

        l3 = ttk.Label(frameSpectrum, text="Precursormass:")
        l3.grid(row=2, column=0, sticky="NE")
        self.v3 = Tkinter.StringVar()
        self.c3 = ttk.Entry(frameSpectrum, textvariable=self.v3)
        self.c3.grid(row=2, column=1, sticky="NW")

        l4 = ttk.Label(frameSpectrum, text="Precursorcharge:")
        l4.grid(row=3, column=0, sticky="NE")
        self.v4 = Tkinter.StringVar()
        self.c4 = ttk.Entry(frameSpectrum, textvariable=self.v4)
        self.c4.grid(row=3, column=1, sticky="NW")

        l5 = ttk.Label(frameSpectrum, text="Score:")
        l5.grid(row=4, column=0, sticky="NE")
        self.v5 = Tkinter.StringVar()
        self.c5 = ttk.Entry(frameSpectrum, textvariable=self.v5)
        self.c5.grid(row=4, column=1, sticky="NW")

        l6 = ttk.Label(frameSpectrum, text="Is Glycopeptide:")
        l6.grid(row=5, column=0, sticky="NE")
        self.v6 = Tkinter.IntVar()
        self.c6 = glyxtoolms.gui.Appearance.Checkbutton(frameSpectrum, variable=self.v6)

        #self.c6 = Tkinter.Checkbutton(frameSpectrum, variable=self.v6)
        self.c6.grid(row=5, column=1)

        b1 = ttk.Button(frameSpectrum, text="save Changes", command=self.saveChanges)
        b1.grid(row=4, rowspan=2, column=2)

        # show treeview of mzML file MS/MS and MS
        scrollbar = ttk.Scrollbar(frameTree)
        self.tree = ttk.Treeview(frameTree, yscrollcommand=scrollbar.set)

        columns = ("Spec Nr", "RT", "Mass", "Charge", "Score", "Is Glyco", "Status")
        self.tree["columns"] = columns
        self.tree.column("#0", width=100)
        self.tree.heading("#0", text="Feature", command=lambda col='#0': self.sortColumn(col))
        for col in columns:
            self.tree.column(col, width=80)
            self.tree.heading(col, text=col, command=lambda col=col: self.sortColumn(col))

        self.tree.grid(row=0, column=0, sticky=("N", "W", "E", "S"))

        scrollbar.grid(row=0, column=1, sticky=("N", "W", "E", "S"))
        scrollbar.config(command=self.tree.yview)

        self.treeIds = {}

        # treeview style
        self.tree.tag_configure('oddUnknown', background='Moccasin')
        self.tree.tag_configure('evenUnknown', background='PeachPuff')

        #self.tree.tag_configure('oddDeleted', background='LightSalmon')
        #self.tree.tag_configure('evenDeleted', background='Salmon')

        #self.tree.tag_configure('oddAccepted', background='PaleGreen')
        #self.tree.tag_configure('evenAccepted', background='YellowGreen')

        #self.tree.tag_configure('oddRejected', background='LightBlue')
        #self.tree.tag_configure('evenRejected', background='SkyBlue')

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

        # layout frameTree
        frameTree.rowconfigure(0, weight=1)

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

    def popup(self, event):
        self.aMenu.post(event.x_root, event.y_root)
        self.aMenu.focus_set()
        self.aMenu.bind("<FocusOut>", self.removePopup)

    def removePopup(self,event):
        if self.focus_get() != self.aMenu:
            self.aMenu.unpost()

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
            status = self.tree.item(k)["values"][5]

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


    def updateTree(self):

        # clear tree
        self.tree.delete(*self.tree.get_children())
        self.treeIds = {}

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
            for feature in spectrum.features:
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
        # apply possible sorting
        if not "NotebookScoring" in analysis.sorting:
            analysis.sorting["NotebookScoring"] = ("#0", False)

        sortingColumn, reverse = analysis.sorting["NotebookScoring"]
        analysis.sorting["NotebookScoring"] = (sortingColumn, not reverse)
        self.sortColumn(sortingColumn)

    def clickedTree(self, event):
        selection = self.tree.selection()
        if len(selection) != 1:
            return
        item = selection[0]
        spec, spectrum = self.treeIds[item]

        # set values of spectrum
        self.v1.set(spectrum.nativeId)
        self.v2.set(round(spectrum.rt, 1))
        self.v3.set(round(spectrum.precursorMass, 4))
        self.v4.set(spectrum.precursorCharge)
        self.v5.set(round(spectrum.logScore, 2))
        self.v6.set(spectrum.isGlycopeptide)

        # make calculations
        ms2, ms1 = self.model.currentProject.mzMLFile.experimentIds[spectrum.nativeId]
        mz = spectrum.precursorMass
        charge = spectrum.precursorCharge
        p = ms2.getPrecursors()[0]
        low = p.getIsolationWindowLowerOffset()
        high = p.getIsolationWindowUpperOffset()
        if low == 0:
            low = 2
        if high == 0:
            high = 2
        low = mz-low
        high = mz+high

        #rtLow = ms1.getRT()-100
        #rtHigh = ms1.getRT()+100

        # create chromatogram
        c = glyxtoolms.gui.DataModel.Chromatogram()
        c.plot = True
        c.name = "test"
        c.rangeLow = mz-0.1
        if charge != 0:
            c.rangeHigh = mz+3/abs(float(charge))+0.1
        else:
            c.rangeHigh = mz+1+0.1
        c.rt = []
        c.intensity = []
        c.msLevel = 1
        c.selected = True
        if len(spectrum.chromatogramSpectra) == 0:
            print "no chromatogram spectra", spectrum
            return
        rtLow = spectrum.chromatogramSpectra[0].getRT()
        rtHigh = spectrum.chromatogramSpectra[-1].getRT()

        for spec in spectrum.chromatogramSpectra:
            c.rt.append(spec.getRT())
            peaks = spec.get_peaks()
            if hasattr(peaks, "shape"):
                mzArray = peaks[:, 0]
                intensArray = peaks[:, 1]
            else:
                mzArray, intensArray = peaks
            # get intensity in range
            choice = np.logical_and(np.greater(mzArray, c.rangeLow),
                                    np.less(mzArray, c.rangeHigh))
            c.intensity.append(np.extract(choice, intensArray).sum())

        # set chromatogram within analysis
        self.model.currentAnalysis.chromatograms[c.name] = c
        self.model.currentAnalysis.selectedChromatogram = c

        # init spectrum view
        self.model.classes["SpectrumView"].initSpectrum(ms2)

        # init precursor spectrum view
        self.model.classes["PrecursorView"].initSpectrum(ms1, mz, charge, low, high)

        # init chromatogram view
        self.model.classes["ChromatogramView"].initChromatogram(rtLow, rtHigh, ms2.getRT())

    def saveChanges(self):
        selection = self.tree.selection()
        if len(selection) == 0:
            return
        item = selection[0]
        spec, spectrum = self.treeIds[item]

        spectrum.rt = float(self.v2.get())
        spectrum.precursorMass = float(self.v3.get())
        spectrum.precursorCharge = int(self.v4.get())
        spectrum.logScore = float(self.v5.get())
        spectrum.isGlycopeptide = bool(self.v6.get())

        # change values in table view
        isGlycopeptide = "no"
        if spectrum.isGlycopeptide:
            isGlycopeptide = "yes"
        self.tree.item(item,
                       values=(round(spectrum.rt, 1),
                               round(spectrum.precursorMass, 4),
                               spectrum.precursorCharge,
                               round(spectrum.logScore, 2),
                               isGlycopeptide))

    def setSelectedSpectrum(self, index):
        for itemSpectra in self.treeIds:
            if index == self.treeIds[itemSpectra][1].index:
                self.tree.selection_set(itemSpectra)
                self.tree.see(itemSpectra)
                break
