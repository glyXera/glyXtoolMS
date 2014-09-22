import re    
from matplotlib import pyplot as plt



class Histogram:
    
    def __init__(self,binwidth):
        self.bins = {}
        self.colors = {}
        self.binwidth = float(binwidth)
        self.maxValue = 0

    def __version__(self):
        return "0.0.1"

    def addSeries(self,series,label="",color="black"):
        if not label in self.bins:
            self.bins[label] = {}
        self.colors[label] = color
        for x in series:
            b = int(x/self.binwidth)
            if not b in self.bins[label]:
                self.bins[label][b] = 0
            self.bins[label][b] += 1
            if self.bins[label][b] > self.maxValue:
                self.maxValue = self.bins[label][b]

    def ploth(self,order=None,axis=None):
        if not order:
            order = self.bins.keys()        
        leftStart = {}
        for label in order:
            bottom = []
            width = []
            left = []
            for b in self.bins[label]:
                if not b in leftStart:
                    leftStart[b] = 0
                bottom.append(b*self.binwidth)
                width.append(self.bins[label][b])
                left.append(leftStart[b])
                leftStart[b] += self.bins[label][b]
            if axis:
                axis.barh(bottom,width,height=self.binwidth,left=left,label=label,color=color)
            else:
                plt.barh(bottom,width,height=self.binwidth,left=left,label=label,color=color)

    def plot(self,order=None,axis=None):
        if not order:
            order = self.bins.keys()        
        bottomStart = {}
        for label in order:
            bottom = []
            height = []
            left = []
            if not label in self.bins:
                continue
            for b in self.bins[label]:
                if not b in bottomStart:
                    bottomStart[b] = 0
                left.append(b*self.binwidth)
                height.append(self.bins[label][b])
                bottom.append(bottomStart[b])
                bottomStart[b] += self.bins[label][b]
            if axis:
                axis.bar(left,height,width=self.binwidth,bottom=bottom,label=label,color=self.colors[label])
            else:
                plt.bar(left,height,width=self.binwidth,bottom=bottom,label=label,color=self.colors[label]) 


# ---------------------------- Protein Digest -------------------------------------


class AminoAcids:

    def __init__(self):
        self.amino = {}
        self.amino["A"] = 71.03711
        self.amino["R"] = 156.10111
        self.amino["N"] = 114.04293
        self.amino["D"] = 115.02694
        self.amino["C"] = 103.00919
        self.amino["E"] = 129.04259
        self.amino["Q"] = 128.05858
        self.amino["G"] = 57.02146
        self.amino["H"] = 137.05891
        self.amino["I"] = 113.08406
        self.amino["L"] = 113.08406
        self.amino["K"] = 128.09496
        self.amino["M"] = 131.04049
        self.amino["F"] = 147.06841
        self.amino["P"] = 97.05276
        self.amino["S"] = 87.03203
        self.amino["T"] = 101.04768
        self.amino["W"] = 186.07931
        self.amino["Y"] = 163.06333
        self.amino["V"] = 99.06841


    def calcPeptideMass(self,sequence):
        mass = 18.01057
        for s in sequence: 
            mass += self.amino[s]
        return mass

class Peptide:
    
    def __init__(self,sequence,mass,N_carbamidation, N_carboxylation,N_oxidation):
        self.sequence = sequence
        self.mass = mass
        self.N_carbamidation = N_carbamidation
        self.N_carboxylation = N_carboxylation
        self.N_oxidation = N_oxidation
        self.GlycosylationSiteN = False
        self.GlycosylationSiteO = False        
                

