"""
Mass list of aminoacids, protenimodifications, glycan monomers, etc.
Contains also all functions for mass calculation.
Source of mass values from: 
http://web.expasy.org/findmod/findmod_masses.html
"""
import re
import math
import itertools
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
PROTEINMODIFICATION["Cys_CAM"] = 57.021464 
# Cys_CM, Iodoacetic acid treatment (carboxylation)
PROTEINMODIFICATION["Cys_CM"] = 58.005479 
# Cys_PAM Acrylamide Adduct
PROTEINMODIFICATION["Cys_PAM"] = 71.03712 
PROTEINMODIFICATION["MSO"] = 15.884915 # MSO
PROTEINMODIFICATION["ACET"] = 42.0106 # Acetylation
PROTEINMODIFICATION["AMID"] = -0.9840 # Amidation
PROTEINMODIFICATION["DEAM"] = 0.9840 # Deamidation
PROTEINMODIFICATION["HYDR"] = 15.9949 # Hydroxylation
PROTEINMODIFICATION["METH"] = 14.0157 # Methylation
PROTEINMODIFICATION["PHOS"] = 79.9663 # Phosphorylation

# ------------------------------ Glycans ------------------------------#

GLYCAN = {}
GLYCAN["DHEX"] = 146.0579
GLYCAN["HEX"] =  162.0528
GLYCAN["HEXNAC"] =  203.0794
GLYCAN["NEUAC"] = 291.0954


# --------------------------- Other masses ----------------------------#
MASS = {}
MASS["H2O"] = 18.01057
MASS["H+"] = 1.00728
MASS["H"] = 1.00783

# ----------------------------- Isotopes ------------------------------#
"""
Dictionary of isotopes, containing massshift, actual atomic mass
and the probability of the isotope
"""
ISOTOPES = {}
ISOTOPES["H"] = {0:(1.007825,99.9885),1:(2.014102,0.0115)}
ISOTOPES["C"] = {0:(12.0,98.93),1:(13.003355,1.07)}
ISOTOPES["N"] = {0:(14.003074,99.632),1:(15.000109,0.368)}
ISOTOPES["O"] = {0:(15.994915,99.757),
                 1:(16.999132,0.038),
                 2:(17.999160,0.205)}
ISOTOPES["S"] = {0:(31.972071,94.93),
                 1:(32.971458,0.76),
                 2:(33.967867,4.29),
                 3:(35.967081,0.02)}

# ------------------------------- Functions ---------------------------#
def calcPeptideMass(sequence):
    mass = MASS["H2O"]
    for s in sequence:
        try: 
            mass += AMINOACID[s]
        except KeyError:
            print "Unknown Aminoacid '"+s+"'!"
            raise
    return mass   
     

def calcIonMass(name):
    """
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
    
    if re.match("^(\(.+?\)-?\d+)+$",name) == None:
        raise Exception(
        """Input string '{}' doesn't follow the regex '^(\(.+?\)-?\d+)+$'
        Please surrond monomers by brackets followed by the amount of 
        the monomer, e.g. '(NeuAc)1(H2O)-1(H+)1'""".format(name))
    
    mass = 0
    charge = 0
    for part in re.findall("\(.+?\)-?\d+",name.upper()):
        monomer,amount = part.split(")")
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
        else:
            raise Exception("cannot find monomer {} in {}".format(monomer,name))
    if charge == 0:
        return mass
    else:
        return mass/float(charge)
    
def calculateIsotopicPattern(C=0,H=0,N=0,O=0,S=0,maxShift=10):
    """
    Calculates the isotopic pattern of the given elemental composition
    Currently only supports C,H,N,O and S
    maxShift option sets the calculated pattern size, which significantly
    speeds up the calculation
    
    Result: tuple of summed probability (if significantly smaller than 1
        increase maxShift), the monoisotopic mass and the pattern
    """
            
    def element(name,N,maxShift=10):
        """
        Generates the isotpic pattern of an element with a given number N of
        atoms. maxShift option sets maximum pattern size
        
        Result: dict of massshift and probabilities
        """
                
        def _binominal(n,k):
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
                raise Exception("The sum of k has to equal n!")
            divisor = 1
            for k in newK:
                divisor *= math.factorial(k)
            return math.factorial(n)/divisor
        
        # generate isotope list
        isotope = []
        shifts = sorted(ISOTOPES[name])
        summ = sum([ISOTOPES[name][shift][1] for shift in shifts])
        for shift in shifts:
            isotope.append((shift,ISOTOPES[name][shift][1]/summ))

        # Generate amount ranges for each isotope, limited by the
        # maximum shift allowed
        amountList = []
        for shift,p in isotope:
            if shift == 0:
                amountList.append(range(0,N+1))
            else:
                amountList.append(range(0,int(math.ceil(maxShift/shift))))
        masses = {}
        for amounts in itertools.product(*amountList):
            if sum(amounts) != N:
                continue
            p = _binominal(N,amounts)
            mass = 0
            for i,amount in enumerate(amounts):
                shift,probability = isotope[i]
                p *= probability**amount
                mass += shift*amount
            masses[mass] = masses.get(mass,0)+p
        trans = {}
        for mass in masses:
            if mass > maxShift and maxShift != 0:
                continue
            trans[mass] = masses[mass]
        return trans    
    
    probs = []
    monoMass = 0
    if C > 0:
        probs.append(element("C",C,maxShift=maxShift))
        monoMass += C*ISOTOPES["C"][0][0]
    if H > 0:
        probs.append(element("H",H,maxShift=maxShift))
        monoMass += H*ISOTOPES["H"][0][0]
    if N > 0:
        probs.append(element("N",N,maxShift=maxShift))   
        monoMass += N*ISOTOPES["N"][0][0]
    if O > 0:
        probs.append(element("O",O,maxShift=maxShift))
        monoMass += O*ISOTOPES["O"][0][0]
    if S > 0:
        probs.append(element("S",S,maxShift=maxShift))
        monoMass += S*ISOTOPES["S"][0][0]
    elementKeys = [e.keys() for e in probs]
    masses = {}
    for amounts in itertools.product(*elementKeys):
        shift = sum(amounts)
        if shift > maxShift:
            continue
        p = 1
        for i,amount in enumerate(amounts):
            p *= probs[i][amount]
        masses[shift] = masses.get(shift,0) + p
        
    maxProb = max([masses[shift] for shift in masses])
    
    
    # test if accumulated probability accounts for 
    sumProb = sum([masses[shift] for shift in masses])
    #print "sumProb",sumProb
    trans = []
    for shift in sorted(masses.keys()):
        trans.append((shift,masses[shift]/maxProb*100))
        #print shift,masses[shift]/maxProb*100
    return sumProb,monoMass,trans
    
    
