"""
Viewer for analysis file
GUI:
|---------------------------------------------------|
|         Menubar                                   |
|---------------------------------------------------|
| Feature list | 2D View  | Chroma    |  Isotope    |
|                         | togram    |  pattern    |
|                         |           |             |
|                         |           |             |
|-------------------------|-------------------------|
| Identifications|Spectra |  Spectrumview           |
|                         |                         |
|                         |   Consensusspectrum     |
|                         |   or                    |
|                         |   single spectrum       |
|                         |   depending on tab      |
|---------------------------------------------------|
"""

import Tkinter
import ttk
import tkFileDialog

from glyxtoolms.gui import DataModel
from glyxtoolms.gui import ProjectFrame
from glyxtoolms.gui import NotebookScoring2
from glyxtoolms.gui import FeaturesFrame
from glyxtoolms.gui import NotebookIdentification
from glyxtoolms.gui import ExtensionScoring
from glyxtoolms.gui import ExtensionFeature
from glyxtoolms.gui import HistogramView
from glyxtoolms.gui import ExtensionIdentification
from glyxtoolms.gui import FilterPanel
from glyxtoolms.gui import ConsensusSpectrumFrame
from glyxtoolms.gui import FeaturePrecursorView
from glyxtoolms.gui import FeatureChromatogramView
from glyxtoolms.gui import TwoDView
from glyxtoolms.gui import SpectrumView2
from glyxtoolms.gui import PeptideCoverageFrame
from glyxtoolms.gui import OxoniumIonPlot

