import Tkinter
import ttk
import tkFileDialog
import time
import pyopenms
import SpectrumView
import DataModel
import ChromatogramView
import TwoDView
import ProjectFrame
import NotebookScoring
import NotebookFeature
import NotebookIdentification
import ExtensionScoring
import ExtensionFeature

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


class App(Tkinter.Frame):
    def __init__(self, master):
        self.master = master
        menubar = Tkinter.Menu(self.master)
        self.master.config(menu=menubar)
        self.model = DataModel.DataModel()
        
        self.model.root = master
        
        filemenu = Tkinter.Menu(menubar, tearoff=0)
        filemenu.add_command(label="Parameters")
        filemenu.add_separator()
        filemenu.add_command(label="Exit", command=self.master.destroy)
        menubar.add_cascade(label="Program", menu=filemenu)
        
        analysisMenu = Tkinter.Menu(menubar, tearoff=0)
        analysisMenu.add_command(label="Open Analysis")
        analysisMenu.add_command(label="Save Analysis")
        analysisMenu.add_separator()
        analysisMenu.add_command(label="Close Analysis")
        menubar.add_cascade(label="Analysisfile", menu=analysisMenu) 
        
        mzfileMenu = Tkinter.Menu(menubar, tearoff=0)
        mzfileMenu.add_command(label="Open mzML file")
        mzfileMenu.add_command(label="Save mzML file")
        mzfileMenu.add_separator()
        mzfileMenu.add_command(label="Close mzML file")
        menubar.add_cascade(label="mzMLFile", menu=mzfileMenu) 
        
        toolMenu = Tkinter.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Tool", menu=toolMenu) 
        
        frameProject = ttk.Labelframe(master,text="Projects")
        pojectFrame = ProjectFrame.ProjectFrame(frameProject,self.model)
        #pojectFrame.pack()
        pojectFrame.grid(row=0,column=0,sticky=("N", "W", "E", "S"))
        frameProject.grid(row=0,column=0,sticky=("N", "W", "E", "S"))
        
        self.notebook = ttk.Notebook(master)
        
        n1 = NotebookScoring.NotebookScoring(self.notebook,self.model)
        n2 = NotebookFeature.NotebookFeature(self.notebook,self.model)
        n3 = NotebookIdentification.NotebookIdentification(self.notebook,self.model)
        n4 = Tkinter.Frame(self.notebook)

        self.notebook.add(n1, text='1. Scoring')
        self.notebook.add(n2, text='2. Features')
        self.notebook.add(n3, text='3. Identification')
        self.notebook.add(n4, text='4. Results')

        self.notebook.grid(row=1,column=0,sticky=("N", "W", "E"))
        self.notebook.bind("<<NotebookTabChanged>>", self.changedNotebook)
        
        # configure column and row behaviour
        self.master.columnconfigure(0, minsize=200,weight=0)
        self.master.columnconfigure(1, minsize=300,weight=1)
        self.master.rowconfigure(0, minsize=200,weight=0)
        self.master.rowconfigure(1, minsize=200,weight=1)
        #self.master.rowconfigure(1, minsize=200,weight=1)
        
        # Add extention frames
        self.e1 = ExtensionScoring.ExtensionScoring(master,self.model,'1. Scoring')
        self.e1.grid(row=0,column=1,rowspan=2,sticky="NWES")
        self.e2 = ExtensionFeature.ExtensionFeature(master,self.model,'2. Features')
        self.e2.grid(row=0,column=1,rowspan=2,sticky="NWES")
        self.e3 = ttk.Labelframe(master,text = '3. Identification')
        self.e3.grid(row=0,column=1,rowspan=2,sticky="NWES")
        self.e4 = ttk.Labelframe(master,text = '4. Results')
        self.e4.grid(row=0,column=1,rowspan=2,sticky="NWES")
        
        
    def changedNotebook(self,event):
        #self.model.debug = event
        idx = self.notebook.select()
        # hide all extensions
        self.e1.lower()
        self.e2.lower()
        self.e3.lower()
        self.e4.lower()
        # show selected extension
        text = self.notebook.tab(idx,"text") 
        if "1" in text:
            self.e1.lift()
        elif "2" in text:
            self.e2.lift()
        elif "3" in text:
            self.e3.lift()
        else:
            self.e4.lift()

def run():
    global app
    root = Tkinter.Tk()
    app = App(root)
    root.mainloop()
    return app

