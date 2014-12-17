import ThreadedIO
import ttk 
import Tkinter
import pyopenms
import tkFileDialog
import tkMessageBox
import DataModel
import os
import ThreadedIO

"""
|---------------|
|      Tools    |
|---------------|
|               |
|   Treeview    |
|   of Projects |
|               |
|---------------|

"""
class ThreadedOpenMZML(ThreadedIO.ThreadedIO):
    
    def __init__(self,path,model,master):
        ThreadedIO.ThreadedIO.__init__(self)
        self.path = path
        self.model = model
        self.master = master
        
        
    def updateExternal(self,running=False):
        if running:
            print "running"
        else:
            print "loading finished"
            self.model.exp = self.result
            self.master.updateMZMLView()
            
    def threadedAction(self):
        try:
            print "loading experiment"
            exp = pyopenms.MSExperiment()
            fh = pyopenms.FileHandler()
            fh.loadExperiment(self.path,exp)
            self.queue.put(exp)
            print "loading finnished"
        except:
            self.running = False
            raise
        

class ProjectFrame(ttk.Frame):
    
    def __init__(self,master,model):
        ttk.Frame.__init__(self,master=master)
        self.master = master
        self.model = model
        
        tools = ttk.Labelframe(self,text="Tools")
        b1 = Tkinter.Button(tools, text="add Project",command=self.addProject)
        b1.grid(row=0,column=0)
        
        b1 = Tkinter.Button(tools, text="delete Project",command=self.deleteProject)
        b1.grid(row=0,column=1)
        
        tools.grid(row=0,column=0,sticky=('N','W','E','S'))
        
        scrollbar = Tkinter.Scrollbar(self)    
        self.projectTree = ttk.Treeview(self,yscrollcommand=scrollbar.set)
        columns = ("Filename",)
        self.projectTree["columns"] = columns
        
        for col in columns:
            self.projectTree.column(col,width=100)
            self.projectTree.heading(col, text=col)
        
        self.projectTree.grid(row=1,column=0,sticky=('N','W','E','S'))
        
        self.rowconfigure(0, minsize=100,weight=0)
        self.rowconfigure(1, minsize=200,weight=1)
        self.columnconfigure(0,minsize=100,weight=1)
    
    def addProject(self):
        print "hi"
        
    def deleteProject(self):
        print "hi"


