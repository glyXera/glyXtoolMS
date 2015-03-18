"""
Mass list of aminoacids, protenimodifications, glycan monomers, etc.
Contains also all functions for mass calculation.
Source of mass values from: 
http://web.expasy.org/findmod/findmod_masses.html
"""
import re

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
    
