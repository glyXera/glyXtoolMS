import ttk
import tkFont
import Tkinter
import re
import os
import tkFileDialog
import glyxtoolms

def parseFragmentname(name):
    b = re.sub("\(.+\)","",name)
    sp = re.split("(\+|-)",b)
    ion = sp[0]
    mods = []
    for i in range(1,len(sp),2):
        mods.append(sp[i]+sp[i+1])
    
    fragType = ""
    abc = -1
    for match in re.findall("(a\d+|b\d+|c\d+)",ion):
        typ = re.sub("\d","",match)
        pos = int(re.sub("\D","",match))
        abc = pos
        fragType += typ
    xyz = -1
    for match in re.findall("(x\d+|y\d+|z\*?\d+)",ion):
        typ = re.sub("\d","",match)
        pos = int(re.sub("\D","",match))
        xyz = pos
        fragType += typ
    return fragType, abc,xyz, mods

class PeptideCoverageFrame(Tkinter.Frame):

    def __init__(self, master, model):
        Tkinter.Frame.__init__(self, master=master)

        self.master = master
        self.model = model

        self.hit = None
        self.coverage = {}
        self.fragmentCoverage = {}
        self.indexList = set()

        self.height = 0
        self.width = 0

        self.rowconfigure(0, weight=0, minsize=38)
        self.rowconfigure(1, weight=1)
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=0)

        self.canvas = Tkinter.Canvas(self, height=100)
        self.canvas.config(bg="white")
        #self.canvas.grid(row=1, column=0, sticky="NSEW")
        #self.canvas.pack(expand=True, fill="both")

        self.canvas.config(highlightthickness=0)
        self.canvas.grid(row=1, column=0, columnspan=2, sticky="NSEW")



        # Bindings
        self.canvas.bind("<Button-1>", self.eventMouseClick)
        self.canvas.bind("<Configure>", self.on_resize)
        #self.canvas.bind("<Motion>", self.eventMouseMotion, "+")
        self.canvas.bind("<Control-s>", self.savePlot, "+")

        self.menuVar = Tkinter.StringVar(self)
        self.menuVar.trace("w", self.plotSingleFragment)

        self.aMenu = Tkinter.OptionMenu(self, self.menuVar, [])
        self.aMenu.grid(row=0, column=0)
        self.setMenuChoices([])
        
        self.typeFrame = Tkinter.Frame(self)
        self.typeFrame.grid(row=0,column=1)
        
        self.setOptions()
        
        # add checkbuttons
        self.checkButtons = {}
        buttonOrder =  ["a","b","c","x","y","z","z*","by","-NH3","-H2O","-CO","+Glycan"]
        self.buttonNames = {"a":"showa","b":"showb","c":"showc",
                            "x":"showx", "y":"showy", "z":"showz",
                            "z*":"showzone", "by":"showby", "-NH3":"shownh3",
                            "-H2O":"showh2o", "-CO":"showco", "+Glycan":"showglycan"}
        for name in buttonOrder:
            var = Tkinter.IntVar()
            c = Tkinter.Checkbutton(self.typeFrame, text=name,variable=var)
            c.pack(side="left")
            self.checkButtons[name] = var
            var.set(self.options["select"].get(self.buttonNames[name],True))
            var.trace("w", lambda a,b,c: self.setIonselection())
            

        # link function
        self.model.registerClass("PeptideCoverageFrame", self)
    
    def setIonselection(self):
        for name in self.buttonNames:
            var = self.checkButtons.get(name,None)
            self.options["select"][self.buttonNames[name]] = var.get() == 1
        self.paint_canvas()

    def plotSingleFragment(self, *args):
        if self.hit == None:
            return
        name = self.menuVar.get()
        if name in self.hit.fragments:
            self.model.classes["ConsensusSpectrumFrame"].plotSelectedFragments([name],zoomIn=True)

    def setMenuChoices(self, choices):
        self.aMenu['menu'].delete(0, 'end')
        if len(choices) == 0:
            choice = "no further peptide ions"
            self.menuVar.set(choice)
            self.aMenu['menu'].add_command(label=choice, command=Tkinter._setit(self.menuVar, choice))
            return
        self.menuVar.set(choices[0])
        for choice in choices:
            self.aMenu['menu'].add_command(label=choice, command=Tkinter._setit(self.menuVar, choice))
        # clear
        self.model.classes["ConsensusSpectrumFrame"].plotSelectedFragments([],zoomIn=False)

    #def eventMouseMotion(self, event):
    #    self.canvas.focus_set()

    def savePlot(self, event):
        if self.model.currentAnalysis == None:
            return
        options = {}
        options['filetypes'] = [('post script', '.eps'), ]
        workingdir = os.path.dirname(self.model.currentAnalysis.path)
        options['initialdir'] = workingdir
        options['parent'] = self
        filename = tkFileDialog.asksaveasfilename(**options)
        if filename == "":
            return
        self.canvas.postscript(file=filename, height=self.height, width=self.width)

    def on_resize(self,event):
        self.width = event.width
        self.height = event.height
        #self.canvas.config(width=self.width, height=self.height)
        self.paint_canvas()
        self.colorIndex(zoomIn=False)

    def init(self, hit):
        analysis = self.model.currentAnalysis
        if analysis == None:
            return
        self.hit = hit
        self.indexList = set()
        self.paint_canvas()


    def paint_canvas(self):

        def drawSugarUnit(unit, x, y, size):
            h = size/2.0
            if unit == "HEXNAC":
                self.canvas.create_rectangle(x,y-h,x-size, y+h)
            if unit == "GLCNAC":
                self.canvas.create_rectangle(x,y-h,x-size, y+h, fill="blue", outline="black")
            if unit == "GALNAC":
                self.canvas.create_rectangle(x,y-h,x-size, y+h, fill="yellow", outline="black")
            elif unit == "HEX":
                self.canvas.create_oval(x,y-h,x-size, y+h)
            elif unit == "MAN":
                self.canvas.create_oval(x,y-h,x-size, y+h, fill="green", outline="black")
            elif unit == "DHEX":
                self.canvas.create_polygon(x,y+h,x-size,y+h,x-h,y-h, fill="red", outline="black")
            elif unit == "NEUAC":
                self.canvas.create_polygon(x,y,x-h,y-h,x-size,y,x-h,y+h, fill="violet", outline="black")
            elif unit == "NEUGC":
                self.canvas.create_polygon(x,y,x-h,y-h,x-size,y,x-h,y+h, fill="azure", outline="black")


        self.canvas.delete(Tkinter.ALL)
        self.setMenuChoices([])
        if self.hit == None:
            return

        # collect positions of glycosylationsites
        glycosites = set()
        glycotypes = set()
        for pos, typ in self.hit.peptide.glycosylationSites:
            glycosites.add(pos-self.hit.peptide.start)
            glycotypes.add(typ)

        glycan = self.hit.glycan
        sugars = dict(glycan.sugar)
        # calculate size

        xlen = []
        ylen = []
        drawCoreStructure = False
        if glycan.typ == "N" or "N" in glycotypes:
            if glycan.sugar.get("HEXNAC", 0) >= 2 and glycan.sugar.get("HEX", 0) >= 3:
                sugars["HEXNAC"] = sugars["HEXNAC"]-2
                sugars["HEX"] = sugars["HEX"]-3
                drawCoreStructure = True
                xlen.append(5)
                ylen.append(2)

        # group sugars
        group = {}
        for sugar in sugars:
            if sugars[sugar] == 0:
                continue
            if sugar in ["HEXNAC", "GLCNAC", "GALNAC"]:
                key = "HEXNAC"
            elif sugar in ["HEX", "GLC", "GAL", "MAN"]:
                key = "HEX"
            else:
                key = "REST"
            group[key] = group.get(key, [])
            for i in range(0, sugars[sugar]):
                group[key].append(sugar)
        ylen.append(len(group))
        for key in group:
            if drawCoreStructure == True:
                xlen.append(len(group[key])+5)
            else:
                xlen.append(len(group[key]))
        xlen = max(xlen)
        ylen = max(ylen)

        # calc size
        peptideWidth = self.width/3.0*2.0
        glycanWidth = self.width/3.0


        size1 = int(glycanWidth/xlen)
        size2 = int(self.height/ylen)
        size_comp = min((size1,size2))

        size = int(size_comp*2/3.0)
        size = size - size%2
        gap = size_comp - size
        gap = gap -gap%2
        x = peptideWidth+size
        y = self.height/2.0
        if drawCoreStructure == True:
            # draw core
            self.canvas.create_line(x, y,x+1.5*size+gap,y, fill="black")
            drawSugarUnit("GLCNAC", x, y, size)
            x += size+gap
            drawSugarUnit("GLCNAC", x, y, size)
            x += size+gap
            self.canvas.create_line(x-size/2.0, y,x+size, y-size, fill="black")
            self.canvas.create_line(x-size/2.0, y,x+size, y+size, fill="black")
            drawSugarUnit("MAN", x, y, size)
            x += size+gap
            drawSugarUnit("MAN", x, y-size, size)
            drawSugarUnit("MAN", x, y+size, size)
            # draw bracket
            x += gap
            self.canvas.create_line(x, size,
                                    x+gap, size,
                                    x+gap, self.height/2.0,
                                    x+size+gap, self.height/2.0,
                                    x+gap, self.height/2.0,
                                    x+gap, self.height-size,
                                    x, self.height-size,
                                    smooth=True,
                                    fill="black")
            x += size + gap


        diff = self.height/float(len(group)+1)
        y = diff
        x += size
        for key in group:
            for i, sugar in enumerate(group[key]):
                drawSugarUnit(sugar, x+i*(size+10), y, size)
            y += diff

        peptideSequence = self.hit.peptide.sequence
        peptideLength = len(peptideSequence)

        parts = {}
        for i in range(0, peptideLength):
            for e in range(i+1, peptideLength+1):
                name = peptideSequence[i:e]
                key = "".join(sorted(name))
                parts[key] = parts.get(key, []) + [name]

        xyzSeries = {}
        abcSeries = {}
        self.fragmentCoverage = {}

        peptideFragments = []
        TYPE = glyxtoolms.fragmentation.FragmentType
        for name in self.hit.fragments:
            fragment = self.hit.fragments[name]
            if fragment.typ == TYPE.ISOTOPE:
                continue
            if fragment.typ in [TYPE.PEPTIDEION, TYPE.GLYCOPEPTIDEION]:
                peptideFragments.append(fragment)
                continue
            elif fragment.typ not in [TYPE.AION,
                                      TYPE.BION,
                                      TYPE.CION,
                                      TYPE.XION,
                                      TYPE.YION,
                                      TYPE.ZION,
                                      TYPE.BYION]:
                continue
                
            fragType,abc,xyz,mods = parseFragmentname(name)
            # check if ion is active
            active = True
            if fragType in self.checkButtons:
                active = self.checkButtons.get(fragType).get()
            # check if modifications are allowed
            for mod in mods:
                if mod.startswith("+"): # is glycan
                    mod = "+Glycan"
                if mod not in self.checkButtons:
                    continue
                if self.checkButtons.get(mod).get() == False:
                    active = False
                    
            if not active:
                continue

            if xyz != -1:
                xyzSeries[xyz] = xyzSeries.get(xyz, []) + [fragType]
                key = "xyz" + str(xyz)
                self.fragmentCoverage[key] = self.fragmentCoverage.get(key, []) + [name]
            if abc != -1:
                abcSeries[abc] = abcSeries.get(abc, []) + [fragType]
                key = "abc" + str(abc)
                self.fragmentCoverage[key] = self.fragmentCoverage.get(key, []) + [name]
            
        for key in abcSeries:
            abcSeries[key] = set(abcSeries[key])
        for key in xyzSeries:
            xyzSeries[key] = set(xyzSeries[key])   

        restNames = [fragment.name for fragment in sorted(peptideFragments, key=lambda x:(x.mass*x.charge))]
        self.setMenuChoices(restNames)

        # write peptide sequence

        xc = peptideWidth/2.0
        yc = self.height/2.0
        text = self.hit.peptide.sequence

        # find fitting text size
        s = 0
        for s in range(0, self.height-20):
            font = tkFont.Font(family="Courier", size=s)
            if (font.measure(" ")+4)*len(text) > peptideWidth:
                break


        s -= 1
        font = tkFont.Font(family="Courier", size=s)
        letterSize = font.measure(" ")+4
        start = xc - letterSize/2.0*(len(text)-1)
        for index, letter in enumerate(text):
            x = start + index*letterSize
            # check if letter is a glycoslyation site
            fillcolor = "black"
            if index in glycosites:
                fillcolor = "red"
            self.canvas.create_text((x, yc, ), text=letter,
                                    font=("Courier", s),
                                    fill=fillcolor,
                                    anchor="center",
                                    justify="center")


        # plot lines

        self.coverage = {}
        for index in xyzSeries:
            x = start + (peptideLength - index-0.5)*letterSize
            color = "black"
            text = str(index)
            if len(xyzSeries[index]) == 1:
                text = "".join(xyzSeries[index])+str(index)

            item1 = self.canvas.create_line(x, yc,
                                            x, 20,
                                            tags=("site", ),
                                            fill=color)
            item2 = self.canvas.create_line(x, 20,
                                            x+10, 20,
                                            tags=("site", ),
                                            fill=color)
            item3 = self.canvas.create_text((x+5, 10),
                                            text=text,
                                            tags=("site", ),
                                            fill=color,
                                            anchor="center",
                                            justify="center")
            self.coverage[item1] = "xyz" + str(index)
            self.coverage[item2] = "xyz" + str(index)
            self.coverage[item3] = "xyz" + str(index)


        for index in abcSeries:
            x = start + (index-0.5)*letterSize
            color = "black"
            text = str(index)
            if len(abcSeries[index]) == 1:
                text = "".join(abcSeries[index])+str(index)
            item1 = self.canvas.create_line(x, yc,
                                            x, self.height-20,
                                            tags=("site", ),
                                            fill=color)
            item2 = self.canvas.create_line(x, self.height-20,
                                            x-10, self.height-20,
                                            tags=("site", ),
                                            fill=color)
            item3 = self.canvas.create_text((x-5, self.height-10),
                                            text=text,
                                            tags=("site", ),
                                            fill=color,
                                            anchor="center",
                                            justify="center")
            self.coverage[item1] = "abc" + str(index)
            self.coverage[item2] = "abc" + str(index)
            self.coverage[item3] = "abc" + str(index)

    def identifier(self):
        return "PeptideCoverageFrame"

    def eventMouseClick(self, event):
        # clear color from all items
        self.canvas.itemconfigure("site", fill="black")

        overlap = set(self.canvas.find_overlapping(event.x-10,
                                                   event.y-10,
                                                   event.x+10,
                                                   event.y+10))

        self.indexList = set()
        for item in overlap:
            if item in self.coverage:
                key = self.coverage[item]
                self.indexList.add(key)
        self.colorIndex(zoomIn=True)

    def colorIndex(self,zoomIn=False):
        found = []
        for index in self.indexList:
            found += self.fragmentCoverage[index]
            for item in self.coverage:
                if self.coverage[item] == index:
                    self.canvas.itemconfigure(item, fill="red")
        self.model.classes["ConsensusSpectrumFrame"].plotSelectedFragments(found,zoomIn=True)

    def setOptions(self, reset=False):
        self.options = {}
        default = self.getDefaultOptions()
        if reset == False and self.identifier().lower() in self.model.options :
            self.options = self.model.options[self.identifier().lower()]
            # copy over missing default options
            for keyDefault in default:
                if not keyDefault in self.options:
                    self.options[keyDefault] = {}
                for typDefault in default[keyDefault]:
                    if typDefault not in self.options[keyDefault]:
                        value = default[keyDefault][typDefault]
                        self.options[keyDefault][typDefault] = value
        else:
            self.options = self.getDefaultOptions()

        # relink options to model options
        self.model.options[self.identifier().lower()] = self.options

    def getDefaultOptions(self):
        options = {}
        options["select"] = {}
        options["select"]["showa"] = True
        options["select"]["showb"] = True
        options["select"]["showc"] = True
        options["select"]["showx"] = True
        options["select"]["showy"] = True
        options["select"]["showz"] = True
        options["select"]["showzone"] = True
        options["select"]["showby"] = True
        options["select"]["shownh3"] = True
        options["select"]["showco"] = True
        options["select"]["showh2o"] = True
        options["select"]["showglycan"] = True
        return options
