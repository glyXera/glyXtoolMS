"""
Panel to set Filteroptions for all Data

"""
import Tkinter
import ttk
import glyxtoolms
import re

class FilterPanel(Tkinter.Toplevel):

    def __init__(self, master, model):
        Tkinter.Toplevel.__init__(self, master=master)
        w = 600
        h = 300
        self.minsize(w,h)
        self.master = master
        self.model = model

        # center window
        # get screen width and height
        ws = master.winfo_screenwidth() # width of the screen
        hs = master.winfo_screenheight() # height of the screen

        # calculate x and y coordinates for the Tk root window
        x = (ws/2) - (w/2)
        y = (hs/2) - (h/2)

        # set the dimensions of the screen
        # and where it is placed
        #self.geometry('%dx%d+%d+%d' % (w, h, x, y))
        self.focus_set()
        self.transient(master)
        self.lift()
        self.wm_deiconify()

        #self.protocol("WM_DELETE_WINDOW", self._delete_window)
        #self.bind("<Destroy>", self._destroy)


        self.title("Filter Options")

        #   ------- Identifications ------ #
        self.N_Identification = 0

        frameIdentification = ttk.Labelframe(self, text="1. Identifications")
        frameIdentification.grid(row=0, column=0, columnspan=2, sticky="NWES")
        frameIdentification.columnconfigure(0, weight=0)
        frameIdentification.columnconfigure(1, weight=1)

        buttonIdentification = Tkinter.Button(frameIdentification,
                                              text="add Filter",
                                              command=self.addIdentificationFilter)
        buttonIdentification.grid(row=0, column=0,columnspan=3, sticky="NW")


        self.filterIdentification = ttk.Frame(frameIdentification)
        self.filterIdentification.grid(row=1, column=0, columnspan=2, sticky="NWES")
        self.filterIdentification.columnconfigure(1, weight=1)
        self.filterIdentification.evalLogic = lambda x=self.filterIdentification:self.evalLogic(x)
        self.filterIdentification.checkValidity = self.checkValidity
        self.filterIdentification.entries = []



        #   ------- Features ------ #
        self.N_Features = 0

        frameFeature = ttk.Labelframe(self, text="2. Features")
        frameFeature.grid(row=1, column=0, columnspan=2, sticky="NWES")
        frameFeature.columnconfigure(0, weight=0)
        frameFeature.columnconfigure(1, weight=1)

        buttonFeature = Tkinter.Button(frameFeature,
                                       text="add Filter",
                                       command=self.addFeatureFilter)
        buttonFeature.grid(row=0, column=0, sticky="NWES")


        self.filterFeature = ttk.Frame(frameFeature)
        self.filterFeature.grid(row=1, column=0, columnspan=2, sticky="NWES")
        self.filterFeature.columnconfigure(1, weight=1)
        self.filterFeature.evalLogic = lambda x=self.filterFeature:self.evalLogic(x)
        self.filterFeature.checkValidity = self.checkValidity
        self.filterFeature.entries = []

        #   ------- Scoring ------ #
        self.N_Scoring = 0

        frameScoring = ttk.Labelframe(self, text="3. Scoring")
        frameScoring.grid(row=2, column=0, columnspan=2, sticky="NWES")
        frameScoring.columnconfigure(0, weight=0)
        frameScoring.columnconfigure(1, weight=1)

        buttonScoring = Tkinter.Button(frameScoring,
                                       text="add Filter",
                                       command=self.addScoringFilter)
        buttonScoring.grid(row=0, column=0, sticky="NWES")


        self.filterScoring = ttk.Frame(frameScoring)
        self.filterScoring.grid(row=1, column=0, columnspan=2, sticky="NWES")
        self.filterScoring.columnconfigure(1, weight=1)
        self.filterScoring.evalLogic = lambda x=self.filterScoring:self.evalLogic(x)
        self.filterScoring.checkValidity = self.checkValidity
        self.filterScoring.entries = []

        self.buttonCancel = Tkinter.Button(self, text="Cancel", command=self.cancel)
        self.buttonCancel.grid(row=3, column=0, sticky="NE")

        self.buttonOk = Tkinter.Button(self, text="OK", command=self.ok)
        self.buttonOk.grid(row=3, column=1, sticky="NW")

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

    def cancel(self):
        self.destroy()

    def checkValidity(self):
        valid = True
        if self.evalLogic(self.filterIdentification) == False:
            valid = False
        if self.evalLogic(self.filterFeature) == False:
            valid = False
        if self.evalLogic(self.filterScoring) == False:
            valid = False

        for entry in self.filterIdentification.entries:
            if entry.currentFilter.valid == False:
                valid = False
                break
        for entry in self.filterFeature.entries:
            if entry.currentFilter.valid == False:
                valid = False
                break

        for entry in self.filterScoring.entries:
            if entry.currentFilter.valid == False:
                valid = False
                break
        if valid == True:
            self.buttonOk['state'] = 'normal'
        else:
            self.buttonOk['state'] = 'disabled'
        return valid

    def ok(self):
        # gather active filters
        if self.checkValidity() == False:
            return
        self.model.filters["Identification"] = []
        for entry in self.filterIdentification.entries:
            self.model.filters["Identification"].append(entry.currentFilter)

        self.model.filters["Features"] = []
        for entry in self.filterFeature.entries:
            self.model.filters["Features"].append(entry.currentFilter)

        self.model.filters["Scoring"] = []
        for entry in self.filterScoring.entries:
            self.model.filters["Scoring"].append(entry.currentFilter)

        self.model.runFilters()
        self.model.classes["NotebookFeature"].updateTree()
        features = self.model.classes["NotebookFeature"].getSelectedFeatures()
        self.model.classes["NotebookScoring"].updateTree(features)
        self.model.classes["NotebookIdentification"].updateTree(features)
        self.model.classes["TwoDView"].init()
        self.destroy()

    def evalLogic(self, container):
        text = ""
        for entry in container.entries:
            text += entry.currentFilter.logicLeft
            text += str(True)
            text += entry.currentFilter.logicRight
        valid = True
        try:
            if text != "":
                eval(text)
        except:
            valid = False
        for entry in container.entries:
            entry.setLogicState(valid)
        return valid

    def addIdentificationFilter(self, definedFilter=None):
        filters = []
        filters.append(EmptyFilter())
        filters.append(GlycanRegexFilter())
        filters.append(GlycopeptideMassError_Filter())
        filters.append(GlycopeptideMass_Filter())
        filters.append(Fragmentmass_Filter_Identification())
        filters.append(Fragmentname_Filter(self.model))
        filters.append(StatusFilter())
        filters.append(FeatureStatusFilter())
        filters.append(GlycosylationSite_Filter(self.model))
        filters.append(Tag_Filter_Identification(self.model))

        f = FilterEntry(self.model,self.filterIdentification,
                        filters,
                        self.N_Identification,
                        definedFilter=definedFilter)
        f.grid(row=self.N_Identification, column=1, sticky=("N", "W", "E", "S"))
        self.N_Identification += 1


    def addFeatureFilter(self, definedFilter=None):
        filters = []
        filters.append(EmptyFilter())
        filters.append(Feature_RT_Filter())
        filters.append(Fragmentmass_Filter_Feature())
        filters.append(StatusFilter())
        filters.append(Tag_Filter_Feature(self.model))

        f = FilterEntry(self.model,self.filterFeature,
                        filters,
                        self.N_Features,
                        definedFilter=definedFilter)
        f.grid(row=self.N_Features, column=1, sticky=("N", "W", "E", "S"))
        self.N_Features += 1

    def addScoringFilter(self, definedFilter=None):
        filters = []
        filters.append(EmptyFilter())
        filters.append(StatusFilter())

        f = FilterEntry(self.model,self.filterScoring,
                        filters,
                        self.N_Scoring,
                        definedFilter=definedFilter)
        f.grid(row=self.N_Scoring, column=1, sticky=("N", "W", "E", "S"))
        self.N_Scoring += 1

