import ttk
import Tkinter

import tkFileDialog
import tkMessageBox
import os

import pyopenms
import glyxtoolms
from glyxtoolms.gui import ThreadedIO
from glyxtoolms.gui import DataModel

class ThreadedOpenMZML(ThreadedIO.ThreadedIO):

    def __init__(self, master, path, project):
        ThreadedIO.ThreadedIO.__init__(self)
        self.path = path
        self.project = project
        self.master = master
        self.error = False


    def updateExternal(self, running=False):
        if not running:
            print "loading finished"
            self.project.mzMLFile.exp = self.result
            self.master.loadedMzMLFile(self.error, self.project)

    def threadedAction(self):
        try:
            print "loading experiment"
            exp = pyopenms.MSExperiment()
            fh = pyopenms.FileHandler()
            fh.loadExperiment(self.path, exp)
            self.queue.put(exp)
            print "loading finnished"
        except:
            self.running = False
            self.error = True
            tkMessageBox.showerror("File input error",
                                   "Error while loading pyopenms file!")
            raise

class ThreadedAnalysisFile(ThreadedIO.ThreadedIO):

    def __init__(self, master, path, analysis):
        ThreadedIO.ThreadedIO.__init__(self)
        self.path = path
        self.analysis = analysis
        self.master = master
        self.error = False


    def updateExternal(self, running=False):
        if not running:
            print "stopped"
            self.analysis.analysis = self.result
            self.master.loadedAnalysisFile(self.error, self.analysis)

    def threadedAction(self):
        try:
            print "loading experiment"
            glyMl = glyxtoolms.io.GlyxXMLFile()
            glyMl.readFromFile(self.path)
            self.queue.put(glyMl)
            print "loading finnished"
        except:
            tkMessageBox.showerror("File input error",
                                   "Error while loading analysis "
                                   "file! Please check glyML version.")
            self.running = False
            raise

class ProjectFrame(ttk.Frame):

    def __init__(self, master, model):
        ttk.Frame.__init__(self, master=master)
        self.master = master
        self.model = model

        tools = ttk.Frame(self)
        self.b1 = ttk.Button(tools, text="Add Project", command=self.clickedAddProject)
        self.b1.grid(row=0, column=0)

        self.b2 = ttk.Button(tools, text="Close Project", command=self.closeProject)
        self.b2.grid(row=0, column=1)
        self.b2.config(state=Tkinter.DISABLED)

        self.b3 = ttk.Button(tools, text="Add Analysis", command=self.clickedAddAnalysis)
        self.b3.grid(row=1, column=0)
        self.b3.config(state=Tkinter.DISABLED)

        #NORMAL, ACTIVE or DISABLED

        self.b4 = ttk.Button(tools, text="Close Analysis", command=self.closeAnalysis)
        self.b4.grid(row=1, column=1)
        self.b4.config(state=Tkinter.DISABLED)

        self.b5 = ttk.Button(tools, text="Save Analysis", command=self.saveAnalysis)
        self.b5.grid(row=1, column=2)
        self.b5.config(state=Tkinter.DISABLED)

        #self.b1 = ttk.Button(tools, text="Load Test", command=self.loadTest)
        #self.b1.grid(row=0, column=2)


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

    def loadTest(self):
        name = "test"
        path = "/afs/mpi-magdeburg.mpg.de/data/bpt/bptglycan/DATA_EXCHANGE/Terry/GlyxMSuite/AMAZON/CID/testdata/20141202_FETinsol03_HILIC_TNK_BB4_01_3743.mzML"
        self.addProject(name, path)

    def clickedAddProject(self):
        AddProject(self, self.model)


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

        t = ThreadedAnalysisFile(self, path, analysis)
        t.start()

    def addProject(self, name, path):
        print "loading path", path
        project = DataModel.Project(name, path)

        mzMLContainer = DataModel.ContainerMZMLFile(project, path)
        project.mzMLFile = mzMLContainer

        # load file in new thread
        t = ThreadedOpenMZML(self, path, project)
        t.start()

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

        obj.analysis.writeToFile(path)
        obj.project.analysisFiles.pop(obj.name)
        # set new analysis name
        obj.path = path
        name = os.path.basename(path)
        obj.name = name
        self.projectTree.item(item, text=name)
        obj.project.analysisFiles[name] = obj


    def clickedTree(self, event):
        item, obj, typ = self.getSelectedItem()
        if item == None:
            # deaktive all buttons, except addProject
            self.b2.config(state=Tkinter.DISABLED)
            self.b3.config(state=Tkinter.DISABLED)
            self.b4.config(state=Tkinter.DISABLED)
            self.b5.config(state=Tkinter.DISABLED)
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
            self.model.currentAnalysis = obj
            self.model.currentProject = obj.project
            self.b4.config(state=Tkinter.NORMAL)
            self.b5.config(state=Tkinter.NORMAL)
            self.model.runFilters()
            self.model.classes["NotebookScoring"].updateTree([])
            self.model.classes["NotebookIdentification"].updateTree([])
            self.model.classes["NotebookFeature"].updateFeatureTree()
            self.model.classes["TwoDView"].init()
            self.model.classes["NotebookIdentification"].updateHeader()

        else:
            self.model.currentAnalysis = None
            self.b4.config(state=Tkinter.DISABLED)
            self.b5.config(state=Tkinter.DISABLED)
            self.model.classes["NotebookScoring"].updateTree([])
            self.model.classes["NotebookIdentification"].updateTree([])
            self.model.classes["NotebookFeature"].updateFeatureTree()

    def loadedMzMLFile(self, error, project):
        if error == True:
            return

        # reorganize data
        project.mzMLFile.createIds()

        item = self.projectTree.insert("", "end", text=project.name, tags=("project", ))
        self.model.projects[project.name] = project
        self.projectsTreeIds[item] = project

        # set workingdir
        self.model.workingdir = os.path.split(project.path)[0]
        self.model.currentProject = project

        itemMZML = self.projectTree.insert(item, "end",
                                           text=os.path.basename(project.path),
                                           tags=("mzMLFile", ))

        # add ContainerMZMLFile
        self.projectsTreeIds[itemMZML] = project.mzMLFile

        # Aktivate close button
        if len(self.model.projects) > 0:
            self.b2.config(state=Tkinter.NORMAL)
        else:
            self.b2.config(state=Tkinter.DISABLED)

        print "loaded mzml file"

    def loadedAnalysisFile(self, error, analysis):
        if error == True:
            return
        itemAnalysis = self.projectTree.insert(analysis.projectItem, "end",
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
        self.model.classes["NotebookFeature"].updateFeatureTree()

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
        self.update()
        h = self.winfo_height()
        w = self.winfo_width()

        # get screen width and height
        ws = master.winfo_screenwidth() # width of the screen
        hs = master.winfo_screenheight() # height of the screen

        # calculate x and y coordinates for the Tk window
        x = (ws/2) - (w/2)
        y = (hs/2) - (h/2)
        # set the dimensions of the screen 
        # and where it is placed
        self.geometry('%dx%d+%d+%d' % (w, h, x, y))

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


