import ThreadedIO
import ttk 
from Tkinter import * 
import pyopenms
import tkFileDialog
        
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
            print "stopped"
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
        

        

class FileViewMZML(ttk.Frame):
    
    def __init__(self,master,model):
        ttk.Frame.__init__(self,master=master)
        self.master = master
        self.model = model
        b = Button(self, text="Open mzML file",command=self.openMzMLFile)
        b.grid(row=0,column=0,sticky=(N, W, E, S))
        
        tree = ttk.Treeview(self)
        
        tree["columns"]=("one","two")
        tree.column("one", width=100 )
        tree.column("two", width=100)
        
        tree.heading("one", text="coulmn A")
        tree.heading("two", text="column B")
        for i in range(0,20):
            tree.insert("" , "end",text="Line "+str(i), values=(str(i)+"A","1b"))
        tree.grid(row=1,column=0,sticky=(N, W, E, S))

        
    def openMzMLFile(self):

        
        options = {}
        options['defaultextension'] = '.mzML'
        options['filetypes'] = [('mzML files', '.mzML'),('all files', '.*')]
        options['initialdir'] = self.model.workingdir
        options['parent'] = self.master
        options['title'] = 'This is a title'
        #path = tkFileDialog.askopenfilename(**options)
        path = '/afs/mpi-magdeburg.mpg.de/data/bpt/bptglycan/DATA_EXCHANGE/Terry/GlyxMSuite/AMAZON/CID/20140904_TNK_FET_TA_A8001_BA1_01_3142/20140904_TNK_FET_TA_A8001_BA1_01_3142_20140922.mzML'
        #print path
        if path != "":
            # load file in new thread
            t = ThreadedOpenMZML(path,self.model,self)
            t.start() 


    def updateMZMLView(self):
        self.spectra = {}
        for spec in self.model.exp:
            if spec.getMSLevel() == 2:
                key = spec.getNativeID()
                self.model.spectra[key] = spec
        return
