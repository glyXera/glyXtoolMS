import ttk
import Tkinter

import tkFileDialog
import tkMessageBox
import os

import pyopenms
import glyxtoolms
from glyxtoolms.gui import ThreadedIO
from glyxtoolms.gui import DataModel

#class ThreadedOpenMZML(ThreadedIO.ThreadedIO):
#
#    def __init__(self, master, path, project):
#        ThreadedIO.ThreadedIO.__init__(self)
#        self.path = path
#        self.project = project
#        self.master = master
#        self.error = False
#
#
#    def updateExternal(self, running=False):
#        if not running:
#            print "loading finished"
#            self.project.mzMLFile.exp = self.result
#            self.master.loadedMzMLFile(self.error, self.project)
#
#    def threadedAction(self):
#        try:
#            print "loading experiment"
#            exp = pyopenms.MSExperiment()
#            fh = pyopenms.FileHandler()
#            fh.loadExperiment(self.path, exp)
#            self.queue.put(exp)
#            print "loading finnished"
#        except:
#            self.running = False
#            self.error = True
#            tkMessageBox.showerror("File input error",
#                                   "Error while loading pyopenms file!")
#            raise

#class ThreadedAnalysisFile(ThreadedIO.ThreadedIO):
#
#    def __init__(self, master, path, analysis):
#        ThreadedIO.ThreadedIO.__init__(self)
#        self.path = path
#        self.analysis = analysis
#        self.master = master
#        self.error = False
#
#
#    def updateExternal(self, running=False):
#        if not running:
#            print "stopped"
#            self.analysis.analysis = self.result
#            self.master.loadedAnalysisFile(self.error, self.analysis)
#
#    def threadedAction(self):
#        try:
#            print "loading experiment"
#            glyMl = glyxtoolms.io.GlyxXMLFile()
#            glyMl.readFromFile(self.path)
#            self.queue.put(glyMl)
#            print "loading finnished"
#        except:
#            tkMessageBox.showerror("File input error",
#                                   "Error while loading analysis "
#                                   "file! Please check glyML version.")
#            self.running = False
#            raise

