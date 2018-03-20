"""
Mass list of aminoacids, protenimodifications, glycan monomers, etc.
Contains also all functions for mass calculation.
Source of mass values from:
http://web.expasy.org/findmod/findmod_masses.html
"""
import re
import math
import itertools
import numpy as np
from pkg_resources import resource_stream
import pickle

# --------------------------- Aminoacids ------------------------------#

AMINOACID = {}
AMINOACID["A"] = 71.03711
AMINOACID["R"] = 156.10111
AMINOACID["N"] = 114.04293
AMINOACID["D"] = 115.02694
AMINOACID["C"] = 103.00919
AMINOACID["E"] = 129.04259
AMINOACID["Q"] = 128.05858
AMINOACID["G"] = 57.02146
AMINOACID["H"] = 137.05891
AMINOACID["I"] = 113.08406
AMINOACID["L"] = 113.08406
AMINOACID["K"] = 128.09496
AMINOACID["M"] = 131.04049
AMINOACID["F"] = 147.06841
AMINOACID["P"] = 97.05276
AMINOACID["S"] = 87.03203
AMINOACID["T"] = 101.04768
AMINOACID["W"] = 186.07931
AMINOACID["Y"] = 163.06333
AMINOACID["V"] = 99.06841

# --------------------------- Proteinmodifications---------------------#

PROTEINMODIFICATION = {}
# Cys_CAM Idoacetamide treatment (carbamidation)
PROTEINMODIFICATION["CYS_CAM"] = {"mass": 57.021464,
                                  "targets": {"C"},
                                  "composition":{'C':2, 'H':3, 'O':1, 'N':1}
                                  }
PROTEINMODIFICATION["NTERM_CAM"] = {"mass": 57.021464,
                                    "targets": {"NTERM"},
                                    "composition":{'C':2, 'H':3, 'O':1, 'N':1}
                                    }
PROTEINMODIFICATION["CAM"] = {"mass": 57.021464,
                              "targets": {"C","NTERM"},
                              "composition":{'C':2, 'H':3, 'O':1, 'N':1}
                             }
# Cys_CM, Iodoacetic acid treatment (carboxylation)
PROTEINMODIFICATION["CYS_CM"] = {"mass": 58.005479,
                                 "targets": {"C"},
                                 "composition":{'C': 2, 'H': 2, 'O': 2}
                                }
PROTEINMODIFICATION["CM"] = {"mass": 58.005479,
                             "targets": {"C"},
                             "composition":{'C': 2, 'H': 2, 'O': 2}
                            }
# Cys_PAM Acrylamide Adduct
PROTEINMODIFICATION["CYS_PAM"] = {"mass": 71.03712,
                                  "targets": {"C"},
                                  "composition":{'C': 3, 'H': 5, 'O': 1, 'N': 1}
                                 }
PROTEINMODIFICATION["PAM"] = {"mass": 71.03712}

PROTEINMODIFICATION["MSO"] = {"mass": 15.9949,
                              "targets": {"M"},
                              "composition":{'O': 1}
                             } # MSO
PROTEINMODIFICATION["ACET"] = {"mass": 42.0106,
                               "composition":{'C': 2, 'H': 2, 'O': 1}
                              } # Acetylation
PROTEINMODIFICATION["AMID"] = {"mass": -0.9840,
                               "targets": {"CTERM"},
                               "composition":{'H': 1, 'O': -1, 'N': 1}
                              } # Amidation
PROTEINMODIFICATION["HYDR"] = {"mass": 15.9949,
                               "composition":{'O': 1}
                              } # Hydroxylation
PROTEINMODIFICATION["METH"] = {"mass": 14.0157,
                               "composition":{'C': 1, 'H': 2}
                              } # Methylation
PROTEINMODIFICATION["PHOS"] = {"mass": 79.9663,
                               "targets": {"S", "T", "Y"},
                               "composition":{'P': 1, 'O': 3, 'H': 1}
                              } # Phosphorylation
PROTEINMODIFICATION["SER_PHOS"] = {"mass": 79.9663,
                              "targets": {"S"},
                               "composition":{'P': 1, 'O': 3, 'H': 1}
                             } # Phosphorylation Serine
