"""
Panel to set Filteroptions for all Data

""" 
import Tkinter
import ttk
import glyxsuite

class FilterPanel(Tkinter.Toplevel):

    def __init__(self, master, model):
        Tkinter.Toplevel.__init__(self, master=master)
        self.minsize(600,300)
        self.master = master
        self.model = model
        
        self.protocol("WM_DELETE_WINDOW", self._delete_window)
        #self.bind("<Destroy>", self._destroy)

        
        self.title("Filter Options")
        
        #   ------- Identifications ------ #
        self.N_Identification = 0
        
        frameIdentification = ttk.Labelframe(self, text="1. Identifications")
        frameIdentification.grid(row=0, column=0, sticky="NWES")
        
        buttonIdentification = Tkinter.Button(frameIdentification,
                                              text="add Filter",
                                              command=self.addIdentificationFilter)
        buttonIdentification.grid(row=0, column=0, sticky="NWES")
        
        
        self.filterIdentification = ttk.Frame(frameIdentification)
        self.filterIdentification.grid(row=1, column=0, columnspan=2, sticky="NWES")
        
        self.filterIdentification.columnconfigure(0, weight=1)
        
        frameIdentification.columnconfigure(0, weight=0)
        frameIdentification.columnconfigure(1, weight=1)
        
        #   ------- Features ------ #
        self.N_Features = 0

        frameFeature = ttk.Labelframe(self, text="2. Features")
        frameFeature.grid(row=1, column=0, sticky="NWES")
        
        buttonFeature = Tkinter.Button(frameFeature,
                                       text="add Filter",
                                       command=self.addFeatureFilter)
        buttonFeature.grid(row=0, column=0, sticky="NWES")
        
        
        self.filterFeature = ttk.Frame(frameFeature)
        self.filterFeature.grid(row=1, column=0, columnspan=2, sticky="NWES")  

        #   ------- Scoring ------ #        
        self.N_Scoring = 0
        
        frameScoring = ttk.Labelframe(self, text="3. Scoring")
        frameScoring.grid(row=2, column=0, sticky="NWES")
        
        buttonScoring = Tkinter.Button(frameScoring,
                                       text="add Filter",
                                       command=self.addScoringFilter)
        buttonScoring.grid(row=0, column=0, sticky="NWES")
        
        
        self.filterScoring = ttk.Frame(frameScoring)
        self.filterScoring.grid(row=1, column=0, columnspan=2, sticky="NWES")

        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        self.rowconfigure(2, weight=1)

        # add predefined filters
        for f in self.model.filters["Identification"]:
            f.reinitialize()
            self.addIdentificationFilter(f)
            
        for f in self.model.filters["Features"]:
            f.reinitialize()
            self.addFeatureFilter(f)
            
        for f in self.model.filters["Scoring"]:
            f.reinitialize()
            self.addScoringFilter(f)

    def _delete_window(self):
        try:
            self.destroy()
            self.model.runFilters()
            self.model.classes["NotebookScoring"].updateTree()
            self.model.classes["NotebookIdentification"].updateTree()
            self.model.classes["NotebookFeature"].updateFeatureTree()
            self.model.classes["TwoDView"].init()
            
        except:
            pass


        
    def addIdentificationFilter(self, definedFilter=None):
        filters = []
        filters.append(EmptyFilter())
        filters.append(GlycopeptideMass_Filter())
        filters.append(Fragmentmass_Filter())
        filters.append(Fragmentname_Filter(self.model))
        filters.append(StatusFilter())
        
        f = FilterEntry(self.filterIdentification,
                        filters,
                        self.model.filters["Identification"],
                        definedFilter=definedFilter)
        f.grid(row=self.N_Identification, column=0, sticky=("N", "W", "E", "S"))
        self.N_Identification += 1
        
        
    def addFeatureFilter(self, definedFilter=None):
        filters = []
        filters.append(EmptyFilter())
        filters.append(Feature_RT_Filter())
        filters.append(StatusFilter())
        
        f = FilterEntry(self.filterFeature,
                        filters,
                        self.model.filters["Features"],
                        definedFilter=definedFilter)
        f.grid(row=self.N_Features, column=0, sticky=("N", "W", "E", "S"))
        self.N_Features += 1
        
    def addScoringFilter(self, definedFilter=None):
        filters = []
        filters.append(EmptyFilter())
        filters.append(StatusFilter())
        
        f = FilterEntry(self.filterScoring,
                        filters,
                        self.model.filters["Scoring"],
                        definedFilter=definedFilter)
        f.grid(row=self.N_Scoring, column=0, sticky=("N", "W", "E", "S"))
        self.N_Scoring += 1
        
