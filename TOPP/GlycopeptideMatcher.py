# Tool for selecting possible glycan + peptide masses for given precursor masses

# out: Glycancompositionfile.txt, each line containing one structure
      

def handle_args(argv=None):
    import argparse
    usage = "\nFile Glycan composition builder"
    parser = argparse.ArgumentParser(description=usage)
    parser.add_argument("--inAnalysis", dest="infileAnalysis",help="File input Analysis file .xml")
    parser.add_argument("--inGlycan", dest="infileGlycan",help="File input Glycan composition file .txt")
    parser.add_argument("--inPeptide", dest="infilePeptide",help="File input Glycopeptide file .xml")    
    parser.add_argument("--out", dest="outfile",help="File output Analysis file with appended Glycopeptide hits")
    parser.add_argument("--tolerance", dest="tolerance",
                        help="Mass tolerance in either Da or ppm",
                        type=float)
    parser.add_argument("--toleranceType", dest="toleranceType",
                        help="Type of the given mass tolerance",
                        choices=["Da", "ppm"])
                
    if not argv:
        args = parser.parse_args(sys.argv[1:])
    else:
        args = parser.parse_args(argv)
    return args


def main(options):
    print "parsing input parameters"
    tolerance = float(options.tolerance)
    toleranceType = options.toleranceType
    
    print "parsing input files"
    # Analysis file
    glyML = glyxtoolms.io.GlyxXMLFile()
    glyML.readFromFile(options.infileAnalysis)
    # Peptide file
    pepFile = glyxtoolms.io.XMLPeptideFile()
    pepFile.loadFromFile(options.infilePeptide)
    # Glycan file
    glycans = []
    glycanFile = glyxtoolms.io.GlycanCompositionFile()
    glycanFile.read(options.infileGlycan)
    for glycan in glycanFile.glycans:
        glycans.append((glycan.mass,glycan))

    # sort glycan file for faster comparison
    glycans.sort()
    
    # remove old hits
    keepHits = []
    glyML.glycoModHits = keepHits
    print "starting search for new identifcation hits"
    for feature in glyML.features:
        if feature.status == glyxtoolms.io.ConfirmationStatus.Rejected:
            continue
        #precursorMass = feature.getMZ()*feature.getCharge()-glyxtoolms.masses.MASS["H+"]*(feature.getCharge()-1)
        found = False
        for peptide in pepFile.peptides:
            # collect glycosylation types for peptide
            glycosites = set()
            glycosites.add("?")
            for pos,site in peptide.glycosylationSites:
                glycosites.add(site)
            
            for glycanmass, glycan in glycans:
                mass = (peptide.mass+glycanmass+glyxtoolms.masses.MASS["H+"]*feature.getCharge())/float(feature.getCharge())
                error = glyxtoolms.lib.calcMassError(feature.getMZ(), mass, toleranceType)
                if error > tolerance:
                    break
                if abs(error) > tolerance:
                    continue
                # check if glycan type can exist on the peptides glycosylationsites
                if glycan.typ not in glycosites:
                    continue
                    
                # check if an accepted hit exists already for feature
                hit = glyxtoolms.io.GlyxXMLGlycoModHit()
                hit.featureID = feature.getId()
                hit.glycan = glycan
                hit.peptide = peptide
                hit.error = mass - feature.getMZ()
                glyML.glycoModHits.append(hit)

    print "found ",len(glyML.glycoModHits), " hits"
    print "writing output"
    glyML.writeToFile(options.outfile)
    print "done"
    return

import sys
import glyxtoolms
from itertools import product

if __name__ == "__main__":
    options = handle_args()
    main(options)
 
