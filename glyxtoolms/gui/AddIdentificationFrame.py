import ttk
import Tkinter
import tkMessageBox

import glyxtoolms
from glyxtoolms.gui import ConsensusSpectrumFrame3

class AddIdentificationFrame(Tkinter.Toplevel):

    def __init__(self, master, model, feature):
        Tkinter.Toplevel.__init__(self, master=master)
        #self.minsize(600, 300)
        self.master = master
        self.feature = feature
        self.title("Add Identification")
        self.config(bg="#d9d9d9")
        self.model = model
        self.glycan = None
        self.peptide = None
        self.tolerance = 0.05
        self.toleranceType = "Da"
        
        self.ownModifications = set()

        self.minsize(600, 300)

        self.columnconfigure(0, weight=0)
        self.columnconfigure(1, weight=0)
        self.columnconfigure(2, weight=1)
        self.rowconfigure(0, weight=0)
        self.rowconfigure(1, weight=1)
        self.rowconfigure(2, weight=0)
        self.rowconfigure(3, weight=0)
        self.rowconfigure(4, weight=0)

        frameFeature = ttk.Labelframe(self, text="Feature")
        frameGlycan = ttk.Labelframe(self, text="Glycan")
        framePeptide = ttk.Labelframe(self, text="Peptide")
        frameAddCancel = ttk.Labelframe(self, text="Add Identification / Cancel")
        self.frameSpec = ConsensusSpectrumFrame3.ConsensusSpectrumFrame(self, model)

        frameGlycan.grid(row=0, column=0, sticky=("NWES"))
        frameFeature.grid(row=0, column=1, sticky=("NWES"))
        frameAddCancel.grid(row=0, column=2, sticky=("NWES"))

        framePeptide.grid(row=1, column=0, columnspan=3, sticky=("NWES"))
        framePeptide.columnconfigure(0, weight=0)
        framePeptide.columnconfigure(1, weight=1)
        framePeptide.rowconfigure(0, weight=0)
        framePeptide.rowconfigure(1, weight=0)
        framePeptide.rowconfigure(2, weight=0)
        framePeptide.rowconfigure(3, weight=1)

        self.frameSpec.grid(row=4, column=0, columnspan=3, sticky=("NWES"))

        self.precursorMass = (self.feature.getMZ()*self.feature.getCharge()-
                              glyxtoolms.masses.MASS["H+"]*(self.feature.getCharge()-1))

        labelMass = Tkinter.Label(frameFeature, text="Feature Mass")
        labelMassValue = Tkinter.Label(frameFeature, text=str(round(self.precursorMass,4))+ " Da")
        labelMass.grid(row=0, column=0, sticky="NWES")
        labelMassValue.grid(row=0, column=1, columnspan=2, sticky="NWES")

        labelError = Tkinter.Label(frameFeature, text="Feature Error")
        self.labelErrorValue = Tkinter.Label(frameFeature, text="- Da")
        labelError.grid(row=1, column=0, sticky="NWES")
        self.labelErrorValue.grid(row=1, column=1, columnspan=2, sticky="NWES")

        labelGlycan = Tkinter.Label(frameGlycan, text="Glycan")
        self.glycanVar = Tkinter.StringVar()
        self.glycanVar.trace("w", self.valuesChanged)
        self.entryGlycan = Tkinter.Entry(frameGlycan, textvariable=self.glycanVar)
        labelGlycanMassLabel = Tkinter.Label(frameGlycan, text="Glycan Mass")
        self.labelGlycanMass = Tkinter.Label(frameGlycan, text="")

        labelGlycan.grid(row=0, column=0, sticky="NWES")
        self.entryGlycan.grid(row=0, column=1, columnspan=2, sticky="NWES")
        labelGlycanMassLabel.grid(row=1, column=0, sticky="NWES")
        self.labelGlycanMass.grid(row=1, column=1, columnspan=2, sticky="NWES")


        labelPeptide = Tkinter.Label(framePeptide, text="Sequence")
        self.peptideVar = Tkinter.StringVar()
        self.peptideVar.trace("w", self.valuesChanged)
        self.entryPeptide = Tkinter.Entry(framePeptide, textvariable=self.peptideVar)
        labelPeptideMassLabel = Tkinter.Label(framePeptide, text="Mass")
        self.labelPeptideMass = Tkinter.Label(framePeptide, text="")

        labelPeptide.grid(row=0, column=0, sticky="NWES")
        self.entryPeptide.grid(row=0, column=1, columnspan=3, sticky="NWES")
        labelPeptideMassLabel.grid(row=1, column=0, sticky="NWES")
        self.labelPeptideMass.grid(row=1, column=1, columnspan=1, sticky="NWS")
        
        
        labelProtein = Tkinter.Label(framePeptide, text="Protein")
        self.proteinVar = Tkinter.StringVar()
        self.proteinVar.trace("w", self.valuesChanged)
        self.entryProtein = Tkinter.Entry(framePeptide, textvariable=self.proteinVar)
        self.entryProtein.config(bg="white")
        labelProtein.grid(row=2, column=0, sticky="NWES")
        self.entryProtein.grid(row=2, column=1, columnspan=2, sticky="NWS")
        
        labelPeptideStart = Tkinter.Label(framePeptide, text="Peptide Start")
        self.peptideStartVar = Tkinter.StringVar()
        self.peptideStartVar.trace("w", self.valuesChanged)
        self.entryPeptideStart = Tkinter.Entry(framePeptide, textvariable=self.peptideStartVar)
        self.entryPeptideStart.config(bg="white")
        labelPeptideStart.grid(row=1, column=2, sticky="NWES")
        self.entryPeptideStart.grid(row=1, column=3, sticky="NWS")
        

        frameModifications = ttk.Labelframe(framePeptide, text="Modifications")
        frameModifications.grid(row=3, column=0, columnspan=4, sticky="NWES")

        frameModifications.columnconfigure(0, weight=1)
        frameModifications.columnconfigure(1, weight=0)
        frameModifications.columnconfigure(2, weight=0)
        frameModifications.columnconfigure(3, weight=1)
        frameModifications.rowconfigure(0, weight=1)
        frameModifications.rowconfigure(1, weight=1)
        frameModifications.rowconfigure(2, weight=0)
        frameModifications.rowconfigure(3, weight=0)

        frameTreeLeft = ttk.Labelframe(frameModifications, text="Available Modifications")
        frameTreeMiddle = ttk.Labelframe(frameModifications, text="Available Aminoacids")
        frameTreeRight = ttk.Labelframe(frameModifications, text="Set Modifications")
        self.b1 = Tkinter.Button(frameModifications, text=">", command=self.addModification)
        self.b2 = Tkinter.Button(frameModifications, text="<", command=self.removeModification)
        b3 = Tkinter.Button(frameModifications, text="define new modification", command=self.defineModification)
        self.b4 = Tkinter.Button(frameModifications, text="remove modification definition", command=self.deleteDefinition)

        self.useFragmentInfo = Tkinter.IntVar()
        checkBox = Tkinter.Checkbutton(frameModifications, text="Solve modification positions with fragments in spectrum ", variable=self.useFragmentInfo)
        
        
        massErrorFrame = ttk.Labelframe(frameModifications, text="Annotation Mass Error")
        self.massErrorVar = Tkinter.StringVar()
        self.massErrorEntry = Tkinter.Entry(massErrorFrame,textvariable=self.massErrorVar)
        self.massErrorEntry.config(bg="white")
        self.massErrorVar.set("0.05")
        
        self.errorTypeVar = Tkinter.StringVar()
        massErrorTypeDa = Tkinter.Radiobutton(massErrorFrame, text="Da", variable=self.errorTypeVar, value="Da")
        massErrorTypePPM = Tkinter.Radiobutton(massErrorFrame, text="ppm", variable=self.errorTypeVar, value="ppm")
        self.errorTypeVar.set("Da")
        self.massErrorVar.trace("w", self.errorChanged)
        self.errorTypeVar.trace("w", self.errorChanged)
        self.massErrorEntry.grid(row=0,column=1,sticky="NWES")
        massErrorTypeDa.grid(row=0,column=2,sticky="NWES")
        massErrorTypePPM.grid(row=0,column=3,sticky="NWES")
        
        frameTreeLeft.grid(row=0, column=0, rowspan=2, sticky="NWES")
        frameTreeMiddle.grid(row=0, column=1, rowspan=2, sticky="NWES")

        self.b1.grid(row=0, column=2, sticky="NWES")
        self.b2.grid(row=1, column=2, sticky="NWES")
        b3.grid(row=2, column=0, sticky="NWES")
        self.b4.grid(row=3, column=0, sticky="NWES")
        checkBox.grid(row=2, column=1, sticky="NWES")
        massErrorFrame.grid(row=3, column=1, sticky="NWES")
        

        frameTreeRight.grid(row=0, column=3, rowspan=2, sticky="NWES")

        frameTreeLeft.columnconfigure(0, weight=1)
        frameTreeLeft.columnconfigure(1, weight=0)
        frameTreeLeft.rowconfigure(0, weight=1)

        frameTreeMiddle.columnconfigure(0, weight=1)
        frameTreeMiddle.columnconfigure(1, weight=0)
        frameTreeMiddle.rowconfigure(0, weight=1)

        frameTreeRight.columnconfigure(0, weight=1)
        frameTreeRight.columnconfigure(1, weight=0)
        frameTreeRight.rowconfigure(0, weight=1)

        scrollbarLeft = Tkinter.Scrollbar(frameTreeLeft)
        self.treeModLeft = ttk.Treeview(frameTreeLeft, selectmode='browse', yscrollcommand=scrollbarLeft.set)
        self.treeModLeft.grid(row=0, column=0, sticky="NWES")
        scrollbarLeft.grid(row=0, column=1, sticky="NWES")
        scrollbarLeft.config(command=self.treeModLeft.yview)

        scrollbarMiddle = Tkinter.Scrollbar(frameTreeMiddle)
        self.treeModMiddle = ttk.Treeview(frameTreeMiddle, selectmode='browse', yscrollcommand=scrollbarMiddle.set)
        self.treeModMiddle.grid(row=0, column=0, sticky="NWES")
        scrollbarMiddle.grid(row=0, column=1, sticky="NWES")
        scrollbarMiddle.config(command=self.treeModLeft.yview)

        scrollbarRight = Tkinter.Scrollbar(frameTreeRight)
        self.treeModRight = ttk.Treeview(frameTreeRight, selectmode='browse', yscrollcommand=scrollbarRight.set)
        self.treeModRight.grid(row=0, column=0, sticky="NWES")
        scrollbarRight.grid(row=0, column=1, sticky="NWES")
        scrollbarRight.config(command=self.treeModLeft.yview)

        cancelButton = Tkinter.Button(frameAddCancel, text="Cancel", command=self.cancel)
        saveButton = Tkinter.Button(frameAddCancel, text="Add Identification", command=self.addIdentification)

        cancelButton.grid(row=0, column=0, sticky="NWES")
        saveButton.grid(row=0, column=1, sticky="NWES")

        # setup treeviews
        columnsLeft = ("Mass", "Positions",)
        self.treeModLeft["columns"] = columnsLeft
        self.treeModLeft.heading("#0", text="Modification")
        self.treeModLeft.heading("Mass", text="Mass")
        self.treeModLeft.heading("Positions", text="Positions")

        self.treeModLeft.column("#0", width=100)
        self.treeModLeft.column("Mass", width=100)
        self.treeModLeft.column("Positions", width=100)

        columnsMiddle = ("Aminoacid",)
        self.treeModMiddle["columns"] = columnsMiddle
        self.treeModMiddle.heading("#0", text="#")
        self.treeModMiddle.heading("Aminoacid", text="Aminoacid")
        self.treeModMiddle.column("#0", width=30)
        self.treeModMiddle.column("Aminoacid", width=80)

        columnsRight = ("Modification",)
        self.treeModRight["columns"] = columnsRight
        self.treeModRight.heading("#0", text="#")
        self.treeModRight.heading("Modification", text="Modification")
        self.treeModRight.column("#0", width=30)
        self.treeModRight.column("Modification", width=100)

        # add available modifications
        self.fillAvailableModifications()

        # get window size
        self.update()
        h = self.winfo_height()
        w = self.winfo_width()

        # get screen width and height
        ws = master.winfo_screenwidth() # width of the screen
        hs = master.winfo_screenheight() # height of the screen

        # calculate x and y coordinates for the Tk window
        x = (ws/2) - (w/2)
        y = (hs/2) - (h/2)
        # set the dimensions of the screen
        # and where it is placed
        self.geometry('%dx%d+%d+%d' % (w, h, x, y))

        # create treeview bindings
        self.treeModLeft.bind("<<TreeviewSelect>>", self.clickedTreeLeft)
        self.treeModMiddle.bind("<<TreeviewSelect>>", self.clickedTreeMiddle)
        self.treeModRight.bind("<<TreeviewSelect>>", self.clickedTreeRight)

        self.treeModLeft.tag_configure('predefined', background='Moccasin')
        self.treeModLeft.tag_configure('own', background='LightSalmon')

        # init values
        self.peptideVar.set("")
        self.glycanVar.set("")
        self.proteinVar.set("")
        self.frameSpec.init(feature, None)
        self.plotFragments()
        
    def errorChanged(self,*args):
        try:
            error = abs(float(self.massErrorVar.get()))
            self.massErrorEntry.config(bg="white")
        except:
            self.massErrorEntry.config(bg="red")
            return
        self.tolerance = error
        self.toleranceType = self.errorTypeVar.get()
        
        self.plotFragments()

    def plotFragments(self):
        if self.peptide == None:
            return
        
        types = set("a,a-H2O,a-NH3,b,b-H2O,b-NH3,by,c,c-H2O,c-NH3,x,x-H2O,x-NH3,y,y-H2O,y-NH3,z,z-H2O,z-NH3,z*".split(","))
        
        active = self.model.classes["PeptideCoverageFrame"].getActiveIons()
        for mod in ["-NH3","-H2O"]:
            if mod in active:
                for ion in ["a","b","c","x","y","z"]:
                    if ion in active:
                        active.add(ion+mod)
        
        fragmentProvider = glyxtoolms.fragmentation.FragmentProvider(types=active)
        result = fragmentProvider.annotateSpectrumWithFragments(self.peptide,
                                                                self.glycan,
                                                                self.feature.consensus,
                                                                self.tolerance,
                                                                self.toleranceType,
                                                                self.feature.getCharge())

        peptidevariant = result["peptidevariant"]
        fragments = result["fragments"]

        # write fragments to hit
        if peptidevariant == None:
            self.frameSpec.init(self.feature, None)
            return
        if self.useFragmentInfo.get() == 1:
            self.peptideVar.set(peptidevariant.toString())
        if self.valid == False:
            self.frameSpec.init(self.feature, None)
            return
        # create hit
        mass = self.peptide.mass+self.glycan.mass+glyxtoolms.masses.MASS["H+"]
        self.peptide.proteinID = self.proteinVar.get()
        diff = mass-self.precursorMass
        self.hit = glyxtoolms.io.GlyxXMLGlycoModHit()
        self.hit.featureID = self.feature.getId()
        self.hit.glycan = self.glycan
        self.hit.peptide = self.peptide
        self.hit.error = diff
        self.hit.feature = self.feature
        self.hit.fragments = fragments

        self.frameSpec.init(self.feature, self.hit)

    def defineModification(self):
        ElementCompositionFrame(self,self.model)

    def deleteDefinition(self):
        if self.peptide == None:
            return
        selectionLeft = self.treeModLeft.selection()
        if len(selectionLeft) == 0:
            return
        itemLeft = selectionLeft[0]
        mod = self.treeModLeft.item(itemLeft, "text")
        self.ownModifications.remove(mod)
        self.valuesChanged()


    def fillAvailableModifications(self):
        self.treeModLeft.delete(*self.treeModLeft.get_children())
        self.b1.config(state=Tkinter.DISABLED)
        self.b2.config(state=Tkinter.DISABLED)
        self.b4.config(state=Tkinter.DISABLED)

        if self.peptide == None:
            return
        # add available modifications
        copypeptide = self.peptide.copy()
        for mod in glyxtoolms.masses.PROTEINMODIFICATION:
            content = glyxtoolms.masses.PROTEINMODIFICATION[mod]
            if "targets" not in content:
                continue
            # generate peptide variant with added modification
            copypeptide.modifications = list(self.peptide.modifications)
            copypeptide.addModification(mod)
            if copypeptide.testModificationValidity() == False:
                continue
            mass = content.get("mass", 0.0)
            targets = content.get("targets", set())
            if len(targets) == 0:
                targetstring = "?"
            else:
                targetstring = ", ".join(targets)

            item = self.treeModLeft.insert("",
                                           "end",
                                           text=mod,
                                           values=(str(round(mass,4)), targetstring),
                                           tags=("predefined",))
        for modname in self.ownModifications:
            # generate peptide variant with added modification
            copypeptide.modifications = list(self.peptide.modifications)
            # get all possible free positions
            taken = set([mod.position for mod in copypeptide.modifications if mod.position != -1])
            free = set(range(0,len(copypeptide.sequence))).difference(taken)
            if len(free) == 0:
                continue
            copypeptide.addModification(modname, positions=free)
            if copypeptide.testModificationValidity() == False:
                continue
            # parse composition again, and calulate mass
            comp = glyxtoolms.masses.getModificationComposition(modname)
            mass = glyxtoolms.masses.calcMassFromElements(comp)
            targetstring = "?"
            item = self.treeModLeft.insert("",
                                           "end",
                                           text=modname,
                                           values=(str(round(mass,4)), targetstring),
                                           tags=("own",))

    def fillSetModifications(self):
        # construct from current peptide
        self.treeModRight.delete(*self.treeModRight.get_children())
        self.b1.config(state=Tkinter.DISABLED)
        self.b2.config(state=Tkinter.DISABLED)
        if self.peptide == None:
            return
        for mod in sorted(self.peptide.modifications, key=lambda x:x.position):
            if mod.position == -1:
                text = "?"
            else:
                text = str(mod.position+1)
            item = self.treeModRight.insert("", "end", text=text,
                                               values=(mod.name,))
    def addModification(self):
        if self.peptide == None:
            return
        selectionLeft = self.treeModLeft.selection()
        if len(selectionLeft) == 0:
            return
        itemLeft = selectionLeft[0]
        modname = self.treeModLeft.item(itemLeft, "text")

        selectionMiddle = self.treeModMiddle.selection()
        if len(selectionMiddle) == 0:
            return
        itemMiddle = selectionMiddle[0]
        pos = self.treeModMiddle.item(itemMiddle, "text")

        if pos == "?":
            pos = -1
        else:
            pos = int(pos) - 1
        self.peptide.addModification(modname, position=pos)
        self.peptideVar.set(self.peptide.toString())

    def removeModification(self):
        if self.peptide == None:
            return
        selection = self.treeModRight.selection()
        if len(selection) == 0:
            return
        item = selection[0]
        pos = self.treeModRight.item(item, "text")
        modname = self.treeModRight.item(item, "values")[0]
        if pos == "?":
            pos = -1
        else:
            pos = int(pos)-1
        for mod in self.peptide.modifications:
            if mod.name == modname and mod.position == pos:
                self.peptide.modifications.remove(mod)
                break
        self.peptideVar.set(self.peptide.toString())

    def clickedTreeLeft(self, event=None):
        # update middle tree with valid aminoacids
        self.treeModMiddle.delete(*self.treeModMiddle.get_children())
        self.b1.config(state=Tkinter.DISABLED)
        self.b2.config(state=Tkinter.DISABLED)

        if self.peptide == None:
            return
        selection = self.treeModLeft.selection()
        if len(selection) == 0:
            return
        item = selection[0]
        modname = self.treeModLeft.item(item, "text")

        copypeptide = self.peptide.copy()
        if modname in self.ownModifications:
            taken = set([mod.position for mod in copypeptide.modifications if mod.position != -1])
            free = set(range(0,len(copypeptide.sequence))).difference(taken)
            copypeptide.addModification(modname, positions=free)
            self.b4.config(state=Tkinter.NORMAL)
        else:
            copypeptide.addModification(modname)
            self.b4.config(state=Tkinter.DISABLED)

        # get available positions on the peptide
        positions = set()
        for pepvariant in glyxtoolms.fragmentation.getModificationVariants(copypeptide,glycantyp={"N":0,"O":0}):
            for mod in pepvariant.modifications:
                if mod.name.upper() == modname.upper():
                    positions.add(mod.position)
        taken = set([mod.position for mod in self.peptide.modifications if mod.position != -1])
        item = self.treeModMiddle.insert("", "end", text="?", values=("?",))
        for i in range(0, len(self.peptide.sequence)):
            if i in taken:
                continue
            if i in positions:
                amino = self.peptide.sequence[i]
                values = (amino,)
                item = self.treeModMiddle.insert("", "end", text=str(i+1), values=values)

    def clickedTreeMiddle(self, event=None):
        self.b1.config(state=Tkinter.NORMAL)

    def clickedTreeRight(self, event=None):
        self.b2.config(state=Tkinter.NORMAL)

    def valuesChanged(self, *args):
        # check entries for validity

        self.valid = True
        try:
            self.glycan = glyxtoolms.lib.Glycan(self.glycanVar.get())
            self.labelGlycanMass.config(text=str(self.glycan.mass) +" Da")
            self.glycanVar.set(self.glycan.toString())
            self.entryGlycan.config(bg="white")
            index = len(self.glycanVar.get())
            self.entryGlycan.icursor(index)

        except:
            self.valid = False
            self.glycan = None
            self.labelGlycanMass.config(text=" - Da")
            self.entryGlycan.config(bg="red")

        try:
            pepstring = self.peptideVar.get()
            if pepstring.strip() == "":
                raise Exception("No Peptide defined")
            self.peptide = glyxtoolms.io.XMLPeptide()
            self.peptide.fromString(pepstring)
            if self.peptide.testModificationValidity() == False:
                raise Exception("Invalid Modification")
            self.peptide.proteinID = self.proteinVar.get()
            self.labelPeptideMass.config(text=str(self.peptide.mass) +" Da")
            self.entryPeptide.config(bg="white")
        except:
            self.valid = False
            self.peptide = None
            self.labelPeptideMass.config(text=" - Da")
            self.entryPeptide.config(bg="red")


        # TODO: Checks for circular updating
        self.clickedTreeLeft(None)
        self.fillAvailableModifications()
        self.fillSetModifications()

        # calculate Identification error
        if self.valid == True:
            mass = self.peptide.mass+self.glycan.mass+glyxtoolms.masses.MASS["H+"]
            diff = mass-self.precursorMass
            self.labelErrorValue.config(text=str(round(diff,4)) + " Da")
            self.plotFragments()

        else:
            self.labelErrorValue.config(text="- Da")

    def defineNewModification(self, mod):
        self.ownModifications.add(mod)
        self.valuesChanged()

    def addIdentification(self):
        
        def getGlycoType(pos, peptide):
            amino = peptide.sequence[pos]
            if amino == "N":
                return (pos+peptide.start, "N")
            elif amino == "S" or amino == "T":
                return (pos+peptide.start, "O")
            else:
                raise Exception("Unkown glycosylation type")
        
        if self.valid == False:
            tkMessageBox.showerror("Invalid Identification", "Identification is invalid, please provide correct peptide and glycan input!",parent=self)
            return
            
        # separate glyco modification from other
        otherModifications = []
        glycoMod = []
        for mod in self.hit.peptide.modifications:
            if mod.name == "GLYCO":
                glycoMod.append(mod)
            else:
                otherModifications.append(mod)
                
                
        glycosylationSites = []
        for mod in glycoMod:
            if mod.position == -1:
                for pos in mod.positions:
                    glycosylationSites.append(getGlycoType(pos, self.hit.peptide))
            else:
                glycosylationSites.append(getGlycoType(mod.position, self.hit.peptide))

        self.hit.peptide.modifications = otherModifications
        self.hit.peptide.glycosylationSites = glycosylationSites
        
        self.feature.hits.add(self.hit)

        self.model.currentAnalysis.analysis.glycoModHits.append(self.hit)

        self.destroy()
        self.model.runFilters()
        self.model.classes["NotebookFeature"].updateTree()
        self.model.classes["NotebookIdentification"].updateTree()
        tkMessageBox.showinfo("Added new Identification", "Sucessfully added new Identification!")

    def cancel(self):
        self.destroy()