class FilterEntry(ttk.Frame):
    def __init__(self, master, filters, source, definedFilter=None):
        ttk.Frame.__init__(self, master=master)
        
        self.master = master
        self.source = source
        
        # | type | <Field1> | Operator | <Field2> |
        
        self.traceChanges = True
        
        button = Tkinter.Button(self, text=" - ", command=self.delete)
        button.grid(row=0, column=0, sticky=("N", "W", "E", "S"))
        
        # register new filters here
        self.filters = filters

        self.var = Tkinter.StringVar(self)
        
        self.currentFilter = self.filters[0]
        
        self.var.set(self.currentFilter.name)
        self.var.trace("w", self.filterChanged)
        
        self.currentOperator = self.currentFilter.operator

        choices = []
        for f in self.filters:
            choices.append(f.name)
            
        option = Tkinter.OptionMenu(self, self.var, *choices)
        option.grid(row=0, column=1, sticky=("N", "W", "E", "S"))

        self.field1Var = Tkinter.StringVar(self)
        self.field1Var.trace("w", self.valuesChanged)
        self.entry1 = Tkinter.Entry(self, textvariable=self.field1Var)
        self.entry1.grid(row=0, column=2, sticky=("N", "W", "E", "S"))
        
        choices = ['', ]
        self.options1 = Tkinter.OptionMenu(self, self.field1Var, *choices)
        self.options1.grid(row=0, column=2, sticky=("N", "W", "E", "S"))
        
        self.assisted1 = InteractiveEntry(self, self.field1Var)
        self.assisted1.grid(row=0, column=2, sticky=("N", "W", "E", "S"))
    
        self.operatorVar = Tkinter.StringVar(self)
        self.operatorVar.trace("w", self.valuesChanged)
        choicesOperator = ['', ]
        self.optionOperator = Tkinter.OptionMenu(self, self.operatorVar, *choicesOperator)
        self.optionOperator.grid(row=0, column=3, sticky=("N", "W", "E", "S"))
        
        self.field2Var = Tkinter.StringVar(self)
        self.field2Var.trace("w", self.valuesChanged)
        self.entry2 = Tkinter.Entry(self, textvariable=self.field2Var)
        self.entry2.grid(row=0, column=4, sticky=("N", "W", "E", "S"))
        
        choices = ['', ]
        self.options2 = Tkinter.OptionMenu(self, self.field2Var, *choices)
        self.options2.grid(row=0, column=4, sticky=("N", "W", "E", "S"))
        
        self.assisted2 = InteractiveEntry(self, self.field2Var)
        self.assisted2.grid(row=0, column=4, sticky=("N", "W", "E", "S"))
        
        if definedFilter != None:
            self.currentFilter = definedFilter
        self.traceChanges = False
        self.paintCurrentFilter()
        self.traceChanges = True
        
    def valuesChanged(self, *args):
        if self.traceChanges == False:
            return
        self.currentFilter.valid = True
        try:
            self.currentFilter.parseField1(self.field1Var.get())
            self.entry1.config(bg="grey")
            self.assisted1.config(bg="grey")
            self.options1.config(bg="grey")
        except:
            self.currentFilter.valid = False
            self.entry1.config(bg="red")
            self.assisted1.config(bg="red")
            self.options1.config(bg="red")
            
        try:
            self.currentFilter.parseOperator(self.operatorVar.get())
            self.optionOperator.config(bg="grey")
        except:
            self.currentFilter.valid = False
            self.optionOperator.config(bg="red")
                     
        try:
            self.currentFilter.parseField2(self.field2Var.get())
            self.entry2.config(bg="grey")
            self.assisted2.config(bg="grey")
            self.options2.config(bg="grey")
        except:
            self.currentFilter.valid = False
            self.entry2.config(bg="red")
            self.assisted2.config(bg="red")
            self.options2.config(bg="red")
 
    def filterChanged(self, *args):
        if self.traceChanges == False:
            return
        name = self.var.get()
        if self.currentFilter.name == name:
            return
        # remove currentFilter from model
        if self.currentFilter in self.source:
            self.source.remove(self.currentFilter)
        
        self.currentFilter = None
        for f in self.filters:
            if f.name == name:
                self.currentFilter = f
        if self.currentFilter == None:
            raise Exception("Unknown Filter")
                
        self.paintCurrentFilter()

        self.source.append(self.currentFilter)

    def paintCurrentFilter(self):
        self.traceChanges = False
        self.var.set(self.currentFilter.name)
        if self.currentFilter.type1 == FieldTypes.INACTIVE:
            self.entry1.grid_remove()
            self.options1.grid_remove()
            self.assisted1.grid_remove()
            self.assisted1.setVisible(False)
        elif self.currentFilter.type1 == FieldTypes.ENTRY:
            self.entry1.grid()
            self.options1.grid_remove()
            self.assisted1.grid_remove()
            self.assisted1.setVisible(False)
            self.field1Var.set(self.currentFilter.field1)
        elif self.currentFilter.type1 == FieldTypes.MENU:
            self.entry1.grid_remove()
            self.options1.grid()
            self.assisted1.grid_remove()
            self.assisted1.setVisible(False)
            self.setMenuChoices(self.options1,self.currentFilter.choices1, self.field1Var)
            self.field1Var.set(self.currentFilter.field1)           
        elif self.currentFilter.type1 == FieldTypes.ASSISTED:
            self.entry1.grid_remove()
            self.options1.grid_remove()
            self.assisted1.grid()
            self.assisted1.all_choices = self.currentFilter.choices1
            self.field1Var.set(self.currentFilter.field1)
            self.assisted1.setVisible(True)
        else:
            raise Exception("Unknown FieldType!")

        self.setMenuChoices(self.optionOperator, self.currentFilter.operatorChoices, self.operatorVar)
        self.operatorVar.set(self.currentFilter.operator)
        if self.currentFilter.type2 == FieldTypes.INACTIVE:
            self.entry2.grid_remove()
            self.options2.grid_remove()
            self.assisted2.grid_remove()
            self.assisted2.setVisible(False)
        elif self.currentFilter.type2 == FieldTypes.ENTRY:
            self.entry2.grid()
            self.options2.grid_remove()
            self.assisted2.grid_remove()
            self.assisted2.setVisible(False)
            self.field2Var.set(self.currentFilter.field2)
        elif self.currentFilter.type2 == FieldTypes.MENU:
            self.entry2.grid_remove()
            self.options2.grid()
            self.assisted2.grid_remove()
            self.assisted2.setVisible(False)
            self.setMenuChoices(self.options2, self.currentFilter.choices2, self.field2Var)
            self.field2Var.set(self.currentFilter.field2)
        elif self.currentFilter.type2 == FieldTypes.ASSISTED:
            self.entry2.grid_remove()
            self.options2.grid_remove()
            self.assisted2.grid()
            self.assisted2.all_choices = self.currentFilter.choices2
            self.field2Var.set(self.currentFilter.field2)
            self.assisted2.setVisible(True)
            
        else:
            raise Exception("Unknown FieldType!")
        self.traceChanges = True
        self.valuesChanged()
        
        
    def setMenuChoices(self, menu, choices, var):
        menu['menu'].delete(0, 'end')
        if len(choices) == 0:
            var.set("")
            return
        var.set(choices[0])
        for choice in choices:
            menu['menu'].add_command(label=choice, command=Tkinter._setit(var, choice))

    def delete(self):
        self.grid_forget()
        if self.currentFilter in self.source:
            self.source.remove(self.currentFilter)
        return
        
