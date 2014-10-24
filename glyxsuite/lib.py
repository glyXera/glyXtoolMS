import re    
from matplotlib import pyplot as plt
from itertools import product 
import copy

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
    
    def __init__(self,peptideSequence = "",mass = 0.0, start=-1, end = -1, N_carbamidation=0,N_carboxylation=0,N_acrylamide=0,N_oxidation=0,glycosylationSites=[]):
        self.sequence = peptideSequence
        self.start = start
        self.end = end
        self.mass = mass
        self.N_carbamidation = N_carbamidation
        self.N_carboxylation = N_carboxylation
        self.N_acrylamide = N_acrylamide
        self.N_oxidation = N_oxidation
        self.glycosylationSites = list(glycosylationSites) # make copy of this list, otherwise leads to weird behaviour where the object pointer occurs in several peptides
        
    
    def toString(self):
        return self.sequence+" CAM:"+str(self.N_carbamidation)+" CM:"+str(self.N_carboxylation)+" PAM:"+str(self.N_acrylamide)+" MSO:"+str(self.N_oxidation)

                

class ProteinDigest:

    def __init__(self):

        self._aminoAcids = AminoAcids()
        self._carbamidation = False
        self._carboxylation = False
        self._oxidation = False
        self._acrylamideAdducts = False

        self._mod = {}
        self._mod["carbamidation"] = 57.021464 # Cys_CAM Idoacetamide treatment
        self._mod["carboxylation"] = 58.005479 # Cys_CM, Iodoacetic acid treatment
        self._mod["acrylamideAdduct"] = 71.03712 # Cys_PAM Acrylamide Adduct
        self._mod["oxidation"] = 15.884915 # MSO

        self._breakpoints = []
        self._proteinSequence = ""


    def setCarbamidation(self,boolean):
        if boolean == True:
            self._carbamidation = True
            self._carboxylation = False
        else:
            self._carbamidation = False

    def setCarboxylation(self,boolean): # Iodoacetic acid
        if boolean == True:
            self._carboxylation = True
            self._carbamidation = False
        else:
            self._carboxylation = False

    def setAcrylamideAdducts(self,boolean):
        self._acrylamideAdducts = boolean
            
    def setOxidation(self,boolean):
        self._oxidation = boolean

    def calcPeptideMasses(self,peptide):

        
        try:
            sequence = peptide.sequence
        except AttributeError:
            raise Exception("missing attribute 'sequence'! (String)")

        try:
            start = peptide.start
        except AttributeError:
            raise Exception("missing attribute 'start'! (Integer)")
            
        try:
            end = peptide.end
        except AttributeError:
            raise Exception("missing attribute 'end'! (Integer)")
        
        peptideMass = self._aminoAcids.calcPeptideMass(sequence)
        
        # count Nr of Cysteine
        c = sequence.count("C")
        # count Nr of Methionine
        m = sequence.count("M")

        N_Cys_CAM = 0
        N_Cys_CM = 0
        N_Cys_PAM = 0
        N_MSO = 0
        if self._carbamidation == True:
            N_Cys_CAM = c
        elif self._carboxylation == True:
            N_Cys_CM = c
        if self._acrylamideAdducts == True:
            N_Cys_PAM = c
        if self._oxidation == True:
            N_MSO = m
        # make permutations
        masses = []
        for cys_CAM,cys_CM,cys_PAM,MSO in product(range(0,N_Cys_CAM+1),
                                                   range(0,N_Cys_CM+1),
                                                   range(0,N_Cys_PAM+1),
                                                   range(0,N_MSO+1)):
            if cys_CAM+cys_CM+cys_PAM > c:
                continue 
            mass = peptideMass + cys_CAM*self._mod["carbamidation"]
            mass += cys_CM*self._mod["carboxylation"]
            mass += cys_PAM*self._mod["acrylamideAdduct"]
            mass += MSO*self._mod["oxidation"]
            
            newPeptide = copy.deepcopy(peptide)
            newPeptide.mass = mass
            newPeptide.N_carbamidation = cys_CAM
            newPeptide.N_carboxylation=cys_CM
            newPeptide.N_acrylamide=cys_PAM
            newPeptide.N_oxidation=MSO
            
            masses.append(newPeptide)
        """masses = []
        for cys_CAM in range(0,N_Cys_CAM+1):
            for cys_CM in range(0,N_Cys_CM+1):
                for cys_PAM in range(0,N_Cys_PAM+1):
                    # check nr of modified cysteine
                    if cys_CAM+cys_CM+cys_PAM > c:
                        continue
                    for MSO in range(0,N_MSO+1):
                        mass = peptideMass + cys_CAM*self._mod["carbamidation"]
                        mass += cys_CM*self._mod["carboxylation"]
                        mass += cys_PAM*self._mod["acrylamideAdduct"]
                        mass += MSO*self._mod["oxidation"]
                        masses.append(Peptide(peptideSequence=sequence, mass=mass,
                                              start=start,end=end,
                                              N_carbamidation=cys_CAM,
                                              N_carboxylation=cys_CM,
                                              N_acrylamide=cys_PAM,
                                              N_oxidation=MSO)
                                        )"""
                        
        return masses

    def newDigest(self,proteinSequence):
        self._proteinSequence = proteinSequence
        self._breakpoints = []

    def _checkSequenceSet(self):
        if self._proteinSequence == "":
            raise Exception("Sequence not set, please use 'newDigest(sequence)' to initialize!")
        
    def add_tryptic_digest(self):
        # cleaves C-terminal side of K or R, except if P is C-term to K or R
        self._checkSequenceSet()
        i = 0
        while i < len(self._proteinSequence):
            if self._proteinSequence[i] == "R" or self._proteinSequence[i] == "K":
                if not (i+1 < len(self._proteinSequence) and self._proteinSequence[i+1] == "P"):
                    self._breakpoints.append(i)
            i += 1


    def add_AspN_digest(self):
        # cleaves N-terminal side of D
        self._checkSequenceSet()
        i = 1
        while i < len(self._proteinSequence):
            if self._proteinSequence[i] == "D":
                self._breakpoints.append(i-1)
            i += 1
           
    def digest(self,maxMissedCleavage):
        # check if breakpoints exists
        #if len(self._breakpoints) == 0:
        #    raise Exception("No digest added! Please use 'add_tryptic_digest()' or similar beforehand!")
        # Add  end
        #self._breakpoints.append(0)
        self._breakpoints.append(len(self._proteinSequence)-1)
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
                peptideSequence = self._proteinSequence[start+1:stop+1]
                peptide = Peptide(peptideSequence=peptideSequence,start=start+1, end=stop+1) # stop+1?
                peptides.append(peptide)
            start = self._breakpoints[i]
            i += 1
        
        return peptides

    def _getGlycosylationsites(self,NGlycosylation, OGlycosylation):
        return
        """
        # a) N-Glycan: N-X(not P)-S/T
        # b) O-Glycan: S/T
        if NGlycosylation
        N = len(re.findall("N[^P](S|T)",sequence))
        O = len(re.findall("(S|T)",sequence))
        if not glycosylationType:
            return N+O
        elif glycosylationType == "N":
            return N
        else:
            return O
        #return {"N":len(re.findall("N[^P](S|T)",sequence)),"O":len(re.findall("(S|T)",sequence))}"""

    def findGlycopeptides(self,maxMissedCleavage, NGlycosylation = False, OGlycosylation = False):

        # make digest
        peptides = self.digest(maxMissedCleavage)
        
        # generate list of glycosylationsites
        sites = []
        if NGlycosylation == True:
            for match in re.finditer("N[^P](S|T)",self._proteinSequence):
                sites.append((match.start(),"N"))
        if OGlycosylation == True:
            for match in re.finditer("(S|T)",self._proteinSequence):
                sites.append((match.start(),"O"))
            
        sites.sort()
        
        glycopeptides = []
        # b) search peptides with possible glycosylation site
        for peptide in peptides:
            glycopeptide = False
            for site,typ in sites:
                if peptide.start <= site and site <= peptide.end:
                    peptide.glycosylationSites.append((site,typ))
                    glycopeptide = True
            if glycopeptide == True:
                glycopeptides += self.calcPeptideMasses(peptide)
        return glycopeptides
  
# ------------------------- Glycan calculations -------------------------------------
class GlycanMass:

    def __init__(self):
        self.glycan = {}
        self.glycan["DHEX"] = 146.0579
        self.glycan["HEX"] =  162.0528
        self.glycan["HEXNAC"] =  203.0794
        self.glycan["NEUAC"] = 291.0954

    def getMass(self,name):
        return self.glycan[name]

    def getAll(self,DHEX,HEX,HEXNAC,NEUAC):
        mass = self.glycan["DHEX"]*DHEX
        mass += self.glycan["HEX"]*HEX
        mass += self.glycan["HEXNAC"]*HEXNAC
        mass += self.glycan["NEUAC"]*NEUAC
        return mass




# --------------------------- Helper functions ------------------------------------ 

def openDialog(path = "."):
    import Tkinter, tkFileDialog
    root = Tkinter.Tk()
    root.withdraw()

    file_path = tkFileDialog.askopenfilename(initialdir=path)
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

