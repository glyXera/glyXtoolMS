import ThreadedIO
import ttk 
from Tkinter import * 
import pyopenms
import tkFileDialog
import AddChromatogram
import tkMessageBox
import DataModel
import os

class ToolFrame(ttk.Frame):
    
    def __init__(self,master,model):
        ttk.Frame.__init__(self,master=master)
        self.master = master
        self.model = model
        b = Button(self, text="Open mzML file",command=self.openMzMLFile)
        b.grid(row=0,column=0,sticky=(N, W, E, S))
        
    def openMzMLFile(self,event):
        print "hi"