class ProjectFrame(ttk.Frame):

    def __init__(self, master, model):
        ttk.Frame.__init__(self, master=master)
        self.master = master
        self.model = model

        tools = ttk.Frame(self)
        
        self.buttonNewProject = ttk.Button(tools, text="New Project", command=self.clickedAddProject)
        self.buttonNewProject.grid(row=0, column=0)
        
        self.buttonOpenProject = ttk.Button(tools, text="Open Project", command=self.openProject)
        self.buttonOpenProject.grid(row=0, column=1)
        
        #self.buttonFindProject = ttk.Button(tools, text="Find Project", command=self.clickedFindAnalysis)
        #self.buttonFindProject.grid(row=0, column=2)

        self.buttonCloseProject = ttk.Button(tools, text="Close Project", command=self.closeProject)
        self.buttonCloseProject.grid(row=0, column=2)
        self.buttonCloseProject.config(state=Tkinter.DISABLED)

        self.buttonSaveProject = ttk.Button(tools, text="Save Project", command=self.saveProject)
        self.buttonSaveProject.grid(row=0, column=3)
        self.buttonSaveProject.config(state=Tkinter.DISABLED)
        
        #self.buttonEditProject = ttk.Button(tools, text="Change Project Name", command=self.foo)
        #self.buttonEditProject.grid(row=0, column=5)
        #self.buttonEditProject.config(state=Tkinter.DISABLED)



        self.buttonAddAnalysis = ttk.Button(tools, text="Add Analysis", command=self.clickedAddAnalysis)
        self.buttonAddAnalysis.grid(row=1, column=0)
        self.buttonAddAnalysis.config(state=Tkinter.DISABLED)

        self.buttonCloseAnalysis = ttk.Button(tools, text="Close Analysis", command=self.closeAnalysis)
        self.buttonCloseAnalysis.grid(row=1, column=1)
        self.buttonCloseAnalysis.config(state=Tkinter.DISABLED)

        self.buttonSaveAnalysis = ttk.Button(tools, text="Save Analysis", command=self.saveAnalysis)
        self.buttonSaveAnalysis.grid(row=1, column=2)
        self.buttonSaveAnalysis.config(state=Tkinter.DISABLED)

        #self.buttonOpenProject = ttk.Button(tools, text="Load Test", command=self.loadTest)
        #self.buttonOpenProject.grid(row=0, column=2)


        tools.grid(row=0, column=0, sticky="NWES")

        projects = ttk.Frame(self)
        projects.grid(row=1, column=0, sticky="NWES")

        yscrollbar = Tkinter.Scrollbar(projects, orient=Tkinter.VERTICAL)

        self.projectTree = ttk.Treeview(projects,
                                        yscrollcommand=yscrollbar.set)

        self.projectTree.grid(row=0, column=0, sticky="NWES")

        yscrollbar.grid(row=0, column=1, sticky="NWES")
        yscrollbar.config(command=self.projectTree.yview)

        self.projectsTreeIds = {}
        self.objectsToItems = {}

        self.projectTree.heading("#0", text="Projects")

        #tree.heading("size", text="File Size", anchor='w')
        #self.projectTree.column("#0", stretch=0, width=500)

        #self.rowconfigure(0, minsize=100, weight=0)
        #self.rowconfigure(1, minsize=200, weight=1)
        projects.columnconfigure(0, weight=1)
        projects.columnconfigure(1, weight=0)
        projects.rowconfigure(0, weight=1)

        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        # Events
        self.projectTree.bind("<<TreeviewSelect>>", self.clickedTree)

    def checkButtonState(self):
        
        item, obj, typ = self.getSelectedItem()
        if item == None:
            # deaktive all buttons, except all that add or open projects
            self.buttonCloseProject.config(state=Tkinter.DISABLED)
            self.buttonAddAnalysis.config(state=Tkinter.DISABLED)
            self.buttonCloseAnalysis.config(state=Tkinter.DISABLED)
            self.buttonSaveAnalysis.config(state=Tkinter.DISABLED)
            return
        if typ == "analysis":
            self.buttonCloseProject.config(state=Tkinter.NORMAL)
            self.buttonSaveProject.config(state=Tkinter.NORMAL)
            self.buttonAddAnalysis.config(state=Tkinter.NORMAL)
            self.buttonCloseAnalysis.config(state=Tkinter.NORMAL)
            self.buttonSaveAnalysis.config(state=Tkinter.NORMAL)
        else:
            self.buttonCloseProject.config(state=Tkinter.NORMAL)

            self.buttonSaveProject.config(state=Tkinter.NORMAL)
            self.buttonAddAnalysis.config(state=Tkinter.NORMAL)
            self.buttonCloseAnalysis.config(state=Tkinter.DISABLED)
            self.buttonSaveAnalysis.config(state=Tkinter.DISABLED)

        # Aktivate close button
        if len(self.model.projects) > 0:
            self.buttonCloseProject.config(state=Tkinter.NORMAL)
        else:
            self.buttonCloseProject.config(state=Tkinter.DISABLED)

    def foo(self):
        return
        
    def openProject(self):
        options = {}
        options['defaultextension'] = '.glyXtoolMS'
        options['filetypes'] = [('GlyXtoolMS Project file', '.glyXtoolMS')]
        options['initialdir'] = self.model.workingdir
        options['parent'] = self
        options['title'] = 'Open Project'
        path = tkFileDialog.askopenfilename(**options)
        if len(path) == 0:
            return
        project = DataModel.Project(self,"NoName", self.model)
        project.load(path)
        # check if project with this name already exists
        orignName = project.name
        i = 0
        name = orignName
        while name in self.model.projects:
            i += 1
            name = orignName+str(i)
        project.name = name
        # start queue
        project.loadByQueue = True
        project._checkQueue()
        
        
    def saveProject(self):
        # check if a project was selected
        if self.model.currentProject == None:
            return
        project = self.model.currentProject
        
        # get save path
        options = {}
        options['defaultextension'] = '.glyXtoolMS'
        options['filetypes'] = [('GlyXtoolMS Project file', '.glyXtoolMS')]
        workingdir = os.path.dirname(project.path)
        options['initialdir'] = workingdir
        options['initialfile'] = project.path
        options['title'] = 'Save Project'
        options['confirmoverwrite'] = True
        path = tkFileDialog.asksaveasfilename(**options)
        if path == "" or path == ():
            return
        project.save(path)
        tkMessageBox.showinfo(title="Info",
                              message="Project saved!")

    def clickedAddProject(self):
        AddProject(self, self.model)

    def clickedFindAnalysis(self):
        FindAnalysis(self, self.model)

    def clickedAddAnalysis(self):
        item, obj, typ = self.getSelectedItem()
        if item == None:
            return
        # check if a project was selected
        if self.model.currentProject == None:
            return
        project = self.model.currentProject
        # get basedir
        if project.mzMLFile == None:
            return
        workingdir = os.path.dirname(project.mzMLFile.path)

        options = {}
        options['defaultextension'] = '.xml'
        options['filetypes'] = [('Analysis files', '.xml'), ('all files', '.*')]
        options['initialdir'] = workingdir
        options['parent'] = self
        options['title'] = 'Open Analysis file'
        path = tkFileDialog.askopenfilename(**options)
        print path
        if len(path) == 0:
            return

        analysis = DataModel.ContainerAnalysisFile(self.model, project, path)
        if analysis.name in project.analysisFiles:
            tkMessageBox.showinfo(title="Warning",
                                  message="Analysisfile with this name"
                                  " already exists!")
            return

        # get project itemId
        while not "project" in self.projectTree.item(item, "tags"):
            item = self.projectTree.parent(item)

        analysis.projectItem = item
        
        project.addAnalysisFile(path)

        #t = ThreadedAnalysisFile(self, path, analysis)
        #t.start()

    def loadedAnalysisFile(self, error, analysis, silent=False):
        if error == True:
            return
        # get project and project item
        projectItem = self.objectsToItems[analysis.project.name]
        itemAnalysis = self.projectTree.insert(projectItem, "end",
                                               text=analysis.name,
                                               tags=("analysis", ))

        analysis.project.analysisFiles[analysis.name] = analysis
        # add analysis to idTree
        self.projectsTreeIds[itemAnalysis] = analysis
        print "loaded analysis file"
        self.model.debug = analysis

        # update internal ids
        analysis.createIds()

        # collect specta within features
        analysis.collectFeatureSpectra()

        # merge data
        # insert all ms2 spectra
        analysis.data = []

        for spec in analysis.project.mzMLFile.exp:
            if spec.getMSLevel() != 2:
                continue
            name = spec.getNativeID()

            # find correspondig analysis entry
            if not name in analysis.spectraIds:
                continue
            spectrum = analysis.spectraIds[name]
            analysis.data.append((spec, spectrum)) # Use ??


        # create chromatogram
        analysis.chromatogram = None
        # presort spectra for faster chromatogram creation
        precursors = []
        for ms2, spectrum in analysis.data:
            rtLow = spectrum.rt-100
            rtHigh = spectrum.rt+100
            # reset spectra
            spectrum.chromatogramSpectra = []
            precursors.append((rtHigh, rtLow, spectrum))
        precursors.sort(reverse=True)


        for spec in analysis.project.mzMLFile.exp:
            if spec.getMSLevel() != 1:
                continue
            rt = spec.getRT()
            for rtHigh, rtLow, spectrum in precursors:
                if rtHigh < rt:
                    break
                if rtLow > rt:
                    continue
                spectrum.chromatogramSpectra.append(spec)

        # update Notebooks
        self.model.classes["NotebookScoring"].updateTree([])
        self.model.classes["NotebookIdentification"].updateTree([])
        self.model.classes["NotebookFeature"].updateTree()
        
        if silent == False:
            tkMessageBox.showinfo(title="Info",
                      message="Analysis file loaded!")
            self.projectTree.see(itemAnalysis)
            self.projectTree.selection_set(itemAnalysis)


    def addProject(self, name, path):
        print "loading path", path
        project = DataModel.Project(self, name, self.model)
        project.addMZMLFile(path)
        # Function call after threading is finished, look for function 'loadedMzMLFile'

    def loadedMzMLFile(self, project, error, silent=False):
        if error == True:
            return
        
        # reorganize data
        project.mzMLFile.createIds()
        
        item = self.projectTree.insert("", "end", text=project.name + "  ("+project.mzMLFile.name+")", tags=("project", ))
        self.projectsTreeIds[item] = project
        self.objectsToItems[project.name] = item
        

        #itemMZML = self.projectTree.insert(item, "end",
        #                                   text=os.path.basename(project.path),
        #                                   tags=("mzMLFile", ))

        # add ContainerMZMLFile
        #self.projectsTreeIds[itemMZML] = project.mzMLFile

        self.checkButtonState()
        if silent == False:
            tkMessageBox.showinfo("Loaded mzML file", "mzML file sucessfully loaded!")
            # select mzML file in treeview
            self.projectTree.selection_set(item)
            
            

    def closeProject(self):
        item, obj, typ = self.getSelectedItem()
        if item == None:
            return
        if not tkMessageBox.askyesno('Close Project',
                                     'Do you want to close this project?'):
            return
        # get project itemId
        while not "project" in self.projectTree.item(item, "tags"):
            item = self.projectTree.parent(item)

        project = self.model.currentProject

        # delete project from model
        if project.name in self.model.projects:
            self.model.projects.pop(project.name)

        # delete project from TreeviewID
        if item in self.projectsTreeIds:
            self.projectsTreeIds.pop(item)

        # delete project from Treeview
        self.projectTree.delete(item)
        
        self.checkButtonState()


    def closeAnalysis(self):
        item, obj, typ = self.getSelectedItem()
        if item == None:
            return
        if typ != "analysis":
            return
        # get analysis
        if not item in self.projectsTreeIds:
            return
        if not tkMessageBox.askyesno('Close Analysis',
                                     'Do you want to close this analysis?'):
            return

        analysis = self.projectsTreeIds[item]
        project = self.model.currentProject

        # delete analysis from project
        if analysis.name in project.analysisFiles:
            project.analysisFiles.pop(analysis.name)

        # delete analysisId from Treeview-ID-tracker
        if item in self.projectsTreeIds:
            self.projectsTreeIds.pop(item)

        # delete analysis from Treeview
        self.projectTree.delete(item)
        
        self.checkButtonState()

    def saveAnalysis(self):
        item, obj, typ = self.getSelectedItem()
        if item == None:
            return
        if typ != "analysis":
            return
        # get analysis
        if not item in self.projectsTreeIds:
            return
        # get save path
        options = {}
        options['defaultextension'] = '.xml'
        options['filetypes'] = [('Analysis files', '.xml'), ('all files', '.*')]
        workingdir = os.path.dirname(obj.project.mzMLFile.path)
        options['initialdir'] = workingdir
        options['title'] = 'Save Analysis'
        options['confirmoverwrite'] = True
        path = tkFileDialog.asksaveasfilename(**options)
        if path == "" or path == ():
            return
        try:
            obj.analysis.writeToFile(path)
        except:
            tkMessageBox.showerror("Save Error", "Error saving Analysis!")
            raise
            return
        obj.project.analysisFiles.pop(obj.name)
        # set new analysis name
        obj.path = path
        name = os.path.basename(path)
        obj.name = name
        self.projectTree.item(item, text=name)
        obj.project.analysisFiles[name] = obj
        tkMessageBox.showinfo("Saved Info", "Analysis saved to file!")

    def clickedTree(self, event):
        self.checkButtonState()
        item, obj, typ = self.getSelectedItem()
        if item == None:
            return
            
        # get project
        if typ == "project":
            self.model.currentProject = obj
        elif typ == "mzMLFile":
            self.model.currentProject = obj.project

        # set button state
        if typ == "analysis":
            self.model.currentAnalysis = obj
            self.model.currentProject = obj.project
            self.model.runFilters()
            self.model.classes["NotebookScoring"].updateTree([])
            self.model.classes["NotebookIdentification"].updateTree([])
            self.model.classes["NotebookFeature"].updateTree()
            self.model.classes["TwoDView"].init()
            self.model.classes["NotebookIdentification"].updateHeader()

        else:
            self.model.currentAnalysis = None
            self.model.classes["NotebookScoring"].updateTree([])
            self.model.classes["NotebookIdentification"].updateTree([])
            self.model.classes["NotebookFeature"].updateTree()





    def getSelectedItem(self):
        # returns ItemId, Object, ObjectType
        selection = self.projectTree.selection()
        if len(selection) == 0:
            return (None, None, "")
        item = selection[0]
        if not item in self.projectsTreeIds:
            return (None, None, "")
        # get type of item
        taglist = list(self.projectTree.item(item, "tags"))
        if "project" in taglist:
            return (item, self.projectsTreeIds[item], "project")
        if "mzMLFile" in taglist:
            return (item, self.projectsTreeIds[item], "mzMLFile")
        if "analysis" in taglist:
            return (item, self.projectsTreeIds[item], "analysis")
        return (item, self.projectsTreeIds[item], "")