PROTEINMODIFICATION["THR_PHOS"] = {"mass": 79.9663,
                              "targets": {"T"},
                               "composition":{'P': 1, 'O': 3, 'H': 1}
                             } # Phosphorylation Threonin
PROTEINMODIFICATION["TYR_PHOS"] = {"mass": 79.9663,
                              "targets": {"Y"},
                               "composition":{'P': 1, 'O': 3, 'H': 1}
                             } # Phosphorylation Tyrosin

PROTEINMODIFICATION["DEHYDR"] = {"mass": -18.0106,
                              "targets": {"S", "T"},
                               "composition":{'H': -2, 'O': -1}
                             } # Dehydration Serine
PROTEINMODIFICATION["SER_DEHYDR"] = {"mass": -18.0106,
                              "targets": {"S"},
                               "composition":{'H': -2, 'O': -1}
                             } # Dehydration Serine
PROTEINMODIFICATION["THR_DEHYDR"] = {"mass": -18.0106,
                              "targets": {"T"},
                               "composition":{'H': -2, 'O': -1}
                             } # Dehydration Threonin

PROTEINMODIFICATION["DEAM"] = {"mass": 0.9840,
                               "targets": {"N", "Q"},
                               "composition":{'H': -1, 'O': 1, 'N': -1}
                              } # Deamidation
PROTEINMODIFICATION["ASN_DEAM"] = {"mass": 0.9840,
                               "targets": {"N"},
                               "composition":{'H': -1, 'O': 1, 'N': -1}
                              } # Deamidation Asparagine
PROTEINMODIFICATION["GLN_DEAM"] = {"mass": 0.9840,
                               "targets": {"Q"},
                               "composition":{'H': -1, 'O': 1, 'N': -1}
                              } # Deamidation Glutamine

PROTEINMODIFICATION["OX"] = {"mass": 15.9949,
                              "targets": {"W", "Y"},
                               "composition":{'O': 1}
                              } # Oxidation Tyrosin

PROTEINMODIFICATION["TRP_OX"] = {"mass": 15.9949,
                              "targets": {"W"},
                               "composition":{'O': 1}
                              } # Oxidation Tryptophan

PROTEINMODIFICATION["TYR_OX"] = {"mass": 15.9949,
                              "targets": {"Y"},
                               "composition":{'O': 1}
                              } # Oxidation Tyrosin

PROTEINMODIFICATION["DIOX"] = {"mass": 31.9899,
                              "targets": {"W", "Y"},
                               "composition":{'O': 2}
                              } # Dioxidation Tryptophan and Tyrosin

PROTEINMODIFICATION["TRP_DIOX"] = {"mass": 31.9899,
                              "targets": {"W"},
                               "composition":{'O': 2}
                              } # Dioxidation Tryptophan

PROTEINMODIFICATION["TYR_DIOX"] = {"mass": 31.9899,
                              "targets": {"Y"},
                               "composition":{'O': 2}
                              } # Dioxidation Tyrosin

PROTEINMODIFICATION["TRP_KYN"] = {"mass":3.9949 ,
                              "targets": {"W"},
                               "composition":{'O': 1, 'C':-1}
                              }

def getModificationNames():
    """ Return a sorted list of Modification names.
    Only contains modifications with targets declaration"""
    def sort_names(name):
        if "_" in name:
            amino, mod = name.split("_")
            return mod, amino
        return name, " "
    names = set()
    for key in PROTEINMODIFICATION:
        if "targets" in PROTEINMODIFICATION[key]:
            names.add(key)
    return sorted(names, key=sort_names)


def getModificationTargets(modification):
    modification = modification.upper()
    if modification in PROTEINMODIFICATION:
        targets = PROTEINMODIFICATION[modification].get("targets", set())
        if len(targets) > 0:
            return targets
    return set(AMINOACID.keys())

def getModificationComposition(modification):
    if modification.upper() in PROTEINMODIFICATION:
        return PROTEINMODIFICATION[modification.upper()]["composition"]
    if not re.search("^([\+-][A-z0-9]+?)+$", modification):
        raise Exception("Cannot parse Proteinmodification: ", modification)
    composition = {}
    for group in re.findall("[\+-][A-z0-9]+", modification):
        sign = group[0]
        for match in re.findall("[A-Z][a-z]?\d*", group):
            element = re.search("[A-z]+",match).group()
            if element not in MASS:
                raise Exception("Unknown element!")
            amount = re.sub("[A-z]+","",match)
            if len(amount) == 0:
                amount = 1
            else:
                amount = int(amount)
            if sign == "-":
                amount = -amount
            composition[element] = composition.get(element, 0) + amount
    return composition


