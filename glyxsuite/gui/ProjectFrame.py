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
            self.project.mzMLContainer.exp =  self.result
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
        self.name = name
        self.mzMLContainer = None
        self.analysisFiles = []
        self.exp = None
        
        
class ContainerMZMLFile:
    
    def __init__(self,project,path):
        self.exp = None
        self.path = path
        self.project = project
        
class ContainerAnalysisFile:
    
    def __init__(self,project,path):
        self.path = path
        self.project = project

class DebugScrollbar(Tkinter.Scrollbar):
    def set(self, *args):
        print "SCROLLBAR SET", args
        Tkinter.Scrollbar.set(self, *args)


class ProjectFrame(ttk.Frame):
    
    def __init__(self,master,model):
        ttk.Frame.__init__(self,master=master)
        self.master = master
        self.model = model
        
        tools = ttk.Labelframe(self,text="Tools")
        self.b1 = Tkinter.Button(tools, text="add Project",command=self.clickedAddProject)
        self.b1.grid(row=0,column=0)
        
        self.b2 = Tkinter.Button(tools, text="delete Project",command=self.deleteProject)
        self.b2.grid(row=0,column=1)
        self.b2.config(state=Tkinter.DISABLED)
        
        self.b3 = Tkinter.Button(tools, text="add Analysis",command=self.clickedAddAnalysis)
        self.b3.grid(row=1,column=0)
        self.b3.config(state=Tkinter.DISABLED)

        #NORMAL, ACTIVE or DISABLED
        
        self.b4 = Tkinter.Button(tools, text="delete Analysis",command=self.deleteProject)
        self.b4.grid(row=1,column=1)
        self.b4.config(state=Tkinter.DISABLED)
        
        
        tools.grid(row=0,column=0,sticky=('N','W','E','S'))
        
        #yscrollbar = Tkinter.Scrollbar(self,orient=Tkinter.VERTICAL)
        yscrollbar = DebugScrollbar(self,orient=Tkinter.VERTICAL)
        
        xscrollbar = Tkinter.Scrollbar(self,orient=Tkinter.HORIZONTAL)
        self.projectTree = ttk.Treeview(self,
                            xscrollcommand=xscrollbar.set,
                            yscrollcommand=yscrollbar.set)
                            
        self.projectTree.grid(row=1,column=0,sticky=('N','W','E','S'))
        
        xscrollbar.grid(row=2,column=0,sticky=('N','W','E','S'))
        #xscrollbar.grid(row=2,column=0)
        xscrollbar.config(command=self.projectTree.xview)
        
        yscrollbar.grid(row=1,column=1,sticky=('N','W','E','S'))
        yscrollbar.config(command=self.projectTree.yview)
        
        
        columns = ("Filename",)
        self.projectTree["columns"] = columns
        self.projectsTreeIds = {}
        
        # debug
        self.model.debug = self.projectTree
        
        self.projectTree.heading("#0", text="Projects")
        
        for col in columns:
            #self.projectTree.column(col,stretch= 0,minwidth=300,width=300)
            self.projectTree.heading(col, text=col, anchor='w')
            self.projectTree.column(col,width=300, stretch=0)
        
        
        #tree.heading("size", text="File Size", anchor='w')
        #tree.column("size", stretch=0, width=100)
        
        #self.rowconfigure(0, minsize=100,weight=0)
        #self.rowconfigure(1, minsize=200,weight=1)
        #self.columnconfigure(0,minsize=100,weight=1)
        
        # Events
        self.projectTree.bind("<<TreeviewSelect>>", self.clickedTree)
        
        # add test content into treeview
        #for i in range(0,20):
        #    item = self.projectTree.insert("", "end",text="test"+str(i),
        #        values=("blahblahblahblahblahblahblahblahblahblahblahblahblahblahblahblahblahblahblahblahblahblahblahblahblahblahblahblah"),tags = ("blah",))
                
        

    
    def clickedAddProject(self):
        AddProject(self,self.model)

        
    def clickedAddAnalysis(self):
        item,obj,typ = self.getSelectedItem()
        if item == None:
            return
        # check if a project was selected
        if self.model.currentProject == None:
            return
        
        options = {}
        options['defaultextension'] = '.xml'
        options['filetypes'] = [('Analysis files', '.xml'),('all files', '.*')]
        options['initialdir'] = self.model.workingdir
        options['parent'] = self.master
        options['title'] = 'This is a title'
        path = tkFileDialog.askopenfilename(**options)
        print path
        if len(path) == 0:
            return
            
        # get project itemId
        while not "project" in self.projectTree.item(item,"tags"):
            item = self.projectTree.parent(item)           
        
        itemAnalysis = self.projectTree.insert(item, "end",
            text=os.path.basename(path),
            values=(path,),tags = ("analysis",))
        analysis = ContainerAnalysisFile(self.model.currentProject,path)
        self.model.currentProject.analysisFiles.append(analysis)
        # add analysis to idTree
        self.projectsTreeIds[itemAnalysis] = analysis

    def addProject(self,name,path):
        item = self.projectTree.insert("", "end",text=name,tags = ("project",))
        project = Project(name)
        self.model.projects[name] = project
        self.projectsTreeIds[item] = project
        
        # set workingdir
        self.model.workingdir = os.path.split(path)[0]
        # load file in new thread
        print "loading path", path
        self.model.currentProject = project
        
        itemMZML = self.projectTree.insert(item, "end",text="mzMLFile",
            values=(os.path.basename(path),),tags = ("mzMLFile",))
        
        # add ContainerMZMLFile
        mzMLContainer = ContainerMZMLFile(project,path)
        project.mzMLContainer = mzMLContainer
        self.projectsTreeIds[itemMZML] = mzMLContainer
        #t = ThreadedOpenMZML(path,self.model.currentProject,self)
        #t.start()
        
        # Aktivate delete button
        if len(self.model.projects) > 0:
            self.b2.config(state=Tkinter.NORMAL)
        else:
            self.b2.config(state=Tkinter.DISABLED)



        
        
    def deleteProject(self):
       
        item,obj,typ = self.getSelectedItem()
        if item == None:
            return
        print "to delete: ", item,obj
        
    def clickedTree(self,event):
        item,obj,typ = self.getSelectedItem()
        if item == None:
            # deaktive all buttons, except addProject
            self.b2.config(state=Tkinter.DISABLED)
            self.b3.config(state=Tkinter.DISABLED)
            self.b4.config(state=Tkinter.DISABLED)
            return
        else:
            self.b2.config(state=Tkinter.NORMAL)
            self.b3.config(state=Tkinter.NORMAL)
        # get project
        if typ == "project":
            self.model.currentProject = obj
        elif typ == "mzMLFile":
            self.model.currentProject = obj.project

            
            
        # set button state
        if typ == "analysis":
            self.model.currentProject = obj.project
            self.b4.config(state=Tkinter.NORMAL)
        else:
            self.b4.config(state=Tkinter.DISABLED)
            
        
            
        print "current project ",self.model.currentProject.name

    def loadingFinished(self):
        return

    def getSelectedItem(self):
        # returns ItemId,Object,ObjectType
        selection = self.projectTree.selection()
        if len(selection) == 0:
            return (None,None,"")
        item = selection[0]
        if not item in self.projectsTreeIds:
            return (None,None,"")
        # get type of item
        taglist = list(self.projectTree.item(item,"tags"))
        if "project" in taglist:
            return (item, self.projectsTreeIds[item],"project")
        if "mzMLFile" in taglist:
            return (item, self.projectsTreeIds[item],"mzMLFile")
        if "analysis" in taglist:
            return (item, self.projectsTreeIds[item],"analysis")    
        return (item, self.projectsTreeIds[item],"")
        
        
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

    
