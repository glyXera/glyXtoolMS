"""
Viewer for analysis file
a) MS/MS spectra, annotation
b) scored spectra
c) scored features
d) Histogram

GUI:
|---------------------------------------------------|
|         Menubar                                   |
|---------------------------------------------------|
|   Project   |  tab structure, context dependend   |
|   control   |                                     |
|             |                                     |
|-------------|                                     |
| ProjectView |                                     |
|             |                                     |
|             |                                     |
|             |                                     |
|             |                                     |
|             |                                     |
|             |                                     |
|             |                                     |
|---------------------------------------------------|
"""

import Tkinter
import ttk
import tkFileDialog

from glyxsuite.gui import DataModel
from glyxsuite.gui import ProjectFrame
from glyxsuite.gui import NotebookScoring
from glyxsuite.gui import NotebookFeature
from glyxsuite.gui import NotebookIdentification
from glyxsuite.gui import ExtensionScoring
from glyxsuite.gui import ExtensionFeature
from glyxsuite.gui import HistogramView
from glyxsuite.gui import ExtensionIdentification

class App(ttk.Frame):

    def __init__(self, master):

        ttk.Frame.__init__(self)

        self.master = master
        menubar = Tkinter.Menu(self.master, bg="#d9d9d9")
        self.master.config(menu=menubar)
        self.master.config(bg="#d9d9d9")
        self.model = DataModel.DataModel()

        self.model.root = master

        filemenu = Tkinter.Menu(menubar, tearoff=0, bg="#d9d9d9")
        filemenu.add_command(label="Set workspace", command=self.setWorkspace)
        filemenu.add_separator()
        filemenu.add_command(label="Exit", command=self.master.destroy)
        menubar.add_cascade(label="Program", menu=filemenu)

        projectMenu = Tkinter.Menu(menubar, tearoff=0, bg="#d9d9d9")
        projectMenu.add_command(label="New Project")
        projectMenu.add_command(label="Open Analysis")
        projectMenu.add_command(label="Save Analysis")
        projectMenu.add_separator()
        projectMenu.add_command(label="Close Project")
        projectMenu.add_command(label="Close Analysis")
        menubar.add_cascade(label="Project", menu=projectMenu)

        statisticsMenu = Tkinter.Menu(menubar, tearoff=0, bg="#d9d9d9")
        statisticsMenu.add_command(label="Scorehistogram", command=self.showHistogram)
        menubar.add_cascade(label="Statistics", menu=statisticsMenu)

        #toolMenu = Tkinter.Menu(menubar, tearoff=0, bg="#d9d9d9")
        #menubar.add_cascade(label="Tool", menu=toolMenu)

        frameProject = ttk.Labelframe(master, text="Projects")
        pojectFrame = ProjectFrame.ProjectFrame(frameProject, self.model)
        #pojectFrame.pack()
        pojectFrame.grid(row=0, column=0, sticky=("N", "W", "E", "S"))
        frameProject.grid(row=0, column=0, sticky=("N"))


        frameNotebook = ttk.Labelframe(master, text="Analysis")
        frameNotebook.grid(row=1, column=0, sticky=("NWES"))
        frameNotebook.rowconfigure(0, weight=1)


        self.notebook = ttk.Notebook(frameNotebook)

        n1 = NotebookIdentification.NotebookIdentification(self.notebook, self.model)
        n2 = NotebookFeature.NotebookFeature(self.notebook, self.model)
        n3 = NotebookScoring.NotebookScoring(self.notebook, self.model)
        
        
        self.notebook.add(n1, text='1. Identification')
        self.notebook.add(n2, text='2. Features')
        self.notebook.add(n3, text='3. Scoring')
        #self.notebook.add(n4, text='4. Results')

        #self.notebook.grid(row=1, column=0, sticky=("N", "W", "E"))
        self.notebook.grid(row=0, column=0, sticky="NWES")

        self.notebook.bind("<<NotebookTabChanged>>", self.changedNotebook)



        # Add extention frames
        
        self.e1 = ExtensionIdentification.ExtensionIdentification(master, self.model, '1. Identification')
        self.e1.grid(row=0, column=1, rowspan=2, sticky="NWES")
        
        self.e2 = ExtensionFeature.ExtensionFeature(master, self.model, '2. Features')
        self.e2.grid(row=0, column=1, rowspan=2, sticky="NWES")
        
        self.e3 = ExtensionScoring.ExtensionScoring(master, self.model, '3. Scoring')
        self.e3.grid(row=0, column=1, rowspan=2, sticky="NWES")

        # configure column and row behaviour
        self.master.columnconfigure(0, minsize=200, weight=0)
        self.master.columnconfigure(1, minsize=300, weight=1)
        self.master.rowconfigure(0, weight=0)
        self.master.rowconfigure(1, weight=1)
        #self.master.rowconfigure(1, minsize=200, weight=1)

    def changedNotebook(self, event):
        idx = self.notebook.select()
        # hide all extensions
        self.e1.lower()
        self.e2.lower()
        self.e3.lower()
        # show selected extension
        text = self.notebook.tab(idx, "text")
        if "1" in text:
            self.e1.lift()
        elif "2" in text:
            self.e2.lift()
        elif "3" in text:
            self.e3.lift()

    def showHistogram(self):
        if self.model.currentAnalysis == None:
            return
        if self.model.currentAnalysis.analysis == None:
            return
        HistogramFrame(self.master, self.model)
        return

    def setWorkspace(self):
        options = {}
        options['initialdir'] = self.model.workingdir
        options['title'] = 'Set Workspace'
        options['mustexist'] = True
        path = tkFileDialog.askdirectory(**options)
        if path == "" or path == ():
            return
        self.model.workingdir = path
        self.model.saveSettings()
        return

