import ttk
import Tkinter
import tkMessageBox
import random

import numpy as np

import glyxtoolms
from glyxtoolms.gui import AddIdentificationFrame
from glyxtoolms.gui import TreeTable
from glyxtoolms.gui import TagEditorWindow


class FragmentIonTable(TreeTable.TreeTable):

    def __init__(self, master, model):
        TreeTable.TreeTable.__init__(self, master, model)
        self.tree.bind("a", lambda e: self.setStatus("Accepted"))
        self.tree.bind("u", lambda e: self.setStatus("Unknown"))
        self.tree.bind("r", lambda e: self.setStatus("Rejected"))
        self.tree.bind("<Button-3>", self.popup)
        self.hit = None
        self.fragmentToItem = {}

    def identifier(self):
        return "FragmentIonTable"

    def initializeColumnHeader(self):

        self.columns = ["Type", "z", "th. Mass", "obs. Mass", "error", "Intensity", "Status"]
        self.columnNames = {"Type":"Type", "z":"z", "th. Mass":"th. Mass", "obs. Mass":"obs. Mass", "error":"Error [ppm]", "Intensity":"Intensity", "Status":"Status"}
        self.columnsWidth = {"Intensity":80, "z":20, "th. Mass":80, "obs. Mass":80, "Type":80, "error":80, "Status":80}

        self.showColumns = {}
        for name in self.columns:
            self.showColumns[name] = Tkinter.BooleanVar()
            self.showColumns[name].set(True)
            self.showColumns[name].trace("w", self.columnVisibilityChanged)

        self.tree.column("#0", width=80)
        self.tree.heading("#0", text="Fragment Name", command=lambda col='#0': self.sortColumn(col))


        self.tree["columns"] = self.columns
        for col in self.columns:
            self.tree.column(col, width=self.columnsWidth[col])
            self.tree.heading(col, text=col, command=lambda col=col: self.sortColumn(col))

        self.setHeadingNames()



    def setStatus(self,status):
        # get currently active hit
        selection = self.tree.selection()
        if len(selection) == 0:
            return
        for item in selection:
            fragment = self.treeIds[item]

            if status == "Accepted":
                fragment.status = glyxtoolms.io.ConfirmationStatus.Accepted
            elif status == "Rejected":
                fragment.status = glyxtoolms.io.ConfirmationStatus.Rejected
            elif status == "Unknown":
                fragment.status = glyxtoolms.io.ConfirmationStatus.Unknown
            # Update on Treeview
            values = self.tree.item(item)["values"]
            values[6] = fragment.status

            taglist = list(self.tree.item(item, "tags"))
            taglist = self.setHighlightingTag(taglist, fragment.status)
            self.tree.item(item, values=values, tags=taglist)
            
            # set isotopes if available
            for childItem in self.tree.get_children(item):
                childFragment = self.treeIds[childItem]
                childFragment.status = fragment.status
                values = self.tree.item(childItem)["values"]
                values[6] = fragment.status
                self.tree.item(childItem, values=values, tags=taglist)
        self.model.classes["PeptideCoverageFrame"].paint_canvas()
        self.model.classes["ConsensusSpectrumFrame"]._paintCanvas()
        
            

    def seeItem(self, feature):
        itemId = self.featureItems[feature.getId()]
        self.tree.see(itemId)

    def setHeadingNames(self):
        if self.model.errorType == "Da":
            self.columnNames["error"] = "Error [Da]"
        else:
            self.columnNames["error"] = "Error [ppm]"
        for col in self.columnNames:
            self.tree.heading(col, text=self.columnNames.get(col, col),command=lambda col=col: self.sortColumn(col))

    def updateHeader(self):
        # append possible ToolValue Columns and Tag column
        if self.model.currentAnalysis != None and not "Tag" in self.columns:
            for columnname in self.columns:
                self.columnsWidth[columnname] = self.tree.column(columnname, "width")
            for toolname in self.model.currentAnalysis.analysis.toolValueDefaults:
                if toolname in self.columns:
                    continue
                self.toolNameOrder.append(toolname)
                self.columns.append(toolname)
                self.columnNames[toolname] = toolname
                self.columnsWidth[toolname] = 80
                self.showColumns[toolname] = Tkinter.BooleanVar()
                self.showColumns[toolname].set(False)
                self.showColumns[toolname].trace("w", self.columnVisibilityChanged)
            self.tree["columns"] = self.columns
            self.setHeadingNames()
            for columnname in self.columns:
                self.tree.column(columnname, width=self.columnsWidth[columnname])

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
            self.aMenu.add_command(label="Set to  Rejected",
                                   command=lambda x="Rejected": self.setStatus(x))
            self.aMenu.add_command(label="Set to Unknown",
                                   command=lambda x="Unknown": self.setStatus(x))
            self.aMenu.add_separator()
            self.aMenu.add_command(label="Show in Spectrum",
                       command=self.showSelectedFragments)
            #self.aMenu.add_separator()
            #self.aMenu.add_command(label="Change Feature",
            #                       command=self.changeFeature)
            #self.aMenu.add_command(label="Copy Feature",
            #                       command=self.copyFeature)
            #self.aMenu.add_command(label="Add Identification",
            #                       command=self.addIdentification)
            #self.aMenu.add_separator()
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
    
    def showSelectedFragments(self):
        selection = self.tree.selection()
        if len(selection) == 0:
            return
        names = []
        for item in selection:
            fragment = self.treeIds[item]
            names.append(fragment.name)
        #self.model.classes["ConsensusSpectrumFrame"].plotSelectedFragments(names,zoomIn=True)
        self.model.classes["PeptideCoverageFrame"].indexList = set()
        self.model.classes["PeptideCoverageFrame"].colorIndex(found=names)
        self.model.classes["main"].switchToSpectrumNotebook()

    def sortColumn(self, col):

        if self.model == None or self.model.currentAnalysis == None:
            return
        sortingColumn, reverse = self.model.currentAnalysis.sorting[self.identifier()]
        if col == sortingColumn:
            reverse = not reverse
        else:
            sortingColumn = col
            reverse = False
        self.model.currentAnalysis.sorting[self.identifier()] = (sortingColumn, reverse)

        children = self.tree.get_children('')
        if col == "#0":
            l = [(self.tree.item(k, "text"), k) for k in children]
        elif col in ["Type","Status"]:
            l = [(self.tree.set(k, col), k) for k in children]
        elif col in ["z"]:
            l = [(int(self.tree.set(k, col).split("/")[0]), k) for k in children]
        elif col == "error":
            l = [(abs(float(self.tree.set(k, col))), k) for k in children]
        else:
            l = [(float(self.tree.set(k, col)), k) for k in children]

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
            else:
                taglist.append("odd")
            taglist = self.setHighlightingTag(taglist, status)
            self.tree.item(k, tags=taglist)
            for childItem in self.tree.get_children(k):
                self.tree.item(childItem, tags=taglist)
                

    def addFragmentToTree(self, fragment, parentItem):
        # ["Type", "z", "th. Mass", "obs. Mass", "Error", "Intensity", "Status"]
        # error
        error = fragment.peak.x-fragment.mass
        if self.model.errorType == "Da":
            error = round(error, 4)
        else:
            error = round(error/float(fragment.mass)*1E6, 1)
        
        values = [fragment.typ,
                  fragment.charge,
                  round(fragment.mass,4),
                  round(fragment.peak.x, 4),
                  error,
                  round(fragment.peak.y, 1),
                  fragment.status
                  ]
        item = self.tree.insert(parentItem, "end", text=fragment.name,
                                       values=values)
        self.treeIds[item] = fragment
        self.fragmentToItem[fragment.name] = item
        return item

    def updateTree(self, hit):

            
        # clear tree
        self.tree.delete(*self.tree.get_children())
        self.treeIds = {}
        self.fragmentToItem = {}
        self.setHeadingNames()
        
        self.hit = hit
        if self.hit == None:
            return


        for fragment in self.hit.fragments.values():
            if fragment.typ == glyxtoolms.fragmentation.FragmentType.ISOTOPE:
                continue
            parentIndex = self.addFragmentToTree(fragment, "")
            for child in sorted(fragment.children, key = lambda frag: frag.mass):
                if child.typ != glyxtoolms.fragmentation.FragmentType.ISOTOPE:
                    continue
                self.addFragmentToTree(child, parentIndex)

        # apply possible sorting
        if not self.identifier() in self.model.currentAnalysis.sorting:
            self.model.currentAnalysis.sorting[self.identifier()] = ("#0", False)

        sortingColumn, reverse = self.model.currentAnalysis.sorting[self.identifier()]
        self.model.currentAnalysis.sorting[self.identifier()] = (sortingColumn, not reverse)
        self.sortColumn(sortingColumn)


    def clickedTree(self, event):
        return

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
        
    def selectFragments(self, names):
        selected_items = []
        for name in set(names):
            if name in self.fragmentToItem:
                item = self.fragmentToItem[name]
                selected_items.append(item)
                self.tree.see(item)
        self.tree.selection_set(tuple(selected_items))
