import re    
from itertools import product 
import copy
from glyxsuite import masses as glyxmass
from glyxsuite.io import XMLPeptide

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
                raise Exception("Please provide a plot axis, eg 'axis=plt'")

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
                raise Exception("Please provide a plot axis, eg 'axis=plt'")


# ---------------------------- Protein Digest -------------------------------------

class Protein:
        
    def __init__(self):
        self.identifier = ""
        self.description = ""
        self.sequence = ""
        self.modifications = []
        
        
    def loadFromFasta(self,identifier, description, sequence):
        self.identifier = identifier
        self.description = description
        self.modifications = []
        diff = 0
        for x in re.finditer("\(.+?\)",sequence):
            name = x.group()[1:-1]
            pos = x.start()-diff-1
            self.modifications.append((name,sequence[pos],pos))
            diff += x.end()-x.start()
        self.sequence = re.sub("\(.+?\)","",sequence)
        
        # check aminoacids and modifications
        try:
            for s in self.sequence:
                glyxmass.AMINOACID[s]
            for name,amino,pos in self.modifications:
                glyxmass.PROTEINMODIFICATION[name]
        except KeyError:
            print "Error in protein ", identifier
            raise
            
    def getPeptide(self,start,end):
        peptide = XMLPeptide()
        peptide.sequence = self.sequence[start:end]
        peptide.start = start
        peptide.end = end
        for mod,amino,pos in self.modifications:
            if start <= pos and pos < end:
                peptide.modifications.append((mod,amino,pos))
        return peptide
        
        
"""
class Peptide(XMLPeptide):
    
    def __init__(self):
        self.sequence = ""
        self.start = -1
        self.end = -1
        self.mass = 0.0
        self.modifications = []
        self.glycosylationSites = []
            
    def toString(self):
        s = self.sequence
        modi = {}
        for mod,amino,pos in self.modifications:
            if not mod in modi:
                modi[mod] = []
            modi[mod].append(pos)
        for mod in modi:
            modi[mod].sort()
            s += " " + mod + "("+", ".join(map(str,modi[mod]))+")"
        return s

    def calcPeptideMass(self):
        mass = glyxmass.calcPeptideMass(self.sequence)
        for mod,amino,pos in self.modifications:
            mass += glyxmass.PROTEINMODIFICATION[mod]
        self.mass = mass
            
"""            
            