class FilterEntry(ttk.Frame):
    def __init__(self,model, master, filters, row, definedFilter=None):
        ttk.Frame.__init__(self, master=master)

        self.master = master
        self.master.entries.append(self)
        self.model = model

        # Connection | type | <Field1> | Operator | <Field2> |

        self.traceChanges = False

        self.filters = filters
        if definedFilter == None:
            self.currentFilter = self.filters[0]
        else:
            self.currentFilter = definedFilter

        choices = [" "," and ", " or ", " ( ", " ) ", " ) and ( ", ") or ( ", " and (", " or ( ", " ) and ", ") or "]
        self.logicLeftVar = Tkinter.StringVar(self)
        self.logicLeftVar.trace("w", self.logicLeftChanged)
        self.logicLeftOption = Tkinter.OptionMenu(self.master, self.logicLeftVar, *choices)
        self.logicLeftOption.grid(row=row, column=0, sticky=("N", "W", "E", "S"))
        if definedFilter == None:
            if len(self.master.entries) == 1:
                self.logicLeftVar.set(" ")
            else:
                self.logicLeftVar.set(" and ")
        else:
            self.logicLeftVar.set(self.currentFilter.logicLeft)


        self.logicRightVar = Tkinter.StringVar(self)
        self.logicRightVar.trace("w", self.logicRightChanged)
        self.logicRightOption = Tkinter.OptionMenu(self.master, self.logicRightVar, *choices)
        self.logicRightOption.grid(row=row, column=2, sticky=("N", "W", "E", "S"))
        self.logicRightVar.set(self.currentFilter.logicRight)

        self.delButton = Tkinter.Button(self.master, text="x", command=self.delete)
        self.delButton.grid(row=row, column=3)

        self.var = Tkinter.StringVar(self)
        self.currentOperator = self.currentFilter.operator

        choices = []
        for f in self.filters:
            if f.name == "":
                continue
            choices.append(f.name)

        option = Tkinter.OptionMenu(self, self.var, *choices)
        option.grid(row=0, column=1, sticky=("N", "W", "E", "S"))
        self.var.set(self.currentFilter.name)
        self.var.trace("w", self.filterChanged)

        self.field1Var = Tkinter.StringVar(self)
        self.field1Var.trace("w", self.valuesChanged)

        self.entry1 = Tkinter.Entry(self, textvariable=self.field1Var)
        self.entry1.grid(row=0, column=2, sticky=("N", "W", "E", "S"))
        self.entry1.config(bg="white")

        choices = ['', ]
        self.options1 = Tkinter.OptionMenu(self, self.field1Var, *choices)
        self.options1.grid(row=0, column=2, sticky=("N", "W", "E", "S"))

        self.assisted1 = InteractiveEntry(self, self.field1Var)
        self.assisted1.grid(row=0, column=2, sticky=("N", "W", "E", "S"))
        self.assisted1.config(bg="white")

        self.range1 = RangeEntry(self, self.field1Var)
        self.range1.grid(row=0, column=2, sticky=("N", "W", "E", "S"))

        self.unit1 = UnitEntry(self, self.field1Var, ["1", "2"])
        self.unit1.grid(row=0, column=2, sticky=("N", "W", "E", "S"))

        self.label1 = Tkinter.Label(self, text="Foobar")
        self.label1.grid(row=0, column=2, sticky=("N", "W", "E", "S"))

        # ----------------

        self.operatorVar = Tkinter.StringVar(self)
        self.operatorVar.trace("w", self.valuesChanged)
        choicesOperator = ['', ]
        self.optionOperator = Tkinter.OptionMenu(self, self.operatorVar, *choicesOperator)
        self.optionOperator.grid(row=0, column=3, sticky=("N", "W", "E", "S"))

        # -----------------

        self.field2Var = Tkinter.StringVar(self)
        self.field2Var.trace("w", self.valuesChanged)
        self.entry2 = Tkinter.Entry(self, textvariable=self.field2Var)
        self.entry2.config(bg="white")
        self.entry2.grid(row=0, column=4, sticky=("N", "W", "E", "S"))

        choices = ['', ]
        self.options2 = Tkinter.OptionMenu(self, self.field2Var, *choices)
        self.options2.grid(row=0, column=4, sticky=("N", "W", "E", "S"))

        self.assisted2 = InteractiveEntry(self, self.field2Var)
        self.assisted2.grid(row=0, column=4, sticky=("N", "W", "E", "S"))
        self.assisted2.config(bg="white")

        self.range2 = RangeEntry(self, self.field2Var)
        self.range2.grid(row=0, column=4, sticky=("N", "W", "E", "S"))

        self.unit2 = UnitEntry(self, self.field2Var, ["3", "4"])
        self.unit2.grid(row=0, column=4, sticky=("N", "W", "E", "S"))

        self.label2 = Tkinter.Label(self, text="Foobar")
        self.label2.grid(row=0, column=2, sticky=("N", "W", "E", "S"))


        self.paintCurrentFilter()
        self.traceChanges = True
        self.logicLeftChanged()
        self.logicRightChanged()
        self.master.checkValidity()



    def valuesChanged(self, *args):
        if self.traceChanges == False:
            return
        self.currentFilter.valid = True
        try:
            self.currentFilter.parseField1(self.field1Var.get())
            self.entry1.config(highlightbackground="#eff0f1")
            self.entry1.config(highlightcolor="black")
            self.assisted1.config(highlightbackground="#eff0f1")
            self.assisted1.config(highlightcolor="black")
            self.options1.config(highlightbackground="#eff0f1")
            self.options1.config(highlightcolor="black")
            self.unit1.config(highlightbackground="#eff0f1")
            self.unit1.config(highlightcolor="black")
        except:
            self.currentFilter.valid = False
            self.entry1.config(highlightbackground="red")
            self.entry1.config(highlightcolor="red")
            self.assisted1.config(highlightbackground="red")
            self.assisted1.config(highlightcolor="red")
            self.options1.config(highlightbackground="red")
            self.options1.config(highlightcolor="red")
            self.unit1.config(highlightbackground="red")
            self.unit1.config(highlightcolor="red")

        try:
            self.currentFilter.parseOperator(self.operatorVar.get())
            self.optionOperator.config(highlightbackground="#eff0f1")
            self.optionOperator.config(highlightcolor="black")
        except:
            self.currentFilter.valid = False
            self.optionOperator.config(highlightbackground="red")
            self.optionOperator.config(highlightcolor="red")

        try:
            self.currentFilter.parseField2(self.field2Var.get())
            self.entry2.config(highlightbackground="#eff0f1")
            self.entry2.config(highlightcolor="black")
            self.assisted2.config(highlightbackground="#eff0f1")
            self.assisted2.config(highlightcolor="black")
            self.options2.config(highlightbackground="#eff0f1")
            self.options2.config(highlightcolor="black")
            self.unit2.config(highlightbackground="#eff0f1")
            self.unit2.config(highlightcolor="black")
        except:
            self.currentFilter.valid = False
            self.entry2.config(highlightbackground="red")
            self.entry2.config(highlightcolor="red")
            self.assisted2.config(highlightbackground="red")
            self.assisted2.config(highlightcolor="red")
            self.options2.config(highlightbackground="red")
            self.options2.config(highlightcolor="red")
            self.unit2.config(highlightbackground="red")
            self.unit2.config(highlightcolor="red")
        self.master.checkValidity()

    def filterChanged(self, *args):
        if self.traceChanges == False:
            return
        name = self.var.get()
        if name == "":
            self.delete()
            return
        if self.currentFilter.name == name:
            return
        logicLeft = self.currentFilter.logicLeft
        logicRight = self.currentFilter.logicRight

        self.currentFilter = None
        for f in self.filters:
            if f.name == name:
                self.currentFilter = f
        if self.currentFilter == None:
            raise Exception("Unknown Filter")


        self.currentFilter.logicLeft = logicLeft
        self.currentFilter.logicRight = logicRight

        self.paintCurrentFilter()
        self.master.evalLogic()
        self.master.checkValidity()

    def paintCurrentFilter(self):
        self.traceChanges = False
        self.var.set(self.currentFilter.name)

        self.entry1.grid_remove()
        self.options1.grid_remove()
        self.assisted1.grid_remove()
        self.assisted1.setVisible(False)
        self.range1.grid_remove()
        self.unit1.grid_remove()
        self.label1.grid_remove()

        if self.currentFilter.type1 == FieldTypes.INACTIVE:
            pass
        elif self.currentFilter.type1 == FieldTypes.ENTRY:
            self.entry1.grid()
        elif self.currentFilter.type1 == FieldTypes.MENU:
            self.options1.grid()
            self.setMenuChoices(self.options1, self.currentFilter.choices1, self.field1Var)
        elif self.currentFilter.type1 == FieldTypes.ASSISTED:
            self.assisted1.grid()
            self.assisted1.all_choices = self.currentFilter.choices1
            self.field1Var.set(self.currentFilter.field1)
            self.assisted1.setVisible(True)
            self.assisted1.showOptions(0)
        elif self.currentFilter.type1 == FieldTypes.RANGE:
            self.range1.setFieldValue(self.currentFilter.field1)
            self.range1.grid()
        elif self.currentFilter.type1 == FieldTypes.UNIT:
            self.unit1.grid()
        elif self.currentFilter.type1 == FieldTypes.LABEL:
            self.label1.config(text=self.currentFilter.field1)
            self.label1.grid()
        else:
            raise Exception("Unknown FieldType!")
        self.field1Var.set(self.currentFilter.field1)

        if len(self.currentFilter.operatorChoices) > 0:
            self.optionOperator.grid()
            self.setMenuChoices(self.optionOperator, self.currentFilter.operatorChoices, self.operatorVar)
            self.operatorVar.set(self.currentFilter.operator)
        else:
            self.optionOperator.grid_remove()

        self.entry2.grid_remove()
        self.options2.grid_remove()
        self.assisted2.grid_remove()
        self.assisted2.setVisible(False)
        self.range2.grid_remove()
        self.unit2.grid_remove()
        self.label2.grid_remove()

        if self.currentFilter.type2 == FieldTypes.INACTIVE:
            pass
        elif self.currentFilter.type2 == FieldTypes.ENTRY:
            self.entry2.grid()
        elif self.currentFilter.type2 == FieldTypes.MENU:
            self.options2.grid()
            self.setMenuChoices(self.options2, self.currentFilter.choices2, self.field2Var)
        elif self.currentFilter.type2 == FieldTypes.ASSISTED:
            self.assisted2.grid()
            self.assisted2.all_choices = self.currentFilter.choices2
            self.assisted2.setVisible(True)
            self.assisted2.showOptions(0)
        elif self.currentFilter.type2 == FieldTypes.RANGE:
            self.range2.setFieldValue(self.currentFilter.field2)
            self.range2.grid()
        elif self.currentFilter.type2 == FieldTypes.UNIT:
            self.unit2.grid()
            self.unit2.setUnits(self.currentFilter.unitChoices)
            self.unit2.setFieldValue(self.currentFilter.field2)
        elif self.currentFilter.type2 == FieldTypes.LABEL:
            self.label2.config(text=self.currentFilter.field2)
            self.label2.grid()
        else:
            raise Exception("Unknown FieldType!")
        self.field2Var.set(self.currentFilter.field2)

        self.traceChanges = True
        self.valuesChanged()


    def setMenuChoices(self, menu, choices, var):
        menu['menu'].delete(0, 'end')
        if len(choices) == 0:
            var.set("")
            return
        for choice in choices:
            menu['menu'].add_command(label=choice, command=Tkinter._setit(var, choice))
        var.set(choices[0])


    def logicLeftChanged(self, *args):
        if self.traceChanges == False:
            return
        option = self.logicLeftVar.get()
        self.currentFilter.logicLeft = option
        self.master.evalLogic()


    def logicRightChanged(self, *args):
        if self.traceChanges == False:
            return
        option = self.logicRightVar.get()
        self.currentFilter.logicRight = option
        self.master.evalLogic()

    def setLogicState(self, valid):
        if valid == True:
            self.logicLeftOption.config(highlightbackground="#eff0f1")
            self.logicLeftOption.config(highlightcolor="#eff0f1")
            self.logicRightOption.config(highlightbackground="#eff0f1")
            self.logicRightOption.config(highlightcolor="#eff0f1")

        else:
            self.logicLeftOption.config(highlightbackground="red")
            self.logicLeftOption.config(highlightcolor="red")
            self.logicRightOption.config(highlightbackground="red")
            self.logicRightOption.config(highlightcolor="red")


    def delete(self):
        self.logicLeftOption.destroy()
        self.logicRightOption.destroy()
        self.delButton.destroy()
        self.destroy()
        if self in self.master.entries:
            self.master.entries.remove(self)
        self.master.evalLogic()
        self.master.checkValidity()

