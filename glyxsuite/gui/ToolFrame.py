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


