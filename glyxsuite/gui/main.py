from Tkinter import *
import ttk
import tkFileDialog
import time
import pyopenms
import FileViewMZML
import FileViewAnalysis
import SpectrumView

"""
Viewer for analysis file
a) MS/MS spectra, annotation
b) scored spectra
c) scored features
d) Histogram
"""

    

       
class DataModel:
    
    def __init__(self):
        self.workingdir = "/afs/mpi-magdeburg.mpg.de/home/pioch/Data/Projekte/GlyxBox/glycoMod/"
        self.mzMLFilename = ""
        self.fileMzMLFile = None
        self.exp = None
        self.analyis = None
        self.test = None
        self.debug = None
        self.combination = {}
        self.spectra = {}
        self.treeIds = {}
        self.spec = None
        self.root = None
        
        
        self.funcPaintSpectrum = None
        
        
    def combineDatasets(self):
        if self.exp == None or self.analysis == None:
            return False
        
        # connect MS2 spectra
        self.combination = {}
        #for spec in exp:
            
        
class App(Frame):
    def __init__(self, master):
        self.master = master
        menubar = Menu(self.master)
        self.master.config(menu=menubar)
        self.model = DataModel()
        
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
        
        frameUL = ttk.Labelframe(master,text="Files")
        # Add notebook for file selection
        fileNotebook = ttk.Notebook(frameUL)
        f1 = FileViewMZML.FileViewMZML(fileNotebook,self.model) # first page, which would get widgets gridded into it
        f2 = FileViewAnalysis.FileViewAnalysis(fileNotebook,self.model) # second page
        fileNotebook.add(f1, text='One')
        fileNotebook.add(f2, text='Two')
        fileNotebook.grid(row=0,column=0,sticky=(N, W, E, S))
        #frameUL.config(bg="grey")
        frameUL.grid(row=0,column=0,sticky=(N, W, E, S))
        
        frameLL = ttk.Labelframe(master,text="Status")
        #frameLL.config(bg="yellow")
        frameLL.grid(row=1,column=0,sticky=(N, W, E, S))
        
        frameR = ttk.Labelframe(master,text="Annotation")
        #frameR.config(bg="blue")
        frameR.grid(row=0,column=1,rowspan=2,sticky=(N, W, E, S))
        
        msmsFrame = SpectrumView.SpectrumView(frameR,self.model)
        msmsFrame.pack()
        
        """
        frameUL.config(bg="grey")
        frameUL.grid(row=0,column=0,sticky=(N, W, E, S))

        frameUR = Frame(master)
        frameUR.config(bg="yellow")
        frameUR.grid(row=0,column=1,sticky=(N, W, E, S))
        
        frameLL = Frame(master)
        frameLL.config(bg="yellow")
        frameLL.grid(row=1,column=0,sticky=(N, W, E, S))

        frameLR = Frame(master)
        frameLR.config(bg="grey")
        frameLR.grid(row=1,column=1,sticky=(N, W, E, S))
        """
        # configure column and row behaviour
        self.master.columnconfigure(0, minsize=200,weight=0)
        self.master.columnconfigure(1, minsize=200,weight=1)
        self.master.rowconfigure(0, minsize=200,weight=1)
        self.master.rowconfigure(1, minsize=200,weight=1)
        

def run():
    global app
    root = Tk()
    app = App(root)
    root.mainloop()
    return app