class UnitEntry(Tkinter.Frame):

    def setChoice(self, value):
        if self.keepTrace == False:
            return
        self.menubutton["text"] = value
        self.valuesChanged()

    def __init__(self, master, var, units):
        Tkinter.Frame.__init__(self, master=master)
        self.fieldVar = var
        self.units = units
        self.v = Tkinter.StringVar()
        self.e = Tkinter.Entry(self, textvariable=self.v, width=8)
        self.e.config(bg="white")
        self.e.grid(row=0, column=0, sticky=("N", "W", "E", "S"))
        self.menubutton = Tkinter.Menubutton(self, text=self.units[0], relief="raised")
        self.menubutton.grid(row=0, column=1, sticky=("N", "W", "E", "S"))
        self.rowconfigure(0,weight=1)
        self.menubutton.menu = Tkinter.Menu(self.menubutton, tearoff=0)
        self.menubutton["menu"] = self.menubutton.menu
        for unit in units:
            self.menubutton.menu.add_command(label=unit, command=lambda x=unit: self.setChoice(x))
        self.keepTrace = True
        self.v.trace("w", self.valuesChanged)

    def setUnits(self, choices):
        self.keepTrace = False
        self.menubutton.menu.delete(0, self.menubutton.menu.index("end"))
        for unit in choices:
            self.menubutton.menu.add_command(label=unit, command=lambda x=unit: self.setChoice(x))
        if len(choices) > 0:
            self.menubutton.config(text=choices[0])
        self.keepTrace = True


    def valuesChanged(self, *args):
        text = self.v.get().strip()
        # parse value
        try:
            value = float(text)
            self.e.config(highlightbackground="#eff0f1")
            self.e.config(highlightcolor="black")

        except:
            self.e.config(highlightbackground="red")
            self.e.config(highlightcolor="red")
        # parse unit
        text += " " + self.menubutton["text"]
        self.fieldVar.set(text)

    def setFieldValue(self, fieldValue):
        self.keepTrace = False
        value,unit = fieldValue.split(" ")
        self.v.set(value)
        self.menubutton["text"] = unit
        self.keepTrace = True

