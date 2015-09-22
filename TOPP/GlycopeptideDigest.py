# Tool for digesting Proteins and extracting occuring glycopeptide sequences


# inFile: Proteinsequencefile (.fasta)
# Enzymelist
# Oxidation
# Carbamidation / Carboxylation
# AcrylamideAdducts
# Missed Cleavages
# out: Peptidefile, containing Peptidesequence, Modifications, Mass, Glycosylationsites

def handle_args(argv=None):
    import argparse
    usage = "\nFile Glycopeptide Digestor tool"
    parser = argparse.ArgumentParser(description=usage)
    parser.add_argument("--inFasta", dest="infile",help="File input - Protein sequences as .fasta file")
    parser.add_argument("--out", dest="outfile",help="File output Glycopeptide file .glycopep")
    parser.add_argument("--enzymes", dest="enzymes",help="Digestion enzymes: Comma separated list of [Trypsin, AspN]")
    parser.add_argument("--cystTreatment", dest="cystTreatment",help="Cystein treatment (C): Either None, Iodacetic acid or Iodoacetamide")
    parser.add_argument("--modifications", dest="modifications",help="variable modifications: List of [Oxidation (M),AcrylamideAdduct (C)]")
    parser.add_argument("--glycosylation", dest="glycosylation",help="Glycosylation: List of [N-Glycosylation,O-Glycosylation]")
    parser.add_argument("--missedCleavageSites", dest="missedCleavageSites",help="maximum missed cleavage sites")
                
    if not argv:
        args = parser.parse_args(sys.argv[1:])
    else:
        args = parser.parse_args(argv)
    return args


def main(options):
    
    print "loading fasta file"
    fh = pyopenms.FASTAFile()
    fastaData = []
    fh.load(pyopenms.String(options.infile),fastaData)
    
    # initialize outfile parameters
    
    parameters = glyxsuite.io.XMLPeptideParameters()

    print "setting digest parameters"
    proteinDigest = glyxsuite.lib.ProteinDigest()
    
    if options.cystTreatment == "None":
        proteinDigest.setCarbamidation(False)
        proteinDigest.setCarboxylation(False)
    elif options.cystTreatment == "Iodacetic acid":
        parameters.modifications.append(options.cystTreatment)
        proteinDigest.setCarbamidation(False)
        proteinDigest.setCarboxylation(True)
    elif options.cystTreatment == "Iodoacetamide":
        parameters.modifications.append(options.cystTreatment)
        proteinDigest.setCarbamidation(True)
        proteinDigest.setCarboxylation(False)
    else:
        raise Exception("Unspecified Cystein treatment!")

    for modification in options.modifications.split(" "):
        if modification == "Oxidation(M)":
            proteinDigest.setOxidation(True)
        elif modification == "AcrylamideAdduct(C)":
            proteinDigest.setAcrylamideAdducts(True)
        elif modification == "None":
            continue
        else:
            raise Exception("Unknown modification used!")
        parameters.modifications.append(modification)
    
    missedCleavages = int(options.missedCleavageSites)
    parameters.missedCleavages = missedCleavages
    findOGlycosylation = "O-Glycosylation" in options.glycosylation
    findNGlycosylation = "N-Glycosylation" in options.glycosylation
    parameters.NGlycosylation = findNGlycosylation
    parameters.OGlycosylation = findOGlycosylation

    digests = []
    for digest in options.enzymes.split(" "):
        parameters.digestionEnzymes.append(digest)
        if digest == "Trypsin":
            digests.append(proteinDigest.add_tryptic_digest)
        elif digest == "AspN":
            digests.append(proteinDigest.add_AspN_digest)
        elif digest == "Unspecific":
            digests.append(proteinDigest.add_Unspecific_digest)
        else:
            raise Exception("Unknown digestion enzyme used!")
            
            
    print "make digests"
   
    allGlycopeptides = []
    for fastaEntry in fastaData:
        protein = glyxsuite.lib.Protein()
        
        protein.loadFromFasta(fastaEntry.identifier,fastaEntry.description,fastaEntry.sequence)
        parameters.proteins.append(protein)
        proteinDigest.newDigest(protein)
        # call digest functions to set cleavage sites
        for digestFunc in digests:
            digestFunc()
        # digest protein
        peptides = proteinDigest.digest(missedCleavages)
        
        # find glycopeptides
        glycopeptides = proteinDigest.findGlycopeptides(peptides,
                                    findNGlycosylation,
                                    findOGlycosylation)
        allGlycopeptides += glycopeptides
    
    
    print "found ",len(allGlycopeptides), " peptides"
    
    print "writing to file"
    outf = glyxsuite.io.XMLPeptideFile()
    outf.peptides = allGlycopeptides
    outf.parameters = parameters
    print options.outfile
    outf.writeToFile(options.outfile)

    print "done"
    return

import sys
import pyopenms
import glyxsuite

if __name__ == "__main__":
    options = handle_args()
    main(options)
 
