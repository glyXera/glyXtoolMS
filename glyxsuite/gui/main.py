from Tkinter import *
import ttk
import tkFileDialog
import time
import pyopenms
import FileViewMZML
import FileViewAnalysis
import SpectrumView
import DataModel
import ChromatogramView
import TwoDView

"""
Viewer for analysis file
a) MS/MS spectra, annotation
b) scored spectra
c) scored features
d) Histogram
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
        
        frameUL = ttk.Labelframe(master,text="Files")
        # Add notebook for file selection
        fileNotebook = ttk.Notebook(frameUL)
        f1 = FileViewMZML.FileViewMZML(fileNotebook,self.model) # first page, which would get widgets gridded into it
        f2 = FileViewAnalysis.FileViewAnalysis(fileNotebook,self.model) # second page
        fileNotebook.add(f1, text='mzmlFile')
        fileNotebook.add(f2, text='Analysis')
        fileNotebook.grid(row=0,column=0,sticky=(N, W, E, S))
        #frameUL.config(bg="grey")
        frameUL.grid(row=0,column=0,sticky=(N, W, E, S))
        
        frameLL = ttk.Labelframe(master,text="FeatureView")
        f3 = TwoDView.TwoDView(frameLL,self.model)
        f3.grid(row=0,column=0,sticky=(N, W, E, S))
        frameLL.grid(row=1,column=0,sticky=(N, W, E, S))
        
        frameUR = ttk.Labelframe(master,text="Chromatogram")
        #frameR.config(bg="blue")
        #frameR.grid(row=0,column=1,rowspan=2,sticky=(N, W, E, S))
        frameUR.grid(row=0,column=1,rowspan=1,sticky=(N, W, E, S))

        chromFrame = ChromatogramView.ChromatogramView(frameUR,self.model)
        chromFrame.grid(row=0,column=0,sticky=(N, W, E, S))
        
        frameLR = ttk.Labelframe(master,text="Spectrum")
        frameLR.grid(row=1,column=1,rowspan=1,sticky=(N, W, E, S))
        
        msmsFrame = SpectrumView.SpectrumView(frameLR,self.model)
        msmsFrame.grid(row=1,column=0,sticky=(N, W, E, S))
        
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

