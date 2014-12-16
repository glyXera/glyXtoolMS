import ttk 
from Tkinter import * 

class ToolAnalysis(ttk.Frame):
    def __init__(self,master,model):
        ttk.Frame.__init__(self,master=master)
        self.master = master
        b1 = Button(self, text="Open Analysis file",command=self.openMzMLFile)
        b1.grid(row=0,column=0,sticky=(N, W, E, S))   
        
    def openMzMLFile(self,event):
        print "hi"
