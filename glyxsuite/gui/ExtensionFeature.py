import ttk
import Tkinter
import TwoDView

class ExtensionFeature(ttk.Labelframe):
    
    def __init__(self,master,model,text):
        ttk.Labelframe.__init__(self,master=master,text=text)
        self.master = master
        self.model = model
        twoDFrame = ttk.Labelframe(self,text="Precursor Chromatogram")
        twoDFrame.grid(row=0,column=0)
        twoDView = TwoDView.TwoDView(twoDFrame,model,height=450,width=500)
        twoDView.grid(row=0,column=0)

        scrollbar = Tkinter.Scrollbar(self)    
        self.tree = ttk.Treeview(self,yscrollcommand=scrollbar.set)
        columns = ("RT","Mass","Charge","Score","Is Glyco")
        self.tree["columns"] = columns
        self.tree.column("#0",width=100)
        for col in columns:
            self.tree.column(col,width=80)
            self.tree.heading(col, text=col, command=lambda col=col: self.sortColumn(col))
            
        self.tree.grid(row=1,column=0,sticky=("N", "W", "E", "S"))
        
        scrollbar.grid(row=1,column=1,sticky=("N", "W", "E", "S"))
        scrollbar.config(command=self.tree.yview)
        
        self.model.funcUpdateExtentionFeature = self.updateTree

    def sortColumn(self,col):
        
        if col == self.model.currentAnalysis.sortedColumn:
            self.model.currentAnalysis.reverse = not self.model.currentAnalysis.reverse
        else:
            self.model.currentAnalysis.sortedColumn = col
            self.model.currentAnalysis.reverse = False
        if col == "Is Glyco":
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
        print "update"
        # clear tree
        self.tree.delete(*self.tree.get_children());

        analysis = self.model.currentAnalysis
        
        if analysis == None:
            #print "foo1"
            return
        
        feature = analysis.currentFeature
        if feature == None:
            #print "foo2"
            return
        #print "foo3",len(analysis.data)
        # insert all ms2 spectra
        minRT,maxRT,minMZ,maxMZ = feature.getBoundingBox()
        #print feature.getBoundingBox()
        index = 0
        for spec,spectrum in analysis.data:

            if spectrum.rt < minRT:
                continue
            if spectrum.rt > maxRT:
                continue
            if spectrum.precursorMass < minMZ:
                continue
            if spectrum.precursorMass > maxMZ:
                continue                

            index += 1
            if index%2 == 0:    
                tag = ("oddrowFeature",)
            else:
                tag = ("evenrowFeature",)
                
            isGlycopeptide = "no"
            if spectrum.isGlycopeptide:
                isGlycopeptide = "yes"
            name = spectrum.nativeId
            
            itemSpectra = self.tree.insert("" , "end",text=name,
                values=(round(spectrum.rt,1),
                        round(spectrum.precursorMass,4),
                        spectrum.precursorCharge,
                        round(spectrum.logScore,2),
                        isGlycopeptide),
                tags = tag)
            #self.treeIds[itemSpectra] = (spec,spectrum)
