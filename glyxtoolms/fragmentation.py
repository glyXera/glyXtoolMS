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
        for mod, pos in permutation:
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
    UNKNOWN = "UNKNOWN"
    ISOTOPE = "ISOTOPE"
    IMMONIUMION = "IMMONIUMION"
    OXONIUMION = "OXONIUMION"
    YION = "YION"
    BION = "BION"
    BYION = "BYION"
    PEPTIDEION = "PEPTIDEION"
    GLYCOPEPTIDEION = "GLYCOPEPTIDEION"
    _colors = {"UNKNOWN":"black",
               "ISOTOPE":"yellow",
               "IMMONIUMION":"violet",
               "OXONIUMION":"red",
               "YION":"blue",
               "BION":"blue",
               "BYION":"blue",
               "PEPTIDEION":"orange",
               "GLYCOPEPTIDEION":"green"
              }

    def getColor(self, name):
        return self._colors.get(name, "black")

class FragmentList(dict):
    def __add__(self, fragment):
        self[fragment.name] = fragment
        return self



class Fragment(object):

    def __init__(self, name, mass, charge, typ=FragmentType.UNKNOWN, peak=None, parents=set([])):
        self.name = name
        self.typ = typ
        self.mass = mass
        self.peak = peak
        self.charge = charge
        self.parents = set(parents) # Link to parent fragments name, if available


def generatePeptideFragments(peptide):

    sequence = peptide.sequence

    # assure that modifications are localized and have a known composition
    modifications = {}
    for mod in peptide.modifications:
        assert mod.position > -1
        assert mod.position not in modifications
        amino = peptide.sequence[mod.position]
        modifications[mod.position] = (mod.name, amino)

    data = FragmentList()
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
            data += Fragment("b"+key, b.mass(), 1, typ=FragmentType.BION)
            if ("R" in sequence or
                    "K" in sequence or
                    "Q" in sequence or
                    "N" in sequence):
                data += Fragment("b"+key+"-NH3", bNH3.mass(),1, typ=FragmentType.BION)
            if ("S" in sequence or
                    "T" in sequence or
                    sequence.startswith("E")):
                data += Fragment("b"+key+"-H2O", bH2O.mass(), 1, typ=FragmentType.BION)

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
            data += Fragment("y"+key, y.mass(), 1, typ=FragmentType.YION)
            if ("R" in sequence or
                    "K" in sequence or
                    "Q" in sequence or
                    "N" in sequence):
                data += Fragment("y"+key+"-NH3", yNH3.mass(), 1, typ=FragmentType.YION)
            if ("S" in sequence or
                    "T" in sequence or
                    sequence.startswith("E")):
                data += Fragment("y"+key+"-H2O", yH2O.mass(), 1, typ=FragmentType.YION)

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
            data += Fragment(key, by.mass(), 1, typ=FragmentType.BYION)
            data += Fragment(key+"-NH3", byNH3.mass(), 1, typ=FragmentType.BYION)
            data += Fragment(key+"-H2O", byH2O.mass(), 1, typ=FragmentType.BYION)
            data += Fragment(key+"-CO", byCO.mass(), 1, typ=FragmentType.BYION)

    return data

