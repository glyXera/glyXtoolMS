"""
Functions for generation of theoretical peptide fragments.
Uses a peptide and its modifications as input.
The function getModificationVariants(peptide) can be used to generate
alle modification variants if the position of a peptide is not known.

Usage:
p = glyxtoolms.io.XMLPeptide()
p.sequence = "DPTPLANCSVR"
p.modifications = [('Cys_CAM', 'C', -1)]

for modifications in getModificationVariants(p):
    pepvariant = glyxtoolms.io.XMLPeptide()
    pepvariant.sequence = p.sequence
    pepvariant.modifications = modifications
    fragments = generatePeptideFragments(pepvariant)

"""

import glyxtoolms
import itertools

class Composition(dict):

    def __add__(self, other):
        new = Composition()
        for key in self:
            new[key] = self[key]
        for key in other:
            new[key] = new.get(key, 0) + other[key]
        return new


    def __sub__(self, other):
        new = Composition()
        for key in self:
            new[key] = self[key]
        todelete = set()
        for key in other:
            new[key] = new.get(key, 0) - other[key]
            if new[key] == 0:
                todelete.add(key)
        # check if value is zero
        for key in todelete:
            new.pop(key)
        return new

    def __mul__(self, other):
        new = Composition()
        for key in self:
            new[key] = self[key]*other
        return new

    def toString(self):
        s = ""
        for key in sorted(self.keys()):
            if self[key] == 0:
                continue
            s += key + str(self[key])
        return s

    def mass(self):
        mass = 0
        for key in self:
            mass += glyxtoolms.masses.MASS[key] * self[key]
        return mass

def getModificationVariants(peptide):
    modify = []
    for mod, pos in peptide.modifications:
        if pos != -1:
            x = set()
            x.add((mod, pos))
            modify.append(x)
        else:
            # get possible target positions
            targets = glyxtoolms.masses.getModificationTargets(mod)
            positions = set()
            for pos, amino in enumerate(peptide.sequence):
                if amino in targets:
                    positions.add((mod, pos))
            if "NTERM" in targets:
                positions.add((mod, 0))
            if "CTERM" in targets:
                positions.add((mod, len(peptide.sequence)-1))
            modify.append(positions)

    def isValidPermutation(permutation):
        valid_list = set()
        for mod, pos in i:
            if pos in valid_list:
                return False
            valid_list.add(pos)
        return True

    final = set()
    for i in itertools.product(*modify):
        # check positions validity
        if isValidPermutation(i) == True:
            final.add(tuple(sorted(i)))
    return final


def generatePeptideFragments(peptide):

    sequence = peptide.sequence

    # assure that modifications are localized and have a known composition
    modifications = {}
    for mod, pos in peptide.modifications:
        assert pos > -1
        assert pos not in modifications
        amino = peptide.sequence[pos]
        modifications[pos] = (mod, amino)
    
    data = {}
    for i in range(0, len(sequence)):

        m = sequence[:i+1]
        n = sequence[i:]
        peptidestring = ""

        nterm = Composition() + {"H":2, "O":1}
        for index, acid in enumerate(m):
            pos = index
            peptidestring += acid
            nterm -= {"H":2, "O":1}
            nterm += glyxtoolms.masses.COMPOSITION[acid]
            if pos in modifications:
                mod, amino = modifications[pos]
                peptidestring += "("+mod+")"
                nterm += glyxtoolms.masses.getModificationComposition(mod)
        a = nterm - {"C":1, "H":1, "O":2}
        b = nterm - {"H":1, "O":1}
        c = nterm - {"O":1} + {"H":2, "N":1}

        aNH3 = a - {"N":1, "H":3}
        aH2O = a - {"O":1, "H":2}

        bNH3 = b - {"N":1, "H":3}
        bH2O = b - {"O":1, "H":2}
        bHEXNAC = b + glyxtoolms.masses.COMPOSITION["HEXNAC"]

        if i < len(sequence)-1: # generate a,b and c ions
            key = str(i+1)
            data["b"+key] = (b.mass(), peptidestring, "b")
            data["b"+key+"+HexNAc"] = (bHEXNAC.mass(), peptidestring+"+HexNac", "b")
            
            if ("R" in sequence or
                "K" in sequence or
                "Q" in sequence or
                "N" in sequence):
                data["b"+key+"-NH3"] = (bNH3.mass(), peptidestring+"-NH3", "b")
            if ("S" in sequence or
                "T" in sequence or
                sequence.startswith("E")):
                data["b"+key+"-H2O"] = (bH2O.mass(), peptidestring+"-H2O", "b")

        cTerm = Composition() + {"H":2, "O":1}
        peptidestring = ""
        for index, acid in enumerate(n):
            pos = index+i
            peptidestring += acid
            cTerm -= {"H":2, "O":1}
            cTerm += glyxtoolms.masses.COMPOSITION[acid]
            if pos in modifications:
                mod, amino = modifications[pos]
                peptidestring += "("+mod+")"
                cTerm += glyxtoolms.masses.getModificationComposition(mod)
        x = cTerm + {"C":1, "O":1} - {"H":1}
        y = cTerm + {"H":1}
        z = cTerm - {"H":2, "N":1}

        yNH3 = y - {"N":1, "H":3}
        yH2O = y - {"O":1, "H":2}

        yHEXNAC = y + glyxtoolms.masses.COMPOSITION["HEXNAC"]

        key = str(len(sequence)-i)

        if i > 0:
            data["y"+key] = (y.mass(), peptidestring, "y")
            data["y"+key+"+HexNAc"] = (yHEXNAC.mass(), peptidestring+"+HexNac", "y")
            if ("R" in sequence or
                "K" in sequence or
                "Q" in sequence or
                "N" in sequence):
                data["y"+key+"-NH3"] = (yNH3.mass(), peptidestring+"-NH3", "y")
            if ("S" in sequence or
                "T" in sequence or
                sequence.startswith("E")):
                data["y"+key+"-H2O"] = (yH2O.mass(), peptidestring+"-H2O", "y")

    # calc internal fragments
    for i in range(1, len(sequence)):
        for e in range(i+1, len(sequence)):
            m = sequence[i:e]

            nterm = Composition() + {"H":2, "O":1}
            mod = 0
            peptidestring = ""
            for index, acid in enumerate(m):
                pos = index+i
                peptidestring += acid
                nterm -= {"H":2, "O":1}
                nterm += glyxtoolms.masses.COMPOSITION[acid]
                if pos in modifications:
                    mod, amino = modifications[pos]
                    assert acid == amino
                    peptidestring += "("+mod+")"
                    nterm += glyxtoolms.masses.getModificationComposition(mod)
            by = nterm - {"O":1, "H":1}
            byNH3 = by - {"N":1, "H":3}
            byH2O = by - {"O":1, "H":2}
            byCO = by - {"C":1, "O":1}

            key = "y"+str(len(sequence)-i)+"b"+str(e)
            data[key] = (by.mass(), peptidestring, "yb")
            data[key+"-NH3"] = (byNH3.mass(), peptidestring+"-NH3", "yb")
            data[key+"-H2O"] = (byH2O.mass(), peptidestring+"-H2O", "yb")
            data[key+"-CO"] = (byCO.mass(), peptidestring+"-CO", "yb")

    return data


