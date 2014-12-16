import ttk 
from Tkinter import * 


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
            self.master.fileLoadingFinished()
            
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


class ToolMZML(ttk.Frame):
    def __init__(self,master,model):
        ttk.Frame.__init__(self,master=master)
        self.master = master
        b1 = Button(self, text="Open mzML file",command=self.openMzMLFile)
        b1.grid(row=0,column=0,sticky=(N, W, E, S))   
        
    def openMzMLFile(self,event):
        print "hi"
        
        
    def fileLoadingFinished(self):
        return
    