class InteractiveEntry(Tkinter.Entry):
    def __init__(self, master, var):
        Tkinter.Entry.__init__(self, master=master, textvariable=var)
        self.var = var
        self.var.trace("w", self.valuesChanged)
        
        self.all_choices = []
        self.currentText = None
        self.choices = []
        self.keepTrace = True
        self.isVisible = False
        
        self.aMenu = Tkinter.Menu(self.master, tearoff=0)
        self.aMenu.bind("<FocusOut>", self.removeOptions, "+")
        self.bind("<FocusIn>", lambda x: self.valuesChanged(2), "+")
        self.bind("<FocusOut>", self.removeOptions, "+")
        
        
    def setVisible(self, boolean):
        self.isVisible = boolean
    
    def showOptions(self, event):
        if self.isVisible == False:
            return
        if len(self.all_choices) == 0:
            return
        x = self.winfo_rootx()
        y = self.winfo_rooty()+self.winfo_height()
        self.aMenu.post(x, y)
        self.aMenu.bind("<FocusOut>", lambda x: self.removeOptions())
        self.aMenu.unbind_class("Menu", "<Button>") # needed to properly use the FocusOut binding
        
    def removeOptions(self, event = None):
        if self.focus_get() != self.aMenu or self.focus_get() != self:
            self.aMenu.unpost()
            
    def valuesChanged(self, *args):
        if self.isVisible == False:
            return
        if len(self.all_choices) == 0:
            return
        if self.keepTrace == False:
            return
        if self.currentText == self.var.get():
            return
        self.currentText = self.var.get()
        self.removeOptions()

        self.choices = []
        for choice in self.all_choices:
            if self.currentText in choice:
                self.choices.append(choice)
        self.choicePosition = 0
        self.showChoices(0)
        self.showOptions(None)
        
    def showChoices(self, position):
        # delete old options
        self.aMenu.delete(0,"last")
        self.collapseMenu = True
        self.choicePosition = position
        if len(self.choices) > 10 and self.choicePosition > 0:
            self.aMenu.add_command(label="...", command=self.showPrev)
            self.aMenu.add_separator()
        for i in range(self.choicePosition, self.choicePosition+10):
            if i >= len(self.choices):
                break
            choice = self.choices[i]
            item = self.aMenu.add_command(label=choice,
                                          command=lambda x=choice: self.setValue(x))
        if self.choicePosition+10 < len(self.choices):
            self.aMenu.add_separator()
            self.aMenu.add_command(label="...", command=self.showNext)
            
    def setValue(self,choice):
        self.keepTrace = False
        self.var.set(choice)
        self.removeOptions()
        self.master.focus_set()
        self.keepTrace = True
    
    def showNext(self, *args):
        if self.choicePosition+5 < len(self.choices):
            self.removeOptions()
            self.showChoices(self.choicePosition+5)
            self.showOptions(None)
            self.focus_set()

    def showPrev(self):
        self.keepTrace = False
        self.removeOptions()
        if self.choicePosition-5 >= 0:
            self.showChoices(self.choicePosition-5)
        self.showOptions(None)
        self.keepTrace = True

