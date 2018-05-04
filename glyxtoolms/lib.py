import re
from itertools import product
import copy
import glyxtoolms
import pyopenms
import numpy as np

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
        bars = {}
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
                bars[label] = bar
            else:
                raise Exception("Please provide a plot axis, eg 'axis=plt'")
        return bars


# ---------------------------- Protein Digest -------------------------------------

class Protein(object):

    def __init__(self,identifier="", description="", sequence=""):
        self.identifier = identifier
        self.description = description
        self.sequence = sequence
        self.modifications = []


    def loadFromFasta(self, fasta):
        self.identifier = fasta.identifier
        self.description = fasta.description
        self.modifications = []
        diff = 0
        for x in re.finditer(r"\(.+?\)", fasta.sequence):
            name = x.group()[1:-1]
            pos = x.start()-diff-1
            self.modifications.append((name, fasta.sequence[pos], pos))
            diff += x.end()-x.start()
        self.sequence = re.sub(r"\(.+?\)", "", fasta.sequence)
        # check aminoacids and modifications
        try:
            #for s in self.sequence:
            #    assert s in glyxtoolms.masses.AMINOACID
            for name, amino, pos in self.modifications:
                assert name in glyxtoolms.masses.PROTEINMODIFICATION
        except KeyError:
            print "Error in protein ", identifier
            raise

    def getPeptide(self, start, end):
        peptide = glyxtoolms.io.XMLPeptide()
        peptide.sequence = self.sequence[start:end]
        peptide.start = start
        peptide.end = end
        peptide.proteinID = self.identifier
        for modname, amino, pos in self.modifications:
            if start <= pos and pos < end:
                peptide.addModification(modname, position=pos)
        return peptide

class Glycopeptide:

    def __init__(self,peptidesequence, glycancomposition, modifications=list()):
        """
        peptidesequence, glycancomposition, peptidemodifications
        modifications as list with (modificationname, aminoacid, position)
        """
        # generate peptide
        self.peptide = glyxtoolms.io.XMLPeptide()
        for s in peptidesequence:
            assert s in glyxtoolms.masses.AMINOACID
        self.peptide.sequence = peptidesequence

        # add modifications
        for name, amino, pos in modifications:
            assert name in glyxtoolms.masses.PROTEINMODIFICATION
            assert amino == self.peptide.sequence[pos]
            self.peptide.addModification(name, position=pos)
        self.peptide.mass = glyxtoolms.masses.calcPeptideMass(self.peptide)
        # generate glycan
        self.glycan = glyxtoolms.lib.Glycan(glycancomposition)

    def calcIonMass(self, charge):
        # TODO: Extend for Sodium and Potassium
        if charge < 1:
            return self.peptide.mass + self.glycan.mass
        else:
            return (self.peptide.mass + self.glycan.mass + charge*glyxtoolms.masses.MASS["H+"]) / float(charge)


