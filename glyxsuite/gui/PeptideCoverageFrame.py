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
        self.canvas.pack(expand=True, fill="both")
        self.canvas.config(highlightthickness=0)
        self.canvas.bind("<Configure>", self.on_resize)
        #self.canvas.grid(row=0, column=0, sticky="NSEW")

        #self.grid_rowconfigure(0, weight=1)
        #self.grid_columnconfigure(0, weight=1)

        #self.grid_columnconfigure(0, weight=1)

        # Bindings
        self.canvas.bind("<Button-1>", self.eventMouseClick)

        # link function
        self.model.funcUpdateIdentificationCoverage = self.init

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

        ySeries = {}
        bSeries = {}
        self.fragmentCoverage = {}
        for name in self.hit.fragments:
            y, b = parseInternalFragment(name, peptideLength)
            if y == None:
                y, b = parseBFragment(name)
            if y == None:
                y, b = parseYFragment(name, peptideLength)
            if y == None:
                continue
            yHit = ySeries.get(y, False)
            bHit = ySeries.get(b, False)
            self.fragmentCoverage[y] = self.fragmentCoverage.get(y, []) + [name]
            self.fragmentCoverage[b] = self.fragmentCoverage.get(b, []) + [name]

            fragmentSequence = self.hit.fragments[name]["sequence"].split("-")[0]
            fragmentSequence = re.sub(r"\(.+?\)", "", fragmentSequence)
            key = "".join(sorted(fragmentSequence))
            if len(parts[key]) == 1:
                yHit = True
                bHit = True

            ySeries[y] = yHit
            bSeries[b] = bHit

        # remove 0 and len
        if 0 in ySeries:
            ySeries.pop(0)
        if 0 in bSeries:
            bSeries.pop(0)

        if peptideLength in ySeries:
            ySeries.pop(peptideLength)
        if peptideLength in bSeries:
            bSeries.pop(peptideLength)

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
            if ySeries[index] == True:
                item1 = self.canvas.create_line(x, yc,
                                                x, 10,
                                                tags=("site", ),
                                                fill=color)
                item2 = self.canvas.create_line(x, 10,
                                                x+10, 10,
                                                tags=("site", ),
                                                fill=color)
            else:
                item1 = self.canvas.create_line(x, yc,
                                                x, 10,
                                                tags=("site", ),
                                                fill=color, dash=(3, 5))
                item2 = self.canvas.create_line(x, 10,
                                                x+10, 10,
                                                tags=("site", ),
                                                fill=color, dash=(3, 5))
            self.coverage[item1] = index
            self.coverage[item2] = index


        for index in bSeries:
            x = start + (index-0.5)*letterSize
            color = "black"
            if bSeries[index] == True:
                item1 = self.canvas.create_line(x, yc,
                                                x, self.height-10,
                                                tags=("site", ),
                                                fill=color)
                item2 = self.canvas.create_line(x, self.height-10,
                                                x-10, self.height-10,
                                                tags=("site", ),
                                                fill=color)
            else:
                item1 = self.canvas.create_line(x, yc,
                                                x, self.height-10,
                                                tags=("site", ),
                                                fill=color, dash=(3, 5))
                item2 = self.canvas.create_line(x, self.height-10,
                                                x-10, self.height-10,
                                                tags=("site", ),
                                                fill=color, dash=(3, 5))
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