class FieldTypes:
    INACTIVE=1
    ENTRY=2
    MENU=3
    ASSISTED=4

class Filter(object):
    
    def __init__(self, name):
        self.name = name
        self.field1 = ""
        self.choices1 = []
        self.type1 = FieldTypes.INACTIVE
        self.operator = ""
        self.operatorChoices = []
        self.field2 = ""
        self.choices2 = []
        self.type2 = FieldTypes.INACTIVE
        self.valid = False
    
    def reinitialize(self):
        return

    def parseValues(self, field1, operator, field2):
        raise Exception("overwrite this function!")
        
    def parseField1(self, field1):
        raise Exception("overwrite this function!")
        
    def parseField2(self, field1):
        raise Exception("overwrite this function!")
        
    def parseOperator(self, operator):
        assert operator in self.operatorChoices
        self.operator = operator

    def evaluate(self, obj, typ):
        raise Exception("overwrite this function!")
    
    def parseFloatRange(self, string):
        if not "-" in string:
            raise Exception("please provide a range")
        
        sp = string.replace(" ", "").split("-")
        if len(sp) != 2:
            raise Exception("use only one '-'")
        a,b = sp
        try:
            a = float(a)
            b = float(b)
            return a,b
        except:
            raise Exception("cannot convert to number")
            
    def parseFloat(self,string):
        try:
            return float(string)
        except:
            raise Exception("cannot convert to number")    
    
