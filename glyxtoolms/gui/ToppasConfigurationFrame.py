import Tkinter
import ttk
import tkFileDialog
from glyxtoolms.gui import Appearance
import os
import imp
import tkMessageBox
import shutil
import sys

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


        frameOpenMS = ttk.Labelframe(self, text="OpenMS Intallation Path")
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

        #frameScripts= ttk.Labelframe(self, text="Copy GlyXtool Scripts to TOPPPAS")
        #frameScripts.grid(row=1, column=0, sticky="NWES")
        #self.buttonCopy = Tkinter.Button(frameScripts, text="Copy Files", command=self.copyFiles)
        #self.buttonCopy.grid(row=0, column=0)

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

    def setButtonState(self):
        if not self.checkOpenMSPath():
            self.openMSPathEntry.config(bg="red")
            self.saveButton.config(state=Tkinter.DISABLED)
            #self.buttonCopy.config(state=Tkinter.DISABLED)
        else:
            self.openMSPathEntry.config(bg="white")
            self.saveButton.config(state=Tkinter.NORMAL)
            #self.buttonCopy.config(state=Tkinter.NORMAL)

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
        #print "here", imp.find_module("glyxtoolms")
        # check if the following paths exist:
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
        tkMessageBox.showinfo("Synchronized files", "TOPPAs Scripts are now up-to date!",parent=self)
        self.destroy()


