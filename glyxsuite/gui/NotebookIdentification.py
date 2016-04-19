import ttk
import Tkinter

import glyxsuite

class NotebookIdentification(ttk.Frame):

    def __init__(self, master, model):
        ttk.Frame.__init__(self, master=master)
        self.master = master
        self.model = model
        
        # create popup menu
        self.aMenu = Tkinter.Menu(self, tearoff=0)
        self.aMenu.add_command(label="Set to Accepted", 
                               command=lambda x="Accepted": self.setStatus(x))
        self.aMenu.add_command(label="Set to Rejected",
                               command=lambda x="Rejected": self.setStatus(x))
        self.aMenu.add_command(label="Set to Unknown",
                               command=lambda x="Unknown": self.setStatus(x))

        # show treeview of mzML file MS/MS and MS
        scrollbar = Tkinter.Scrollbar(self)
        self.tree = ttk.Treeview(self, yscrollcommand=scrollbar.set)

        columns = {"Mass":70, "error":70, "Peptide":160, "Glycan":160, "Status":80}
        self.tree["columns"] = ("Mass", "error", "Peptide", "Glycan", "Status")
        self.tree.column("#0", width=40)

        self.tree.heading("#0", text="Nr.", command=lambda col='#0': self.sortColumn(col))
        for col in columns:
            self.tree.column(col, width=columns[col])
            self.tree.heading(col, text=col, command=lambda col=col: self.sortColumn(col))

        self.tree.grid(row=0, column=0, sticky=("N", "W", "E", "S"))

        scrollbar.grid(row=0, column=1, sticky=("N", "W", "E", "S"))
        scrollbar.config(command=self.tree.yview)

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

        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=0)

        self.model.classes["NotebookIdentification"] = self

    def setStatus(self,status):
        # get currently active hit
        selection = self.tree.selection()
        if len(selection) == 0:
            return
        for item in selection:
            hit = self.treeIds[item]
            
            if status == "Accepted":
                hit.status = glyxsuite.io.ConfirmationStatus.Accepted
            elif status == "Rejected":
                hit.status = glyxsuite.io.ConfirmationStatus.Rejected
            elif status == "Unknown":
                hit.status = glyxsuite.io.ConfirmationStatus.Unknown
            # Update on Treeview
            values = self.tree.item(item)["values"]
            values[4] = hit.status
            self.tree.item(item, values=values)
            
            taglist = list(self.tree.item(item, "tags"))
            taglist = self.setHighlightingTag(taglist, hit.status)
            self.tree.item(item, tags=taglist)
        
    def popup(self, event):
        self.aMenu.post(event.x_root, event.y_root)
        self.aMenu.focus_set()
        self.aMenu.bind("<FocusOut>", self.removePopup)
        
    def removePopup(self,event):
        if self.focus_get() != self.aMenu:
            self.aMenu.unpost()

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

        # insert all glycomod hits

        index = 0
        for hit in analysis.analysis.glycoModHits:
            
            # check if hit passes filters
            if hit.passesFilter == False:
                continue
                        
            feature = hit.feature
            name = feature.index
            # mass
            mass = (feature.getMZ()-glyxsuite.masses.MASS["H+"])*feature.getCharge()
            peptide = hit.peptide.toString()
            # clean up glycan
            glycan = glyxsuite.lib.Glycan(hit.glycan.composition)

            if index%2 == 0:
                taglist = ("even" + hit.status, "even")
            else:
                taglist = ("odd" + hit.status, "odd")
            index += 1
            itemSpectra = self.tree.insert("", "end", text=name,
                                           values=(round(mass, 4),
                                                   round(hit.error, 4),
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

        # update Extention
        self.model.classes["IdentificationStatsFrame"].init()

    def clickedTree(self, event):
        selection = self.tree.selection()
        if len(selection) == 0:
            return
        elif len(selection) == 1:
            item = selection[0]
            self.model.classes["NotebookFeature"].setSelectedFeature(self.tree.item(item, "text"))
            self.model.classes["ConsensusSpectrumFrame"].init(self.treeIds[item])
            self.model.classes["PeptideCoverageFrame"].init(self.treeIds[item])

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