class ProteinDigest:

    def __init__(self):

        self.carbamidation = False
        self.carboxylation = False
        self.oxidation = False
        self.acrylamideAdducts = False
        self.breakpoints = []
        self.protein = None


    def setCarbamidation(self,boolean):
        if boolean == True:
            self.carbamidation = True
            self.carboxylation = False
        else:
            self.carbamidation = False

    def setCarboxylation(self,boolean): # Iodoacetic acid
        if boolean == True:
            self.carboxylation = True
            self.carbamidation = False
        else:
            self.carboxylation = False

    def setAcrylamideAdducts(self,boolean):
        self.acrylamideAdducts = boolean
            
    def setOxidation(self,boolean):
        self.oxidation = boolean

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
        
        
        # count Nr of Cysteine
        c = sequence.count("C")

        # count Nr of Methionine
        m = sequence.count("M")
        
        # substract already specified modifications
        for mod,amino,pos in peptide.modifications:
            if amino == "C":
                c -= 1
            elif amino == "M":
                m -= 1
                
        N_Cys_CAM = 0
        N_Cys_CM = 0
        N_Cys_PAM = 0
        N_MSO = 0
        if self.carbamidation == True:
            N_Cys_CAM = c
        elif self.carboxylation == True:
            N_Cys_CM = c
        if self.acrylamideAdducts == True:
            N_Cys_PAM = c
        if self.oxidation == True:
            N_MSO = m
        # make permutations
        masses = []
        for cys_CAM,cys_CM,cys_PAM,MSO in product(range(0,N_Cys_CAM+1),
                                                   range(0,N_Cys_CM+1),
                                                   range(0,N_Cys_PAM+1),
                                                   range(0,N_MSO+1)):
            if cys_CAM+cys_CM+cys_PAM > c:
                continue 
                            
            newPeptide = copy.deepcopy(peptide)
            
            newPeptide.modifications += [("Cys_CAM","C",-1)]*cys_CAM
            newPeptide.modifications += [("Cys_CM","C",-1)]*cys_CM
            newPeptide.modifications += [("Cys_PAM","C",-1)]*cys_PAM
            newPeptide.modifications += [("MSO","M",-1)]*MSO
            # calc peptide mass
            newPeptide.mass = glyxmass.calcPeptideMass(newPeptide.sequence)
            for mod,amino,pos in newPeptide.modifications:
                newPeptide.mass += glyxmass.PROTEINMODIFICATION[mod]          
            masses.append(newPeptide)
                        
        return masses

    def newDigest(self,protein):
        self.protein = protein
        self.breakpoints = []


    def add_tryptic_digest(self):
        # cleaves C-terminal side of K or R, except if P is C-term to K or R
        i = 0
        while i < len(self.protein.sequence):
            if self.protein.sequence[i] == "R" or self.protein.sequence[i] == "K":
                if not (i+1 < len(self.protein.sequence) and self.protein.sequence[i+1] == "P"):
                    self.breakpoints.append(i)
            i += 1


    def add_AspN_digest(self):
        # cleaves N-terminal side of D
        i = 1
        while i < len(self.protein.sequence):
            if self.protein.sequence[i] == "D":
                self.breakpoints.append(i-1)
            i += 1
           
    def digest(self,maxMissedCleavage):
        self.breakpoints.append(len(self.protein.sequence)-1)
        # clean up breakpoints
        self.breakpoints = list(set(self.breakpoints))
        self.breakpoints.sort()

        peptides = []
        start = -1
        i = 0
        while i < len(self.breakpoints):
            for m in range(0,maxMissedCleavage+1):
                if i+m >= len(self.breakpoints):
                    break
                stop = self.breakpoints[i+m]
                #peptideSequence = self.protein.sequence[start+1:stop+1]
                #peptide = Peptide(peptideSequence=peptideSequence,start=start+1, end=stop+1) # stop+1?
                peptides.append(self.protein.getPeptide(start+1,stop+1))
            start = self.breakpoints[i]
            i += 1
        
        return peptides

    def findGlycopeptides(self,maxMissedCleavage, NGlycosylation = False, OGlycosylation = False):

        # make digest
        peptides = self.digest(maxMissedCleavage)
        
        # generate list of glycosylationsites
        sites = []
        if NGlycosylation == True:
            for match in re.finditer("N[^P](S|T)",self.protein.sequence):
                sites.append((match.start(),"N"))
        if OGlycosylation == True:
            for match in re.finditer("(S|T)",self.protein.sequence):
                sites.append((match.start(),"O"))
            
        sites.sort()
        
        glycopeptides = []
        # b) search peptides with possible glycosylation site
        for peptide in peptides:
            glycopeptide = False
            for site,typ in sites:
                if peptide.start <= site and site < peptide.end:
                    peptide.glycosylationSites.append((site,typ))
                    glycopeptide = True
            if glycopeptide == True:
                glycopeptides += self.calcPeptideMasses(peptide)
        return glycopeptides

# --------------------------------------- Glycan -----------------------
class Glycan:

    def __init__(self,composition):
        self.composition = composition
        self.sugar = {'DHEX': 0, 'HEX': 0, 'HEXNAC': 0, 'NEUAC': 0}
        self.mass = 0
        self._splitComposition(composition)


    def _splitComposition(self,composition):
        self.mass = 0
        for comp in re.findall("[A-z]+\d+",composition):
            unit = re.search("[A-z]+",comp).group()
            amount = int(re.search("\d+",comp).group())
            self.sugar[unit] = amount
            self.mass += glyxmass.GLYCAN[unit]*amount
            
    def getComposition(self,typ="N"):
        comp = self.sugar.copy()
        if typ == "N" and self.checkNCore() == "core":
            comp["HEX"] -= 3
            comp["HEXNAC"] -= 2
            composition = "(GlcNAc)2 (Man)3 + "
        else:
            composition = ""    

        for sugar in ["DHEX","HEX","HEXNAC","NEUAC"]:
            if comp[sugar] > 0:
                composition += sugar+str(comp[sugar])
        return composition
        
        
    def checkNCore(self): # ouput: "None", "sub","core"
        # Core: 2 HexNac + 3 Hex
        # Subcore:
        # 2 / 3
        # 2/2   
        # 2/1
        #2/0
        # 1/0
        hexnac = self.sugar["HEXNAC"]
        hexose = self.sugar["HEX"]
        if hexnac >= 2 and hexose >= 3:
            return "core"
        if hexnac >= 2:
            return "sub"
        if hexnac == 1 and hexose == 0:
            return "sub"
        return "none"
        



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