def run():
    global app
    root = Tkinter.Tk()
    root.title("glyXtool-MS Viewer")
    app = App(root)
    root.mainloop()
    return app


class HistogramFrame(Tkinter.Toplevel):

    def __init__(self, master, model):
        Tkinter.Toplevel.__init__(self, master=master)
        self.master = master
        self.title("Score Histogram")
        self.config(bg="#d9d9d9")
        self.model = model
        self.view = HistogramView.HistogramView(self, model, height=450, width=500)
        self.view.grid(row=0, column=0, columnspan=2, sticky="NW")

        analysisFile = self.model.currentAnalysis.analysis

        l1 = ttk.Label(self, text="Score-Threshold:")
        l1.grid(row=1, column=0, sticky="NE")
        self.v1 = Tkinter.StringVar()
        c1 = ttk.Entry(self, textvariable=self.v1)
        c1.grid(row=1, column=1, sticky="NW")
        self.v1.set(analysisFile.parameters.getScoreThreshold())

        #l2 = Tkinter.Label(self, text="Score-Threshold:")
        #l2.grid(row=1, column=0, sticky="NE")
        b2 = Tkinter.Button(self, text="set Score-Threshold", command=self.validateEntry)
        b2.grid(row=2, column=1, sticky="NW")

        b3 = Tkinter.Button(self, text="close", command=self.close)
        b3.grid(row=3, column=1, sticky="NW")
        self.makeHistogram()

    def makeHistogram(self):
        self.view.bins = {}
        self.view.colors = {}
        # calculate series
        seriesGlyco = []
        seriesNon = []
        for ms1, spectrum in self.model.currentAnalysis.data:
            if spectrum.logScore >= 10:
                continue
            if spectrum.isGlycopeptide == True:
                seriesGlyco.append(spectrum.logScore)
            else:
                seriesNon.append(spectrum.logScore)
        self.view.addSeries(seriesGlyco, label="glyco", color="green")
        self.view.addSeries(seriesNon, label="noglyco", color="blue")
        self.view.initHistogram(self.model.currentAnalysis.analysis.parameters.getScoreThreshold())

    def close(self):
        self.destroy()


    def validateEntry(self):
        try:
            newThreshold = float(self.v1.get())
            self.model.currentAnalysis.analysis.parameters.setScoreThreshold(newThreshold)
            self.view.initHistogram(newThreshold)
            for spectrum in self.model.currentAnalysis.analysis.spectra:
                spectrum.isGlycopeptide = spectrum.logScore < newThreshold
            self.model.funcUpdateNotebookScoring()
            self.makeHistogram()
        except ValueError:
            print "cannot convert"
            self.v1.set(self.model.currentAnalysis.analysis.parameters.getScoreThreshold())


