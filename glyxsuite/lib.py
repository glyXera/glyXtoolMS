import re
from itertools import product
import copy
import glyxsuite
import pyopenms
import glyxsuite.io

class Histogram(object):

    def __init__(self, binwidth):
        self.bins = {}
        self.colors = {}
        self.binwidth = float(binwidth)
        self.maxValue = 0

    def __version__(self):
        return "0.0.1"

    def addSeries(self, series, label="", color="black"):
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

    def ploth(self, order=None, axis=None):
        if not order:
            order = self.bins.keys()
        leftStart = {}
        bars = []
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
                bar = axis.barh(bottom, width, height=self.binwidth, left=left, label=label, color=self.colors[label])
                bars.append(bar)
            else:
                raise Exception("Please provide a plot axis, eg 'axis=plt'")
        return bars

    def plot(self, order=None, axis=None):
        if not order:
            order = self.bins.keys()
        bottomStart = {}
        bars = []
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
                bar = axis.bar(left, height, width=self.binwidth, bottom=bottom, label=label, color=self.colors[label])
                bars.append(bar)
            else:
                raise Exception("Please provide a plot axis, eg 'axis=plt'")
        return bars


# ---------------------------- Protein Digest -------------------------------------

class Protein(object):

    def __init__(self):
        self.identifier = ""
        self.description = ""
        self.sequence = ""
        self.modifications = []


    def loadFromFasta(self, identifier, description, sequence):
        self.identifier = identifier
        self.description = description
        self.modifications = []
        diff = 0
        for x in re.finditer("\(.+?\)", sequence):
            name = x.group()[1:-1]
            pos = x.start()-diff-1
            self.modifications.append((name, sequence[pos], pos))
            diff += x.end()-x.start()
        self.sequence = re.sub("\(.+?\)", "", sequence)

        # check aminoacids and modifications
        try:
            for s in self.sequence:
                assert s in glyxsuite.masses.AMINOACID
            for name, amino, pos in self.modifications:
                assert name in glyxsuite.masses.PROTEINMODIFICATION
        except KeyError:
            print "Error in protein ", identifier
            raise

    def getPeptide(self, start, end):
        peptide = glyxsuite.io.XMLPeptide()
        peptide.sequence = self.sequence[start:end]
        peptide.start = start
        peptide.end = end
        peptide.proteinID = self.identifier
        for mod, amino, pos in self.modifications:
            if start <= pos and pos < end:
                peptide.modifications.append((mod, amino, pos))
        return peptide

class ProteinDigest(object):

    def __init__(self):

        self.carbamidation = False
        self.carboxylation = False
        self.oxidation = False
        self.acrylamideAdducts = False
        self.breakpoints = []
        self.protein = None


    def setCarbamidation(self, boolean):
        if boolean == True:
            self.carbamidation = True
            self.carboxylation = False
        else:
            self.carbamidation = False

    def setCarboxylation(self, boolean): # Iodoacetic acid
        if boolean == True:
            self.carboxylation = True
            self.carbamidation = False
        else:
            self.carboxylation = False

    def setAcrylamideAdducts(self, boolean):
        self.acrylamideAdducts = boolean

    def setOxidation(self, boolean):
        self.oxidation = boolean

    def calcPeptideMasses(self, peptide):


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
        for mod, amino, pos in peptide.modifications:
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
        for cys_CAM, cys_CM, cys_PAM, MSO in product(range(0, N_Cys_CAM+1),
                                                     range(0, N_Cys_CM+1),
                                                     range(0, N_Cys_PAM+1),
                                                     range(0, N_MSO+1)):
            if cys_CAM+cys_CM+cys_PAM > c:
                continue

            newPeptide = copy.deepcopy(peptide)

            newPeptide.modifications += [("Cys_CAM", "C", -1)]*cys_CAM
            newPeptide.modifications += [("Cys_CM", "C", -1)]*cys_CM
            newPeptide.modifications += [("Cys_PAM", "C", -1)]*cys_PAM
            newPeptide.modifications += [("MSO", "M", -1)]*MSO
            # calc peptide mass
            newPeptide.mass = glyxsuite.masses.calcPeptideMass(newPeptide)
            masses.append(newPeptide)

        return masses

    def newDigest(self, protein):
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

    def add_AspN_digest_2(self):
        # cleaves N-terminal side of E, D and C
        i = 1
        while i < len(self.protein.sequence):
            if self.protein.sequence[i] in ["E","D","C"]:
                self.breakpoints.append(i-1)
            i += 1

    def add_ProtinaseK_digest(self):
        # cleaves D-terminal side of multiple aminoacids
        i = 1
        while i < len(self.protein.sequence):

            if self.protein.sequence[i] in ["A", "F", "Y", "W", "L", "I", "V"]:
                self.breakpoints.append(i)
            i += 1

    def add_Unspecific_digest(self):
        # cleaves all possible aminoacids
        for i in range(0,len(self.protein.sequence)):
            self.breakpoints.append(i)

    def digest(self, maxMissedCleavage):
        self.breakpoints.append(len(self.protein.sequence)-1)
        # clean up breakpoints
        self.breakpoints = list(set(self.breakpoints))
        self.breakpoints.sort()

        peptides = []
        start = -1
        i = 0
        while i < len(self.breakpoints):
            for m in range(0, maxMissedCleavage+1):
                if i+m >= len(self.breakpoints):
                    break
                stop = self.breakpoints[i+m]
                peptides.append(self.protein.getPeptide(start+1, stop+1))
            start = self.breakpoints[i]
            i += 1

        return peptides

    def findGlycopeptides(self, peptides, NGlycosylation=False,
                          OGlycosylation=False):

        # generate list of glycosylationsites
        sites = []
        if NGlycosylation == True:
            for match in re.finditer("N[^P](S|T)", self.protein.sequence):
                sites.append((match.start(), "N"))
        if OGlycosylation == True:
            for match in re.finditer("(S|T)", self.protein.sequence):
                sites.append((match.start(), "O"))

        sites.sort()

        glycopeptides = []
        # b) search peptides with possible glycosylation site
        for peptide in peptides:
            glycopeptide = False
            for site, typ in sites:
                if peptide.start <= site and site < peptide.end:
                    peptide.glycosylationSites.append((site, typ))
                    glycopeptide = True
            if glycopeptide == True:
                glycopeptides += self.calcPeptideMasses(peptide)
        return glycopeptides