class RangeEntry(Tkinter.Frame):

    def setChoice(self, value):
        if self.keepTrace == False:
            return
        self.menubutton["text"] = value
        self.valuesChanged()

    def __init__(self, master, var):
        Tkinter.Frame.__init__(self, master=master)
        self.fieldVar = var
        self.v1 = Tkinter.StringVar()
        self.e1 = Tkinter.Entry(self, textvariable=self.v1, width=8)
        self.e1.grid(row=0, column=0, sticky=("N", "W", "E", "S"))
        self.e1.config(bg="white")
        self.menubutton = Tkinter.Menubutton(self, text=" - ", relief="raised")
        self.menubutton.grid(row=0, column=1, sticky=("N", "W", "E", "S"))
        self.rowconfigure(0,weight=1)
        self.menubutton.menu = Tkinter.Menu(self.menubutton, tearoff=0)
        self.menubutton["menu"] = self.menubutton.menu
        self.menubutton.menu.add_command(label=" - ", command=lambda x=" - ": self.setChoice(x))
        self.menubutton.menu.add_command(label="+/-", command=lambda x="+/-": self.setChoice(x))

        self.v2 = Tkinter.StringVar()
        self.e2 = Tkinter.Entry(self, textvariable=self.v2, width=8)
        self.e2.grid(row=0, column=3, sticky=("N", "W", "E", "S"))
        self.e2.config(bg="white")
        self.keepTrace = True
        self.v1.trace("w", self.valuesChanged)
        self.v2.trace("w", self.valuesChanged)

    def valuesChanged(self, *args):

        if self.menubutton["text"] == " - ":
            text = ""
            try:
                value = self.v1.get()
                text += str(float(value))
                self.e1.config(highlightbackground="#eff0f1")
                self.e1.config(highlightcolor="black")
            except:
                self.e1.config(highlightbackground="red")
                self.e1.config(highlightcolor="red")
            text += "-"
            try:
                value = self.v2.get()
                text += str(float(value))
                self.e2.config(highlightbackground="#eff0f1")
                self.e2.config(highlightcolor="black")
            except:
                self.e2.config(highlightbackground="red")
                self.e2.config(highlightcolor="red")
        else:
            text = ""
            try:
                value = self.v1.get()
                float(value)
                text += value
                self.e1.config(highlightbackground="#eff0f1")
                self.e1.config(highlightcolor="black")
            except:
                self.e1.config(highlightbackground="red")
                self.e1.config(highlightcolor="red")
            text += "+/-"
            try:
                content = self.v2.get()
                m1 = re.match("^\d+\.?\d*(\W*| ppm| Da)$",content)
                assert m1 is not None
                m2 = re.match("^\d+\.?\d*\W*",content)
                value = float(m2.group())
                typ = content[m2.end():]
                assert typ in ["", "Da", "ppm"]
                if typ == "":
                    typ = "Da"
                text += str(value) + " "+typ
                self.e2.config(highlightbackground="#eff0f1")
                self.e2.config(highlightcolor="black")
            except:
                self.e2.config(highlightbackground="red")
                self.e2.config(highlightcolor="red")
        self.fieldVar.set(text)

    def setFieldValue(self, fieldValue):
        self.keepTrace = False
        if "+/-" in fieldValue:
            a,b = fieldValue.split("+/-")
            self.menubutton["text"] = "+/-"
        else:
            a,b = fieldValue.split("-")
            self.menubutton["text"] = " - "
        self.v1.set(a.strip())
        self.v2.set(b.strip())
        self.keepTrace = True

