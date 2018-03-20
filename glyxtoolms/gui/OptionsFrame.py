import Tkinter
import ttk
import tkFileDialog
from glyxtoolms.gui import Appearance

class OptionsFrame(Tkinter.Toplevel):

    def __init__(self, master, model):
        Tkinter.Toplevel.__init__(self, master=master)
        #self.minsize(600, 300)
        self.master = master
        self.title("Options")
        #self.config(bg="#d9d9d9")
        self.model = model
        
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=0)
        self.rowconfigure(1, weight=0)
        self.rowconfigure(2, weight=0)
        self.rowconfigure(3, weight=0)
        self.rowconfigure(4, weight=1)
        
        self.columnconfigure(0, weight=1)
        
        
        frameOpenMS = ttk.Labelframe(self, text="OpenMS/TOPPAS")
        frameOpenMS.grid(row=0, column=0, sticky="NWES")
        frameOpenMS.columnconfigure(0, weight=0)
        frameOpenMS.columnconfigure(1, weight=1)
        buttonOpenMS = Tkinter.Button(frameWorkspace, text="Configure OpenMS", command=self.configureOpenMS)
        
        self.openMSVar = Tkinter.StringVar()
        self.openMSVar.set(self.model.workingdir)
        entryWorkspace = Tkinter.Entry(frameWorkspace, textvariable=self.workspaceVar, width=60)
        
        frameWorkspace = ttk.Labelframe(self, text="Set Workspace")
        frameWorkspace.grid(row=1, column=0, sticky="NWES")
        frameWorkspace.columnconfigure(0, weight=0)
        frameWorkspace.columnconfigure(1, weight=1)
        buttonWorkspace = Tkinter.Button(frameWorkspace, text="Set workspace", command=self.setWorkspace)
        
        self.workspaceVar = Tkinter.StringVar()
        self.workspaceVar.set(self.model.workingdir)
        entryWorkspace = Tkinter.Entry(frameWorkspace, textvariable=self.workspaceVar, width=60)
        
        buttonWorkspace.grid(row=0, column=0, sticky="NWES")
        entryWorkspace.grid(row=0, column=1, sticky="NWES")
        
        frameTimeAxis = ttk.Labelframe(self, text="Timeaxis")
        frameTimeAxis.grid(row=2, column=0, sticky="NWES")
        
        self.timeAxisVar = Tkinter.StringVar()
        self.timeAxisVar.set(self.model.timescale)
        
        timeAxisChoice1 = Appearance.Radiobutton(frameTimeAxis, text="In seconds", variable=self.timeAxisVar, value="seconds")
        timeAxisChoice2 = Appearance.Radiobutton(frameTimeAxis, text="In minutes", variable=self.timeAxisVar, value="minutes")
        
        timeAxisChoice1.grid(row=0, column=0, sticky="NWS")
        timeAxisChoice2.grid(row=0, column=1, sticky="NWS")
        
        frameError = ttk.Labelframe(self, text="Mass Error")
        frameError.grid(row=3, column=0, sticky="NWES")
        
        self.errorVar = Tkinter.StringVar()
        self.errorVar.set(self.model.errorType)
        
        errorChoice1 = Appearance.Radiobutton(frameError, text="In Dalton", variable=self.errorVar, value="Da")
        errorChoice2 = Appearance.Radiobutton(frameError, text="In ppm", variable=self.errorVar, value="ppm")
        
        errorChoice1.grid(row=0, column=0, sticky="NWS")
        errorChoice2.grid(row=0, column=1, sticky="NWS")
        
        frameClipboard = ttk.Labelframe(self, text="Clipboard")
        frameClipboard.grid(row=4, column=0, sticky="NWES")
        
        self.clipVar = Tkinter.StringVar()
        self.clipVar.set(self.model.clipboard)
        
        boards = ('osx','qt','xclip','xsel','klipper','windows')
        # test which boards are available here
        avlBoards = []
        for board in boards:
            try:
                pyperclip.set_clipboard(board)
                avlBoards.append(board)
            except:
                pass
        avlBoards = ['Tkinter'] + avlBoards
        for i, board in enumerate(avlBoards):
            clipboardChoice = Appearance.Radiobutton(frameClipboard, text=board, variable=self.clipVar, value=board)
            clipboardChoice.grid(row=5+i/3, column=1+i%3, sticky="NWS")

        frameDifferences= ttk.Labelframe(self, text="Massdifferences")
        frameDifferences.grid(row=5, column=0, sticky="NWES")
        
        scrollbar = Tkinter.Scrollbar(frameDifferences)
        self.tree = ttk.Treeview(frameDifferences, yscrollcommand=scrollbar.set, selectmode='browse')
        self.columns = ("Mass", "Charge", "Type")
        self.tree["columns"] = self.columns
        self.tree.grid(row=0, column=0, sticky="NWES")
        self.tree["columns"] = self.columns
        self.tree.heading("#0", text="Name", command=lambda col="#0": self.sortColumn(col))
        for col in self.columns:
            self.tree.heading(col, text=col, command=lambda col=col: self.sortColumn(col))
        scrollbar.grid(row=0, column=1, sticky="NWES")
        scrollbar.config(command=self.tree.yview)
        self.tree.bind("<<TreeviewSelect>>", self.clickedTree)
         
        frameEntry = ttk.Labelframe(frameDifferences, text="Entry")
        frameEntry.grid(row=0, column=2, sticky="NWE")
        l1 = ttk.Label(frameEntry,text="Name:")
        l2 = ttk.Label(frameEntry,text="Mass:")
        l3 = ttk.Label(frameEntry,text="Charge:")
        l4 = ttk.Label(frameEntry,text="Type:")
        l1.grid(row=0, column=0, sticky="NW")
        l2.grid(row=1, column=0, sticky="NW")
        l3.grid(row=2, column=0, sticky="NW")
        l4.grid(row=3, column=0, sticky="NW")
        
        self.v1 = Tkinter.StringVar()
        self.v2 = Tkinter.StringVar()
        self.v3 = Tkinter.StringVar()
        self.v4 = Tkinter.StringVar()
        
        self.v1.trace("w", lambda a,b,c:self.valueChanged("v1"))
        self.v2.trace("w", lambda a,b,c:self.valueChanged("v2"))
        self.v3.trace("w", lambda a,b,c:self.valueChanged("v3"))
        self.v4.trace("w", lambda a,b,c:self.valueChanged("v4"))
        
        self.e1 = Tkinter.Entry(frameEntry, textvariable=self.v1)
        self.e2 = Tkinter.Entry(frameEntry, textvariable=self.v2)
        self.e3 = Tkinter.Entry(frameEntry, textvariable=self.v3)
        self.e4 = Tkinter.Entry(frameEntry, textvariable=self.v4)
        self.e1.grid(row=0, column=1, sticky="NW")
        self.e2.grid(row=1, column=1, sticky="NW")
        self.e3.grid(row=2, column=1, sticky="NW")
        self.e4.grid(row=3, column=1, sticky="NW")
        self.e1.config(bg="white")
        self.e2.config(bg="white")
        self.e3.config(bg="white")
        self.e4.config(bg="white")
        
        frameEntry2 = ttk.Frame(frameEntry)
        frameEntry2.grid(row=4, column=0, columnspan=2, sticky="NWES")
        self.b1 = Tkinter.Button(frameEntry2, text="Delete Entry",command=self.deleteEntry)
        self.b2 = Tkinter.Button(frameEntry2, text="New Entry",command=self.newEntry)
        self.b1.grid(row=0, column=0, sticky="SW")
        self.b2.grid(row=0, column=1, sticky="SE")

        # add data
        for mass, name, charge, typ in self.model.massdifferences:
            self.tree.insert("", "end", text=name,
                                           values = (str(round(mass,4)), str(charge), typ))
            
        self.sorting = ("#0", False)
        frameButtons = ttk.Frame(self)
        frameButtons.grid(row=5, column=0, sticky="NWES")
        
        cancelButton = Tkinter.Button(frameButtons, text="Cancel", command=self.cancel)        
        saveButton = Tkinter.Button(frameButtons, text="Save options", command=self.save)

        cancelButton.grid(row=0, column=0, sticky="NWES")
        saveButton.grid(row=0, column=1, sticky="NWES")
        
    def configureOpenMS(self):
        pass

        
    def setWorkspace(self):
        options = {}
        options['initialdir'] = self.workspaceVar.get()
        options['title'] = 'Set Workspace'
        options['mustexist'] = True
        path = tkFileDialog.askdirectory(**options)
        if path == "" or path == ():
            return
        self.workspaceVar.set(path)
        
    def cancel(self):
        self.destroy()
    
    def save(self):
        self.model.workingdir = self.workspaceVar.get()
        self.model.timescale = self.timeAxisVar.get()
        self.model.clipboard = self.clipVar.get()
        self.model.errorType = self.errorVar.get()
        
        # get mass difference values from tree
        massdifferences = []
        for itemid in self.tree.get_children():
            data = self.tree.item(itemid)
            mass, charge, typ = data["values"]
            name = data["text"]
            charge = int(charge)
            mass = float(mass)
            massdifferences.append((mass, name, charge, typ))
        self.model.massdifferences = sorted(massdifferences)
        self.model.saveSettings()
        # update plots
        self.model.classes["NotebookIdentification"].updateTree()
        self.model.classes["NotebookFeature"].updateTree()
        self.model.classes["ConsensusSpectrumFrame"]._paintCanvas()
        
        self.destroy()
        
    def valueChanged(self, varname):
        selection = self.tree.selection()
        if len(selection) != 1:
            return
        itemid = selection[0]
        if varname == "v1":
            name = self.v1.get()
            self.tree.item(itemid, text=name)
        elif varname == "v2":
            mass = self.v2.get()
            try:
                float(mass)
                self.tree.set(itemid, column="Mass", value=mass)
                self.e2.config(bg="white")
            except:
                self.e2.config(bg="red")
        elif varname == "v3":
            charge = self.v3.get()
            try:
                int(charge)
                self.tree.set(itemid, column="Charge", value=charge)
                self.e3.config(bg="white")
            except:
                self.e3.config(bg="red")
        else:
            typ = self.v4.get()
            self.tree.set(itemid, column="Type", value=typ)
        
        
    def clickedTree(self, event):
        selection = self.tree.selection()
        if len(selection) != 1:
            self.v1.set("")
            self.v2.set("")
            self.v3.set("")
            self.v4.set("")
            return
        itemid = selection[0]
        
        data = self.tree.item(itemid)
        mass, charge, typ = data["values"]
        name = data["text"]
        self.v1.set(name)
        self.v2.set(mass)
        self.v3.set(charge)
        self.v4.set(typ)
        
    def deleteEntry(self,*arg, **args):
        selection = self.tree.selection()
        if len(selection) != 1:
            return
        itemid = selection[0]
        self.tree.delete(itemid)
        self.clickedTree(None)

    def newEntry(self,*arg, **args):
        itemid = self.tree.insert("", "end", text="-",
                                  values = ("0.0", "1", "?"))
        self.tree.selection_set(itemid)
        self.tree.see(itemid)
        
    def sortColumn(self, col):

        sortingColumn, reverse = self.sorting
        if col == sortingColumn:
            reverse = not reverse
        else:
            sortingColumn = col
            reverse = False
        self.sorting = (sortingColumn, reverse)

        if col == "Mass":
            l = [(float(self.tree.set(k, col)), k) for k in self.tree.get_children('')]
        elif col == "#0":
            l = [(self.tree.item(k, "text"),k) for k in self.tree.get_children('')]
        else:
            l = [(self.tree.set(k, col), k) for k in self.tree.get_children('')]
        l.sort(reverse=reverse)

        # rearrange items in sorted positions
        for index, (val, k) in enumerate(l):
            self.tree.move(k, '', index)
