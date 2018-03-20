import ttk
import Tkinter
import tkFileDialog
import tkMessageBox
import os
import pyperclip

import glyxtoolms


class TreeTable(ttk.Frame):

    def __init__(self, master, model):
        ttk.Frame.__init__(self, master=master)
        self.master = master
        self.model = model

        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=0)
        self.rowconfigure(0,weight=0)
        self.rowconfigure(1,weight=1)

        # create popup menu
        self.aMenu = Tkinter.Menu(self, tearoff=0)

        # show treeview of mzML file MS/MS and MS
        self.options = Tkinter.Button(self,image=self.model.resources["options"],command=self.openOptions)
        scrollbar = Tkinter.Scrollbar(self)
        self.tree = ttk.Treeview(self, yscrollcommand=scrollbar.set, selectmode='extended')

        self.initializeColumnHeader()

        self.tree.grid(row=0, column=0, rowspan=2, sticky=("N", "W", "E", "S"))

        scrollbar.grid(row=1, column=1, sticky="NWES")
        scrollbar.config(command=self.tree.yview)
        self.options.grid(row=0, column=1)

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

        self.tree.bind("<Control-Key-a>", self.selectAllRows)
        self.tree.bind("<Control-Key-c>", self.copyToClipboard)

        self.model.registerClass(self.identifier(), self)

    def initializeColumnHeader(self):
        raise Exception("Overwrite this function!")

    def identifier(self):
        raise Exception("Overwrite this function!")

    def clickedTree(self, event):
        raise Exception("Overwrite this function!")

    def columnVisibilityChanged(self, *arg, **args):
        header = []
        for columnname in self.columns:
            self.columnsWidth[columnname] = self.tree.column(columnname, "width")
            if self.showColumns[columnname].get() == True:
                header.append(columnname)
        self.tree["displaycolumns"] = tuple(header)
        space = self.grid_bbox(column=0, row=0, col2=0, row2=0)[2]
        width = space/(len(header)+1)
        rest = space%(len(header)+1)
        for column in ["#0"] + header:
            self.tree.column(column, width=width+rest)
            rest = 0

    def selectAllRows(self, event):
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

    def openOptions(self):
        pass