def annotateSpectrumWithFragments(peptide, spectrum, tolerance, maxCharge):

    # helper function to search masses in a spectrum
    def searchMassInSpectrum(mass,tolerance,spectrum):
        hits = []
        for peak in spectrum:
            if abs(peak.x - mass) < tolerance:
                hits.append(peak)
        if len(hits) == 0:
            return None
        return max(hits, key=lambda p:p.y)
    
    # helper function to calculate charged ion masses
    def calcChargedMass(singlyChargedMass,charge):
        mass = singlyChargedMass+(charge-1)*glyxtoolms.masses.MASS["H"]
        return mass/float(charge)
    
    # calculate peptide mass
    pepIon = peptide.mass+glyxtoolms.masses.MASS["H+"]
    pepGlcNAcIon = pepIon+glyxtoolms.masses.GLYCAN["HEXNAC"]
    pepNH3 = pepIon-glyxtoolms.masses.MASS["N"] - 3*glyxtoolms.masses.MASS["H"]
    pep83 = pepIon + glyxtoolms.masses.calcMassFromElements({"C":4, "H":5, "N":1, "O":1})
    pepHex = pepIon+glyxtoolms.masses.GLYCAN["HEX"]
    pepHexHex = pepIon+glyxtoolms.masses.GLYCAN["HEX"]*2
    
    # determine all peptide modification variants
    bestVariant = (None, {})
    
    for i in glyxtoolms.fragmentation.getModificationVariants(peptide):
        pepvariant = peptide.copy()
        pepvariant.modifications = i
        fragments = glyxtoolms.fragmentation.generatePeptideFragments(pepvariant)
        # add peptide + HexNAc variants
        for charge in range(1, maxCharge):
            pepIonMass = calcChargedMass(pepIon,charge)
            pepGlcNAcIonMass = calcChargedMass(pepGlcNAcIon,charge)
            pepNH3Mass = calcChargedMass(pepNH3,charge)
            pep83Mass = calcChargedMass(pep83,charge)
            pepHexMass = calcChargedMass(pepHex,charge)
            pep2HexMass = calcChargedMass(pepHexHex,charge)
            
            chargeName = "+("+str(charge)+"H+)"
            fragments["peptide"+chargeName] = (pepIonMass, peptide.sequence+chargeName, "pep")
            fragments["peptide+HexNAc"+chargeName] = (pepGlcNAcIonMass, peptide.sequence+"+HexNAC"+chargeName, "pep")
            fragments["peptide-NH3"+chargeName] = (pepNH3Mass, peptide.sequence+"-NH3"+chargeName, "pep")
            fragments["peptide+HexNAC0.2X"+chargeName] = (pep83Mass, peptide.sequence+"+HexNAC0.2X"+chargeName, "pep")
            fragments["peptide+Hex"+chargeName] = (pepHexMass, peptide.sequence+"+Hex"+chargeName, "pep")
            fragments["peptide+2Hex"+chargeName] = (pep2HexMass, peptide.sequence+"+2Hex"+chargeName, "pep")
        
        # search for the existence of each fragment within the spectrum
        found_fragments = {}
        for fragmentkey in fragments:
            try:
                fragmentmass, fragmentsequence, typ = fragments[fragmentkey]
            except:
                print fragmentkey
                raise
            # search highest peak within tolerance
            peak = searchMassInSpectrum(fragmentmass, tolerance, spectrum)
            if peak == None:
                continue
            fragment = {}
            fragment["mass"] = fragmentmass
            fragment["sequence"] = fragmentsequence
            fragment["counts"] = peak.y
            fragment["typ"] = typ
            found_fragments[fragmentkey] = fragment
        
        # check if peptide variant has highest fragment count
        if len(found_fragments) > len(bestVariant[1]):
            bestVariant = (pepvariant, found_fragments)
    
    return {"peptidevariant":bestVariant[0], "fragments":bestVariant[1]}
