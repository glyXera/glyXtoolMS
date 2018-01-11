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
    for mod in peptide.modifications:
        if mod.position != -1:
            x = set()
            x.add((mod.name, mod.position))
            modify.append(x)
        else:
            positions = set()
            for pos in mod.positions:
                positions.add((mod.name, pos))
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
    
class FragmentType(object):
    UNKNOWN=0
    IMMONIUMION=1
    OXONIUMION=2
    YION=3
    BION=4
    BYION=5
    GLYCANION=6
    ISOTOPE=7
    

class Fragment(object):
    
    def __init__(self, name, mass,typ=0, peak=None):
        self.name = name
        self.typ = typ
        self.mass = mass
        self.peak = peak
        
    


def generatePeptideFragments(peptide):

    sequence = peptide.sequence

    # assure that modifications are localized and have a known composition
    modifications = {}
    for mod in peptide.modifications:
        assert mod.position > -1
        assert mod.position not in modifications
        amino = peptide.sequence[mod.position]
        modifications[mod.position] = (mod.name, amino)
    
    # collect glycosylationsite positions
    glycosylationsSites = set()
    for site,typ in peptide.glycosylationSites:
        pos = site-peptide.start
        assert 0 <= pos < len(peptide.sequence)
        amino = peptide.sequence[pos]
        if typ == "N":
            assert amino == "N"
        elif typ == "O":
            assert amino == "S" or amino == "T"
        glycosylationsSites.add(pos)
    if len(glycosylationsSites) == 0:
        for pos, amino in enumerate(peptide.sequence):
            if amino in ["N", "s", "T"]:
                glycosylationsSites.add(pos)
    
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
        bHEXNAC = b + glyxtoolms.masses.COMPOSITION["HEXNAC"] - {"H":2, "O":1}

        if i < len(sequence)-1: # generate a,b and c ions
            key = str(i+1)
            data["b"+key] = (b.mass(), peptidestring, "b", 1)
            if len(glycosylationsSites) > 0 and min(glycosylationsSites) <= i:
                data["b"+key+"+HexNAc"] = (bHEXNAC.mass(), peptidestring+"+HexNac", "b", 1)
            
            if ("R" in sequence or
                "K" in sequence or
                "Q" in sequence or
                "N" in sequence):
                data["b"+key+"-NH3"] = (bNH3.mass(), peptidestring+"-NH3", "b", 1)
            if ("S" in sequence or
                "T" in sequence or
                sequence.startswith("E")):
                data["b"+key+"-H2O"] = (bH2O.mass(), peptidestring+"-H2O", "b", 1)

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

        yHEXNAC = y + glyxtoolms.masses.COMPOSITION["HEXNAC"] - {"H":2, "O":1}

        key = str(len(sequence)-i)

        if i > 0:
            data["y"+key] = (y.mass(), peptidestring, "y", 1)
            if len(glycosylationsSites) > 0 and max(glycosylationsSites) >= i:
                data["y"+key+"+HexNAc"] = (yHEXNAC.mass(), peptidestring+"+HexNac", "y", 1)
            if ("R" in sequence or
                "K" in sequence or
                "Q" in sequence or
                "N" in sequence):
                data["y"+key+"-NH3"] = (yNH3.mass(), peptidestring+"-NH3", "y", 1)
            if ("S" in sequence or
                "T" in sequence or
                sequence.startswith("E")):
                data["y"+key+"-H2O"] = (yH2O.mass(), peptidestring+"-H2O", "y", 1)

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
            data[key] = (by.mass(), peptidestring, "yb", 1)
            data[key+"-NH3"] = (byNH3.mass(), peptidestring+"-NH3", "yb", 1)
            data[key+"-H2O"] = (byH2O.mass(), peptidestring+"-H2O", "yb", 1)
            data[key+"-CO"] = (byCO.mass(), peptidestring+"-CO", "yb", 1)

    return data

def generateGlycanFragments(glycan):
    return

