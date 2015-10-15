import ttk
import Tkinter
import DataModel
import re
import glyxsuite

class NotebookIdentification(ttk.Frame):

    def __init__(self, master, model):
        ttk.Frame.__init__(self, master=master)
        self.master = master
        self.model = model

        # show treeview of mzML file MS/MS and MS
        scrollbar = Tkinter.Scrollbar(self)
        self.tree = ttk.Treeview(self, yscrollcommand=scrollbar.set)

        columns = {"Mass":70, "error":70, "Peptide":160, "Glycan":160}
        self.tree["columns"] = ("Mass", "error", "Peptide", "Glycan")
        self.tree.column("#0", width=40)
        
        self.tree.heading("#0", text="Feature Nr.", command=lambda col='#0': self.sortColumn(col))
        for col in columns:
            self.tree.column(col, width=columns[col])
            self.tree.heading(col, text=col, command=lambda col=col: self.sortColumn(col))

        self.tree.grid(row=0, column=0, sticky=("N", "W", "E", "S"))

        scrollbar.grid(row=0, column=1, sticky=("N", "W", "E", "S"))
        scrollbar.config(command=self.tree.yview)

        self.treeIds = {}

        # treeview style
        self.tree.tag_configure('oddrowFeature', background='Moccasin')
        self.tree.tag_configure('evenrowFeature', background='PeachPuff')

        self.tree.tag_configure('evenSpectrum', background='LightBlue')
        self.tree.tag_configure('oddSpectrum', background='SkyBlue')
        self.tree.bind("<<TreeviewSelect>>", self.clickedTree);

        self.rowconfigure(0, weight=1)

        self.model.funcUpdateNotebookIdentification = self.updateTree

    def sortColumn(self, col):
        if self.model == None or self.model.currentAnalysis == None:
            return
            
        if col == self.model.currentAnalysis.sortedColumn:
            self.model.currentAnalysis.reverse = not self.model.currentAnalysis.reverse
        else:
            self.model.currentAnalysis.sortedColumn = col
            self.model.currentAnalysis.reverse = False
            
        if col == "Peptide" or col == "Glycan":
            l = [(self.tree.set(k, col), k) for k in self.tree.get_children('')]
        elif col == "Mass":
            l = [(float(self.tree.set(k, col)), k) for k in self.tree.get_children('')]
        elif col == "error":
            l = [(abs(float(self.tree.set(k, col))), k) for k in self.tree.get_children('')]
        elif col == "#0":
            l = [(int(self.tree.item(k, "text")), k) for k in self.tree.get_children('')]
        else:
            return
        l.sort(reverse=self.model.currentAnalysis.reverse)


        # rearrange items in sorted positions
        for index, (val, k) in enumerate(l):
            self.tree.move(k, '', index)

            # adjust tags
            taglist = list(self.tree.item(k, "tags"))
            if "oddrowFeature" in taglist:
                taglist.remove("oddrowFeature")
            if "evenrowFeature" in taglist:
                taglist.remove("evenrowFeature")

            if index%2 == 0:
                taglist.append("evenrowFeature")
            else:
                taglist.append("oddrowFeature")
            self.tree.item(k, tags = taglist)


    def updateTree(self):

        # clear tree
        self.tree.delete(*self.tree.get_children());
        self.treeIds = {}

        project = self.model.currentProject

        if project == None:
            return

        if project.mzMLFile.exp == None:
            return

        analysis = self.model.currentAnalysis

        if analysis == None:
            return

        # insert all glycomod hits

        index = 0
        for hit in analysis.analysis.glycoModHits:

            # get feature
            feature = analysis.featureIds[hit.featureID]
            #name = #str(index)
            name = feature.index
            # mass
            mass = (feature.getMZ()-glyxsuite.masses.MASS["H+"])*feature.getCharge()
            peptide = hit.peptide.toString()
            # clean up glycan
            glycan = glyxsuite.lib.Glycan(hit.glycan.composition)
            index += 1
            if index%2 == 0:
                tag = ("oddrowFeature", )
            else:
                tag = ("evenrowFeature", )
            itemSpectra = self.tree.insert("" , "end", text=name,
                values=(round(mass, 4),
                        round(hit.error, 4),
                        peptide,
                        glycan.getShortName()),
                tags = tag)
            self.treeIds[itemSpectra] = hit
        # update Extention
        self.model.funcUpdateExtentionIdentification()

    def clickedTree(self, event):
        selection = self.tree.selection()
        if len(selection) == 0:
            return
        item = selection[0]
        self.model.funcClickedIdentification(self.tree.item(item,"text"))
        self.model.funcUpdateConsensusSpectrum(self.treeIds[item])


