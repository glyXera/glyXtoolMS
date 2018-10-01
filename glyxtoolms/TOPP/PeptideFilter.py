# Tool for filtering digested peptides according to another peptide sequence list


# inFile: Proteinsequencefile (.fasta)
# Enzymelist
# Oxidation
# Carbamidation / Carboxylation
# AcrylamideAdducts
# Missed Cleavages
# out: Peptidefile, containing Peptidesequence, Modifications, Mass, Glycosylationsites

def handle_args(argv=None):
    import argparse
    usage = "\nFile Glycopeptide Filter tool"
    parser = argparse.ArgumentParser(description=usage)
    parser.add_argument("--inKeepPeptides", dest="inKeepPeptides",help="File input - whitelist peptides as .txt file")
    parser.add_argument("--inPeptideDigest", dest="inPeptideDigest",help="File input - digested peptides as .xml file")
    parser.add_argument("--out", dest="outfile",help="File output Glycopeptide file .xml")
    if not argv:
        args = parser.parse_args(sys.argv[1:])
    else:
        args = parser.parse_args(argv)
    return args


def main(options):
    
    print "loading peptide file"
    inPeptides = glyxtoolms.io.XMLPeptideFile()
    inPeptides.loadFromFile(options.inPeptideDigest)
    
    print "loading whitelist peptides"
    f = file(options.inKeepPeptides, "r")
    whitelistPeptides = set()
    for line in f:
        # test if peptide is valid
        p = glyxtoolms.io.XMLPeptide() 
        p.fromString(line[:-1])
        whitelistPeptides.add(p.sequence)
    if len(whitelistPeptides) == 0:
        raise Exception("cannot find any peptides in whitelistPeptides")
    
    keepPeptides = []
    for peptide in inPeptides.peptides:
        if peptide.sequence in whitelistPeptides:
            keepPeptides.append(peptide)
    
    print "writing to file"
    inPeptides.peptides = keepPeptides
    inPeptides.writeToFile(options.outfile)

    print "done"
    return

import sys
import glyxtoolms

if __name__ == "__main__":
    options = handle_args()
    main(options)
 
 
