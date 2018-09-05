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
    fragments = generatePeptideFragments(pepvariant, maxCharge)

"""

import glyxtoolms
import itertools
import re

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

def getModificationVariants(peptide,glycantyp={"N":1,"O":0},check=False):
    # collect glycosylation sites
    N = set()
    O = set()
    for pos,typ in peptide.glycosylationSites:
        if typ == "N":
            N.add(("N",pos-peptide.start))
        elif typ == "O":
            O.add(("O",pos-peptide.start))
    # check if still valid
    if glycantyp["N"] > len(N):
        return set()
    
    if glycantyp["O"] > len(O):
        return set()
    
    modify = []
    # add glycosylation sites
    for i in range(0,glycantyp["N"]):
        modify.append(N)
    for i in range(0,glycantyp["O"]):
        modify.append(O)

    
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
            if check == True:
                return True
    if check == True:
        if len(final) == 0:
            return False
    # generate variants
    variants = set()
    for modificationset in final:
        pepvariant = peptide.copy()
        pepvariant.modifications = []
        pepvariant.glycosylationSites = []
        for modname, pos in modificationset:
            if modname in ["N","O"]:
                pepvariant.glycosylationSites.append((pos+peptide.start,modname))
            else:
                pepvariant.addModification(modname, position=pos)
        variants.add(pepvariant)
    return variants

class FragmentType(object):
    UNKNOWN = "UNKNOWN"
    ISOTOPE = "ISOTOPE"
    IMMONIUMION = "IMMONIUMION"
    OXONIUMION = "OXONIUMION"
    AION = "AION"
    BION = "BION"
    CION = "CION"
    XION = "XION"
    YION = "YION"
    ZION = "ZION"
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

    def __init__(self, name, mass, charge, typ=FragmentType.UNKNOWN, peak=None, parents=set([]),cterm=-1, nterm=-1, status=glyxtoolms.io.ConfirmationStatus.Unknown):
        self.name = name
        self.typ = typ
        self.mass = mass
        self.peak = peak
        self.charge = charge
        self.parents = set(parents) # Link to parent fragments name, if available
        self.cterm = cterm # fragment position from nterminus (to calculate x,y,z position)
        self.nterm = nterm # fragment position from cterminus (to calculate a,b,c position)
        self.status = status
        self.children = set() # Link to child nodes, if available (currently only filled during glyML loading)
        
    def copy(self):
        new = Fragment(self.name, self.mass, self.charge)
        new.typ = self.typ
        new.peak = self.peak
        new.parents = list(self.parents)
        new.cterm = self.cterm
        new.nterm = self.nterm
        new.status = self.status
        return new

class FragmentProvider(object):
    """ Class to generate and store theoretical glycoeptide fragments for use on identical peptides/glycans"""
    def __init__(self ,types={"b","y"}):
        
        self.types = types
        self.unchargedPeptides = {}
        self.chargedPeptides = {}
        self.immoniumIons = {}
        self.subglycanCompositions = {}
        self.oxoniumIons = {}
        
        self.spectrumLookups = {}
        self.toleranceLookup = 1.0
        
        # helper masses
        self.masses = {}
        self.masses["mH2O"] = glyxtoolms.masses.calcMassFromElements({"H":2, "O":1})
        self.masses["mNH3"] = glyxtoolms.masses.calcMassFromElements({"N":1, "H":3})
        self.masses["mCO"] = glyxtoolms.masses.calcMassFromElements({"C":1, "O":1})
        self.masses["mCH2O"] = glyxtoolms.masses.calcMassFromElements({"C":1, "H": 2, "O":1})
        self.masses["mCH2CO"] = glyxtoolms.masses.calcMassFromElements({"C":2, "H": 2, "O":1})
        self.masses["mNx"] = glyxtoolms.masses.calcMassFromElements({"C":4, "H":5, "N":1, "O":1})
        self.masses["mCHOCH3"] = glyxtoolms.masses.calcMassFromElements({"C":2, "H":4, "O":1})
        
    def _getMaxIsotopeNr(self, mass):
        """ Estimate the maximum number of isotopes that need to be annotated based on ion mass
        (Monoisotopic peak is isotope Nr 0)
        """
        return int(mass/500.0+2)
        
    def _getUnchargedPeptideFragments(self,peptide):
        peptideString = peptide.toString()
        if peptideString in self.unchargedPeptides:
            return self.unchargedPeptides[peptideString]
        
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

            nterm = Composition() + {"H+":1, "H":1, "O":1}
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
            
            cNH3 = c - {"N":1, "H":3}
            cH2O = c - {"O":1, "H":2}

            if i < len(sequence)-1: # generate a,b and c ions
                key = str(i+1)
                if "a" in self.types:
                    data += Fragment("a"+key, a.mass(), 1, typ=FragmentType.AION,cterm=i+1)
                if "b" in self.types:    
                    data += Fragment("b"+key, b.mass(), 1, typ=FragmentType.BION,cterm=i+1)
                if "c" in self.types:
                    data += Fragment("c"+key, c.mass(), 1, typ=FragmentType.CION,cterm=i+1)
                
                if ("R" in sequence or
                        "K" in sequence or
                        "Q" in sequence or
                        "N" in sequence):
                    if "a-NH3" in self.types:
                        data += Fragment("a"+key+"-NH3", aNH3.mass(),1, typ=FragmentType.AION,cterm=i+1)
                    if "b-NH3" in self.types:
                        data += Fragment("b"+key+"-NH3", bNH3.mass(),1, typ=FragmentType.BION,cterm=i+1)
                    if "c-NH3" in self.types:
                        data += Fragment("c"+key+"-NH3", cNH3.mass(),1, typ=FragmentType.CION,cterm=i+1)
                if ("S" in sequence or
                        "T" in sequence or
                        sequence.startswith("E")):
                    if "a-H2O" in self.types:
                        data += Fragment("a"+key+"-H2O", aH2O.mass(), 1, typ=FragmentType.AION,cterm=i+1)
                    if "b-H2O" in self.types:
                        data += Fragment("b"+key+"-H2O", bH2O.mass(), 1, typ=FragmentType.BION,cterm=i+1)
                    if "c-H2O" in self.types:
                        data += Fragment("c"+key+"-H2O", cH2O.mass(), 1, typ=FragmentType.CION,cterm=i+1)

            cTerm = Composition() + {"H+":1,"H":1, "O":1}
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
            z = cTerm - {"H":1, "N":1}

            xNH3 = x - {"N":1, "H":3}
            xH2O = x - {"O":1, "H":2}

            yNH3 = y - {"N":1, "H":3}
            yH2O = y - {"O":1, "H":2}
            
            zNH3 = z - {"N":1, "H":3}
            zH2O = z - {"O":1, "H":2}
            zOne = z + {"H":1}

            key = str(len(sequence)-i)

            if i > 0:
                if "x" in self.types:
                    data += Fragment("x"+key, x.mass(), 1, typ=FragmentType.XION,nterm=len(sequence)-i)
                if "y" in self.types:
                    data += Fragment("y"+key, y.mass(), 1, typ=FragmentType.YION,nterm=len(sequence)-i)
                if "z" in self.types:
                    data += Fragment("z"+key, z.mass(), 1, typ=FragmentType.ZION,nterm=len(sequence)-i)
                if "z*" in self.types:
                    data += Fragment("z*"+key, zOne.mass(), 1, typ=FragmentType.ZION,nterm=len(sequence)-i)
                if ("R" in sequence or
                        "K" in sequence or
                        "Q" in sequence or
                        "N" in sequence):
                    if "x-NH3" in self.types:
                        data += Fragment("x"+key+"-NH3", xNH3.mass(), 1, typ=FragmentType.XION,nterm=len(sequence)-i)
                    if "y-NH3" in self.types:
                        data += Fragment("y"+key+"-NH3", yNH3.mass(), 1, typ=FragmentType.YION,nterm=len(sequence)-i)
                    if "z-NH3" in self.types:
                        data += Fragment("z"+key+"-NH3", zNH3.mass(), 1, typ=FragmentType.ZION,nterm=len(sequence)-i)
                    
                if ("S" in sequence or
                        "T" in sequence or
                        sequence.startswith("E")):
                    if "x-H2O" in self.types:
                        data += Fragment("x"+key+"-H2O", xH2O.mass(), 1, typ=FragmentType.XION,nterm=len(sequence)-i)
                    if "y-H2O" in self.types:
                        data += Fragment("y"+key+"-H2O", yH2O.mass(), 1, typ=FragmentType.YION,nterm=len(sequence)-i)
                    if "z-H2O" in self.types:
                        data += Fragment("z"+key+"-H2O", zH2O.mass(), 1, typ=FragmentType.ZION,nterm=len(sequence)-i)

        # calc internal fragments
        if "by" in self.types:
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

                    key = "b"+str(e)+"y"+str(len(sequence)-i)
                    data += Fragment(key, by.mass(), 1, typ=FragmentType.BYION,cterm=e, nterm=len(sequence)-i)
        self.unchargedPeptides[peptideString] = data
        return data
    
    def _getChargedPeptideFragments(self, peptide, maxCharge):
        peptideString = peptide.toString()
        if peptideString in self.chargedPeptides:
            if maxCharge in self.chargedPeptides[peptideString]:
                #print "return available ", peptideString, maxCharge
                return self.chargedPeptides[peptideString][maxCharge]
        else:
            self.chargedPeptides[peptideString] = {}
        #print "generate", peptideString, maxCharge
        # create new charged fragment list
        chargedFragments = FragmentList()
        data = self._getUnchargedPeptideFragments(peptide)
        for fragment in data.values():
            for z in range(1,maxCharge+1):
                name = fragment.name + "(" + str(z) +"+)"
                mass = (fragment.mass+ (z-1)*glyxtoolms.masses.MASS["H+"])/float(z)
                chargedFragments += Fragment(name, mass, z, typ=fragment.typ,cterm=fragment.cterm, nterm=fragment.nterm)
        self.chargedPeptides[peptideString][maxCharge] = chargedFragments
        return chargedFragments

    def _getImmoniumIons(self, peptide):
        if peptide.sequence in self.immoniumIons:
            return self.immoniumIons[peptide.sequence]
        # calculate immonium ions
        immoniumIons = {}
        for pos, aminoacid in enumerate(peptide.sequence): # TODO: account for modifications
            comp = glyxtoolms.fragmentation.Composition() + glyxtoolms.masses.COMPOSITION[aminoacid]
            comp = comp + {"C":-1, "O":-2, "H":-1}
            immoniumIons[aminoacid+"(1+)"] = Fragment(aminoacid+"(1+)", comp.mass(), 1, FragmentType.IMMONIUMION)
        
        immoniumIons = immoniumIons.values()
        self.immoniumIons[peptide.sequence] = immoniumIons
        return immoniumIons

    def _getSubglycanCompositions(self, glycan):
        if glycan.toString() in self.subglycanCompositions:
            return self.subglycanCompositions[glycan.toString()]
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
        self.subglycanCompositions[glycan.toString()] = glycans
        return glycans

    def _getOxoniumIons(self,glycan):
        if glycan.toString() in self.oxoniumIons:
            return self.oxoniumIons[glycan.toString()]
        # add oxoniumIons
        glycans = self._getSubglycanCompositions(glycan)
        fragments = []
        for g in glycans:
            ox = Fragment(g.toString()+"(1+)", g.mass+glyxtoolms.masses.MASS["H+"], 1, FragmentType.OXONIUMION)
            fragments.append(ox)
            oxH2O = Fragment(g.toString()+"-H2O(1+)", ox.mass - self.masses["mH2O"], 1, FragmentType.OXONIUMION, parents={ox.name})
            fragments.append(oxH2O)

            fragments.append(Fragment(g.toString()+"-2*H2O(1+)", oxH2O.mass - self.masses["mH2O"], 1, FragmentType.OXONIUMION, parents={oxH2O.name}))
            fragments.append(Fragment(g.toString()+"-3*H2O(1+)", oxH2O.mass - 2*self.masses["mH2O"], 1, FragmentType.OXONIUMION, parents={oxH2O.name}))
            fragments.append(Fragment(g.toString()+"-CH3COOH(1+)", oxH2O.mass - self.masses["mCH2CO"], 1, FragmentType.OXONIUMION, parents={oxH2O.name}))
            fragments.append(Fragment(g.toString()+"-CH2OH2OH2O(1+)", oxH2O.mass - self.masses["mCH2O"] - self.masses["mH2O"], 1, FragmentType.OXONIUMION, parents={oxH2O.name}))
            fragments.append(Fragment(g.toString()+"-H2OCH2OH2O(1+)", oxH2O.mass - self.masses["mCH2CO"] - self.masses["mH2O"], 1, FragmentType.OXONIUMION, parents={oxH2O.name}))
            fragments.append(Fragment(g.toString()+"-H2OCH2COH2O(1+)", oxH2O.mass - self.masses["mCH2CO"] - self.masses["mH2O"], 1, FragmentType.OXONIUMION, parents={oxH2O.name}))
        
        self.oxoniumIons[glycan.toString()] = fragments
        return fragments

    # helper function to search masses in a spectrum
    def _searchMassInSpectrum(self, mass, tolerance, toleranceType, peakLookup):

        hit = (0,None)
        index = self._getDBIndex(mass)
        for peak in peakLookup.get(index,[]):
            error = abs(glyxtoolms.lib.calcMassError(peak.x, mass, toleranceType))
            if error <= tolerance:
                if hit[1] == None or error < hit[0]:
                    hit = (error,peak)
        return hit[1]

    # helper function to calculate charged ion masses
    def _calcChargedMass(self, singlyChargedMass, charge):
        mass = singlyChargedMass+(charge-1)*glyxtoolms.masses.MASS["H"]
        return mass/float(charge)
        
    def _getDBIndex(self, mass):
        return int(mass/(2*self.toleranceLookup))
        
    def _getSpectrumLookup(self, spectrum, spectrumIdentifier=None):
        if spectrumIdentifier != None:
            if spectrumIdentifier in self.spectrumLookups:
                return self.spectrumLookups[spectrumIdentifier]
        #sort peaks into lookup
        peakLookup = {}
        for peak in spectrum:
            index = self._getDBIndex(peak.x)
            peakLookup[index-1] = peakLookup.get(index-1, set()).union({peak})
            peakLookup[index] = peakLookup.get(index, set()).union({peak})
            peakLookup[index+1] = peakLookup.get(index+1, set()).union({peak})
        
        if spectrumIdentifier != None:
            self.spectrumLookups[spectrumIdentifier] = peakLookup
        return peakLookup
     
    def annotateIsotopes(self, fragments,  tolerance, toleranceType, peakLookup):
        # add isotopes
        for key in fragments.keys():
            fragment = fragments[key]
            for i in range(1, self._getMaxIsotopeNr(fragment.mass)+2):
                mz = fragment.mass + i/float(fragment.charge)
                peak = self._searchMassInSpectrum(mz, tolerance, toleranceType, peakLookup)
                if peak == None:
                    break
                isotope = Fragment(fragment.name + "/"+str(i), mz, fragment.charge, FragmentType.ISOTOPE, peak=peak, parents={fragment.name})
                fragments[isotope.name] = isotope
     
    def annotateSpectrumWithGlycan(self, spectrum, peptideMass, glycan, tolerance, toleranceType, maxCharge, spectrumIdentifier=None):
        
        peakLookup = self._getSpectrumLookup(spectrum, spectrumIdentifier)
        # calculate peptide mass
        pepIon = peptideMass+glyxtoolms.masses.MASS["H+"]
        pepGlcNAcIon = pepIon+glyxtoolms.masses.GLYCAN["HEXNAC"]
        pepNH3 = pepIon - self.masses["mNH3"]
        pep83 = pepIon + self.masses["mNx"]
        pepH2O = pepIon + self.masses["mH2O"]
        pepHex = pepIon+glyxtoolms.masses.GLYCAN["HEX"]
        pepHexHex = pepIon+glyxtoolms.masses.GLYCAN["HEX"]*2
        
        # create Fragmentlist
        fragments = FragmentList()
        
        # add oxoniumIons
        for fragment in self._getOxoniumIons(glycan):
            fragments += fragment
        
        # add peptide and glycopeptide ions
        for charge in range(1, maxCharge+1):
            pepIonMass = self._calcChargedMass(pepIon, charge)
            pepNH3Mass = self._calcChargedMass(pepNH3, charge)
            pepH2OMass = self._calcChargedMass(pepH2O, charge)
            pep83Mass = self._calcChargedMass(pep83, charge)

            chargeName = "("+str(charge)+"+)"
            fragments += Fragment("pep"+chargeName, pepIonMass, charge, FragmentType.PEPTIDEION)
            fragments += Fragment("pep-NH3"+chargeName, pepNH3Mass, charge, FragmentType.PEPTIDEION)
            fragments += Fragment("pep-H2O"+chargeName, pepH2OMass, charge, FragmentType.PEPTIDEION)
            fragments += Fragment("pep+N(0.2X)"+chargeName, pep83Mass, charge, FragmentType.GLYCOPEPTIDEION)
            fragments += Fragment("pep+N(0.2X)-H2O"+chargeName, pep83Mass-self.masses["mH2O"], charge, FragmentType.GLYCOPEPTIDEION)

            # add glycan fragments
            for g in self._getSubglycanCompositions(glycan):
                if g.hasNCorePart() == False:
                    continue
                mass = self._calcChargedMass(pepIon+g.mass, charge)
                massNH3 = self._calcChargedMass(pepIon+g.mass-self.masses["mNH3"], charge)
                massH2O = self._calcChargedMass(pepIon+g.mass-self.masses["mH2O"], charge)
                mass2xH2O = self._calcChargedMass(pepIon+g.mass-2*self.masses["mH2O"], charge)
                massCHOCH3 = self._calcChargedMass(pepIon+g.mass-self.masses["mCHOCH3"], charge)
                fragments += Fragment("pep+"+g.toString()+"("+str(charge)+"+)", mass, charge, FragmentType.GLYCOPEPTIDEION)
                fragments += Fragment("pep+"+g.toString()+"-NH3"+"("+str(charge)+"+)", massNH3, charge, FragmentType.GLYCOPEPTIDEION)
                fragments += Fragment("pep+"+g.toString()+"-H2O"+"("+str(charge)+"+)", massH2O, charge, FragmentType.GLYCOPEPTIDEION)
                fragments += Fragment("pep+"+g.toString()+"-2xH2O"+"("+str(charge)+"+)", mass2xH2O, charge, FragmentType.GLYCOPEPTIDEION)
                fragments += Fragment("pep+"+g.toString()+"-CHOCH3"+"("+str(charge)+"+)", massCHOCH3, charge, FragmentType.GLYCOPEPTIDEION)
                
        #search for the existence of each fragment within the spectrum
        found_fragments = {}
        for fragmentname in fragments:
            fragment = fragments[fragmentname]
            # search highest peak within tolerance
            peak = self._searchMassInSpectrum(fragment.mass, tolerance, toleranceType, peakLookup)
            if peak == None:
                continue
            newFragment = fragment.copy()
            newFragment.peak = peak
            found_fragments[fragmentname] = newFragment
        
        self.annotateIsotopes(found_fragments,  tolerance, toleranceType, peakLookup)
        return found_fragments

    def annotateSpectrumWithFragments(self, peptide, glycan, spectrum, tolerance, toleranceType, maxCharge, spectrumIdentifier=None):

        peakLookup = self._getSpectrumLookup(spectrum, spectrumIdentifier)

        # calculate peptide mass
        pepIon = peptide.mass+glyxtoolms.masses.MASS["H+"]
        pepGlcNAcIon = pepIon+glyxtoolms.masses.GLYCAN["HEXNAC"]
        pepNH3 = pepIon - self.masses["mNH3"]
        pep83 = pepIon + self.masses["mNx"]
        pepH2O = pepIon + self.masses["mH2O"]
        pepHex = pepIon+glyxtoolms.masses.GLYCAN["HEX"]
        pepHexHex = pepIon+glyxtoolms.masses.GLYCAN["HEX"]*2

        

        # determine all peptide modification variants
        bestVariant = (None, {})
        
        pepvariants = []
        for gtyp in glycan.types:
            pepvariants += list(glyxtoolms.fragmentation.getModificationVariants(peptide,gtyp))
            
        # unifiy peptite variants to get rid of exponential explosion searching O glycans
        single = {}
        for pepvariant in pepvariants:
            key = pepvariant.toString()
            if not key in single:
                single[key] = pepvariant
        
        for pepvariant in single.values():
            # add glycosylation sites
            pepvariant.glycosylationSites = list(peptide.glycosylationSites)
            # collect glycosylationsite positions
            glycosylationsSites = set()
            for site, typ in pepvariant.glycosylationSites:
                pos = site-pepvariant.start
                assert 0 <= pos < len(pepvariant.sequence)
                amino = pepvariant.sequence[pos]
                if typ == "N":
                    assert amino == "N"
                elif typ == "O":
                    assert amino == "S" or amino == "T"
                glycosylationsSites.add(pos)
            if len(glycosylationsSites) == 0:
                for pos, amino in enumerate(pepvariant.sequence):
                    if amino in ["N", "s", "T"]:
                        glycosylationsSites.add(pos)
            
            fragments = FragmentList()
            he = self._getChargedPeptideFragments(pepvariant, maxCharge)
            for fragment in he.values():
                fragments += fragment

            # add immonium ions
            for fragment in self._getImmoniumIons(pepvariant):
                fragments += fragment

            # add oxoniumIons
            for fragment in self._getOxoniumIons(glycan):
                fragments += fragment

            # add peptide and glycopeptide ions
            for charge in range(1, maxCharge+1):
                pepIonMass = self._calcChargedMass(pepIon, charge)
                pepNH3Mass = self._calcChargedMass(pepNH3, charge)
                pepH2OMass = self._calcChargedMass(pepH2O, charge)
                pep83Mass = self._calcChargedMass(pep83, charge)

                chargeName = "("+str(charge)+"+)"
                fragments += Fragment("pep"+chargeName, pepIonMass, charge, FragmentType.PEPTIDEION)
                fragments += Fragment("pep-NH3"+chargeName, pepNH3Mass, charge, FragmentType.PEPTIDEION)
                fragments += Fragment("pep-H2O"+chargeName, pepH2OMass, charge, FragmentType.PEPTIDEION)
                fragments += Fragment("pep+N(0.2X)"+chargeName, pep83Mass, charge, FragmentType.GLYCOPEPTIDEION)
                fragments += Fragment("pep+N(0.2X)-H2O"+chargeName, pep83Mass-self.masses["mH2O"], charge, FragmentType.GLYCOPEPTIDEION)

                # add glycan fragments
                for g in self._getSubglycanCompositions(glycan):
                    if g.hasNCorePart() == False:
                        continue
                    mass = self._calcChargedMass(pepIon+g.mass, charge)
                    massNH3 = self._calcChargedMass(pepIon+g.mass-self.masses["mNH3"], charge)
                    massH2O = self._calcChargedMass(pepIon+g.mass-self.masses["mH2O"], charge)
                    mass2xH2O = self._calcChargedMass(pepIon+g.mass-2*self.masses["mH2O"], charge)
                    massCHOCH3 = self._calcChargedMass(pepIon+g.mass-self.masses["mCHOCH3"], charge)
                    fragments += Fragment("pep+"+g.toString()+"("+str(charge)+"+)", mass, charge, FragmentType.GLYCOPEPTIDEION)
                    fragments += Fragment("pep+"+g.toString()+"-NH3"+"("+str(charge)+"+)", massNH3, charge, FragmentType.GLYCOPEPTIDEION)
                    fragments += Fragment("pep+"+g.toString()+"-H2O"+"("+str(charge)+"+)", massH2O, charge, FragmentType.GLYCOPEPTIDEION)
                    fragments += Fragment("pep+"+g.toString()+"-2xH2O"+"("+str(charge)+"+)", mass2xH2O, charge, FragmentType.GLYCOPEPTIDEION)
                    fragments += Fragment("pep+"+g.toString()+"-CHOCH3"+"("+str(charge)+"+)", massCHOCH3, charge, FragmentType.GLYCOPEPTIDEION)

            # add peptide fragments with attached glycans
            lenSeq = len(pepvariant.sequence)
            if len(glycosylationsSites) > 0:
                minSite = min(glycosylationsSites)
                maxSite = max(glycosylationsSites)
                for fragment in fragments.values():
                    if fragment.nterm != -1 and  fragment.cterm != -1: # yb ion
                        if fragment.cterm <= minSite or lenSeq - fragment.nterm > maxSite:
                            continue
                    elif fragment.nterm != -1: # x,y,z ion
                        if lenSeq - fragment.nterm > maxSite:
                            continue
                    elif fragment.cterm != -1: # a,b,c ion
                        if fragment.cterm <= minSite:
                            continue
                    else: # no a,b,c or x,y,z ion
                        continue
                    for g in self._getSubglycanCompositions(glycan):
                        if g.hasNCorePart() == False:
                            continue
                        # generate new name
                        if "-" in fragment.name:
                            sp1, sp2 = fragment.name.split("-")
                            sp3, sp4 = sp2.split("(")
                            name = sp1+"+"+g.toString()+"-"+sp3+"("+sp4
                        else:
                            sp1, sp2 = fragment.name.split("(")
                            name = sp1+"+"+g.toString()+"("+sp2
                            
                        fragment1 = Fragment(name,
                                             fragment.mass + g.mass/float(fragment.charge),
                                             fragment.charge,
                                             fragment.typ)

                        fragments += fragment1

            # search for the existence of each fragment within the spectrum
            found_fragments = {}
            for fragmentname in fragments:
                fragment = fragments[fragmentname]
                # search highest peak within tolerance
                peak = self._searchMassInSpectrum(fragment.mass, tolerance, toleranceType, peakLookup)
                if peak == None:
                    continue
                newFragment = fragment.copy()
                newFragment.peak = peak
                found_fragments[fragmentname] = newFragment
            
            self.annotateIsotopes(found_fragments,  tolerance, toleranceType, peakLookup)

            # check if peptide variant has highest fragment count
            # TODO: Better variant scoring?
            if len(found_fragments) > len(bestVariant[1]):
                bestVariant = (pepvariant, found_fragments)
                # resetet glycoslyation sites
                pepvariant.glycosylationSites = list(peptide.glycosylationSites)
                
        return {"peptidevariant":bestVariant[0], "fragments":bestVariant[1], "all": fragments}
