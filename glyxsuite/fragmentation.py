"""
Functions for generation of theoretical peptide fragments.
Uses a peptide and its modifications as input.
The function getModificationVariants(peptide) can be used to generate
alle modification variants if the position of a peptide is not known.

Usage:
p = glyxsuite.io.XMLPeptide()
p.sequence = "DPTPLANCSVR"
p.modifications = [('Cys_CAM', 'C', -1)]

for modifications in getModificationVariants(p):
    pepvariant = glyxsuite.io.XMLPeptide()
    pepvariant.sequence = p.sequence
    pepvariant.modifications = modifications
    fragments = generatePeptideFragments(pepvariant)

"""

import glyxsuite
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
            mass += glyxsuite.masses.MASS[key] * self[key]
        return mass

def getModificationVariants(peptide):
    # separate static and variable modifications
    modify = []
    static = set()
    amino_numbers = {}
    for mod, amino, pos in peptide.modifications:
        if len(amino) > 0: # special case liek NTerm - dont check consistency
            continue
        amino_numbers[amino] = amino_numbers.get(amino, 0) + 1
        if pos != -1:
            # check if aminoacid exists there
            if not peptide.sequence[pos] == amino:
                raise Exception("Wrong aminoacid position!")
            if pos in static:
                raise Exception("Aminoacid contains two static modifications!")
            static.add(pos)
            modify.append([(mod, amino, pos)])

    # check if number of modifications on one aminoacid is greater than the real amount of aminoacids in the sequence
    for amino in amino_numbers:
        if amino_numbers[amino] > peptide.sequence.count(amino):
            raise Exception("More modifications than modifiable aminoacids in sequence")

    for mod, amino, pos in peptide.modifications:
        if pos == -1:
            positions = []
            for i, e in enumerate(peptide.sequence):
                if e == amino and i not in static:
                    positions.append((mod, amino, i))
            modify.append(positions)

    # make permutations
    def isValidPermutation(permutation):
        valid_list = set()
        for mod, amino, pos in i:
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
    for mod, amino, pos in peptide.modifications:
        assert pos > -1
        assert pos not in modifications
        assert amino == sequence[pos]
        assert mod in glyxsuite.masses.COMPOSITION
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
            nterm += glyxsuite.masses.COMPOSITION[acid]
            if pos in modifications:
                mod, amino = modifications[pos]
                assert acid == amino
                peptidestring += "("+mod+")"
                nterm += glyxsuite.masses.COMPOSITION[mod]
        a = nterm - {"C":1, "H":1, "O":2}
        b = nterm - {"H":1, "O":1}
        c = nterm - {"O":1} + {"H":2, "N":1}

        aNH3 = a - {"N":1, "H":3}
        aH2O = a - {"O":1, "H":2}

        bNH3 = b - {"N":1, "H":3}
        bH2O = b - {"O":1, "H":2}

        if i < len(sequence)-1: # generate a,b and c ions
            key = str(i+1)
            data["a"+key] = (a.mass(), peptidestring, 0, i+1)
            data["a"+key+"-NH3"] = (aNH3.mass(), peptidestring+"-NH3", 0, i+1)
            data["a"+key+"-H2O"] = (aH2O.mass(), peptidestring+"-H2O", 0, i+1)

            data["b"+key] = (b.mass(), peptidestring, 0, i+1)
            data["b"+key+"-NH3"] = (bNH3.mass(), peptidestring+"-NH3", 0, i+1)
            data["b"+key+"-H2O"] = (bH2O.mass(), peptidestring+"-H2O", 0, i+1)

            data["c"+key] = (c.mass(), peptidestring, 0, i+1)

        cTerm = Composition() + {"H":2, "O":1}
        peptidestring = ""
        for index, acid in enumerate(n):
            pos = index+i
            peptidestring += acid
            cTerm -= {"H":2, "O":1}
            cTerm += glyxsuite.masses.COMPOSITION[acid]
            if pos in modifications:
                mod, amino = modifications[pos]
                assert acid == amino
                peptidestring += "("+mod+")"
                nterm += glyxsuite.masses.COMPOSITION[mod]
        x = cTerm + {"C":1, "O":1} - {"H":1}
        y = cTerm + {"H":1}
        z = cTerm - {"H":2, "N":1}

        #yNH3 = y - {"N":1, "H":3}
        yH2O = y - {"O":1, "H":2}


        key = str(len(sequence)-i)

        if i > 0:
            data["x"+key] = (x.mass(), peptidestring, i, len(sequence))
            data["y"+key] = (y.mass(), peptidestring, i, len(sequence))
            #data["y"+key+"-NH3"] = (yNH3.mass(), peptidestring+"-NH3", i, len(sequence)) # equals z ion
            data["y"+key+"-H2O"] = (yH2O.mass(), peptidestring+"-H2O", i, len(sequence))
            data["z"+key] = (z.mass(), peptidestring, i, len(sequence)) # equals y-NH3



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
                nterm += glyxsuite.masses.COMPOSITION[acid]
                if pos in modifications:
                    mod, amino = modifications[pos]
                    assert acid == amino
                    peptidestring += "("+mod+")"
                    nterm += glyxsuite.masses.COMPOSITION[mod]
            by = nterm - {"O":1, "H":1}
            byNH3 = by - {"N":1, "H":3}
            byH2O = by - {"O":1, "H":2}
            byCO = by - {"C":1, "O":1}

            key = "y"+str(len(sequence)-i)+"b"+str(e)
            data[key] = (by.mass(), peptidestring, i, e)
            data[key+"-NH3"] = (byNH3.mass(), peptidestring+"-NH3", i, e)
            data[key+"-H2O"] = (byH2O.mass(), peptidestring+"-H2O", i, e)
            data[key+"-CO"] = (byCO.mass(), peptidestring+"-CO", i, e)


    return data
