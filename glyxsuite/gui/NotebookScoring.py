import ttk
import Tkinter

def treeview_sort_column(tv, col, reverse):
    print "treeview",tv,col
    if col == "isGlycopeptide":
        l = [(tv.set(k, col), k) for k in tv.get_children('')]
    else:
        l = [(float(tv.set(k, col)), k) for k in tv.get_children('')]
    
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

class NotebookScoring(ttk.Frame):
    
    def __init__(self,master,model):
        ttk.Frame.__init__(self,master=master)
        self.master = master
        self.model = model
        
        frameSpectrum = ttk.Labelframe(self,text="Spectrum")
        frameSpectrum.grid(row=0,column=0,sticky=("N", "W", "E", "S"))
        
        l1 = Tkinter.Label(frameSpectrum, text="Spectrum-Id:")
        l1.grid(row=0,column=0,sticky="NE")
        self.v1 = Tkinter.StringVar()
        self.c1 = Tkinter.Label(frameSpectrum, textvariable=self.v1)
        self.c1.grid(row=0,column=1,sticky="NW")
        
        l2 = Tkinter.Label(frameSpectrum, text="RT:")
        l2.grid(row=1,column=0,sticky="NE")
        self.v2 = Tkinter.StringVar()
        self.c2 = Tkinter.Entry(frameSpectrum, textvariable=self.v2)
        self.c2.grid(row=1,column=1,sticky="NW")
        
        l3 = Tkinter.Label(frameSpectrum, text="Precursormass:")
        l3.grid(row=2,column=0,sticky="NE")
        self.v3 = Tkinter.StringVar()
        self.c3 = Tkinter.Entry(frameSpectrum, textvariable=self.v3)
        self.c3.grid(row=2,column=1,sticky="NW")
        
        l4 = Tkinter.Label(frameSpectrum, text="Precursorcharge:")
        l4.grid(row=3,column=0,sticky="NE")
        self.v4 = Tkinter.StringVar()
        self.c4 = Tkinter.Entry(frameSpectrum, textvariable=self.v4)
        self.c4.grid(row=3,column=1,sticky="NW")
        
        l5 = Tkinter.Label(frameSpectrum, text="Score:")
        l5.grid(row=4,column=0,sticky="NE")
        self.v5 = Tkinter.StringVar()
        self.c5 = Tkinter.Entry(frameSpectrum, textvariable=self.v5)
        self.c5.grid(row=4,column=1,sticky="NW")
        
        l6 = Tkinter.Label(frameSpectrum, text="Is Glycopeptide:")
        l6.grid(row=5,column=0,sticky="NE")
        self.v6 = Tkinter.IntVar()
        self.c6 = Tkinter.Checkbutton(frameSpectrum, variable=self.v6)
        self.c6.grid(row=5,column=1)
        
        b1 = Tkinter.Button(frameSpectrum, text="save Changes",command=self.saveChanges)
        b1.grid(row=5,column=2)
        
        # show treeview of mzML file MS/MS and MS   
        scrollbar = Tkinter.Scrollbar(self)    
        self.tree = ttk.Treeview(self,yscrollcommand=scrollbar.set)
            
        columns = ("RT","Precursormass","Charge","Score","isGlycopeptide")
        self.tree["columns"] = columns
        
        for col in columns:
            self.tree.column(col,width=100)
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
        
        self.model.funcUpdateNotebookScoring = self.updateTree

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
        
        print "update NotebookScoring"
        project = self.model.currentProject
        
        if project == None:
            print "no project"
            return
        
        if project.mzMLFile.exp == None:
            print "no exp"
            return
        
        analysis = self.model.currentAnalysis
        
        if analysis == None:
            print "no analysis"
            return
        
        # insert all ms2 spectra
        
        index = 0
        for spec,spectrum in analysis.data:
            index += 1
            if index%2 == 0:    
                tag = ("oddrowFeature",)
            else:
                tag = ("evenrowFeature",)
            isGlycopeptide = "no"
            if spectrum.getIsGlycopeptide():
                isGlycopeptide = "yes"
            name = spectrum.getNativeId()
            
            itemSpectra = self.tree.insert("" , "end",text=name,
                values=(round(spectrum.getRT(),1),
                        round(spectrum.getPrecursorMass(),4),
                        spectrum.getPrecursorCharge(),
                        round(spectrum.getLogScore(),2),
                        isGlycopeptide),
                tags = tag)
            self.treeIds[itemSpectra] = (spec,spectrum)
            
            
    def clickedTree(self,event):
        print "clicked tree"
        selection = self.tree.selection()
        if len(selection) == 0:
            print "is zero"
            return
        item = selection[0]
        spec,spectrum = self.treeIds[item]

        # set values of spectrum
        self.v1.set(spectrum.getNativeId())
        self.v2.set(spectrum.getRT())
        self.v3.set(spectrum.getPrecursorMass())
        self.v4.set(spectrum.getPrecursorCharge())
        self.v5.set(spectrum.getLogScore())          
        self.v6.set(spectrum.getIsGlycopeptide())
       
    def saveChanges(self):
        selection = self.tree.selection()
        if len(selection) == 0:
            return
        item = selection[0]
        spec,spectrum = self.treeIds[item]
        
        spectrum.setRT(float(self.v2.get()))
        spectrum.setPrecursor(float(self.v3.get()),int(self.v4.get()))
        spectrum.setLogScore(float(self.v5.get()))
        spectrum.setIsGlycopeptide(bool(self.v6.get()))
        
        # change values in table view
        isGlycopeptide = "no"
        if spectrum.getIsGlycopeptide():
            isGlycopeptide = "yes"
        self.tree.item(item, values=(round(spectrum.getRT(),1),
                        round(spectrum.getPrecursorMass(),4),
                        spectrum.getPrecursorCharge(),
                        round(spectrum.getLogScore(),2),
                        isGlycopeptide))