class EmptyFilter(Filter):
    def __init__(self):
        super(EmptyFilter, self).__init__("")
        self.type1 = FieldTypes.INACTIVE
        self.type2 = FieldTypes.INACTIVE
        self.operatorChoices = [""]
        
    def parseField1(self, field1):
        return
        
    def parseField2(self, field2):
        return

    def evaluate(self, obj):
        return True

class StatusFilter(Filter):
    def __init__(self):
        super(StatusFilter, self).__init__("Status")
        self.type1 = FieldTypes.INACTIVE
        self.type2 = FieldTypes.MENU
        self.choices2 = glyxsuite.io.ConfirmationStatus._types
        self.operatorChoices = ["is", "is not"]
        self.operator = "is"
        
    def parseField1(self, field1):
        return
        
    def parseField2(self, field2):
        self.field2 = field2

    def evaluate(self, obj):
        if self.operator == "is":
            if obj.status == self.field2:
                return True
            return False
        else:
            if obj.status == self.field2:
                return False
        return True


class GlycopeptideMass_Filter(Filter):
    def __init__(self):
        super(GlycopeptideMass_Filter, self).__init__("Glycopeptidemass")
        self.type1 = FieldTypes.INACTIVE
        self.field2 = "0 - 1"
        self.type2 = FieldTypes.ENTRY
        self.operatorChoices = ["=", "<", ">"]
        self.operator = "="
        self.lowValue = 0
        self.highValue = 0
        self.value = 0
        
    def parseField1(self,field1):
        return
        
    def parseField2(self,field2):
        if self.operator == "=":
            a, b = self.parseFloatRange(field2)
            if a < b:
                self.lowValue, self.highValue = a, b
            else:
                 self.lowValue, self.highValue = b, a
            self.field2 = str(self.lowValue) + " - " + str(self.highValue)
        else:
            self.value = self.parseFloat(field2)
            self.field2 = str(self.value)
            self.field2 = str(self.value)

    def evaluate(self, hit):
        mass = hit.glycan.mass + hit.peptide.mass
        if self.operator == "<":
            if mass < self.value:
                return True
            else:
                return False
        elif  self.operator == ">":
            if mass > self.value:
                return True
            else:
                return False
        else:
            if self.lowValue <= mass <= self.highValue:
                return True
            else:
                return False


