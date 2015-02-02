import ttk
import Tkinter
import DataModel

class NotebookFeature(ttk.Frame):
    
    def __init__(self,master,model):
        ttk.Frame.__init__(self,master=master)
        self.master = master
        self.model = model
        
        # show treeview of mzML file MS/MS and MS   
        scrollbar = Tkinter.Scrollbar(self)    
        self.tree = ttk.Treeview(self,yscrollcommand=scrollbar.set)
            
        columns = ("RT","MZ","Charge","Best Score","Nr Spectra")
        self.tree["columns"] = columns
        self.tree.column("#0",width=100)
        for col in columns:
            self.tree.column(col,width=80)
            #self.tree.heading(col, text=col, command=lambda col=col: treeview_sort_column(self.tree, col, False))
            self.tree.heading(col, text=col, command=lambda col=col: self.sortColumn(col))
            
        self.tree.grid(row=1,column=0,sticky=("N", "W", "E", "S"))
        
        scrollbar.grid(row=1,column=1,sticky=("N", "W", "E", "S"))
        scrollbar.config(command=self.tree.yview)
        
        self.treeIds = {}
        
        # treeview style
        self.tree.tag_configure('oddrowFeature', background='Moccasin')
        self.tree.tag_configure('evenrowFeature', background='PeachPuff')
        
        self.tree.tag_configure('evenSpectrum', background='LightBlue')
        self.tree.tag_configure('oddSpectrum', background='SkyBlue')
        self.tree.bind("<<TreeviewSelect>>", self.clickedTree);
        
        self.model.funcUpdateNotebookFeature = self.updateTree

    def sortColumn(self,col):
        
        if col == self.model.currentAnalysis.sortedColumn:
            self.model.currentAnalysis.reverse = not self.model.currentAnalysis.reverse
        else:
            self.model.currentAnalysis.sortedColumn = col
            self.model.currentAnalysis.reverse = False
        if col == "isGlycopeptide":
            l = [(self.tree.set(k, col), k) for k in self.tree.get_children('')]
        else:
            l = [(float(self.tree.set(k, col)), k) for k in self.tree.get_children('')]
        
        l.sort(reverse=self.model.currentAnalysis.reverse)
        

        # rearrange items in sorted positions
        for index, (val, k) in enumerate(l):
            self.tree.move(k, '', index)
            
            # adjust tags
            taglist = list(self.tree.item(k,"tags"))
            if "oddrowFeature" in taglist:
                taglist.remove("oddrowFeature")
            if "evenrowFeature" in taglist:
                taglist.remove("evenrowFeature")
                
            if index%2 == 0:    
                taglist.append("evenrowFeature")
            else:
                taglist.append("oddrowFeature")
            self.tree.item(k,tags = taglist)


    def updateTree(self):
        
        # clear tree
        self.tree.delete(*self.tree.get_children());
        self.treeIds = {}
        
        project = self.model.currentProject
        
        if project == None:
            return
        
        if project.mzMLFile.exp == None:
            return
        
        analysis = self.model.currentAnalysis
        
        if analysis == None:
            return
        
        # insert all ms2 spectra
        #("RT","MZ","Charge","Best Score","Nr Spectra")
        index = 0
        for feature in analysis.analysis.features:
            index += 1
            if index%2 == 0:    
                tag = ("oddrowFeature",)
            else:
                tag = ("evenrowFeature",)
            name = str(index)
            bestScore = 10.0
            for specId in feature.getSpectraIds():
                spectrum = analysis.spectraIds[specId]
                if spectrum.logScore < bestScore:
                    bestScore = spectrum.logScore
            item = self.tree.insert("" , "end",text=name,
                values=(round(feature.getRT(),1),
                        round(feature.getMZ(),4),
                        feature.getCharge(),
                        round(bestScore,2),
                        len(feature.getSpectraIds())),
                tags = tag)
            self.treeIds[item] = feature
            
            
    def clickedTree(self,event):
        selection = self.tree.selection()
        if len(selection) == 0:
            return
        item = selection[0]
        feature = self.treeIds[item]
        self.model.currentAnalysis.currentFeature = feature
        self.model.funcFeatureTwoDView(keepZoom = True)