class InteractiveEntry(Tkinter.Entry):
    def __init__(self, master, var):
        Tkinter.Entry.__init__(self, master=master, textvariable=var)
        self.var = var


        self.all_choices = []
        self.currentText = None
        self.choices = []
        self.keepTrace = True
        self.isVisible = False

        self.aMenu = Tkinter.Menu(self.master, tearoff=0)
        self.aMenu.bind("<FocusOut>", self.removeOptions, "+")
        #self.bind("<FocusIn>", lambda x: self.valuesChanged(2), "+")
        self.bind("<FocusOut>", self.removeOptions, "+")
        self.var.trace("w", self.valuesChanged)

    def setVisible(self, boolean):
        self.isVisible = boolean

    def showOptions(self, event):
        if self.isVisible == False:
            return
        if len(self.all_choices) == 0:
            return
        self.master.model.root.update_idletasks()
        self.focus()
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
    RANGE=5 # dropdown menu with "-" and "+/-"
    UNIT=6
    LABEL=7

class Filter(object):

    def __init__(self, name):
        self.name = name
        self.logicLeft = " "
        self.logicRight = " "
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

    def evaluate(self, obj, **args):
        raise Exception("overwrite this function!")

    def parseFloatRange(self, string):
        m1 = re.match("^\d+\.?\d*\W*-\W*\d+\.?\d*$",string)
        m2 = re.match("^\d+\.?\d*\W*\+/-\W*\d+\.?\d*\W*(Da|ppm)$",string)
        if m1 is not None:
            a,b = string.replace(" ", "").split("-")
            return float(a), float(b)
        elif m2 is not None:
            x,y = string.replace(" ", "").split("+/-")
            x = float(x)
            if "Da" in y:
                y = float(y[:-2])
                a = x - y
                b = x + y
            else:
                y = float(y[:-3])
                a = x - x*y*1E-6
                b = x + x*y*1E-6
            return a,b
        else:
            raise Exception("Foo")

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
        self.operatorChoices = []

    def parseField1(self, field1):
        return

    def parseField2(self, field2):
        return

    def evaluate(self, obj, **args):
        return True