def annotateIdentification(hit, tolerance):
    
    # helper function to calculate charged ion masses
    def calcChargedMass(singlyChargedMass,charge):
        mass = singlyChargedMass+(charge-1)*glyxtoolms.masses.MASS["H"]
        return mass/float(charge)
    
    feature = hit.feature
    maxCharge = feature.getCharge()
    result = glyxtoolms.fragmentation.annotateSpectrumWithFragments(hit.peptide,
                                                                   hit.glycan,
                                                                   feature.consensus, 
                                                                   tolerance, 
                                                                   maxCharge)
    fragments = result["fragments"]
    
    
    # calc immonium ions
    immIons = {}
    for aminoacid in hit.peptide.sequence: # TODO: account for modifications
        comp = glyxtoolms.fragmentation.Composition() + glyxtoolms.masses.COMPOSITION[aminoacid]
        comp = comp + {"C":-1, "O":-2, "H":-1}
        immIons[aminoacid+"+"] = comp.mass()
        
    
    
    # create composition subsets according to glycan type
    comb = []
    keys = [key for key in hit.glycan.sugar.keys() if hit.glycan.sugar[key] > 0]
    for key in keys:
        comb.append(range(0,hit.glycan.sugar[key]+1))

    glycans = []

    for ii in itertools.product(*comb):
        g = glyxtoolms.lib.Glycan()
        composition = dict(zip(keys, ii))
        g.setComposition(**composition)
        glycans.append(g)
        #if isNGlycan == False or g.checkComposition() == True:
        #    glycans.append(g)

    glycanIons = {}
    pepIon = hit.peptide.mass+glyxtoolms.masses.MASS["H+"]
    for charge in range(1, maxCharge+1):
        for g in glycans:
            mass = calcChargedMass(pepIon+g.mass,charge)
            glycanIons[g.toString()+"("+str(charge)+"H+)"] = (mass,charge)
    

def annotateSpectrumWithFragments(peptide, glycan, spectrum, tolerance, maxCharge):

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
    
    for modificationset in glyxtoolms.fragmentation.getModificationVariants(peptide):
        pepvariant = peptide.copy()
        pepvariant.modifications = []
        for modname, pos in modificationset:
            pepvariant.addModification(modname,position=pos)
        
        fragments = glyxtoolms.fragmentation.generatePeptideFragments(pepvariant)
        # add peptide + HexNAc variants
        for charge in range(1, maxCharge):
            pepIonMass = calcChargedMass(pepIon,charge)
            pepGlcNAcIonMass = calcChargedMass(pepGlcNAcIon,charge)
            pepNH3Mass = calcChargedMass(pepNH3,charge)
            pep83Mass = calcChargedMass(pep83,charge)
            pepHexMass = calcChargedMass(pepHex,charge)
            pep2HexMass = calcChargedMass(pepHexHex,charge)
            
            chargeName = "("+str(charge)+"H+)"
            fragments["peptide"+chargeName] = (pepIonMass, peptide.sequence+chargeName, "pep", charge)
            fragments["peptide+N1"+chargeName] = (pepGlcNAcIonMass, peptide.sequence+"+HexNAC"+chargeName, "pep", charge)
            fragments["peptide-NH3"+chargeName] = (pepNH3Mass, peptide.sequence+"-NH3"+chargeName, "pep", charge)
            fragments["peptide+N(0.2X)"+chargeName] = (pep83Mass, peptide.sequence+"+HexNAC0.2X"+chargeName, "pep", charge)
            fragments["peptide+H1"+chargeName] = (pepHexMass, peptide.sequence+"+Hex"+chargeName, "pep", charge)
            fragments["peptide+H2"+chargeName] = (pep2HexMass, peptide.sequence+"+2Hex"+chargeName, "pep", charge)
        
        # search for the existence of each fragment within the spectrum
        found_fragments = {}
        for fragmentkey in fragments:
            try:
                fragmentmass, fragmentsequence, typ, charge = fragments[fragmentkey]
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
            fragment["type"] = typ
            fragment["peak"] = peak
            fragment["charge"] = charge
            found_fragments[fragmentkey] = fragment
        
        # check if peptide variant has highest fragment count
        if len(found_fragments) > len(bestVariant[1]):
            bestVariant = (pepvariant, found_fragments)
    
    return {"peptidevariant":bestVariant[0], "fragments":bestVariant[1]}
