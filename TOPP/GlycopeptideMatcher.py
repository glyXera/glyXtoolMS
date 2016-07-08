# Tool for selecting possible glycan + peptide masses for given precursor masses

# Range Hex
# Range HexNAc
# Range Fucose
# Range NeuAc

# out: Glycancompositionfile.txt, each line containing one structure
      

def handle_args(argv=None):
    import argparse
    usage = "\nFile Glycan composition builder"
    parser = argparse.ArgumentParser(description=usage)
    parser.add_argument("--inAnalysis", dest="infileAnalysis",help="File input Analysis file .xml")
    parser.add_argument("--inGlycan", dest="infileGlycan",help="File input Glycan composition file .txt")
    parser.add_argument("--inPeptide", dest="infilePeptide",help="File input Glycopeptide file .xml")    
    parser.add_argument("--out", dest="outfile",help="File output Analysis file with appended Glycopeptide hits")
    parser.add_argument("--accuracy", dest="accuracy",help="Mass accuracy in Dalton")
                
    if not argv:
        args = parser.parse_args(sys.argv[1:])
    else:
        args = parser.parse_args(argv)
    return args


def main(options):
    print "parsing input parameters"
    tolerance = float(options.accuracy)
    
    print "parsing input files"
    # Analysis file
    glyML = glyxtoolms.io.GlyxXMLFile()
    glyML.readFromFile(options.infileAnalysis)
    # Peptide file
    pepFile = glyxtoolms.io.XMLPeptideFile()
    pepFile.loadFromFile(options.infilePeptide)
    # Glycan file
    glycans = []
    glycanFile = file(options.infileGlycan,"r")
    for line in glycanFile:
        glycan = glyxtoolms.lib.Glycan(line[:-1])
        glycans.append((glycan.mass,glycan))
    glycanFile.close()

    # sort glycan file for faster comparison
    glycans.sort()

    
    # remove old hits
    keepHits = []
    #~ accepted = {}
    #~ for hit in glyML.glycoModHits:
        #~ if hit.status == glyxtoolms.io.ConfirmationStatus.Accepted:
            #~ 
            #~ glycan = glyxtoolms.lib.Glycan(hit.glycan.composition)
            #~ hit.glycan.composition = glycan.toString()
            #~ keepHits.append(hit)
            #~ key = hit.peptide.toString() + ":"+glycan.toString()
            #~ thisset = accepted.get(key, set())
            #~ thisset.add(hit.feature.id)
            #~ accepted[key] = thisset
    glyML.glycoModHits = keepHits
    #~ print "keeping " + str(len(keepHits)) + " nr of manual accepted identifications"
    print "starting search for new identifcation hits"
    for feature in glyML.features:
        if feature.status == glyxtoolms.io.ConfirmationStatus.Rejected:
            continue
        precursorMass = feature.getMZ()*feature.getCharge()-glyxtoolms.masses.MASS["H+"]*(feature.getCharge()-1)
        found = False
        for peptide in pepFile.peptides:
            for glycanmass, glycan in glycans:
                mass = peptide.mass+glycanmass+glyxtoolms.masses.MASS["H+"]
                diff = mass-precursorMass
                if diff > tolerance:
                    break
                if abs(diff) > tolerance:
                    continue
                # check if an accepted hit exists already for feature
                #~ key = peptide.toString() + ":"+glycan.toString()
                #~ if feature.id in accepted.get(key, set()):
                    #~ continue
                hit = glyxtoolms.io.GlyxXMLGlycoModHit()
                hit.featureID = feature.getId()
                hit.glycan = glycan
                hit.peptide = peptide
                hit.error = diff
                glyML.glycoModHits.append(hit)

    print "found ",len(glyML.glycoModHits), " hits"
    print "writing output"
    glyML.writeToFile(options.outfile)
    #fout = file(options.outfile,"w")
    #fout.write("foo")
    #fout.close()
    print "done"
    return

import sys
import glyxtoolms
from itertools import product

if __name__ == "__main__":
    options = handle_args()
    main(options)
 
