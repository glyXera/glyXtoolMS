import ttk
import Tkinter
import tkFileDialog
import tkMessageBox
import os
import pyperclip
import glyxtoolms
from glyxtoolms.gui import TreeTable
from glyxtoolms.gui import TagEditorWindow



class NotebookIdentification(TreeTable.TreeTable):

    def __init__(self, master, model):
        TreeTable.TreeTable.__init__(self, master, model)

        self.features = []
        self.tree.bind("<Button-3>", self.popup)

        self.tree.bind("a", lambda e: self.setStatus("Accepted"))
        self.tree.bind("u", lambda e: self.setStatus("Unknown"))
        self.tree.bind("r", lambda e: self.setStatus("Rejected"))

        #self.model.registerClass("NotebookIdentification", self)

        #self.model.currentAnalysis = glyxtoolms.io.GlyxXMLFile()
        #self.model.currentAnalysis.readFromFile("/afs/mpi-magdeburg.mpg.de/data/bpt/personnel_folders/MarkusPioch/temp/example/20160417_MH_IgG_FASP_Tryp_HILIC_Enri_HCDstep.xml")

    def identifier(self):
        return "NotebookIdentification"

    def initializeColumnHeader(self):

        self.columns = ["Mass", "error", "Peptide", "Glycan", "Status", "Tags"]
        self.columnNames = {"Mass":"Mass [Da]", "error":"Error", "Peptide":"Peptide", "Glycan":"Glycan", "Status":"Status", "Tags":"Tags"}
        self.columnsWidth = {"Mass":70, "error":80, "Peptide":150, "Glycan":160, "Status":80, "Tags":80}
        self.toolNameOrder = []

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

    def setHeadingNames(self):

        if self.model.errorType == "Da":
            self.columnNames["error"] = "Error [Da]"
        else:
            self.columnNames["error"] = "Error [ppm]"
        for col in self.columnNames:
            self.tree.heading(col, text=self.columnNames.get(col, col),command=lambda col=col: self.sortColumn(col))

    def openOptions(self):
        pass
        #hits = [self.model.currentAnalysis.glycoModHits[0]]
        #TagEditorWindow.TagEditorWindow(self, self.model, hits)

    def editTags(self, *arg, **args):
        # get currently active hit
        selection = self.tree.selection()
        if len(selection) == 0:
            return
        hits = []
        for item in selection:
            hit  = self.treeIds[item]
            hits.append(hit)
        TagEditorWindow.TagEditorWindow(self, self.model, hits, self.updateTagsView)

    def updateTagsView(self):
        # get currently active hit
        selection = self.tree.selection()
        if len(selection) == 0:
            return
        for item in selection:
            hit  = self.treeIds[item]
            values = self.tree.item(item)["values"]
            values[5] = ", ".join(hit.tags)
            self.tree.item(item, values=values)

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
            self.aMenu.add_command(label="Edit Tags",
                       command=self.editTags)
            #editmenu = Tkinter.Menu(self.aMenu, tearoff=0)
            #self.aMenu.menus=[self.aMenu, editmenu]
            #editmenu.add_command(label="Open")
            #self.aMenu.add_cascade(label="Edit Tag", menu=editmenu)
            self.aMenu.add_separator()
            self.aMenu.add_command(label="Copy to Clipboard",
                                   command=self.copyToClipboard)
        self.aMenu.post(event.x_root, event.y_root)
        self.aMenu.focus_set()
        self.aMenu.bind("<FocusOut>", self.removePopup)

    def removePopup(self,event):
        try: # catch bug in Tkinter with tkMessageBox. TODO: workaround
            if self.focus_get() != self.aMenu:
            #if self.focus_get() not in self.aMenu.menus:
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
        elif col in self.model.currentAnalysis.analysis.toolValueDefaults:
            default = self.model.currentAnalysis.analysis.toolValueDefaults[col]
            l = [(default.fromString(self.tree.set(k, col)), k) for k in self.tree.get_children('')]
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
            tags = ", ".join(hit.tags)

            values=[round(mass, 4),
                    error,
                    peptide,
                    glycan.toString(),
                    hit.status,
                    tags]

            # add toolvalues
            for toolname in self.toolNameOrder:
                # get toolvalue default
                toolValueDefault = analysis.analysis.toolValueDefaults.get(toolname, None)
                if toolValueDefault == None:
                    values.append("")
                elif toolname in hit.toolValues:
                    values.append(toolValueDefault.toString(hit.toolValues[toolname]))
                else:
                    # get default value
                    values.append(toolValueDefault.toString(toolValueDefault.default))

            itemSpectra = self.tree.insert("", "end", text=name,
                                           values = values,
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
            self.model.classes["NotebookScoring"].seeItem(hit.feature)
            self.model.classes["NotebookFeature"].plotSelectedFeatures([hit.feature], hit)
            self.model.classes["NotebookFeature"].seeItem(hit.feature)
            self.model.classes["PeptideCoverageFrame"].init(hit)

            self.update()
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
        self.model.classes["NotebookFeature"].updateTree()
