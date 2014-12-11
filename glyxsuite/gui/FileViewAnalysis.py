import ThreadedIO
import ttk 
from Tkinter import *
import glyxsuite
import tkFileDialog
import os
        
class ThreadedAnalysisFile(ThreadedIO.ThreadedIO):
    
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
            print "result",self.result
            self.model.analysis = self.result
            self.master.updateTreeView()
            
    def threadedAction(self):
        try:
            print "loading experiment"
            glyMl = glyxsuite.io.GlyxXMLFile()
            glyMl.readFromFile(self.path)
            self.queue.put(glyMl)
            print "loading finnished"
        except:
            self.running = False
            raise
        
def treeview_sort_column(tv, col, reverse):    
    l = [(tv.set(k, col), k) for k in tv.get_children('')]
    l.sort(reverse=reverse)
    

    # rearrange items in sorted positions
    for index, (val, k) in enumerate(l):
        tv.move(k, '', index)
        
        # adjust tags
        taglist = list(tv.item(k,"tags"))
        if "oddrowFeature" in taglist:
            taglist.remove("oddrowFeature")
        if "evenrowFeature" in taglist:
            taglist.remove("evenrowFeature")
            
        if index%2 == 0:    
            taglist.append("evenrowFeature")
        else:
            taglist.append("oddrowFeature")
        tv.item(k,tags = taglist)        

    # reverse sort next time
    tv.heading(col, command=lambda: treeview_sort_column(tv, col, not reverse))
        

class FileViewAnalysis(ttk.Frame):
    
    def __init__(self,master,model):
        ttk.Frame.__init__(self,master=master)
        self.master = master
        self.model = model
        b = Button(self, text="Open Analysis file",command=self.openAnalysisFile)
        b.grid(row=0,column=0,sticky=(N, W, E, S))
        
        scrollbar = Scrollbar(self)    
        self.tree = ttk.Treeview(self,yscrollcommand=scrollbar.set)
        
        columns = ("RT","Score","Peptide","Glycan")
        self.tree["columns"] =("RT","Score","Peptide","Glycan")
        
        for col in columns:
            self.tree.column(col,width=100)
            self.tree.heading(col, text=col, command=lambda col=col: treeview_sort_column(self.tree, col, False))
        
        self.tree.grid(row=1,column=0,sticky=(N, W, E, S))
        self.model.debug = self.tree
        
        scrollbar.grid(row=1,column=1,sticky=(N, W, E, S))
        scrollbar.config(command=self.tree.yview)
        
        
        # treeview style
        #self.tree.tag_configure('oddrow', background='orange')
        self.tree.tag_configure('oddrowFeature', background='Moccasin')
        self.tree.tag_configure('evenrowFeature', background='PeachPuff')
        
        self.tree.tag_configure('evenSpectrum', background='LightBlue')
        self.tree.tag_configure('oddSpectrum', background='SkyBlue')
        self.tree.bind("<<TreeviewSelect>>", self.clickedTree);
        
        
        
    def clickedTree(self,event):
        item = self.tree.selection()[0]
        print "clicked on ",item, 
        if not item in self.model.treeIds:
            return
        # get tag
        if self.tree.tag_has("feature", item):
            print "feature"
        elif self.tree.tag_has("spectrum", item):
            print "spectrum"
            s = self.model.treeIds[item]
            key = s.getNativeId()
            print key,len(self.model.spectra)
            if not key in self.model.spectra:
                print "no spectra found"
                return
            self.model.funcPaintSpectrum(self.model.spectra[key])
            
        else:
            print "unknown tag"
        
    def openAnalysisFile(self):

        
        options = {}
        options['defaultextension'] = '.xml'
        options['filetypes'] = [('Analysis files', '.xml'),('all files', '.*')]
        options['initialdir'] = self.model.workingdir
        options['parent'] = self.master
        options['title'] = 'This is a title'
        path = tkFileDialog.askopenfilename(**options)
        #path = '/afs/mpi-magdeburg.mpg.de/data/bpt/bptglycan/DATA_EXCHANGE/Terry/GlyxMSuite/AMAZON/CID/20140904_TNK_FET_TA_A8001_BA1_01_3142/20140904_TNK_FET_TA_A8001_BA1_01_3142_20140922.mzML'
        print "path:",path
        if len(path) > 0:
            # set new working dir
            self.model.workingdir = os.path.split(path)[0]
            # load file in new thread
            self.t = ThreadedAnalysisFile(path,self.model,self)
            self.t.start()
            
            
    def updateTreeView(self):
        print "update treeview"
        # create dict of spectra
        spectra = {}
        for s in self.model.analysis.spectra:
            key = s.getNativeId()
            spectra[key] = s
        self.model.combination = spectra
        i = 0
        ids = {}
        
        for feature in self.model.analysis.features:
            i += 1
            # get spectra
            featureSpectra = []
            minScore = 10+i
            for key in feature.getSpectraIds():
                s = spectra[key]
                featureSpectra.append(s)
                if s.getLogScore() < minScore:
                    minScore = s.getLogScore()
            if i%2 == 0:
                bgtag = "oddrowFeature"
            else:
                bgtag = "evenrowFeature"
            itemFeature = self.tree.insert("" , "end",text="Feature "+str(i), values=(round(feature.getRT(),0),round(minScore,2)),tags=('feature',bgtag))
            ids[itemFeature] = feature
            e = 1
            for s in featureSpectra:
                e *= -1
                taglist = ["spectrum"]
                if e == 1:
                    taglist.append("evenSpectrum")
                else:
                    taglist.append("oddSpectrum")
                itemSpectra = self.tree.insert(itemFeature , "end",text="Spectra ", values=(round(s.getRT(),0),round(s.getLogScore(),2)),tags=taglist)
                ids[itemSpectra] = s
                
        self.model.treeIds = ids
        return 
 