class GlycanRegexFilter(Filter):
    def __init__(self):
        super(GlycanRegexFilter, self).__init__("Regex")
        self.type1 = FieldTypes.MENU
        self.choices1 = ["Glycan name", "Peptide sequence"]
        self.field1 = "Glycan name"
        self.type2 = FieldTypes.ENTRY
        self.operatorChoices = ["matches", "matches not"]
        self.operator = "matches"
        self.field2 = ""
        self.pattern = re.compile(self.field2)

    def parseField1(self, field1):
        self.field1 = field1

    def parseField2(self, field2):
        self.field2 = field2
        self.pattern = re.compile(field2)

    def evaluate(self, hit, **args):
        match = True
        if self.field1 == "Glycan name":
            if self.pattern.search(hit.glycan.toString()) == None:
                match = False
        else:
            if self.pattern.search(hit.peptide.toString()) == None:
                match = False
        if self.operator == "matches":
            return match
        else:
            return not match

class StatusFilter(Filter):
    def __init__(self):
        super(StatusFilter, self).__init__("Status")
        self.type1 = FieldTypes.INACTIVE
        self.type2 = FieldTypes.MENU
        self.choices2 = glyxtoolms.io.ConfirmationStatus._types
        self.operatorChoices = ["is", "is not"]
        self.operator = "is"

    def parseField1(self, field1):
        return

    def parseField2(self, field2):
        self.field2 = field2

    def evaluate(self, obj, **args):
        if self.operator == "is":
            if obj.status == self.field2:
                return True
            return False
        else:
            if obj.status == self.field2:
                return False
        return True