# ------------------------------ Glycans ------------------------------#

GLYCAN = {}
GLYCAN["DHEX"] = 146.0579
GLYCAN["HEX"] = 162.0528
GLYCAN["HEXNAC"] = 203.0794
GLYCAN["NEUAC"] = 291.0954
GLYCAN["NEUGC"] = 307.0903


# --------------------------- Other masses ----------------------------#
# http://www.sisweb.com/referenc/source/exactmas.htm
MASS = {}
MASS["H2O"] = 18.01057
MASS["H+"] = 1.00728
MASS["H"] = 1.007825
MASS["C"] = 12.0
MASS["N"] = 14.003074
MASS["O"] = 15.994915
MASS["S"] = 31.972072
MASS["P"] = 30.973763
MASS["Na"] = 22.989770
MASS["K"] = 38.963708
MASS["Mg"] = 23.985045

# ----------------------------- Isotopes ------------------------------#
"""
Dictionary of isotopes, containing massshift, actual atomic mass
and the probability of the isotope
"""
ISOTOPES = {}
ISOTOPES["H"] = {0:(1.007825, 99.9885), 1:(2.014102, 0.0115)}
ISOTOPES["C"] = {0:(12.0, 98.93), 1:(13.003355, 1.07)}
ISOTOPES["N"] = {0:(14.003074, 99.632), 1:(15.000109, 0.368)}
ISOTOPES["O"] = {0:(15.994915, 99.757),
                 1:(16.999132, 0.038),
                 2:(17.999160, 0.205)}
ISOTOPES["S"] = {0:(31.972071, 94.93),
                 1:(32.971458, 0.76),
                 2:(33.967867, 4.29),
                 3:(35.967081, 0.02)}

# --------------------------- Compositions ----------------------------#

# http://www.webqc.org/aminoacids.php

COMPOSITION = {}
COMPOSITION['A'] = {'C': 3, 'H': 7, 'N': 1, 'O': 2}
COMPOSITION['C'] = {'C': 3, 'H': 7, 'N': 1, 'O': 2, 'S': 1}
COMPOSITION['D'] = {'C': 4, 'H': 7, 'N': 1, 'O': 4}
COMPOSITION['E'] = {'C': 5, 'H': 9, 'N': 1, 'O': 4}
COMPOSITION['F'] = {'C': 9, 'H': 11, 'N': 1, 'O': 2}
COMPOSITION['G'] = {'C': 2, 'H': 5, 'N': 1, 'O': 2}
COMPOSITION['H'] = {'C': 6, 'H': 9, 'N': 3, 'O': 2}
COMPOSITION['I'] = {'C': 6, 'H': 13, 'N': 1, 'O': 2}
COMPOSITION['K'] = {'C': 6, 'H': 14, 'N': 2, 'O': 2}
COMPOSITION['L'] = {'C': 6, 'H': 13, 'N': 1, 'O': 2}
COMPOSITION['M'] = {'C': 5, 'H': 11, 'N': 1, 'O': 2, 'S': 1}
COMPOSITION['N'] = {'C': 4, 'H': 8, 'N': 2, 'O': 3}
COMPOSITION['P'] = {'C': 5, 'H': 9, 'N': 1, 'O': 2}
COMPOSITION['Q'] = {'C': 5, 'H': 10, 'N': 2, 'O': 3}
COMPOSITION['R'] = {'C': 6, 'H': 14, 'N': 4, 'O': 2}
COMPOSITION['S'] = {'C': 3, 'H': 7, 'N': 1, 'O': 3}
COMPOSITION['T'] = {'C': 4, 'H': 9, 'N': 1, 'O': 3}
COMPOSITION['V'] = {'C': 5, 'H': 11, 'N': 1, 'O': 2}
COMPOSITION['W'] = {'C': 11, 'H': 12, 'N': 2, 'O': 2}
COMPOSITION['Y'] = {'C': 9, 'H': 11, 'N': 1, 'O': 3}
COMPOSITION["HEX"] = {'C': 6, 'H': 12, 'N': 0, 'O': 6}
COMPOSITION["DHEX"] = {'C': 6, 'H': 12, 'N': 0, 'O': 5}
COMPOSITION["HEXNAC"] = {'C': 8, 'H': 15, 'N': 1, 'O': 6}
COMPOSITION["NEUAC"] = {'C': 11, 'H': 19, 'N': 1, 'O': 9}
COMPOSITION["NEUGC"] = {'C': 11, 'H': 19, 'N': 1, 'O': 10}
COMPOSITION["H2O"] = {'H': 2, 'O': 1}

