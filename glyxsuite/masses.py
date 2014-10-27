"""
Mass list of aminoacids, protenimodifications, glycan monomers, etc.
Contains also all functions for mass calculation.
Source of mass values from: 
http://web.expasy.org/findmod/findmod_masses.html
"""
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
     