class ElementBox(Tkinter.Frame):

    def __init__(self, master, name, update):
        Tkinter.Frame.__init__(self, master=master)
        self.update = update

        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=0)
        self.columnconfigure(2, weight=0)
        self.rowconfigure(0, weight=1)

        self.var = Tkinter.IntVar()
        self.var.trace("w", self.valuesChanged)
        label = Tkinter.Label(self, text=name)
        entry = ttk.Entry(self, textvariable=self.var, width=3)
        scrollbar = ttk.Scrollbar(self)
        label.grid(row=0, column=1, sticky="NWES")
        entry.grid(row=0, column=2, sticky="NWES")
        scrollbar.grid(row=0, column=3, sticky="NWES")
        scrollbar.config(command=self.change)
        self.var.set(0)

    def getValue(self):
        try:
            return int(self.var.get())
        except:
            return 0

    def valuesChanged(self, *args):
        try:
            int(self.var.get())
        except:
            self.var.set("")
        try:
            self.update()
        except:
            pass # function gets called during init, throwing errors everywhere

    def change(self, scroll, direction, units):
        self.var.set(self.getValue()-int(direction))
        self.valuesChanged()

class ElementCompositionFrame(Tkinter.Toplevel):

    def __init__(self, master, model):
        Tkinter.Toplevel.__init__(self, master=master)
        #self.minsize(600, 300)
        self.master = master
        self.title("Define Modification")
        self.config(bg="#d9d9d9")
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=0)
        self.rowconfigure(0, weight=0)
        self.rowconfigure(1, weight=1)
        self.rowconfigure(2, weight=0)

        self.elements = ["C", "H", "O", "N", "S", "P", "Na", "K", "Mg"]
        elementFrame = ttk.Labelframe(self, text="Elements")
        elementFrame.grid(row=0, column=0, columnspan=2, sticky="NWES")
        columns = 5
        self.content = {}
        for i in range(0,len(self.elements)):
            row = i/columns
            col = i%columns
            elementFrame.columnconfigure(col, weight=1)
            elementFrame.rowconfigure(row, weight=1)
            e = ElementBox(elementFrame, self.elements[i], update = self.updateComposition)
            e.grid(row=row, column=col, sticky="NWES")
            self.content[self.elements[i]] = e

        nameFrame = ttk.Labelframe(self, text="Composition")
        nameFrame.grid(row=1, column=0, sticky="NWES")
        nameFrame.columnconfigure(0, weight=1)
        nameFrame.rowconfigure(0, weight=1)

        self.compositionVar = Tkinter.StringVar()
        labelCompositon = Tkinter.Label(nameFrame, textvariable = self.compositionVar, anchor="w", justify="left")
        labelCompositon.grid(row=0, column=0, sticky="NWES")

        massFrame = ttk.Labelframe(self, text="Mass")
        massFrame.grid(row=1, column=1, sticky="NWES")
        massFrame.columnconfigure(0, weight=1)
        massFrame.rowconfigure(0, weight=1)

        self.massVar = Tkinter.StringVar()
        labelMass = Tkinter.Label(massFrame, textvariable = self.massVar, width=15)
        labelMass.grid(row=0, column=0, sticky="NWES")

        okFrame = ttk.Frame(self)
        okFrame.grid(row=2, column=0, columnspan=2, sticky="NWES")


        saveButton = Tkinter.Button(okFrame, text="Add Modification", command=self.addModification)
        cancelButton = Tkinter.Button(okFrame, text="Cancel", command=self.cancel)

        saveButton.grid(row=0, column=0, sticky="NWES")
        cancelButton.grid(row=0, column=1, sticky="NWES")

    def cancel(self):
        self.destroy()

    def addModification(self):
        mod = self.updateComposition()
        if mod == "":
            return
        self.master.defineNewModification(mod)
        self.destroy()

    def updateComposition(self):
        minus = ""
        plus = ""
        for ele in self.elements:
            if ele not in self.content:
                continue
            value = self.content[ele].getValue()
            if value == -1:
                minus += ele
            elif value < -1:
                minus += ele+str(-value)
            elif value == 1:
                plus += ele
            elif value > 1:
                plus += ele+str(value)

        composition = ""
        if plus != "":
            composition += "+"+plus
        if minus != "":
            composition += "-"+minus
        self.compositionVar.set(composition)

        if composition != "":
            # parse composition again, and calulate mass
            comp = glyxtoolms.masses.getModificationComposition(composition)
            mass = glyxtoolms.masses.calcMassFromElements(comp)
            self.massVar.set(round(mass,5))
        else:
            self.massVar.set(0)
        return composition