class FeatureStatusFilter(Filter):
    def __init__(self):
        super(FeatureStatusFilter, self).__init__("FeatureStatus")
        self.type1 = FieldTypes.INACTIVE
        self.type2 = FieldTypes.MENU
        self.choices2 = glyxtoolms.io.ConfirmationStatus._types
        self.operatorChoices = ["is", "is not"]
        self.operator = "is"

    def parseField1(self, field1):
        return

    def parseField2(self, field2):
        self.field2 = field2

    def evaluate(self, hit, **args):
        if self.operator == "is":
            if hit.feature.status == self.field2:
                return True
            return False
        else:
            if hit.feature.status == self.field2:
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

    def evaluate(self, hit, **args):
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

class GlycopeptideMassError_Filter(Filter):
    def __init__(self):
        super(GlycopeptideMassError_Filter, self).__init__("GlycopeptideMass Error")
        self.type1 = FieldTypes.INACTIVE
        self.field2 = "0 ppm"
        self.type2 = FieldTypes.UNIT
        self.unitChoices = ["ppm", "Da"]
        self.unit = "ppm"
        self.operatorChoices = ["<=",]
        self.operator = "<="
        self.lowValue = 0
        self.highValue = 0
        self.value = 0

    def parseField1(self,field1):
        return

    def parseField2(self,field2):
        field2 = field2.strip()
        value, unit = field2.split(" ")
        self.value = float(value)
        assert unit in self.unitChoices
        self.unit = unit
        self.field2 = str(self.value) + " " + unit

    def evaluate(self, hit, **args):
        if self.unit == "Da":
            error = hit.error
        else:
            error = hit.error/float(hit.feature.getMZ())*1E6
        if abs(error) <= self.value:
            return True
        return False