class AddProject(Tkinter.Toplevel):

    def __init__(self, master, model):
        Tkinter.Toplevel.__init__(self, master=master)
        self.master = master
        self.title("Add Project")

        self.model = model
        # ensure correct window stacking
        #self.lift(self.master)

        self.projectName = Tkinter.StringVar()
        projectLabel = Tkinter.Label(self, text="Name: ")
        projectLabel.grid(row=0, column=0, sticky=('N', 'W', 'E', 'S'))

        projectEntry = Tkinter.Entry(self, textvariable=self.projectName)
        projectEntry.grid(row=0, column=1, sticky=('N', 'W', 'E', 'S'))
        projectEntry.config(bg="white")

        self.path = Tkinter.StringVar()
        pathLabel = Tkinter.Label(self, text="mzML-File: ")
        pathLabel.grid(row=1, column=0, sticky=('N', 'W', 'E', 'S'))

        pathEntry = Tkinter.Entry(self, textvariable=self.path)
        pathEntry.grid(row=1, column=1, columnspan=2, sticky=('N', 'W', 'E', 'S'))
        pathEntry.config(bg="white")

        pathButton = Tkinter.Button(self, text="Open MZML-File", command=self.openDialog)
        pathButton.grid(row=1, column=3)

        b1 = Tkinter.Button(self, text="Load", command=self.finish)
        b1.grid(row=2, column=2)
        b2 = Tkinter.Button(self, text="Cancel", command=self.destroy)
        b2.grid(row=2, column=3)

        # get window size
        #self.update()
        self.model.centerWidget(self.master, self)

        # raise to top
        self.focus_set()
        self.transient(master)
        self.lift()
        self.wm_deiconify()

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
        self.master.addProject(name, path)


    def openDialog(self):
        options = {}
        options['defaultextension'] = '.mzML'
        options['filetypes'] = [('mzML files', '.mzML'), ('all files', '.*')]
        options['initialdir'] = self.model.workingdir
        options['parent'] = self
        options['title'] = 'Open mzML file'
        path = tkFileDialog.askopenfilename(**options)
        self.path.set(path)





