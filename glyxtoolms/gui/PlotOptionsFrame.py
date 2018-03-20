import Tkinter

class PlotOptionsFrame(Tkinter.Toplevel):

    def __init__(self, master, model):
        Tkinter.Toplevel.__init__(self, master=master)
        self.master = master
        self.title("Plotting Options")
        self.config(bg="#d9d9d9")
        self.model = model
        self.variables = {}
        self.i = 0
        self.frameRow = {}
        self.oldValues = {}
        for optionname in self.master.options:
            self.oldValues[optionname] = {}
            for key in self.master.options[optionname]:
                self.oldValues[optionname][key] = self.master.options[optionname][key]

        if self.getName() in self.model.toplevel:
            self.model.toplevel[self.getName()].destroy()
        self.model.toplevel[self.getName()] = self

        self.focus_set()
        self.transient(master)
        self.lift()
        self.wm_deiconify()
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        cancelButton = Tkinter.Button(self, text="Cancel", command=self.cancel)
        okButton = Tkinter.Button(self, text="Ok", command=self.ok)

        cancelButton.grid(row=10, column=0, sticky="NWES")
        okButton.grid(row=10, column=1, sticky="NWES")

    def addLabelFrame(self, text):
        frame = ttk.Labelframe(self, text=text)
        frame.grid(row=self.i,column=0, columnspan=2, sticky="NSEW")
        self.i += 1
        frame.row = 0
        return frame

    def addFont(self, frame, optionname, text):
        label = Tkinter.Label(frame, text=text)
        label.grid(row=frame.row,column=0)
        var = Tkinter.IntVar()
        var.set(self.master.options[optionname]["font"].config()["size"])
        entry = Tkinter.Entry(frame, textvariable=var)
        entry.grid(row=frame.row,column=1)
        entry.config(bg="white")
        var.trace("w", lambda a,b,c,d=optionname:self.setFontSize(a,b,c,d))
        if not optionname in self.variables:
            self.variables[optionname] = {}
        self.variables[optionname]["font"] = var
        var.entry = entry
        frame.row += 1

    def setFontSize(self, a,b,c, optionname):
        var = self.variables[optionname]["font"]
        try:
            size = int(var.get())
            var.entry.config(bg="white")
            self.master.options[optionname]["font"] = tkFont.Font(family="Arial",
                                                      size=size)
            self.master._paintCanvas(False)
        except:
            var.entry.config(bg="red")

    def getName(self):
        return "PlotOptionsFrame"

    def on_closing(self):
        if self.getName() in self.model.classes:
            self.model.toplevel.pop(self.getName())
        self.destroy()

    def cancel(self):
        self.master.options = self.oldValues
        self.master._paintCanvas(False)
        self.on_closing()

    def ok(self):
        self.on_closing()
