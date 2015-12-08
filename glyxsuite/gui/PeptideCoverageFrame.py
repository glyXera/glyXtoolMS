import ttk
import tkFont
import Tkinter
import re

def parseInternalFragment(name, length):
    match = re.match(r"^y\d+b\d+", name)
    if match == None:
        return None, None
    y, b = match.group()[1:].split("b")
    y = length-int(y)
    b = int(b)
    return y, b

def parseBFragment(name):
    match = re.match(r"^b\d+", name)
    if match == None:
        return None, None
    b = int(match.group()[1:])
    return 0, b

def parseYFragment(name, length):
    match = re.match(r"^y\d+", name)
    if match == None:
        return None, None
    y = length-int(match.group()[1:])
    return y, length


class PeptideCoverageFrame(ttk.Frame):

    def __init__(self, master, model, height=300, width=800):
        ttk.Frame.__init__(self, master=master)

        self.master = master
        self.model = model

        self.hit = None
        self.coverage = {}
        self.fragmentCoverage = {}
        self.indexList = set()

        self.height = height
        self.width = width

        self.canvas = Tkinter.Canvas(self, width=self.width, height=self.height)
        self.canvas.config(bg="white")
        self.canvas.grid(row=1, column=0, sticky="NSEW")
        #self.canvas.pack(expand=True, fill="both")
        
        self.canvas.config(highlightthickness=0)
        
        #self.canvas.grid(row=0, column=0, sticky="NSEW")

        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=0)

        # Bindings
        self.canvas.bind("<Button-1>", self.eventMouseClick)
        self.canvas.bind("<Configure>", self.on_resize)

        self.menuVar = Tkinter.StringVar(self)
        self.menuVar.trace("w", self.plotSingleFragment)

        self.aMenu = Tkinter.OptionMenu(self, self.menuVar, [])
        self.aMenu.grid(row=0, column=0)
        self.setMenuChoices([])

        # link function
        self.model.classes["PeptideCoverageFrame"] = self
        
    def plotSingleFragment(self, *args):
        if self.hit == None:
            return
        name = self.menuVar.get()
        if name in self.hit.fragments:
            self.model.classes["ConsensusSpectrumFrame"].plotSelectedFragments([name])
        
    def setMenuChoices(self, choices):
        self.aMenu['menu'].delete(0, 'end')
        if len(choices) == 0:
            self.menuVar.set("no further peptide ions")
            return
        self.menuVar.set(choices[0])
        for choice in choices:
            self.aMenu['menu'].add_command(label=choice, command=Tkinter._setit(self.menuVar, choice))

    def on_resize(self,event):
        self.width = event.width
        self.height = event.height
        self.canvas.config(width=self.width, height=self.height)
        self.paint_canvas()
        self.colorIndex()

    def init(self, hit):

        analysis = self.model.currentAnalysis
        if analysis == None:
            return
        if hit.featureID not in analysis.featureIds:
            return
        self.hit = hit
        self.indexList = set()
        self.paint_canvas()
        

    def paint_canvas(self):
        if self.hit == None:
            return
        peptideSequence = self.hit.peptide.sequence
        peptideLength = len(peptideSequence)

        parts = {}
        for i in range(0, peptideLength):
            for e in range(i+1, peptideLength+1):
                name = peptideSequence[i:e]
                key = "".join(sorted(name))
                parts[key] = parts.get(key, []) + [name]

        ySeries = set()
        bSeries = set()
        self.fragmentCoverage = {}
        
        restNames = []
        for name in self.hit.fragments:
            y, b = parseInternalFragment(name, peptideLength)
            if y == None:
                y, b = parseBFragment(name)
            else: # ignore internal fragments
                continue
            if y == None:
                y, b = parseYFragment(name, peptideLength)
            if y == None:
                restNames.append(name)
                continue
            ySeries.add(y)
            bSeries.add(b)
            
            self.fragmentCoverage[y] = self.fragmentCoverage.get(y, []) + [name]
            self.fragmentCoverage[b] = self.fragmentCoverage.get(b, []) + [name]
        
        self.setMenuChoices(restNames)
        
        # remove 0 and len
        if 0 in ySeries:
            ySeries.remove(0)
        if 0 in bSeries:
            bSeries.remove(0)

        if peptideLength in ySeries:
            ySeries.remove(peptideLength)
        if peptideLength in bSeries:
            bSeries.remove(peptideLength)

        self.canvas.delete(Tkinter.ALL)

        # write peptide sequence
        xc = self.width/2.0
        yc = self.height/2.0
        text = self.hit.peptide.sequence

        # find fitting text size
        s = 0
        for s in range(0, 100):
            font = tkFont.Font(family="Courier", size=s)
            if (font.measure(" ")+4)*len(text) > self.width:
                break

        s -= 1
        font = tkFont.Font(family="Courier", size=s)
        letterSize = font.measure(" ")+4
        start = xc - letterSize/2.0*(len(text)-1)
        for index, letter in enumerate(text):
            x = start + index*letterSize
            self.canvas.create_text((x, yc, ), text=letter,
                                    font=("Courier", s),
                                    fill="black",
                                    anchor="center",
                                    justify="center")

        # plot lines

        self.coverage = {}
        for index in ySeries:
            x = start + (index-0.5)*letterSize
            color = "black"
            
            item1 = self.canvas.create_line(x, yc,
                                            x, 20,
                                            tags=("site", ),
                                            fill=color)
            item2 = self.canvas.create_line(x, 20,
                                            x+10, 20,
                                            tags=("site", ),
                                            fill=color)
            item3 = self.canvas.create_text((x+5, 10),
                                            text="y"+str(len(text)-index), 
                                            tags=("site", ),
                                            fill=color,
                                            anchor="center",
                                            justify="center")
            self.coverage[item1] = index
            self.coverage[item2] = index
            self.coverage[item3] = index


        for index in bSeries:
            x = start + (index-0.5)*letterSize
            color = "black"
            item1 = self.canvas.create_line(x, yc,
                                            x, self.height-20,
                                            tags=("site", ),
                                            fill=color)
            item2 = self.canvas.create_line(x, self.height-20,
                                            x-10, self.height-20,
                                            tags=("site", ),
                                            fill=color)
            item3 = self.canvas.create_text((x-5, self.height-10),
                                            text="b"+str(index), 
                                            tags=("site", ),
                                            fill=color,
                                            anchor="center",
                                            justify="center")
            self.coverage[item1] = index
            self.coverage[item2] = index

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
        self.colorIndex()

    def colorIndex(self):
        found = []
        for index in self.indexList:
            found += self.fragmentCoverage[index]
            for item in self.coverage:
                if self.coverage[item] == index:
                    self.canvas.itemconfigure(item, fill="red")

        self.model.classes["ConsensusSpectrumFrame"].plotSelectedFragments(found)