class FindAnalysis(Tkinter.Toplevel):

    def __init__(self, master, model):
        Tkinter.Toplevel.__init__(self, master=master)
        self.master = master
        self.model = model
        self.title("Find Analysis")
        self.minsize(600, 300)

        self.analysisFiles = set()
        self.keywords = set()

        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=0)
        self.rowconfigure(1, weight=0)
        self.rowconfigure(2, weight=1)
        self.rowconfigure(3, weight=0)

        self.frameRoot = ttk.Labelframe(self, text="Set Search Startingpoint")
        self.frameSearch = ttk.Labelframe(self, text="Search for")
        self.frameResults = ttk.Labelframe(self, text="Analysis Files")
        self.frameFinal = Tkinter.Frame(self)

        self.frameRoot.grid(row=0, column=0, sticky="NSEW")
        self.frameSearch.grid(row=1, column=0, sticky="NSEW")
        self.frameResults.grid(row=2, column=0, sticky="NSEW")
        self.frameFinal.grid(row=3, column=0, sticky="NSEW")

        self.frameRoot.columnconfigure(0, weight=1)
        self.frameRoot.columnconfigure(1, weight=0)

        self.frameSearch.columnconfigure(0, weight=1)

        self.frameResults.columnconfigure(0, weight=1)
        self.frameResults.rowconfigure(0, weight=1)

        self.varRoot = Tkinter.StringVar()
        entryRoot = Tkinter.Entry(self.frameRoot, textvariable=self.varRoot)
        entryRoot.config(bg="white")
        entryRoot.grid(row=0, column=0, sticky="NSEW")

        self.varRoot.trace("w", self.rootChanged)

        buttonChoose = Tkinter.Button(self.frameRoot, text="Choose Root", command=self.chooseRoot)
        buttonChoose.grid(row=0, column=1)

        # --------------

        self.varSearch = Tkinter.StringVar()
        entrySearch = Tkinter.Entry(self.frameSearch, textvariable=self.varSearch)
        entrySearch.config(bg="white")
        entrySearch.grid(row=0, column=0, sticky="NSEW")

        self.varSearch.trace("w", self.keywordsChanged)

        # ----------

        scrollbar = Tkinter.Scrollbar(self.frameResults, orient="vertical")
        self.listBox = Tkinter.Listbox(self.frameResults,selectmode="single",yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.listBox.yview)
        self.listBox.grid(row=0, column=0,sticky="NSEW")
        scrollbar.grid(row=0, column=1,sticky="NSEW")

        self.listBox.bind("<<ListboxSelect>>", self.listSelected)

        # ----------
        buttonCancel = Tkinter.Button(self.frameFinal,text="Cancel",command=self.cancel)
        self.buttonOK = Tkinter.Button(self.frameFinal,text="OK",command=self.ok)
        self.buttonOK.pack(side="right", anchor="se")
        buttonCancel.pack(side="right", anchor="se")

        self.varRoot.set(self.model.workingdir)

    def rootChanged(self,*arg,**args):
        print "root changed to ", self.varRoot.get()
        # collect all analysis files
        self.collectAllFiles()
        self.updateListbox()

    def collectAllFiles(self):
        start = self.varRoot.get()
        if os.path.isdir(start) == False:
            return
        self.analysisFiles = set()
        for root, directories, filenames in os.walk(start):
            for filename in filenames:
                if filename.endswith(".xml"):
                    self.analysisFiles.add(os.path.join(root,filename))

    def keywordsChanged(self,*arg,**args):
        self.keywords = set()
        for text in self.varSearch.get().split(","):
            text = text.strip()
            self.keywords.add(text)
        self.updateListbox()

    def updateListbox(self):
        self.buttonOK.config(state="disabled")
        self.listBox.delete(0, "end")
        for analysis in sorted(self.analysisFiles):
            found = True
            for keyword in self.keywords:
                if not keyword in analysis:
                    found = False
                    break
            if found == True:
                self.listBox.insert("end", analysis)

    def cancel(self):
        self.destroy()

    def ok(self):
        selection = self.listBox.curselection()
        if len(selection) == 0:
            self.buttonOK.config(state="disabled")
            return
        else:
            self.buttonOK.config(state="normal")
        analysisPath = self.listBox.get(selection[0])
        mzMLPath = self.chooseMzML(analysisPath)
        if mzMLPath == None:
            return
        else:
            name = os.path.basename(mzMLPath)
            self.master.addProject(name, mzMLPath)
            self.destroy()

    def chooseMzML(self, analysisPath):

        basedir = os.path.dirname(analysisPath)
        print "basedir", basedir
        options = {}
        options['defaultextension'] = '.mzML'
        options['filetypes'] = [('mzML files', '.mzML'), ('all files', '.*')]
        options['initialdir'] = basedir
        options['parent'] = self
        options['title'] = 'Choose mzML file'
        path = tkFileDialog.askopenfilename(**options)
        return path

    def chooseRoot(self):
        options = {}
        #options['defaultextension'] = '.mzML'
        #options['filetypes'] = [('mzML files', '.mzML'), ('all files', '.*')]
        options['initialdir'] = self.varRoot.get()
        options['parent'] = self
        options['title'] = 'Choose search starting point'
        path = tkFileDialog.askdirectory(**options)
        self.varRoot.set(path)

    def listSelected(self,*arg, **args):
        selection = self.listBox.curselection()
        if len(selection) == 0:
            self.buttonOK.config(state="disabled")
            return
        else:
            self.buttonOK.config(state="normal")


