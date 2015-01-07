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
    
    def __init__(self,path,project,master):
        ThreadedIO.ThreadedIO.__init__(self)
        self.path = path
        self.project = project
        self.master = master
        
        
    def updateExternal(self,running=False):
        if running:
            print "running"
        else:
            print "loading finished"
            self.project.exp =  self.result
            self.master.loadingFinished()
            
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
        

class Project:
    
    def __init__(self,name):
        self.exp = None

class ProjectFrame(ttk.Frame):
    
    def __init__(self,master,model):
        ttk.Frame.__init__(self,master=master)
        self.master = master
        self.model = model
        
        tools = ttk.Labelframe(self,text="Tools")
        b1 = Tkinter.Button(tools, text="add Project",command=self.addProjectButton)
        b1.grid(row=0,column=0)
        
        b1 = Tkinter.Button(tools, text="delete Project",command=self.deleteProject)
        b1.grid(row=0,column=1)
        
        tools.grid(row=0,column=0,sticky=('N','W','E','S'))
        
        scrollbar = Tkinter.Scrollbar(self)    
        self.projectTree = ttk.Treeview(self,yscrollcommand=scrollbar.set)
        columns = ("Filename",)
        self.projectTree["columns"] = columns
        
        self.projectsTreeIds = {}
        
        for col in columns:
            self.projectTree.column(col,width=100)
            self.projectTree.heading(col, text=col)
        
        self.projectTree.grid(row=1,column=0,sticky=('N','W','E','S'))
        
        self.rowconfigure(0, minsize=100,weight=0)
        self.rowconfigure(1, minsize=200,weight=1)
        self.columnconfigure(0,minsize=100,weight=1)
        
        # Events
        self.projectTree.bind("<<TreeviewSelect>>", self.clickedTree)
    
    def addProjectButton(self):
        AddProject(self,self.model)
        
    def addProject(self,name,path):
        item = self.projectTree.insert("", "end",text=name)
        project = Project(name)
        self.model.projects[name] = project
        self.projectsTreeIds[item] = project
        
        # set workingdir
        self.model.workingdir = os.path.split(path)[0]
        # load file in new thread
        print "loading path", path
        self.model.currentProject = project
        t = ThreadedOpenMZML(path,self.model.currentProject,self)
        t.start()
        
        
    def deleteProject(self):
        print "hi"
        
    def clickedTree(self,event):
        item = self.projectTree.selection()[0]
        print "clicked on ",item
        if not item in self.projectsTreeIds:
            return

    def loadingFinished(self):
        return


        
class AddProject(Tkinter.Toplevel):
    
    def __init__(self,master,model):
        Tkinter.Toplevel.__init__(self,master=master)
        self.master = master
        self.title("Add Project")
    
        self.model = model
        
        self.projectName = Tkinter.StringVar()
        projectLabel = Tkinter.Label(self,text="Name: ")
        projectLabel.grid(row=0,column=0,sticky=('N','W','E','S'))
        
        projectEntry = Tkinter.Entry(self,textvariable=self.projectName)
        projectEntry.grid(row=0,column=1,sticky=('N','W','E','S'))
        
        self.path = Tkinter.StringVar()
        pathLabel = Tkinter.Label(self,text="mzML-File: ")
        pathLabel.grid(row=1,column=0,sticky=('N','W','E','S'))
        
        pathEntry = Tkinter.Entry(self,textvariable=self.path)
        pathEntry.grid(row=1,column=1,columnspan=2,sticky=('N','W','E','S'))
        
        pathButton = Tkinter.Button(self, text="Open MZML-File",command=self.openDialog)
        pathButton.grid(row=1,column=3)   
        
        b1 = Tkinter.Button(self, text="Load",command=self.finish)
        b1.grid(row=2,column=2)    
        b2 = Tkinter.Button(self, text="Cancel",command=self.destroy)
        b2.grid(row=2,column=3)
        
    def finish(self):
        name = self.projectName.get()
        if name == "":
            tkMessageBox.showinfo(title="Warning", 
                message="Please provide a project name!")
            return
        if name in self.model.projects:
            tkMessageBox.showinfo(title="Warning", 
                message="Project with this name already exists!")
            return
        path = self.path.get()
        if os.path.exists(path) == False:
            tkMessageBox.showinfo(title="Warning", 
                message="Please provide a valid mzML file to load!")
            return   
        self.destroy()
        self.master.addProject(name,path)
        
    
    def openDialog(self):
        options = {}
        options['defaultextension'] = '.mzML'
        options['filetypes'] = [('mzML files', '.mzML'),('all files', '.*')]
        options['initialdir'] = self.model.workingdir
        options['parent'] = self.master
        options['title'] = 'This is a title'
        path = tkFileDialog.askopenfilename(**options)
        self.path.set(path)

    