class Fragmentmass_Filter(Filter):
    def __init__(self):
        super(Fragmentmass_Filter, self).__init__("Fragmentmass")
        self.field1 = "0 - 1"
        self.type1 = FieldTypes.ENTRY
        self.field2 = "0 - 1"
        self.type2 = FieldTypes.ENTRY
        self.operatorChoices = ["=", "<", ">"]
        self.operator = "="
        self.lowIntensity = 0
        self.highIntensity = 0
        self.intensity = 0
        
        self.lowMass = 0
        self.highMass = 0
        
    def parseField1(self,field1):
        a, b = self.parseFloatRange(field1)
        if a < b:
            self.lowMass, self.highMass = a, b
        else:
             self.lowMass, self.highMass = b, a
        self.field1 = str(self.lowMass) + " - " + str(self.highMass)
        
    def parseField2(self,field2):
        if self.operator == "=":
            a, b = self.parseFloatRange(field2)
            if a < b:
                self.lowIntensity, self.highIntensity = a, b
            else:
                 self.lowIntensity, self.highIntensity = b, a
            self.field2 = str(self.lowIntensity) + " - " + str(self.highIntensity)
        else:
            self.intensity = self.parseFloat(field2)
            self.field2 = str(self.intensity)

    def evaluate(self, hit):
        
        intensity = 0
        for peak in hit.feature.consensus:
            if self.lowMass <= peak.x <= self.highMass:
                intensity += peak.y
                
        if self.operator == "<":
            if intensity < self.intensity:
                return True
            else:
                return False
        elif  self.operator == ">":
            if intensity > self.intensity:
                return True
            else:
                return False
        else:
            if self.lowIntensity <= intensity <= self.highIntensity:
                return True
            else:
                return False
                
                
class Fragmentname_Filter(Filter):
    def __init__(self, model):
        super(Fragmentname_Filter, self).__init__("Fragmentname")
        self.model = model
        self.field1 = ""
        self.type1 = FieldTypes.ASSISTED
        self.field2 = "0 - 1"
        self.choices1 = []
        self.type2 = FieldTypes.INACTIVE
        self.operatorChoices = ["exists", "exists not"]
        self.operator = "exists"
        self.collectNames()
        
    def reinitialize(self):
        self.collectNames()
        
    def collectNames(self):
        self.choices1 = set()
        for projectName in self.model.projects:
            project = self.model.projects[projectName]
            for analysisName in project.analysisFiles:
                analysis = project.analysisFiles[analysisName]
                for hit in analysis.analysis.glycoModHits:
                    self.choices1 = self.choices1.union(self.collectLabels(hit))
        self.choices1 = list(self.choices1)
        
    def parseField1(self, field1):
        assert field1 in self.choices1
        self.field1 = field1
        
    def parseField2(self, field2):
        return
        
    def collectLabels(self, hit):
        labels = set()
        for name in hit.fragments:
            labels.add(name)
        for spectrum in hit.feature.spectra:
            for key in spectrum.ions:
                for label in spectrum.ions[key]:
                    labels.add(label)
        return labels
        
    def existsLabel(self, label, hit):
        if self.field1 in hit.fragments:
            return True
        # search spectra for glycan fragments
        for spectrum in hit.feature.spectra:
            for key in spectrum.ions:
                if label in spectrum.ions[key]:
                    return True
        return False

    def evaluate(self, hit):
        if self.operator == "exists":
            return self.existsLabel(self.field1, hit)
        else:
            return not self.existsLabel(self.field1, hit)

class Feature_RT_Filter(Filter):
    def __init__(self):
        super(Feature_RT_Filter, self).__init__("Retentiontime")
        self.type1 = FieldTypes.INACTIVE
        self.field2 = "0 - 1"
        self.type2 = FieldTypes.ENTRY
        self.operatorChoices = ["=", "<", ">"]
        self.operator = "="
        self.lowValue = 0
        self.highValue = 0
        self.value = 0
        
    def parseField1(self,field1):
        return
        
    def parseField2(self,field2):
        if self.operator == "=":
            a, b = self.parseFloatRange(field2)
            if a < b:
                self.lowValue, self.highValue = a, b
            else:
                 self.lowValue, self.highValue = b, a
            self.field2 = str(self.lowValue) + " - " + str(self.highValue)
        else:
            self.value = self.parseFloat(field2)
            self.field2 = str(self.value)
            self.field2 = str(self.value)

    def evaluate(self, feature):
        if self.operator == "<":
            if feature.getRT() < self.value:
                return True
            else:
                return False
        elif  self.operator == ">":
            if feature.getRT() > self.value:
                return True
            else:
                return False
        else:
            if self.lowValue <= feature.getRT() <= self.highValue:
                return True
            else:
                return False