# ------------------------------- Functions ---------------------------#
def calcMassFromElements(composition):
    """ Calculates the mass from the elemental composition
        Input: Dictionary of the element composition
        e.g for water (H2O): {"H":2, "O":1}
    """
    mass = 0
    for element in composition:
        if not element in MASS:
            raise Exception("Unknown element!")
        m = MASS[element]
        mass += m*composition[element]
    return mass


def calcPeptideMass(peptide):
    mass = MASS["H2O"]
    for s in peptide.sequence:
        try:
            mass += AMINOACID[s]
        except KeyError:
            print "Unknown Aminoacid '"+s+"'!"
            raise
    # TODO: Checks for modification consistency
    # a) amount of amino acids must be in sequence
    # b) a given position (except -1) can only be
    for mod in peptide.modifications:
        composition = getModificationComposition(mod.name)
        mass += calcMassFromElements(composition)
    return mass

def calcIonMass(name):
    r"""
    Calculates Ionmass from a given input string:
    Strings consists of possible Monomers surrounded by brackets, followed
    by the amount of the monomer. The amount can be also negative to allow
    for example water loss.

    Examples:
    '(NeuAc)1(H+)1' results in 292.10268
    '(NeuAc)1(H2O)-1(H+)1' results in 274.09211
    '(HexNAc)1(Hex)1(NeuAc)1(H+)1' results in 657.23488

    Parsing of Monomer-Amount combinations consists of the follwing Regex:
    '\(.+?\)-?\d+'
    """
    name = name.replace(" ", "")
    if re.match(r"^(\(.+?\)-?\d+)+$", name) == None:
        raise Exception(r"""Input string '{}' doesn't follow the
        regex  '^(\(.+?\)-?\d+)+$'
        Please surrond monomers by brackets followed by the amount of
        the monomer, e.g. '(NeuAc)1(H2O)-1(H+)1'""".format(name))

    mass = 0
    charge = 0
    for part in re.findall(r"\(.+?\)-?\d+", name.upper()):
        monomer, amount = part.split(")")
        monomer = monomer[1:]
        amount = int(amount)
        if monomer == "H+":
            charge += amount
        elif monomer == "H-": # TODO: Select real charge for negative charges!
            charge -= amount
        if monomer in GLYCAN:
            mass += GLYCAN[monomer]*amount
        elif monomer in MASS:
            mass += MASS[monomer]*amount
        elif monomer in PROTEINMODIFICATION:
            mass += PROTEINMODIFICATION[monomer]["mass"]*amount
        else:
            raise Exception("cannot find monomer {} in {}".format(monomer, name))
    if charge == 0:
        return mass
    else:
        return mass/float(charge), charge




