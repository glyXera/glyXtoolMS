import ttk
import Tkinter
import DataModel
import HistogramView
import glyxsuite

class NotebookScoring(ttk.Frame):
    
    def __init__(self,master,model):
        ttk.Frame.__init__(self,master=master)
        self.master = master
        self.model = model
        
        frameSpectrum = ttk.Labelframe(self,text="Spectrum")
        frameSpectrum.grid(row=0,column=0,sticky=("N", "W", "E", "S"))
        
        frameTree = ttk.Labelframe(self,text="MS/MS Spectra")
        frameTree.grid(row=1,column=0,sticky=("N", "W", "E", "S"))
        
        l1 = ttk.Label(frameSpectrum, text="Spectrum-Id:")
        l1.grid(row=0,column=0,sticky="NE")
        self.v1 = Tkinter.StringVar()
        self.c1 = ttk.Label(frameSpectrum, textvariable=self.v1)
        self.c1.grid(row=0,column=1,sticky="NW")
        
        l2 = ttk.Label(frameSpectrum, text="RT:")
        l2.grid(row=1,column=0,sticky="NE")
        self.v2 = Tkinter.StringVar()
        self.c2 = ttk.Entry(frameSpectrum, textvariable=self.v2)
        self.c2.grid(row=1,column=1,sticky="NW")
        
        l3 = ttk.Label(frameSpectrum, text="Precursormass:")
        l3.grid(row=2,column=0,sticky="NE")
        self.v3 = Tkinter.StringVar()
        self.c3 = ttk.Entry(frameSpectrum, textvariable=self.v3)
        self.c3.grid(row=2,column=1,sticky="NW")
        
        l4 = ttk.Label(frameSpectrum, text="Precursorcharge:")
        l4.grid(row=3,column=0,sticky="NE")
        self.v4 = Tkinter.StringVar()
        self.c4 = ttk.Entry(frameSpectrum, textvariable=self.v4)
        self.c4.grid(row=3,column=1,sticky="NW")
        
        l5 = ttk.Label(frameSpectrum, text="Score:")
        l5.grid(row=4,column=0,sticky="NE")
        self.v5 = Tkinter.StringVar()
        self.c5 = ttk.Entry(frameSpectrum, textvariable=self.v5)
        self.c5.grid(row=4,column=1,sticky="NW")
        
        l6 = ttk.Label(frameSpectrum, text="Is Glycopeptide:")
        l6.grid(row=5,column=0,sticky="NE")
        self.v6 = Tkinter.IntVar()
        self.c6 = ttk.Checkbutton(frameSpectrum, variable=self.v6)
        self.c6.grid(row=5,column=1)
        
        b1 = ttk.Button(frameSpectrum, text="save Changes",command=self.saveChanges)
        b1.grid(row=4,rowspan=2,column=2)
        
        # show treeview of mzML file MS/MS and MS   
        scrollbar = ttk.Scrollbar(frameTree)    
        self.tree = ttk.Treeview(frameTree,yscrollcommand=scrollbar.set)
            
        columns = ("RT","Mass","Charge","Score","Is Glyco")
        self.tree["columns"] = columns
        self.tree.column("#0",width=100)
        for col in columns:
            self.tree.column(col,width=80)
            #self.tree.heading(col, text=col, command=lambda col=col: treeview_sort_column(self.tree, col, False))
            self.tree.heading(col, text=col, command=lambda col=col: self.sortColumn(col))
            
        self.tree.grid(row=0,column=0,sticky=("N", "W", "E", "S"))
        
        scrollbar.grid(row=0,column=1,sticky=("N", "W", "E", "S"))
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
        
        index = 0
        for spec,spectrum in analysis.data:
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
            self.treeIds[itemSpectra] = (spec,spectrum)
            
            
    def clickedTree(self,event):
        selection = self.tree.selection()
        if len(selection) == 0:
            return
        item = selection[0]
        spec,spectrum = self.treeIds[item]

        # set values of spectrum
        self.v1.set(spectrum.nativeId)
        self.v2.set(spectrum.rt)
        self.v3.set(spectrum.precursorMass)
        self.v4.set(spectrum.precursorCharge)
        self.v5.set(spectrum.logScore)          
        self.v6.set(spectrum.isGlycopeptide)
        
        # make calculations
        ms2,ms1 = self.model.currentProject.mzMLFile.experimentIds[spectrum.nativeId]
        mz = spectrum.precursorMass
        charge = spectrum.precursorCharge
        p = ms2.getPrecursors()[0]
        low = p.getIsolationWindowLowerOffset()
        high = p.getIsolationWindowUpperOffset()
        if low == 0:
            low = 2
        if high == 0:
            high = 2
        low = mz-low
        high = mz+high
        
        #rtLow = ms1.getRT()-100
        #rtHigh = ms1.getRT()+100
        
        # create chromatogram
        c = DataModel.Chromatogram()
        c.plot = True
        c.name = "test"
        c.rangeLow = mz-0.1
        if charge != 0:
            c.rangeHigh = mz+3/abs(float(charge))+0.1
        else:
            c.rangeHigh = mz+1+0.1
        c.rt = []
        c.intensity = []
        c.msLevel = 1
        c.selected = True
        # get mz range to extract
        for spec in self.model.currentProject.mzMLFile.exp:
            if spec.getMSLevel() == 1:
                break
        lowPeak = -1
        highPeak = -1
        i = 0
        for mass in spec.get_peaks()[:,0]:
            if lowPeak == -1 and mass > c.rangeLow:
                lowPeak = i
            if highPeak == -1 and mass > c.rangeHigh:
                highPeak = i
                break
            i += 1
        rtLow = spectrum.chromatogramSpectra[0].getRT()
        rtHigh = spectrum.chromatogramSpectra[-1].getRT()
        for spec in spectrum.chromatogramSpectra:
            c.rt.append(spec.getRT())
            # get intensity in range
            c.intensity.append(sum(spec.get_peaks()[lowPeak:highPeak,1]))

        # set chromatogram within analysis
        self.model.currentAnalysis.chromatograms[c.name] = c
        self.model.currentAnalysis.selectedChromatogram = c
        
        # init spectrum view
        self.model.funcScoringMSMSSpectrum(ms2)
        
        # init precursor spectrum view
        self.model.funcScoringMSSpectrum(ms1,mz,charge,low,high)
        
        # init chromatogram view
        self.model.funcScoringChromatogram(rtLow,rtHigh,ms2.getRT())
       
    def saveChanges(self):
        selection = self.tree.selection()
        if len(selection) == 0:
            return
        item = selection[0]
        spec,spectrum = self.treeIds[item]
        
        spectrum.rt = float(self.v2.get())
        spectrum.precursorMass = float(self.v3.get())
        spectrum.precursorCharge = int(self.v4.get())
        spectrum.logScore = float(self.v5.get())
        spectrum.isGlycopeptide = bool(self.v6.get())
        
        # change values in table view
        isGlycopeptide = "no"
        if spectrum.isGlycopeptide:
            isGlycopeptide = "yes"
        self.tree.item(item, values=(round(spectrum.rt,1),
                        round(spectrum.precursorMass,4),
                        spectrum.precursorCharge,
                        round(spectrum.logScore,2),
                        isGlycopeptide))
