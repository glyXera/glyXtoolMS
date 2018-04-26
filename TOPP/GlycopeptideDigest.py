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
    parser.add_argument("--out", dest="outfile",help="File output Glycopeptide file .xml")
    parser.add_argument("--enzymes", dest="enzymes",help="Digestion enzymes: Comma separated list of [Trypsin, AspN]")
    parser.add_argument("--maxNrModifications", dest="maxNrModifications",help="Nr of maximum allowed modifications. CYS_CAM, CYS_CM are excluded. Unlimited with -1.")
    parser.add_argument("--modifications", dest="modifications",help="variable modifications: List of [None,AMID,CAM,CYS_CAM,NTERM_CAM,CM,CYS_CM,DEAM,ASN_DEAM,GLN_DEAM,DEHYDR,SER_DEHYDR,THR_DEHYDR,DIOX,TRP_DIOX,TYR_DIOX,MSO,OX,TRP_OX,TYR_OX,CYS_PAM,PHOS,SER_PHOS,THR_PHOS,TYR_PHOS")
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

    print "setting digest parameters"
    proteinDigest = glyxtoolms.lib.ProteinDigest()

    for modification in options.modifications.split(" "):
        if modification.lower() == "none":
            continue
        proteinDigest.addModification(modification)

    missedCleavages = int(options.missedCleavageSites)
    
    proteinDigest.setMaxModifications(int(options.maxNrModifications))
    proteinDigest.setMaxMissedCleavage(2)
    
    findOGlycosylation = "O-Glycosylation" in options.glycosylation
    findNGlycosylation = "N-Glycosylation" in options.glycosylation
    findNXCGlycosylation = "NXC-Glycosylation" in options.glycosylation

    # initialize outfile parameters
    # TODO: Set maxModifications in parameters
    parameters = glyxtoolms.io.XMLPeptideParameters()
    parameters.modifications = list(proteinDigest.modifications)
    parameters.missedCleavages = missedCleavages
    parameters.modifications = list(proteinDigest.modifications)
    parameters.NGlycosylation = (findNGlycosylation or findNXCGlycosylation)
    parameters.OGlycosylation = findOGlycosylation
    
    # add digests
    for digest in options.enzymes.split(" "):
        parameters.digestionEnzymes.append(digest)
        if digest == "Trypsin":
            proteinDigest.addEnzyme_Trypsin()
        elif digest == "Trypsin/P":
            proteinDigest.addEnzyme_Trypsin_lowSpecific()
        elif digest == "AspN":
            proteinDigest.addEnzyme_AspN()
        elif digest == "AspN2":
            proteinDigest.addEnzyme_AspN2()
        elif digest == "ProtK":
            proteinDigest.addEnzyme_ProtK()
        elif digest == "Unspecific":
            proteinDigest.addEnzyme_Unspecific()
        elif digest == "NoDigest":
            pass
        else:
            raise Exception("Unknown digestion enzyme used!")
            
            
    print "make digests"
   
    allGlycopeptides = []
    for fastaEntry in fastaData:
        protein = glyxtoolms.lib.Protein()
        try:
            protein.loadFromFasta(fastaEntry)
        except:
            print "could not read " + fastaEntry.identifier
            continue
        parameters.proteins.append(fastaEntry.identifier)
        
        # digest protein
        peptides = proteinDigest.digest(protein)
        
        # find glycopeptides
        glycopeptides = proteinDigest.findGlycopeptides(peptides,
                                    findNGlycosylation,
                                    findOGlycosylation,
                                    findNXCGlycosylation)
        allGlycopeptides += glycopeptides
    
    
    print "found ",len(allGlycopeptides), " peptides"
    
    print "writing to file"
    outf = glyxtoolms.io.XMLPeptideFile()
    outf.peptides = allGlycopeptides
    outf.parameters = parameters
    print options.outfile
    outf.writeToFile(options.outfile)

    print "done"
    return

import sys
import pyopenms
import glyxtoolms

if __name__ == "__main__":
    options = handle_args()
    main(options)
 
