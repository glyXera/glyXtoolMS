import Tkinter
import ttk
import tkFileDialog
from glyxtoolms.gui import Appearance
import os
import imp
import tkMessageBox
import shutil
import sys
import re

class ToppasConfigurationFrame(Tkinter.Toplevel):

    def __init__(self, master, model):
        Tkinter.Toplevel.__init__(self, master=master)
        #self.minsize(600, 300)
        self.master = master
        self.title("OpenMS Configuration")
        #self.config(bg="#d9d9d9")
        self.model = model

        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=0)
        self.rowconfigure(1, weight=0)
        self.rowconfigure(2, weight=0)
        self.rowconfigure(3, weight=0)
        self.rowconfigure(4, weight=1)

        self.columnconfigure(0, weight=1)


        frameOpenMS = ttk.Labelframe(self, text="OpenMS Installation Path")
        frameOpenMS.grid(row=0, column=0, sticky="NWES")
        frameOpenMS.columnconfigure(0, weight=0)
        frameOpenMS.columnconfigure(1, weight=1)
        buttonOpenMS = Tkinter.Button(frameOpenMS, text="Set Path", command=self.setOpenMSPath)
        
        buttonOpenMS.grid(row=0, column=0)

        self.openMSPathVar = Tkinter.StringVar()
        self.openMSPathVar.set(self.model.openMSDir)
        self.openMSPathEntry = Tkinter.Entry(frameOpenMS, textvariable=self.openMSPathVar, width=60)
        self.openMSPathEntry.grid(row=0, column=1)
        self.openMSPathEntry.config(bg="white")
        self.openMSPathVar.trace("w", self.setButtonState)
        
        frameWorkflows = ttk.Labelframe(self, text="Change Scriptpath in TOPPAS Workflows")
        frameWorkflows.grid(row=1, column=0, sticky="NWES")
        self.buttonWorkflow = Tkinter.Button(frameWorkflows, text="Select TOPPAS Workflows to edit", command=self.editWorkflows)
        self.buttonWorkflow.grid(row=0, column=0)


        frameButtons = ttk.Frame(self)
        frameButtons.grid(row=5, column=0, sticky="NWES")

        cancelButton = Tkinter.Button(frameButtons, text="Cancel", command=self.cancel)
        self.saveButton = Tkinter.Button(frameButtons, text="Save and Synchronize", command=self.save)

        cancelButton.grid(row=0, column=0, sticky="NWES")
        self.saveButton.grid(row=0, column=1, sticky="NWES")
        self.setButtonState()
        self.focus_set()
        self.transient(master)
        self.lift()
        self.wm_deiconify()

    
    def editWorkflows(self):
        if not self.checkOpenMSPath():
            tkMessageBox.showerror("Invalid OpenMS Path", "Invalid OpenMS Installation path!",parent=self)
            return
        scriptsPath = self.getScriptsPath()
        
        options = {}
        #options['initialdir'] = self.openMSPathVar.get()
        options['title'] = 'Choose one or multiple TOPPAS workflows'
        options['filetypes'] = [('TOPPAS workflow','*.toppas')]
        files = tkFileDialog.askopenfilenames(**options)
        for filepath in files:
            fin = file(filepath,"r")
            text = fin.read()
            fin.close()
            text2 = re.sub('name\=\"scriptpath\" value\=\".+?\"','name="scriptpath" value="'+scriptsPath+'"',text)
            fout = file(filepath,"w")
            fout.write(text2)
            fout.close()
            print "changed", filepath
        if len(files) > 0:
            tkMessageBox.showinfo("Sucessfully edited "+str(len(files))+" Workflows", str(len(files))+" TOPPAS workflows are sucessfully edited!",parent=self)
        else:
            tkMessageBox.showinfo("No workflows selected", "Please select one or ore TOPPAS workflows!",parent=self)

    def setButtonState(self,*args):
        if not self.checkOpenMSPath():
            self.openMSPathEntry.config(bg="red")
            self.saveButton.config(state=Tkinter.DISABLED)
            self.buttonWorkflow.config(state=Tkinter.DISABLED)
        else:
            self.openMSPathEntry.config(bg="white")
            self.saveButton.config(state=Tkinter.NORMAL)
            self.buttonWorkflow.config(state=Tkinter.NORMAL)

    def setOpenMSPath(self):
        options = {}
        options['initialdir'] = self.openMSPathVar.get()
        options['title'] = 'Set Path to OpenMS Folder'
        options['mustexist'] = True
        path = tkFileDialog.askdirectory(**options)
        if path == "" or path == ():
            return
        self.openMSPathVar.set(path)
        self.setButtonState()
        if not self.checkOpenMSPath():
            tkMessageBox.showerror("Invalid OpenMS Path", "Invalid OpenMS Installation path!",parent=self)

    def getScriptsPath(self):
        return os.path.join(self.openMSPathVar.get(), "share/OpenMS/SCRIPTS")

    def getExternalPath(self):
        return os.path.join(self.openMSPathVar.get(), "share/OpenMS/TOOLS/EXTERNAL")

    def checkOpenMSPath(self):
        if os.path.exists(self.getScriptsPath()) == False:
            return False
        if os.path.exists(self.getExternalPath()) == False:
            return False
        return True

    def copyFiles(self):
        pythonpath = sys.executable # get path to the used python environment
        glyxtoolmsPath = imp.find_module("glyxtoolms")[1]
        toppPath = os.path.join(os.path.dirname(glyxtoolmsPath), "TOPP")
        if not self.checkOpenMSPath():
            return
        scriptsPath = self.getScriptsPath()
        externalsPath = self.getExternalPath()
        for filename in os.listdir(toppPath):
            pathFrom = os.path.join(toppPath, filename)
            if filename.endswith(".py"):
                pathTo = os.path.join(scriptsPath, filename)
                shutil.copy2(pathFrom, pathTo)
                print "copy " + filename + " to " + pathTo
            elif filename.endswith(".ttd"):
                pathTo = os.path.join(externalsPath, filename)
                fin = file(pathFrom, "r")
                text = fin.read()
                text = text.replace("{pythonpath}",pythonpath)
                text = text.replace("{scriptpath}",scriptsPath)
                fin.close()

                fout = file(pathTo,"w")
                fout.write(text)
                fout.close()
                print "copy " + filename + " to " + pathTo


    def cancel(self):
        if not self.checkOpenMSPath():
            ask = tkMessageBox.askyesno("Invalid OpenMS Path",
                                    "OpenMS Path is invalid, do you still want to leave?",
                                    default=tkMessageBox.YES)
            if ask == True:
                self.destroy()
        else:
            self.destroy()

    def save(self):
        self.setButtonState()
        if not self.checkOpenMSPath():
            tkMessageBox.showerror("Invalid OpenMS Path", "Invalid OpenMS Installation path!",parent=self)
            return
        self.openMSPathEntry.config(bg="white")
        self.model.openMSDir = self.openMSPathVar.get()
        self.model.saveSettings()
        self.copyFiles()
        tkMessageBox.showinfo("Synchronized files", "TOPPAS Scripts are now up-to date!",parent=self)
        self.destroy()