class Fragmentmass_Filter_Identification(Filter):
    def __init__(self):
        super(Fragmentmass_Filter_Identification, self).__init__("Fragmentmass")
        self.field1 = "0+/-1 ppm"
        self.type1 = FieldTypes.RANGE
        self.field2 = "0"
        self.type2 = FieldTypes.ENTRY
        self.operatorChoices = ["=", "<", ">"]
        self.operator = ">"
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
        self.field1 = field1
        #self.field1 = str(self.lowMass) + " - " + str(self.highMass)

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

    def evaluate(self, hit, **args):

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


class Fragmentmass_Filter_Feature(Filter):
    def __init__(self):
        super(Fragmentmass_Filter_Feature, self).__init__("Fragmentmass")
        self.field1 = "0+/-1 ppm"
        self.type1 = FieldTypes.RANGE
        self.field2 = "0"
        self.type2 = FieldTypes.ENTRY
        self.operatorChoices = ["=", "<", ">"]
        self.operator = ">"
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
        self.field1 = field1

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

    def evaluate(self, feature, **args):

        intensity = 0
        for peak in feature.consensus:
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

    def evaluate(self, hit, **args):
        if self.operator == "exists":
            return self.existsLabel(self.field1, hit)
        else:
            return not self.existsLabel(self.field1, hit)

class Tag_Filter_Identification(Filter):
    def __init__(self, model):
        super(Tag_Filter_Identification, self).__init__("Tagfilter")
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
                self.choices1 = self.choices1.union(analysis.analysis.all_tags)
        self.choices1 = list(self.choices1)

    def parseField1(self, field1):
        assert field1 in self.choices1
        self.field1 = field1

    def parseField2(self, field2):
        return


    def existsTag(self, label, hit):
        if self.field1 in hit.tags:
            return True
        return False

    def evaluate(self, hit, **args):
        if self.operator == "exists":
            return self.existsTag(self.field1, hit)
        else:
            return not self.existsTag(self.field1, hit)

class Tag_Filter_Feature(Filter):
    def __init__(self, model):
        super(Tag_Filter_Feature, self).__init__("Tagfilter")
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
                self.choices1 = self.choices1.union(analysis.analysis.all_tags)
        self.choices1 = list(self.choices1)

    def parseField1(self, field1):
        assert field1 in self.choices1
        self.field1 = field1

    def parseField2(self, field2):
        return


    def existsTag(self, label, feature):
        if self.field1 in feature.tags:
            return True
        return False

    def evaluate(self, feature, **args):
        if self.operator == "exists":
            return self.existsTag(self.field1, feature)
        else:
            return not self.existsTag(self.field1, feature)

class GlycosylationSite_Filter(Filter):
    def __init__(self, model):
        super(GlycosylationSite_Filter, self).__init__("GlycosylationSite")
        self.model = model
        self.field1 = ""
        self.type1 = FieldTypes.ASSISTED
        self.field2 = "0 - 1"
        self.choices1 = []
        self.type2 = FieldTypes.INACTIVE
        self.operatorChoices = ["exists", "exists not"]
        self.operator = "exists"
        self.collectSites()

    def reinitialize(self):
        self.collectSites()

    def collectSites(self):
        self.choices1 = set()
        for projectName in self.model.projects:
            project = self.model.projects[projectName]
            for analysisName in project.analysisFiles:
                analysis = project.analysisFiles[analysisName]
                for hit in analysis.analysis.glycoModHits:
                    for pos, t in hit.peptide.glycosylationSites:
                        name = t+str(pos+1) # FIX position offset!
                        self.choices1.add(name)
        self.choices1 = list(self.choices1)

    def parseField1(self, field1):
        assert field1 in self.choices1
        self.field1 = field1

    def parseField2(self, field2):
        return

    def existsGlycosylationSite(self, site, hit):
        for pos, t in hit.peptide.glycosylationSites:
            name = t+str(pos+1) # FIX position offset!
            if name == site:
                return True
        return False

    def evaluate(self, hit, **args):
        if self.operator == "exists":
            return self.existsGlycosylationSite(self.field1, hit)
        else:
            return not self.existsGlycosylationSite(self.field1, hit)

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

    def evaluate(self, feature, timescale, **args):
        # change rt according to setting
        if timescale == "minutes":
            rt = round(feature.getRT()/60.0, 2)
        else:
            rt = round(feature.getRT(), 1)
        if self.operator == "<":
            if rt < self.value:
                return True
            else:
                return False
        elif  self.operator == ">":
            if rt > self.value:
                return True
            else:
                return False
        else:
            if self.lowValue <= rt <= self.highValue:
                return True
            else:
                return False