class App(ttk.Frame):

    def __init__(self, master):

        ttk.Frame.__init__(self)

        self.master = master
        self.menubar = Tkinter.Menu(self.master, bg="#d9d9d9")
        self.master.config(menu=self.menubar)
        self.master.config(bg="#d9d9d9")
        self.model = DataModel.DataModel()
        

        self.model.root = master
        
        filemenu = Tkinter.Menu(self.menubar, tearoff=0, bg="#d9d9d9")
        #filemenu.add_command(label="Set workspace", command=self.setWorkspace)
        filemenu.add_command(label="Options", command=self.setOptions)
        filemenu.add_separator()
        filemenu.add_command(label="Exit", command=self.master.destroy)
        self.menubar.add_cascade(label="Program", menu=filemenu)

        projectMenu = Tkinter.Menu(self.menubar, tearoff=0, bg="#d9d9d9")
        projectMenu.add_command(label="New Project")
        projectMenu.add_command(label="Open Analysis")
        projectMenu.add_command(label="Save Analysis")
        projectMenu.add_separator()
        projectMenu.add_command(label="Close Project")
        projectMenu.add_command(label="Close Analysis")
        self.menubar.add_cascade(label="Project", menu=projectMenu)

        statisticsMenu = Tkinter.Menu(self.menubar, tearoff=0, bg="#d9d9d9")
        statisticsMenu.add_command(label="Scorehistogram", command=self.showHistogram)
        statisticsMenu.add_command(label="Oxoniumion Plot", command=self.showOxoniumPlot)
        self.menubar.add_cascade(label="Statistics", menu=statisticsMenu)

        filterMenu = Tkinter.Menu(self.menubar, tearoff=0, bg="#d9d9d9")
        filterMenu.add_command(label="Set Filter Options", command=self.showFilterOptions)
        self.menubar.add_cascade(label="Filter", menu=filterMenu) # Index 4 in menubar

        # Divide left and right
        panes = Tkinter.PanedWindow(master, orient="horizontal")
        panes.config(sashwidth=10)
        panes.config(opaqueresize=False)
        panes.config(sashrelief="raised")
        panes.pack(fill="both", expand="yes")
        
        left = Tkinter.PanedWindow(panes, orient="vertical")
        left.pack(fill="both", expand="yes")
        left.config(sashwidth=10)
        left.config(opaqueresize=False)
        left.config(sashrelief="raised")

        right = Tkinter.PanedWindow(panes, orient="vertical")
        right.pack(fill="both", expand="yes")
        right.config(sashwidth=10)
        right.config(opaqueresize=False)
        right.config(sashrelief="raised")

        panes.add(left)
        panes.add(right)

        leftTop = Tkinter.Frame(left,width=100, height=100)
        leftTop.pack()
        leftBottom = Tkinter.Frame(left,width=100, height=100)
        leftBottom.pack()
        
        left.add(leftTop)
        left.add(leftBottom)
        
        # ---- Left side -----
        frameProject = ProjectFrame.ProjectFrame(leftTop, self.model)
        frameProject.pack(fill="both", expand="yes")

        notebookLeft = ttk.Notebook(leftBottom)
        notebookLeft.pack(fill="both", expand="yes")
        
        notebookLeft_n1 = Tkinter.PanedWindow(notebookLeft, orient="vertical")
        notebookLeft_n1.config(sashwidth=10)
        notebookLeft_n1.config(opaqueresize=False)
        notebookLeft_n1.config(sashrelief="raised")
        
        frameFeature = FeaturesFrame.NotebookFeature(notebookLeft_n1, self.model)
        frameFeature.pack(fill="both", expand="yes")
        
        frameChrom = ttk.Frame(notebookLeft_n1)
        frameChrom.pack(fill="both", expand="yes")
        frameChrom.columnconfigure(0,weight=1)
        frameChrom.columnconfigure(1,weight=1)
        frameChrom.rowconfigure(0,weight=1)
        
        notebookLeft_n1.add(frameFeature)
        notebookLeft_n1.add(frameChrom)
        
        notebookLeft_n2 = TwoDView.TwoDView(notebookLeft, self.model)
        
        notebookLeft.add(notebookLeft_n1, text='FeatureList')
        notebookLeft.add(notebookLeft_n2, text='2DView')
        
        chromFrame = ttk.Labelframe(frameChrom, text="Precursor Chromatogram")
        chromFrame.grid(row=0, column=0, sticky="NWES")
        chromView = FeatureChromatogramView.FeatureChromatogramView(chromFrame, self.model)
        chromView.grid(row=0, column=0, sticky="NWES")
        chromFrame.columnconfigure(0, weight=1)
        chromFrame.rowconfigure(0, weight=1)

        msFrame = ttk.Labelframe(frameChrom, text="Precursorspectrum")
        msFrame.grid(row=0, column=1, sticky="NWES")
        msView = FeaturePrecursorView.PrecursorView(msFrame, self.model)
        msView.grid(row=0, column=0, sticky="NWES")
        msFrame.columnconfigure(0, weight=1)
        msFrame.rowconfigure(0, weight=1)
        
        # ---- Right side -----
        notebook = ttk.Notebook(right)
        notebook.pack(fill="both", expand="yes")
        
        n1 = Tkinter.PanedWindow(notebook, orient="vertical")
        n1.config(sashwidth=10)
        n1.config(opaqueresize=False)
        n1.config(sashrelief="raised")
        
        n1_top = NotebookIdentification.NotebookIdentification(n1, self.model)
        n1_top.pack()
        n1_middle = PeptideCoverageFrame.PeptideCoverageFrame(n1, self.model)
        n1_middle.pack()
        n1_bottom = ConsensusSpectrumFrame.ConsensusSpectrumFrame(n1, self.model)
        n1_bottom.pack()
        
        n1.add(n1_top)
        n1.add(n1_middle)
        n1.add(n1_bottom)
        
        n2 = Tkinter.PanedWindow(notebook, orient="vertical")
        n2.config(sashwidth=10)
        n2.config(opaqueresize=False)
        n2.config(sashrelief="raised")
        
        n2_top = NotebookScoring2.NotebookScoring(n2, self.model)
        n2_top.pack()
        
        n2_bottom = SpectrumView2.SpectrumView(n2, self.model)
        n2_bottom.pack()
        
        n2.add(n2_top)
        n2.add(n2_bottom)
        
        notebook.add(n1, text='Identifications')
        notebook.add(n2, text='Spectra')

        self.model.classes["main"] = self
        
               
    def setActiveFilterHint(self, hasActiveFilter):
        if hasActiveFilter == True:
            self.menubar.entryconfig(4, background="#e60000")
            self.menubar.entryconfig(4, activebackground="#b30000")
        else:
            self.menubar.entryconfig(4, background="#d9d9d9")
            self.menubar.entryconfig(4, activebackground="#d6d2d0")


    def changedNotebook(self, event):
        idx = self.notebook.select()
        text = self.notebook.tab(idx, "text")
        if text == "Identifications":
            self.spectrumFrame1.lift()
            self.spectrumFrame2.lower()
        else:
            self.spectrumFrame1.lower()
            self.spectrumFrame2.lift()

    def showHistogram(self):
        if self.model.currentAnalysis == None:
            return
        if self.model.currentAnalysis.analysis == None:
            return
        HistogramFrame(self.master, self.model)
        return
        
    def showOxoniumPlot(self):
        if "OxoniumFrame" in self.model.toplevel:
            self.model.toplevel["OxoniumFrame"].destroy()
        frame = OxoniumFrame(self, self.model)
        self.model.toplevel["OxoniumFrame"] = frame
        
    def showFilterOptions(self):
        FilterPanel.FilterPanel(self.master, self.model)
        
    def setOptions(self):
        OptionsFrame(self.master, self.model)
        

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
    root.title("glyXtool-MS Evaluator")
    app = App(root)
    root.mainloop()
    return app