def annotateSpectrumWithFragments(peptide, glycan, spectrum, tolerance, toleranceType, maxCharge):

    # helper function to search masses in a spectrum
    def searchMassInSpectrum(mass, tolerance, toleranceType, spectrum):

        hit = (0,None)
        for peak in spectrum:
            error = abs(glyxtoolms.lib.calcMassError(peak.x, mass, toleranceType))
            if error <= tolerance:
                if hit[1] == None or error < hit[0]:
                    hit = (error,peak)
        return hit[1]

    # helper function to calculate charged ion masses
    def calcChargedMass(singlyChargedMass, charge):
        mass = singlyChargedMass+(charge-1)*glyxtoolms.masses.MASS["H"]
        return mass/float(charge)

    # helper masses
    mH2O = glyxtoolms.masses.calcMassFromElements({"H":2, "O":1})
    mNH3 = glyxtoolms.masses.calcMassFromElements({"N":1, "H":3})
    mCO = glyxtoolms.masses.calcMassFromElements({"C":1, "O":1})
    mCH2O = glyxtoolms.masses.calcMassFromElements({"C":1, "H": 2, "O":1})
    mCH2CO = glyxtoolms.masses.calcMassFromElements({"C":2, "H": 2, "O":1})
    mNx = glyxtoolms.masses.calcMassFromElements({"C":4, "H":5, "N":1, "O":1})
    mCHOCH3 = glyxtoolms.masses.calcMassFromElements({"C":2, "H":4, "O":1})

    # calculate peptide mass
    pepIon = peptide.mass+glyxtoolms.masses.MASS["H+"]
    pepGlcNAcIon = pepIon+glyxtoolms.masses.GLYCAN["HEXNAC"]
    pepNH3 = pepIon - mNH3
    pep83 = pepIon + mNx
    pepH2O = pepIon + mH2O
    pepHex = pepIon+glyxtoolms.masses.GLYCAN["HEX"]
    pepHexHex = pepIon+glyxtoolms.masses.GLYCAN["HEX"]*2


    # calculate immonium ions
    immoniumIons = {}
    for pos, aminoacid in enumerate(peptide.sequence): # TODO: account for modifications
        comp = glyxtoolms.fragmentation.Composition() + glyxtoolms.masses.COMPOSITION[aminoacid]
        comp = comp + {"C":-1, "O":-2, "H":-1}
        immoniumIons[aminoacid+"+"] = Fragment(aminoacid+"+", comp.mass(), 1, FragmentType.IMMONIUMION)

    # create composition subsets according to glycan type
    comb = []
    keys = [key for key in glycan.sugar.keys() if glycan.sugar[key] > 0]
    for key in keys:
        comb.append(range(0, glycan.sugar[key]+1))

    glycans = []
    for ii in itertools.product(*comb):
        g = glyxtoolms.lib.Glycan()
        composition = dict(zip(keys, ii))
        g.setComposition(**composition)
        if g.mass == 0.0:
            continue
        glycans.append(g)

    # collect glycosylationsite positions
    glycosylationsSites = set()
    for site, typ in peptide.glycosylationSites:
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

    # determine all peptide modification variants
    bestVariant = (None, {})

    for modificationset in glyxtoolms.fragmentation.getModificationVariants(peptide):
        pepvariant = peptide.copy()
        pepvariant.modifications = []
        for modname, pos in modificationset:
            pepvariant.addModification(modname, position=pos)

        fragments = glyxtoolms.fragmentation.generatePeptideFragments(pepvariant)

        # add immonium ions
        for key in immoniumIons:
            fragments += immoniumIons[key]

        # add oxoniumIons
        for g in glycans:
            ox = Fragment(g.toString()+"(+)", g.mass+glyxtoolms.masses.MASS["H+"], 1, FragmentType.OXONIUMION)
            fragments += ox
            oxH2O = Fragment(g.toString()+"-H2O(+)", ox.mass - mH2O, 1, FragmentType.OXONIUMION, parents={ox.name})
            fragments += oxH2O

            fragments += Fragment(g.toString()+"-2*H2O(+)", oxH2O.mass - mH2O, 1, FragmentType.OXONIUMION, parents={oxH2O.name})
            fragments += Fragment(g.toString()+"-3*H2O(+)", oxH2O.mass - 2*mH2O, 1, FragmentType.OXONIUMION, parents={oxH2O.name})
            fragments += Fragment(g.toString()+"-CH3COOH(+)", oxH2O.mass - mCH2CO, 1, FragmentType.OXONIUMION, parents={oxH2O.name})
            fragments += Fragment(g.toString()+"-H2OCH2OH2O(+)", oxH2O.mass - mCH2O - mH2O, 1, FragmentType.OXONIUMION, parents={oxH2O.name})
            fragments += Fragment(g.toString()+"-H2OCH2COH2O(+)", oxH2O.mass - mCH2CO - mH2O, 1, FragmentType.OXONIUMION, parents={oxH2O.name})



        # add peptide and glycopeptide ions
        for charge in range(1, maxCharge+1):
            pepIonMass = calcChargedMass(pepIon, charge)
            pepNH3Mass = calcChargedMass(pepNH3, charge)
            pepH2OMass = calcChargedMass(pepH2O, charge)
            pep83Mass = calcChargedMass(pep83, charge)

            chargeName = "("+str(charge)+"H+)"
            fragments += Fragment("peptide"+chargeName, pepIonMass, charge, FragmentType.PEPTIDEION)
            fragments += Fragment("peptide-NH3"+chargeName, pepNH3Mass, charge, FragmentType.PEPTIDEION)
            fragments += Fragment("peptide-H2O"+chargeName, pepH2OMass, charge, FragmentType.PEPTIDEION)
            fragments += Fragment("peptide+N(0.2X)"+chargeName, pep83Mass, charge, FragmentType.GLYCOPEPTIDEION)
            fragments += Fragment("peptide+N(0.2X)-H2O"+chargeName, pep83Mass-mH2O, charge, FragmentType.GLYCOPEPTIDEION)

            # add glycan fragments
            for g in glycans:
                if g.hasNCorePart() == False:
                    continue
                mass = calcChargedMass(pepIon+g.mass, charge)
                massH2O = calcChargedMass(pepIon+g.mass-mH2O, charge)
                mass2xH2O = calcChargedMass(pepIon+g.mass-2*mH2O, charge)
                massCHOCH3 = calcChargedMass(pepIon+g.mass-mCHOCH3, charge)
                fragments += Fragment("peptide+"+g.toString()+"("+str(charge)+"H+)", mass, charge, FragmentType.GLYCOPEPTIDEION)
                fragments += Fragment("peptide+"+g.toString()+"-H2O"+"("+str(charge)+"H+)", massH2O, charge, FragmentType.GLYCOPEPTIDEION)
                fragments += Fragment("peptide+"+g.toString()+"-2xH2O"+"("+str(charge)+"H+)", mass2xH2O, charge, FragmentType.GLYCOPEPTIDEION)
                fragments += Fragment("peptide+"+g.toString()+"-CHOCH3"+"("+str(charge)+"H+)", massCHOCH3, charge, FragmentType.GLYCOPEPTIDEION)

        # add peptide fragments with attached glycans
        lenSeq = len(peptide.sequence)
        if len(glycosylationsSites) > 0:
            minSite = min(glycosylationsSites)
            maxSite = max(glycosylationsSites)
            for i in range(1, maxSite+1):
                y = lenSeq-i
                for b in range(i+1, lenSeq+1):
                    if b < minSite:
                        continue
                    if y == 1:
                        key = "b"+str(b)
                        typ = FragmentType.BION
                    elif b == lenSeq:
                        key = "y"+str(y)
                        typ = FragmentType.YION
                    else:
                        key = "y"+str(y)+"b"+str(b)
                        typ = FragmentType.BYION

                    ion = fragments.get(key, None)
                    if ion == None:
                        continue

                    for g in glycans:
                        if g.hasNCorePart() == False:
                            continue
                        fragments += Fragment(ion.name+"+"+g.toString(), ion.mass + g.mass,1, typ)
                        fragments += Fragment(ion.name+"+"+g.toString()+"-H2O", ion.mass + g.mass - mH2O, 1, typ, parents={ion.name})

        # search for the existence of each fragment within the spectrum
        found_fragments = {}
        for fragmentname in fragments:
            fragment = fragments[fragmentname]
            # search highest peak within tolerance
            peak = searchMassInSpectrum(fragment.mass, tolerance, toleranceType, spectrum)
            if peak == None:
                continue
            fragment.peak = peak
            found_fragments[fragmentname] = fragment



        # add isotopes
        for key in found_fragments.keys():
            fragment = found_fragments[key]
            for i in range(1, 4):
                mz = fragment.mass + i/float(fragment.charge)
                peak = searchMassInSpectrum(mz, tolerance, toleranceType, spectrum)
                if peak == None:
                    break
                isotope = Fragment(fragment.name + "/"+str(i), mz, fragment.charge, FragmentType.ISOTOPE, peak=peak, parents={fragment.name})
                found_fragments[isotope.name] = isotope

        # check if peptide variant has highest fragment count
        # TODO: Better variant scoring?
        if len(found_fragments) > len(bestVariant[1]):
            bestVariant = (pepvariant, found_fragments)

    return {"peptidevariant":bestVariant[0], "fragments":bestVariant[1], "all": fragments}