class ProteinDigest:

    def __init__(self):

        self._aminoAcids = AminoAcids()
        self._carbamidation = False
        self._carboxylation = False
        self._oxidation = False                             

        self._mod = {}
        self._mod["carbamidation"] = 57.021464 
        self._mod["carboxylation"] = 58.005479
        self._mod["oxidation"] = 15.884915

        self._breakpoints = []


    def setCarbamidation(self,boolean):
        if boolean == True:
            self._carbamidation = True
            self._carboxylation = False
        else:
            self._carbamidation = False

    def setCarboxylation(self,boolean):
        if boolean == True:
            self._carboxylation = True
            self._carbamidation = False
        else:
            self._carboxylation = False

    def setOxidation(self,boolean):
        self._oxidation = boolean

    def calcPeptideMasses(self,sequence):
        
        mass = self._aminoAcids.calcPeptideMass(sequence)
        # count Nr of Cysteine
        c = sequence.count("C")
        # add carbamidation
        N_carbamidation = 0
        N_carboxylation = 0
        if self._carbamidation:
            mass += c*self._mod["carbamidation"]
            N_carbamidation = c
            
        elif self._carboxylation:
            mass += c*self._mod["carboxylation"]
            N_carboxylation = c
        masses = []
        # add Oxidation:
        if self._oxidation:
            for m in range(0,sequence.count("M")+1):
                masses.append(Peptide(sequence,mass+m*self._mod["oxidation"],N_carbamidation,N_carboxylation,m))
        else:
            masses.append(Peptide(sequence,mass,N_carbamidation,N_carboxylation,0))
        return masses

    def newDigest(self):
        self._breakpoints = []
        
    def add_tryptic_digest(self,sequence):
        i = 0
        while i < len(sequence):
            if sequence[i] == "R" or sequence[i] == "K":
                if not (i+1 < len(sequence) and sequence[i+1] == "P"):
                    self._breakpoints.append(i)
            i += 1
           
    def digest(self,sequence,maxMissedCleavage):
        # clean up breakpoints
        self._breakpoints = list(set(self._breakpoints))
        self._breakpoints.sort()

        peptides = []
        start = -1
        i = 0
        while i < len(self._breakpoints):
            for m in range(0,maxMissedCleavage+1):
                if i+m >= len(self._breakpoints):
                    break
                stop = self._breakpoints[i+m]
                sub = sequence[start+1:stop+1]
                #digests.append((sub,self.calcPeptideMass(sub),m))
                peptides.append(sub)
            start = self._breakpoints[i]
            i += 1
        
        return peptides

    def countGlycosylationsites(self,sequence,glycosylationType=None):
        # a) N-Glycan: N-X(not P)-S/T
        # b) O-Glycan: S/T
        N = len(re.findall("N[^P](S|T)",sequence))
        O = len(re.findall("(S|T)",sequence))
        if not glycosylationType:
            return N+O
        elif glycosylationType == "N":
            return N
        else:
            return O
        #return {"N":len(re.findall("N[^P](S|T)",sequence)),"O":len(re.findall("(S|T)",sequence))}

    def findGlycopeptides(self,sequence,maxMissedCleavage, glycosylationType=None):
        # a) make digest
        self.newDigest()
        self.add_tryptic_digest(sequence)
        peptides = self.digest(sequence,maxMissedCleavage)
        glycopeptides = []
        # b) search peptides with possible glycosylation site
        for peptide in peptides:
            if self.countGlycosylationsites(peptide,glycosylationType) > 0:
                glycopeptides += self.calcPeptideMasses(peptide)
        return glycopeptides
        
                    
# ------------------------- Glycan calculations -------------------------------------
class GlycanMass:

    def __init__(self):
        self.glycan = {}
        self.glycan["DHEX"] = 146.058
        self.glycan["HEX"] = 162.052
        self.glycan["HEXNAC"] = 203.079
        self.glycan["NEUAC"] = 291.095

    def getMass(self,name):
        return self.glycan[name]

    def getAll(self,DHEX,HEX,HEXNAC,NEUAC):
        mass = self.glycan["DHEX"]*DHEX
        mass += self.glycan["HEX"]*HEX
        mass += self.glycan["HEXNAC"]*HEXNAC
        mass += self.glycan["NEUAC"]*NEUAC
        return mass




# --------------------------- Helper functions ------------------------------------ 

def openDialog():
    import Tkinter, tkFileDialog
    root = Tkinter.Tk()
    root.withdraw()

    file_path = tkFileDialog.askopenfilename()
    root.destroy()
    return file_path


def openOpenMSExperiment(path):
    if not path.endswith(".mzML"):
        raise Exception("not a .mzML file")
    import pyopenms
    print "loading experiment"
    exp = pyopenms.MSExperiment()
    fh = pyopenms.FileHandler()
    fh.loadExperiment(path,exp)
    print "loading finnished"
    return exp