class OptionsFrame(Tkinter.Toplevel):

    def __init__(self, master, model):
        Tkinter.Toplevel.__init__(self, master=master)
        self.minsize(600, 300)
        self.master = master
        self.title("Options")
        #self.config(bg="#d9d9d9")
        self.model = model
        
        self.columnconfigure(0, weight=0)
        self.columnconfigure(1, weight=0)
        self.columnconfigure(2, weight=1)
        
        buttonWorkspace = Tkinter.Button(self, text="Set workspace", command=self.setWorkspace)
        
        self.workspaceVar = Tkinter.StringVar()
        self.workspaceVar.set(self.model.workingdir)
        entryWorkspace = Tkinter.Entry(self, textvariable=self.workspaceVar)
        
        buttonWorkspace.grid(row=0, column=0, sticky="NWES")
        entryWorkspace.grid(row=0, column=1, columnspan=2, sticky="NWES")
        
        self.timeAxisVar = Tkinter.StringVar()
        self.timeAxisVar.set(self.model.timescale)
        
        timeAxisLabel = Tkinter.Label(self, text="Timeaxis:")
        timeAxisChoice1 = Tkinter.Radiobutton(self, text="In seconds", variable=self.timeAxisVar, value="seconds")
        timeAxisChoice2 = Tkinter.Radiobutton(self, text="In minutes", variable=self.timeAxisVar, value="minutes")
        
        timeAxisLabel.grid(row=1, column=0, sticky="NWS")
        timeAxisChoice1.grid(row=1, column=1, sticky="NWS")
        timeAxisChoice2.grid(row=2, column=1, sticky="NWS")
        
        self.errorVar = Tkinter.StringVar()
        self.errorVar.set("Da")
        
        errorLabel = Tkinter.Label(self, text="Error:")
        errorChoice1 = Tkinter.Radiobutton(self, text="In Dalton", variable=self.errorVar, value="Da")
        errorChoice2 = Tkinter.Radiobutton(self, text="In ppm", variable=self.errorVar, value="ppm")
        
        errorLabel.grid(row=3, column=0, sticky="NWS")
        errorChoice1.grid(row=3, column=1, sticky="NWS")
        errorChoice2.grid(row=4, column=1, sticky="NWS")
        
        cancelButton = Tkinter.Button(self, text="Cancel", command=self.cancel)        
        saveButton = Tkinter.Button(self, text="Save options", command=self.save)

        cancelButton.grid(row=10, column=0, sticky="NWES")
        saveButton.grid(row=10, column=1, sticky="NWES")

        
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
        self.model.saveSettings()
        self.destroy()
        
        

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
        
        # get window size
        self.update()
        h = self.winfo_height()
        w = self.winfo_width()

        # get screen width and height
        ws = master.winfo_screenwidth() # width of the screen
        hs = master.winfo_screenheight() # height of the screen

        # calculate x and y coordinates for the Tk window
        x = (ws/2) - (w/2)
        y = (hs/2) - (h/2)
        # set the dimensions of the screen 
        # and where it is placed
        self.geometry('%dx%d+%d+%d' % (w, h, x, y))

    def makeHistogram(self):
        self.view.bins = {}
        self.view.colors = {}
        # calculate series
        seriesGlyco = []
        seriesNon = []
        for ms1, spectrum in self.model.currentAnalysis.data:
            #if spectrum.logScore >= 10:
            #    continue
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
            self.model.classes["NotebookScoring"].updateTree()
            self.makeHistogram()
        except ValueError:
            print "cannot convert"
            self.v1.set(self.model.currentAnalysis.analysis.parameters.getScoreThreshold())

class OxoniumFrame(Tkinter.Toplevel):

    def __init__(self, master, model):
        Tkinter.Toplevel.__init__(self, master=master)
        self.master = master
        self.title("Oxoniumion Plot")
        self.config(bg="#d9d9d9")
        self.model = model
        self.view = OxoniumIonPlot.OxoniumIonPlot(self, model)
        self.view.grid(row=0, column=0, sticky="NWSE")
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self.focus_set()
        self.transient(master)
        self.lift()
        self.wm_deiconify()
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        # get selected features
        features = self.model.classes["NotebookFeature"].getSelectedFeatures()
        self.view.init(features=features)
            
    def on_closing(self):
        if "OxoniumIonPlot" in self.model.classes:
            self.model.classes.pop("OxoniumIonPlot")
        if "OxoniumFrame" in self.model.toplevel:
            self.model.toplevel.pop("OxoniumFrame")
        self.destroy()


        