def calculateIsotopicPattern(C=0, H=0, N=0, O=0, S=0, maxShift=10):
    """
    Calculates the isotopic pattern of the given elemental composition
    Currently only supports C, H, N, O and S
    maxShift option sets the calculated pattern size, which significantly
    speeds up the calculation

    Result: tuple of summed probability (if significantly smaller than 1
        increase maxShift), the monoisotopic mass and the pattern
    """

    def element(name, N, maxShift=10):
        """
        Generates the isotpic pattern of an element with a given number N of
        atoms. maxShift option sets maximum pattern size

        Result: dict of massshift and probabilities
        """

        def _binominal(n, k):
            try:
                newK = int(k)
                return math.factorial(n)/math.factorial(newK)/math.factorial(n-newK)
            except:
                pass
            try:
                newK = list(k)
            except:
                raise Exception("Unknown type of k, please supply an integer or a list")
            # check if k sums up to n
            if sum(newK) != n:
                raise Exception("The sum of k has to be equal n!")
            divisor = 1
            for k in newK:
                divisor *= math.factorial(k)
            return math.factorial(n)/divisor

        # generate isotope list
        isotope = []
        shifts = sorted(ISOTOPES[name])
        summ = sum([ISOTOPES[name][shift][1] for shift in shifts])
        for shift in shifts:
            isotope.append((shift, ISOTOPES[name][shift][1]/summ))

        # Generate amount ranges for each isotope, limited by the
        # maximum shift allowed
        amountList = []
        for shift, p in isotope:
            if shift == 0:
                amountList.append(range(0, N+1))
            else:
                amountList.append(range(0, int(math.ceil(maxShift/shift))))
        masses = {}
        for amounts in itertools.product(*amountList):
            if sum(amounts) != N:
                continue
            p = _binominal(N, amounts)
            mass = 0
            for i, amount in enumerate(amounts):
                shift, probability = isotope[i]
                p *= probability**amount
                mass += shift*amount
            masses[mass] = masses.get(mass, 0)+p
        trans = {}
        for mass in masses:
            if mass > maxShift and maxShift != 0:
                continue
            trans[mass] = masses[mass]
        return trans

    probs = []
    monoMass = 0
    if C > 0:
        probs.append(element("C", C, maxShift=maxShift))
        monoMass += C*ISOTOPES["C"][0][0]
    if H > 0:
        probs.append(element("H", H, maxShift=maxShift))
        monoMass += H*ISOTOPES["H"][0][0]
    if N > 0:
        probs.append(element("N", N, maxShift=maxShift))
        monoMass += N*ISOTOPES["N"][0][0]
    if O > 0:
        probs.append(element("O", O, maxShift=maxShift))
        monoMass += O*ISOTOPES["O"][0][0]
    if S > 0:
        probs.append(element("S", S, maxShift=maxShift))
        monoMass += S*ISOTOPES["S"][0][0]
    elementKeys = [e.keys() for e in probs]
    masses = {}
    for amounts in itertools.product(*elementKeys):
        shift = sum(amounts)
        if shift > maxShift:
            continue
        p = 1
        for i, amount in enumerate(amounts):
            p *= probs[i][amount]
        masses[shift] = masses.get(shift, 0) + p

    maxProb = max([masses[shift] for shift in masses])


    # test if accumulated probability accounts for
    sumProb = sum([masses[shift] for shift in masses])
    #print "sumProb", sumProb
    trans = []
    for shift in sorted(masses.keys()):
        trans.append((shift, masses[shift]/maxProb*100))
        #print shift, masses[shift]/maxProb*100
    return sumProb, monoMass, trans

def getElementComposition(peptide, glycan): # currently not working, du to change in modification definition
    # calculate element composition
    elements = {}
    def addElements(elements, name, amount):
        if not name in COMPOSITION:
            raise Exception("Cannot find name!")
        for elementname in COMPOSITION[name]:
            elements[elementname] = (elements.get(elementname, 0) +
                                     COMPOSITION[name][elementname]*amount)


    # a) peptide

    addElements(elements, "H2O", 1)
    for aminoacid in set(peptide.sequence):
        amount = peptide.sequence.count(aminoacid)
        addElements(elements, aminoacid, amount)
        addElements(elements, "H2O", -1*amount)

    for mod in peptide.modifications:
        comp = PROTEINMODIFICATION[mod.name]["composition"]
        for elementname in comp:
            elements[elementname] = elements.get(elementname, 0) + comp[elementname]


    # b) glycan
    # parse glycancomposition
    for match in re.findall(r"[A-z]+\d+", glycan.composition):
        glycanname = re.sub(r"\d+", "", match)
        amount = int(re.sub(r"[A-z]+", "", match))
        addElements(elements, glycanname, amount)
        addElements(elements, "H2O", -1*amount)

    return elements

def calcGlycopeptidePattern(peptide, glycan):

    elements = getElementComposition(peptide, glycan)
    res = calculateIsotopicPattern(
        C=elements.get("C", 0),
        H=elements.get("H", 0),
        N=elements.get("N", 0),
        O=elements.get("O", 0),
        S=elements.get("S", 0))
    return res