class ProteinDigest(object):

    def __init__(self, maxModifications=-1, maxMissedCleavage=0):
        
        self.maxModifications = maxModifications
        self.maxMissedCleavage = maxMissedCleavage
        self.modifications = set()
        self.enzymes = set()
        
        self.breakpoints = []
        self.protein = None


    def setMaxModifications(self, maxMod):
        self.maxModifications = maxMod

    def setMaxMissedCleavage(self, maxCleav):
        self.maxMissedCleavage = maxCleav

    def addModification(self, modname):
        assert modname in glyxtoolms.masses.PROTEINMODIFICATION
        assert len(glyxtoolms.masses.PROTEINMODIFICATION[modname].get("targets", [])) > 0
        self.modifications.add(modname)

    def calcPeptideMasses(self, peptide):

        def checkPeptideValidity(Y, Y_names, target):
            Y = Y.copy()
            Ycopy = Y.copy()

            isValid = True
            for i in range(0,len(Y)):
                name = Y_names[i]
                amount = target[name]
                maxAmount = Y[i,i]
                if amount > maxAmount:
                    isValid = False
                Y[i,i] = amount
                for e in range(i+1,len(Y)):
                    overlap = Y[i,e]
                    free = maxAmount - overlap
                    # check if overlap is consumed
                    if amount <= free:
                        continue
                    # overlap is consumed, propagate forward
                    for j in range(i, len(Y)):
                        if Ycopy[j,e] == 0:
                            continue
                        Y[j,e] = Y[j,e] - overlap
                        if Y[j,e] < 0:
                            isValid = False
            return isValid
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

        # calc modification data
        data = {}
        for i,amino in enumerate(sequence):
            possible = set()
            for modname in self.modifications:
                mod = glyxtoolms.masses.PROTEINMODIFICATION[modname]
                for target in mod["targets"]:
                    if i == 0 and target == "NTERM":
                        possible.add(modname)
                    elif i == len(sequence)-1 and target == "CTERM":
                        possible.add(modname)
                    elif amino == target:
                        possible.add(modname)
            if len(possible) > 0:
                data[i] = possible

        # remove already modified sites
        for mod in peptide.modifications:
            if mod.position == -1:
                continue
            if mod.position in data:
                data.pop(mod.position)

        # generate matrix
        keys = sorted(data.keys())
        mods = set()
        for key in data:
            for mod in data[key]:
                mods.add(mod)

        mods = sorted(mods)

        matrix = []
        for mod in mods:
            line = []
            for key in keys:
                if mod in data[key]:
                    line.append(1)
                else:
                    line.append(0)
            matrix.append(line)

        A = np.matrix(matrix)
        AA_T = np.dot(A,A.T)

        # decompose matrix into independent and dependent matrices

        independent = []
        s = len(AA_T)

        for i in range(0,s):
            isIndependent = True
            for e in range(0,s):
                if i != e and AA_T[i,e] != 0:
                    isIndependent = False
                    break
            if isIndependent == True:
                independent.append(i)

        # extract linear dependent matrix
        Y = np.delete(AA_T, independent, axis=0)
        Y = np.delete(Y, independent, axis=1)
        names = np.array(mods)
        Y_names = np.delete(names, independent, axis=0)

        # create permutation matrix of each modification
        perm = []
        diag = AA_T.diagonal()
        for i in range(0,diag.size):
            N_mod = diag[0,i]
            if self.maxModifications > -1 and N_mod > self.maxModifications:
                N_mod = self.maxModifications
            perm.append(range(0,int(N_mod)+1))

        masses = []
        for ii in product(*perm):
            isValid = True
            target = {}
            N_mods = 0
            for amount, name in zip(ii, mods):
                target[name] = amount
                if name != "CYS_CAM" and name != "CYS_CM":
                    N_mods += amount
            # check if more modifications are on than allowed
            if self.maxModifications > -1 and N_mods > self.maxModifications:
                continue

            # check dependent targets
            isValid = checkPeptideValidity(Y, Y_names, target)
            if isValid == False:
                continue

            # create new peptide
            newPeptide = copy.deepcopy(peptide)
            for modname in target:
                amount = target[modname]
                if amount == 0:
                    continue
                for i in range(0,target[modname]):
                    newPeptide.addModification(modname)

            # solve modifications as much as possible
            try:
                newPeptide.solveModifications()

            except:
                print newPeptide.toString()
                raise

            # calc peptide mass
            newPeptide.mass = glyxtoolms.masses.calcPeptideMass(newPeptide)
            masses.append(newPeptide)

        return masses
        
    def addEnzyme_Trypsin(self):
        self.enzymes.add(self._add_tryptic_digest)
    
    def addEnzyme_Trypsin_lowSpecific(self):
        self.enzymes.add(self._add_tryptic_low_specific_digest)
    
    def addEnzyme_AspN(self):
        self.enzymes.add(self._add_AspN_digest)
        
    def addEnzyme_AspN2(self):
        self.enzymes.add(self._add_AspN_digest_2)
        
    def addEnzyme_ProtK(self):
        self.enzymes.add(self._add_ProtinaseK_digest)
        
    def addEnzyme_Unspecific(self):
        self.enzymes.add(self._add_Unspecific_digest)

    def _add_tryptic_digest(self):
        # cleaves C-terminal side of K or R, except if P is C-term to K or R
        i = 0
        while i < len(self.protein.sequence):
            if self.protein.sequence[i] == "R" or self.protein.sequence[i] == "K":
                if not (i+1 < len(self.protein.sequence) and self.protein.sequence[i+1] == "P"):
                    self.breakpoints.append(i)
            i += 1

    def _add_tryptic_low_specific_digest(self):
        # cleaves C-terminal side of K or R, even if P is C-term to K or R
        i = 0
        while i < len(self.protein.sequence):
            if self.protein.sequence[i] == "R" or self.protein.sequence[i] == "K":
                    self.breakpoints.append(i)
            i += 1


    def _add_AspN_digest(self):
        # cleaves N-terminal side of D
        i = 1
        while i < len(self.protein.sequence):
            if self.protein.sequence[i] == "D":
                self.breakpoints.append(i-1)
            i += 1

    def _add_AspN_digest_2(self):
        # cleaves N-terminal side of E, D and C
        i = 1
        while i < len(self.protein.sequence):
            if self.protein.sequence[i] in ["E", "D", "C"]:
                self.breakpoints.append(i-1)
            i += 1

    def _add_ProtinaseK_digest(self):
        # cleaves D-terminal side of multiple aminoacids
        i = 1
        while i < len(self.protein.sequence):

            if self.protein.sequence[i] in ["A", "F", "Y", "W", "L", "I", "V"]:
                self.breakpoints.append(i)
            i += 1

    def _add_Unspecific_digest(self):
        # cleaves all possible aminoacids
        for i in range(0, len(self.protein.sequence)):
            self.breakpoints.append(i)

    def digest(self, protein):
        self.protein = protein
        self.breakpoints = []
        
        # run enzyme breakpoint functions
        for func in self.enzymes:
            func()
        
        self.breakpoints.append(len(self.protein.sequence)-1)
        # clean up breakpoints
        self.breakpoints = list(set(self.breakpoints))
        self.breakpoints.sort()

        peptides = []
        start = -1
        i = 0
        while i < len(self.breakpoints):
            for m in range(0, self.maxMissedCleavage+1):
                if i+m >= len(self.breakpoints):
                    break
                stop = self.breakpoints[i+m]
                p = self.protein.getPeptide(start+1, stop+1)
                peptides.append(p)
            start = self.breakpoints[i]
            i += 1
        return peptides

    def findGlycopeptides(self, peptides, NGlycosylation=False,
                          OGlycosylation=False, NCGlycosylation=False):

        # generate list of glycosylationsites
        sitesType = {}
        sites = []
        if NGlycosylation == True:
            for match in re.finditer(r"(?=(N[^P](S|T)))", self.protein.sequence):
                sites.append((match.start(), "N"))
        if OGlycosylation == True:
            for match in re.finditer(r"(?=(S|T))", self.protein.sequence):
                sites.append((match.start(), "O"))
        if NCGlycosylation == True:
            for match in re.finditer(r"(?=(N[^P]C))", self.protein.sequence):
                sites.append((match.start(), "N"))
        sites.sort()
        for pos, typ in sites:
            sitesType[typ] = sitesType.get(typ, 0) +1

        glycopeptides = []
        # b) search peptides with possible glycosylation site
        aminoacids = set(glyxtoolms.masses.AMINOACID.keys())
        for peptide in peptides:
            glycopeptide = False
            for site, typ in sites:
                if peptide.start <= site and site < peptide.end:
                    peptide.glycosylationSites.append((site, typ))
                    glycopeptide = True
            if glycopeptide == True:
                # check if unknown aminoacids are within peptide sequence
                pepAminoAcids = set(peptide.sequence)
                if len(pepAminoAcids.difference(aminoacids)) > 0:
                    continue
                glycopeptides += self.calcPeptideMasses(peptide)

        return glycopeptides

