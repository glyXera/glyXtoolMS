import ThreadedIO
import ttk 
from Tkinter import * 
import pyopenms
import tkFileDialog
import AddChromatogram
import tkMessageBox
import DataModel
import os
import ToolMZML
import ToolAnalysis

class ToolFrame(ttk.Frame):
    
    def __init__(self,master,model):
        ttk.Frame.__init__(self,master=master)
        self.master = master
        self.model = model
        
        fileNotebook = ttk.Notebook(self)
        f1 = ToolMZML.ToolMZML(fileNotebook,self.model)
        f2 = ToolAnalysis.ToolAnalysis(fileNotebook,self.model)
        fileNotebook.add(f1, text='mzMLFile')
        fileNotebook.add(f2, text='Analysis')
        fileNotebook.grid(row=0,column=0,sticky=(N, W, E, S))