def calcIsotopicPatternFromMass(mass, N_isotopes, maxS=10):
    m_H = 0.068832626663784202
    b_H = -0.2237949069434535

    m_C = 0.045560761070855264
    b_C = -3.4169101305187581

    m_S = 0.00076944265205870766
    b_S = 0.071713743069281355

    m_O = 0.013186649782530958
    b_O = 0.8063769593231811

    m_N = 0.010596216778823579
    b_N = 1.8594274272131806

    N_H = int(round(m_H*mass+b_H))
    N_C = int(round(m_C*mass+b_C))
    N_S = int(round(m_S*mass+b_S))
    N_O = int(round(m_O*mass+b_O))
    N_N = int(round(m_N*mass+b_N))
    if N_S > maxS:
        N_S = maxS

    pattern = calculateIsotopicPattern(C=N_C, H=N_H, N=N_N, O=N_O, S=N_S, maxShift=N_isotopes-1)[2]
    summP = sum([b for a,b in pattern])
    return zip(range(0,len(pattern)),[b/summP for a,b in pattern])

def calcIsotopicPatternFromMass_Old(mass, N_isotopes):

    def binominal(n, k, p):
        return math.factorial(n)/(math.factorial(k)*math.factorial(n-k))*(p**k)*((1-p)**(n-k))

    # parameters
    # estimate of N_carbon from mass
    #est_NCarbon_m = 0.0694521806
    #est_NCarbon_b = -1.4759043747
    est_NHydrogen_m = 0.0694521806
    est_NHydrogen_b = -1.4759043747

    est_NCarbon_m = 0.0456772594
    est_NCarbon_b = -3.4971107586

    # isotopic probability (chosen after best fit)
    #p_Carbon = 0.9916213
    p_Hydrogen =  0.98884015
    p_Carbon = 0.99052649

    # calculate approximate amount of carbon from mass
    N_carbon = round(est_NCarbon_m*mass+est_NCarbon_b)
    N_hydrogen = round(est_NHydrogen_m*mass+est_NHydrogen_b)


    # calculate isotopic distribution of isotopes
    #pattern = [binominal(N_carbon,N_carbon-i,p_Carbon) for i in range(0,N_isotopes)]
    pattern = []
    for i in range(0,N_isotopes):
        p = 0
        if N_hydrogen >= i:
            p += binominal(N_hydrogen,N_hydrogen-i,p_Hydrogen)
        if N_carbon >= i:
            p += binominal(N_carbon,N_carbon-i,p_Carbon)
        pattern.append(p)
    # normalize pattern after sum of all 4 probabilities
    summP = sum(pattern)
    return zip(range(0,N_isotopes),[p/summP for p in pattern])

def findBestFittingMass(x, y, max_charge=5, N_isotopes=4, intensityCutoff=0.2):
    best = None
    if len(x) == 0:
        return None

    assert len(x) == len(y)

    highestPeak = max(y)
    assert highestPeak > 0

    for mass in x:
        for charge in range(1,max_charge):
            # calculate mass array for peaks
            masses_raw = [mass+i*MASS["H+"]/charge for i in range(0,N_isotopes)]

            # interpolate intensities from measurement
            intensities_raw = list(np.interp(masses_raw, x, y))

            masses = []
            intensities = []
            for a, b in zip(masses_raw, intensities_raw):
                if b < highestPeak*intensityCutoff:
                    break
                masses.append(a)
                intensities.append(b)

            # calculate intensitySum
            intensitySum = float(sum(intensities))

            # if intensitySum < 20% of highest peak, continue
            #if intensitySum < highestPeak*intensityCutoff:
            #    continue

            if len(masses) < 3:
                continue

            # calculate theoretical pattern
            pattern = calcIsotopicPatternFromMass(mass*charge, len(masses))

            estimate = [b*intensitySum for a,b in pattern]

            # calculate error
            try:
                error = [abs(b*intensitySum-intensities[a]) for a,b in pattern]
                error = sum(error)/intensitySum*100
            except:
                print masses, intensities
                raise

            if best == None or error < best["error"]:
                best = {}
                best["error"] = error
                best["charge"] = charge
                best["masses"] = masses
                best["intensities"] = intensities
                best["estimate"] = estimate
    return best