# --------------------------------------- Glycan -----------------------
letterCode = {

"M": "HEX",     # Mannose
"G": "HEX",     # Galactose
"H": "HEX",     # Hex
"Hex": "HEX",     # Hex
"HEX": "HEX",     # Hex
"AG": "HEX",    # alpha-Gal

"HEXNAC":"HEXNAC", #Hexnac
"HexNAc":"HEXNAC", #Hexnac
"N": "HEXNAC",  # Hexnac
"HN": "HEXNAC", # Hexnac
"GC": "HEX",    # Glucose
"GN":"HEXNAC",  # GlcNAc
"AN": "HEXNAC", # GalNAc

"DHEX": "DHEX",    # Fucose
"F": "DHEX",    # Fucose
"Fuc": "DHEX",    # Fucose

"NA": "NEUAC",  # NeuAc
"NANA": "NEUAC",  # NeuAc
"NeuAc": "NEUAC",  # NeuAc
"Sa": "NEUAC",  # NeuAc

"NEUGC": "NEUGC",  # NeuGc
"NG": "NEUGC",  # NeuGc
"NeuGc": "NEUGC",  # NeuGc
"Sg": "NEUGC"  # NeuGc
}

msComposition = {
"HEXNAC": "HexNAc",
"HEX": "Hex",
"DHEX": "Fuc",
"NEUAC": "NeuAc",
"NEUGC": "NeuGc"
}

msCompositionOrder = [
"HEXNAC",
"HEX",
"DHEX",
"NEUAC",
"NEUGC"
]

