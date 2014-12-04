import ThreadedIO
import ttk 
from Tkinter import * 
import pyopenms
import tkFileDialog
import AddChromatogram
import tkMessageBox
import DataModel
        
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
        
        self.tree = ttk.Treeview(self)
        
        #tree["columns"]=("one","two")
        #tree.column("one", width=100 )
        #tree.column("two", width=100)
        
        #tree.heading("one", text="coulmn A")
        #tree.heading("two", text="column B")
        #for i in range(0,20):
        #    tree.insert("" , "end",text="Line "+str(i), values=(str(i)+"A","1b"))
        self.treehookChrom = self.tree.insert("" , "end",text="Chromatograms")
        self.tree.grid(row=1,column=0,sticky=(N, W, E, S))

        columns = ("Name","Plot","Color")
        self.tree["columns"] = columns
        for col in columns:
            self.tree.column(col,width=100)
            self.tree.heading(col, text=col)       
        # create chromatograms button
        chombutton = Button(self, text="Add Chromatogram",command=self.openChromatogramChooser)
        chombutton.grid(row=2,column=0,sticky=(N, W, E, S))
        
        
        b1 = Button(self, text="save",command=self.save)
        b1.grid(row=3, column=0, sticky=N+S)
        
        b2 = Button(self, text="load",command=self.read)
        b2.grid(row=3, column=1, sticky=N+S)

        
        
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
        
    def openChromatogramChooser(self):
        if self.model.exp == None:
            return
        top = AddChromatogram.AddChromatogram(self,self.model)
        
    def addChromatogram(self,options):
        name = options["name"]
        if name == "":
            tkMessageBox.showinfo(title="Warning", 
                message="Chromatogram name is empty")
            return
        if name in self.model.chromatograms:
            tkMessageBox.showinfo(title="Warning", 
                message="A chromatogram with this name exists already!")
            return
        
        rangeLow,rangeHigh = options["range"]
        if rangeLow == "":
            tkMessageBox.showinfo(title="Warning", 
                message="Lower mass range is empty")
            return
        if rangeHigh == "":
            tkMessageBox.showinfo(title="Warning", 
                message="Higher mass range is empty")
            return
            
        mslevel = options["mslevel"]
        
        try:
            rangeLow = float(rangeLow)
        except ValueError:
            tkMessageBox.showinfo(title="Warning", 
                message="Could not convert lower mass range to number!")
            return
            
        try:
            rangeHigh = float(rangeHigh)
        except ValueError:
            tkMessageBox.showinfo(title="Warning", 
                message="Could not convert higher mass range to number!")
            return
        
        # rotate range if necessary          
        if rangeLow > rangeHigh:
            rangeHigh,rangeLow = rangeLow,rangeHigh
            
        x = []
        y = []
        for spec in self.model.exp:
            if spec.getMSLevel() != mslevel:
                continue
            x.append(spec.getRT())
            y.append(spec.intensityInRange(rangeLow,rangeHigh))
        print "chrom",len(x),len(y),mslevel
        c = DataModel.Chromatogram()
        c.name = name
        c.rangeLow = rangeLow
        c.rangeHigh = rangeHigh
        c.color = options["color"]
        c.rt = x
        c.intensity = y
        c.plot = True
        c.msLevel = mslevel
        
        self.model.chromatograms[name] = c
        self.model.funcPaintChromatograms()
        # add chromatogram to treeview
        #tree.insert("" , "end",text="Line "+str(i), values=(str(i)+"A","1b"))
        itemSpectra = self.tree.insert(self.treehookChrom, "end",text=c.name)
        
        
    def save(self):
        f = file("chromopt.txt","w")
        for name in self.model.chromatograms:
            chrom = self.model.chromatograms[name]
            f.write("name:"+chrom.name+"\n")
            f.write("color:"+str(chrom.color)+"\n")
            f.write("range:"+str(chrom.rangeLow)+","+str(chrom.rangeHigh)+"\n")
            f.write("mslevel:"+str(chrom.msLevel)+"\n")            
        f.close()
        print "saved"


    def read(self):
        f = file("chromopt.txt","r")
        chroms = {}
        options = {}

        for line in f:
            key,content = line[:-1].split(":")
            if key == "name":
                options = {}
                options["name"] = content
                chroms[content] = options
            if key == "color":
                options["color"] = content
            if key == "range":
                low,high = map(float,content.split(","))
                options["range"] = (low,high)
            if key == "mslevel":
                options["mslevel"] = int(content)
        f.close()
        for name in chroms:
            print chroms[name]
            self.addChromatogram(chroms[name])
        print "loaded", len(chroms), " chromatograms"
