from Tkinter import *
import ttk
import tkFileDialog
import time
import pyopenms
import AnalysisFrame
import ToolFrame
import SpectrumView
import DataModel
import ChromatogramView
import TwoDView
import ProjectFrame
import NotebookMzMLView
import NotebookAnalysisView

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


class App(Frame):
    def __init__(self, master):
        self.master = master
        menubar = Menu(self.master)
        self.master.config(menu=menubar)
        self.model = DataModel.DataModel()
        
        self.model.root = master
        
        filemenu = Menu(menubar, tearoff=0)
        filemenu.add_command(label="Parameters")
        filemenu.add_separator()
        filemenu.add_command(label="Exit", command=self.master.destroy)
        menubar.add_cascade(label="Program", menu=filemenu)
        
        analysisMenu = Menu(menubar, tearoff=0)
        analysisMenu.add_command(label="Open Analysis")
        analysisMenu.add_command(label="Save Analysis")
        analysisMenu.add_separator()
        analysisMenu.add_command(label="Close Analysis")
        menubar.add_cascade(label="Analysisfile", menu=analysisMenu) 
        
        mzfileMenu = Menu(menubar, tearoff=0)
        mzfileMenu.add_command(label="Open mzML file")
        mzfileMenu.add_command(label="Save mzML file")
        mzfileMenu.add_separator()
        mzfileMenu.add_command(label="Close mzML file")
        menubar.add_cascade(label="mzMLFile", menu=mzfileMenu) 
        
        toolMenu = Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Tool", menu=toolMenu) 
        
        frameProject = ttk.Labelframe(master,text="Projects")
        pojectFrame = ProjectFrame.ProjectFrame(frameProject,self.model)
        #pojectFrame.pack()
        pojectFrame.grid(row=0,column=0,sticky=(N, W, E, S))
        frameProject.grid(row=0,column=0,sticky=(N, W, E, S))
        
        notebook = ttk.Notebook(master)
        f1 = NotebookMzMLView.NotebookMzMLView(notebook,self.model)
        f2 = NotebookAnalysisView.NotebookAnalysisView(notebook,self.model)
        notebook.add(f1, text='mzMLView')
        notebook.add(f2, text='AnalysisView')
        notebook.grid(row=0,column=1,sticky=(N, W, E, S))
        
        # configure column and row behaviour
        self.master.columnconfigure(0, minsize=200,weight=0)
        self.master.columnconfigure(1, minsize=300,weight=1)
        self.master.rowconfigure(0, minsize=200,weight=1)
        #self.master.rowconfigure(1, minsize=200,weight=1)
        

def run():
    global app
    root = Tk()
    app = App(root)
    root.mainloop()
    return app