class Glycan(glyxtoolms.io.XMLGlycan):

    def __init__(self, composition=None, typ="?"):
        super(Glycan, self).__init__()
        self.composition = ""
        self.typ = typ
        self.glycosylationSite = None
        self.linearCode = ""
        self.structure = None
        self.sugar = {'DHEX': 0, 'HEX': 0, 'HEXNAC': 0, 'NEUAC': 0, 'NEUGC':0}
        self.mass = 0
        if composition is not None:
            self._splitComposition(composition)

    def setComposition(self, NEUAC=0, NEUGC=0, DHEX=0, HEX=0, HEXNAC=0):

        self.sugar["NEUGC"] = NEUGC
        self.sugar["NEUAC"] = NEUAC
        self.sugar["DHEX"] = DHEX
        self.sugar["HEX"] = HEX
        self.sugar["HEXNAC"] = HEXNAC

        self.mass = 0
        for unit in self.sugar:
            self.mass += glyxtoolms.masses.GLYCAN[unit]*self.sugar[unit]
        self.composition = ""
        for unit in msCompositionOrder:
            amount = self.sugar.get(unit, 0)
            if amount == 0:
                continue
            self.composition += msComposition[unit]+str(amount)

    def checkComposition(self):
        HEX = self.sugar["HEX"]
        HEXNAC = self.sugar["HEXNAC"]
        DHEX = self.sugar["DHEX"]
        NEUAC = self.sugar["NEUAC"]
        NEUGC = self.sugar["NEUGC"]


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
        if HEXNAC <= 2 and HEX > 2 and NEUGC > 0:
            return False
        return True

    def _splitComposition(self, composition):
        """
        Split composition using possible glycan names
        """
        try:
            assert re.match('^([A-z]+\d+)+$', composition) != None
        except:
            raise Exception("Cannot parse composition '"+composition+"'!")
        self.mass = 0
        for comp in re.findall(r"[A-z]+\d+", composition):
            name = re.search(r"[A-z]+", comp).group()
            if name in letterCode:
                unit = letterCode[name]
            else:
                raise Exception("Unknown modification "+ name)
            amount = int(re.search(r"\d+", comp).group())
            self.sugar[unit] = amount
            self.mass += glyxtoolms.masses.GLYCAN[unit]*amount
        self.composition = self.toString()

    def getComposition(self, typ="N"):
        comp = self.sugar.copy()
        if typ == "N" and self.hasNCore() == True:
            comp["HEX"] -= 3
            comp["HEXNAC"] -= 2
            composition = "(GlcNAc)2 (Man)3 + "
        else:
            composition = ""

        for sugar in ["DHEX", "HEX", "HEXNAC", "NEUAC"]:
            if comp[sugar] > 0:
                composition += sugar+str(comp[sugar])
        return composition

    def toString(self):
        result = ""
        for name in msCompositionOrder:
            amount = self.sugar[name]
            if amount == 0:
                continue
            result += msComposition[name] + str(amount)
        return result


    def hasNCore(self):
        """ Checks if the composition contains 2 HexNac and 3 Hexose to build N-Glycan core """
        hexnac = self.sugar["HEXNAC"]
        hexose = self.sugar["HEX"]
        if hexnac >= 2 and hexose >= 3:
            return True
        return False

    def hasNCorePart(self):
        """ Checks if the composition has at least the N-Core Part """
        N = self.sugar["HEXNAC"]
        H = self.sugar["HEX"]

        if N < 1:
            return False
        if H > 0 and N < 2:
            return False
        if N > 2 and H < 2:
            return False
        return True

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

def calcMassError(mass, nominalMass, toleranceType):
    if toleranceType == "Da":
        error = nominalMass - mass
    elif toleranceType == "ppm":
        error = (nominalMass - mass) / float(nominalMass) *1E6
    else:
        raise Exception("Please provide a toleranceType in either 'Da' or 'ppm'!")
    return error

def isInMassTolerance(mass, nominalMass, tolerance, toleranceType, bound="both"):
    """ Calculate Mass error between two masses, toleranceType="Da" or "ppm", 
    side is if only the upper bound or lower bound or both should be tested """
    
    error = calcMassError(mass, nominalMass, toleranceType)
    if bound == "both":
        answer = abs(error) <= tolerance
    elif bound == "lower":
        answer = error <= tolerance
    elif bound == "upper":
        answer = error >= -tolerance
    else:
        raise Exception("Please provide a tolerance bound of either 'lower', 'upper' or 'both'!")
    return answer