# --------------------------------------- Glycan -----------------------
class Glycan(glyxsuite.io.XMLGlycan):

    def __init__(self, composition=None):
        self.composition = composition
        self.typ = None
        self.glycosylationSite = None
        self.linearCode = ""
        self.structure = None
        self.sugar = {'DHEX': 0, 'HEX': 0, 'HEXNAC': 0, 'NEUAC': 0}
        self.mass = 0
        if composition is not None:
            self._splitComposition(composition)

    def setComposition(self,S=0,F=0,H=0,N=0):

        self.sugar["NEUAC"] = S
        self.sugar["DHEX"] = F
        self.sugar["HEX"] = H
        self.sugar["HEXNAC"] = N

        self.mass = 0
        for unit in self.sugar:
            self.mass += glyxsuite.masses.GLYCAN[unit]*self.sugar[unit]

    def checkComposition(self):
        HEX = self.sugar["HEX"]
        HEXNAC= self.sugar["HEXNAC"]
        DHEX= self.sugar["DHEX"]
        NEUAC= self.sugar["NEUAC"]

        if HEX+HEXNAC == 0:
            return False
        # The number of fucose residues plus 1 must be less than or
        # equal to the sum of the number of hexose plus HexNAc residues.
        if DHEX >= HEX+HEXNAC:
            return False
        # If the number of HexNAc residues is less than or equal to 2
        # and the number of hexose residues is greater than 2,
        # then the number of NeuAc and NeuGc residues must be zero.
        if HEXNAC <= 2 and HEX > 2 and NEUAC > 0:
            return False
        return True

    def _splitComposition(self, composition):
        self.mass = 0
        for comp in re.findall("[A-z]+\d+", composition):
            unit = re.search("[A-z]+", comp).group()
            keys = {"S":"NEUAC","F":"DHEX","H":"HEX","N":"HEXNAC"}
            if unit in keys:
                unit = keys[unit]
            amount = int(re.search("\d+", comp).group())
            self.sugar[unit] = amount
            self.mass += glyxsuite.masses.GLYCAN[unit]*amount

    def getComposition(self, typ="N"):
        comp = self.sugar.copy()
        if typ == "N" and self.checkNCore() == "core":
            comp["HEX"] -= 3
            comp["HEXNAC"] -= 2
            composition = "(GlcNAc)2 (Man)3 + "
        else:
            composition = ""

        for sugar in ["DHEX", "HEX", "HEXNAC", "NEUAC"]:
            if comp[sugar] > 0:
                composition += sugar+str(comp[sugar])
        return composition

    def getShortName(self):
        shortName = ""
        short = {'DHEX': "F", 'HEX': "H", 'HEXNAC': "HN", 'NEUAC': "NA",'NEUGC': "NG"}
        for name in sorted(self.sugar.keys()):
            amount = self.sugar[name]
            if amount == 0:
                continue
            shortName += short[name]+str(amount)
        return shortName

    def toString(self):
        result = ""
        for name in sorted(self.sugar.keys()):
            amount = self.sugar[name]
            if amount == 0:
                continue
            result += name + str(amount)
        return result


    def checkNCore(self): # ouput: "None", "sub", "core"
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

def openDialog(path="."):
    import Tkinter, tkFileDialog
    root = Tkinter.Tk()
    root.withdraw()

    file_path = tkFileDialog.askopenfilename(initialdir=path)
    root.destroy()
    return file_path


def openOpenMSExperiment(path):
    if not path.endswith(".mzML"):
        raise Exception("not a .mzML file")

    print "loading experiment"
    exp = pyopenms.MSExperiment()
    fh = pyopenms.FileHandler()
    fh.loadExperiment(path, exp)
    print "loading finnished"
    return exp

