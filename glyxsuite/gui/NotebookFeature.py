import ttk
import Tkinter
import DataModel
import numpy as np

class NotebookFeature(ttk.Frame):

    def __init__(self, master, model):
        ttk.Frame.__init__(self, master=master)
        self.master = master
        self.model = model
        frameFeature = ttk.Labelframe(self, text="Features")
        frameFeature.grid(row=0, column=0, sticky=("N", "W", "E", "S"))

        frameSpectrum = ttk.Labelframe(self, text="Featurespectra")
        frameSpectrum.grid(row=1, column=0, sticky=("N", "W", "E", "S"))

        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=0)

        frameFeature.rowconfigure(0, weight=1)

        # show treeview of mzML file MS/MS and MS
        # ------------------- Feature Tree ----------------------------#

        scrollbar = Tkinter.Scrollbar(frameFeature)
        self.featureTree = ttk.Treeview(frameFeature, yscrollcommand=scrollbar.set)

        columns = ("RT", "MZ", "Charge", "Best Score", "Nr Spectra")
        self.featureTree["columns"] = columns
        self.featureTree.column("#0", width=100)
        self.featureTree.heading("#0", text="Feature Nr.", command=lambda col='#0': self.sortFeatureColumn(col))
        for col in columns:
            self.featureTree.column(col, width=80)
            self.featureTree.heading(col,
                text=col,
                command=lambda col=col: self.sortFeatureColumn(col))

        self.featureTree.grid(row=0, column=0, sticky=("N", "W", "E", "S"))

        scrollbar.grid(row=0, column=1, sticky=("N", "W", "E", "S"))
        scrollbar.config(command=self.featureTree.yview)

        self.featureTreeIds = {}

        # treeview style
        self.featureTree.tag_configure('oddrowFeature', background='Moccasin')
        self.featureTree.tag_configure('evenrowFeature', background='PeachPuff')
        self.featureTree.tag_configure('evenSpectrum', background='LightBlue')
        self.featureTree.tag_configure('oddSpectrum', background='SkyBlue')
        self.featureTree.bind("<<TreeviewSelect>>", self.clickedFeatureTree);

        self.model.funcUpdateNotebookFeature = self.updateFeatureTree

        # ------------------- Spectrum Tree ---------------------------#
        self.spectrumTreeIds = {}

        scrollbar = Tkinter.Scrollbar(frameSpectrum)
        self.spectrumTree = ttk.Treeview(frameSpectrum, yscrollcommand=scrollbar.set)
        columns = ("RT", "Mass", "Charge", "Score", "Is Glyco")
        self.spectrumTree["columns"] = columns
        self.spectrumTree.column("#0", width=100)
        self.spectrumTree.heading("#0", text="Spectrum Nr.", command=lambda col='#0':  self.sortSpectrumColumn(col))
        for col in columns:
            self.spectrumTree.column(col, width=80)
            self.spectrumTree.heading(col, text=col, command=lambda col=col: self.sortSpectrumColumn(col))

        self.spectrumTree.grid(row=0, column=0, sticky=("N", "W", "E", "S"))
        scrollbar.grid(row=0, column=1, sticky=("N", "W", "E", "S"))

        scrollbar.config(command=self.spectrumTree.yview)
        self.spectrumTree.bind("<<TreeviewSelect>>", self.clickedSpectrumTree);

        self.model.funcUpdateExtentionFeature = self.updateSpectrumTree
        self.model.funcClickedIdentification = self.setSelectedFeature

    def sortFeatureColumn(self, col):

        if self.model == None or self.model.currentAnalysis == None:
            return

        if col == self.model.currentAnalysis.sortedColumn:
            self.model.currentAnalysis.reverse = not self.model.currentAnalysis.reverse
        else:
            self.model.currentAnalysis.sortedColumn = col
            self.model.currentAnalysis.reverse = False
            
        if col == "isGlycopeptide":
            l = [(self.featureTree.set(k, col), k) for k in self.featureTree.get_children('')]
        elif col == "#0":
            l = [(int(self.featureTree.item(k, "text")), k) for k in self.featureTree.get_children('')]
        else:
            l = [(float(self.featureTree.set(k, col)), k) for k in self.featureTree.get_children('')]

        l.sort(reverse=self.model.currentAnalysis.reverse)


        # rearrange items in sorted positions
        for index, (val, k) in enumerate(l):
            self.featureTree.move(k, '', index)

            # adjust tags
            taglist = list(self.featureTree.item(k, "tags"))
            if "oddrowFeature" in taglist:
                taglist.remove("oddrowFeature")
            if "evenrowFeature" in taglist:
                taglist.remove("evenrowFeature")

            if index%2 == 0:
                taglist.append("evenrowFeature")
            else:
                taglist.append("oddrowFeature")
            self.featureTree.item(k, tags = taglist)


    def updateFeatureTree(self):

        # clear tree
        self.featureTree.delete(*self.featureTree.get_children());
        self.featureTreeIds = {}

        project = self.model.currentProject

        if project == None:
            return

        if project.mzMLFile.exp == None:
            return

        analysis = self.model.currentAnalysis

        if analysis == None:
            return

        # insert all ms2 spectra
        #("RT", "MZ", "Charge", "Best Score", "Nr Spectra")
        index = 0
        for feature in analysis.analysis.features:
            index += 1
            if index%2 == 0:
                tag = ("oddrowFeature", )
            else:
                tag = ("evenrowFeature", )
            name = str(feature.index)
            bestScore = 10.0
            for specId in feature.getSpectraIds():
                spectrum = analysis.spectraIds[specId]
                if spectrum.logScore < bestScore:
                    bestScore = spectrum.logScore
            item = self.featureTree.insert("" , "end", text=name,
                values=(round(feature.getRT(), 1),
                        round(feature.getMZ(), 4),
                        feature.getCharge(),
                        round(bestScore, 2),
                        len(feature.getSpectraIds())),
                tags = tag)
            self.featureTreeIds[item] = feature


    def clickedFeatureTree(self, event):
        print "clicked feature tree"
        selection = self.featureTree.selection()
        if len(selection) == 0:
            return
        item = selection[0]
        feature = self.featureTreeIds[item]
        self.model.currentAnalysis.currentFeature = feature

        # calculate spectrum and chromatogram
        exp = self.model.currentProject.mzMLFile.exp
        minRT, maxRT, minMZ, maxMZ = feature.getBoundingBox()

        number = 10000
        base = np.linspace(minMZ, maxMZ, num=number)
        sumSpectra = np.zeros_like(base)
        c = DataModel.Chromatogram()
        c.rt = []
        c.intensity = []
        for spec in self.model.currentAnalysis.featureSpectra[feature.getId()]:
            c.rt.append(spec.getRT())
            peaks = spec.get_peaks()
            if hasattr(peaks, "shape"):
                mzArray = peaks[:, 0]
                intensArray = peaks[:, 1]
            else:
                mzArray, intensArray = peaks
            # get intensity in range
            choice = np.logical_and(np.greater(mzArray, minMZ), np.less(mzArray, maxMZ))
            arr_mz = np.extract(choice, mzArray)
            arr_intens = np.extract(choice, intensArray)
            c.intensity.append(arr_intens.sum())
            # interpolate intensity to base
            sumSpectra += np.interp(base, arr_mz, arr_intens)

        self.model.debug = self.model.currentAnalysis.featureSpectra[feature.getId()]
        c.plot = True
        c.name = "test"
        c.rangeLow = minMZ
        c.rangeHigh = maxMZ
        c.msLevel = 1
        c.selected = True

        self.model.funcFeatureTwoDView(keepZoom = True)
        self.model.funcUpdateExtentionFeature()
        self.model.funcUpdateFeaturePrecursorSpectrum(np.vstack((base, sumSpectra)).T, minMZ, maxMZ)
        self.model.funcUpdateFeatureChromatogram(c, c.rt[0], c.rt[-1], None)

    def sortSpectrumColumn(self, col):
        if self.model == None or self.model.currentAnalysis == None:
            return
    
        if col == self.model.currentAnalysis.sortedColumn:
            self.model.currentAnalysis.reverse = not self.model.currentAnalysis.reverse
        else:
            self.model.currentAnalysis.sortedColumn = col
            self.model.currentAnalysis.reverse = False
        if col == "Is Glyco":
            l = [(self.spectrumTree.set(k, col), k) for k in self.spectrumTree.get_children('')]
        elif col == "#0":
            l = [(int(self.spectrumTree.item(k, "text")), k) for k in self.spectrumTree.get_children('')]
        else:
            l = [(float(self.spectrumTree.set(k, col)), k) for k in self.spectrumTree.get_children('')]

        l.sort(reverse=self.model.currentAnalysis.reverse)


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
            self.spectrumTree.item(k, tags = taglist)

    def updateSpectrumTree(self):
        print "update"
        # clear tree
        self.spectrumTree.delete(*self.spectrumTree.get_children());

        analysis = self.model.currentAnalysis

        if analysis == None:
            #print "foo1"
            return

        feature = analysis.currentFeature
        if feature == None:
            #print "foo2"
            return
        #print "foo3", len(analysis.data)
        # insert all ms2 spectra
        minRT, maxRT, minMZ, maxMZ = feature.getBoundingBox()
        #print feature.getBoundingBox()
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

            itemSpectra = self.spectrumTree.insert("" , "end", text=name,
                values=(round(spectrum.rt, 1),
                        round(spectrum.precursorMass, 4),
                        spectrum.precursorCharge,
                        round(spectrum.logScore, 2),
                        isGlycopeptide),
                tags = tag)
            self.spectrumTreeIds[itemSpectra] = (spec, spectrum)
            # set first spectrum as selected
            if index == 1:
                self.spectrumTree.selection_set(itemSpectra)
                self.spectrumTree.see(itemSpectra)

    def clickedSpectrumTree(self, event):
        selection = self.spectrumTree.selection()
        if len(selection) == 0:
            return
        item = selection[0]
        spec, spectrum = self.spectrumTreeIds[item]
        self.model.funcUpdateFeatureMSMSSpectrum(spec)
        self.model.funcClickedFeatureSpectrum(spectrum.index)
        
    def setSelectedFeature(self,index):
        for item in self.featureTreeIds:
            if index == self.featureTreeIds[item].index:
                self.featureTree.selection_set(item)
                self.featureTree.see(item)
                break
        
        

