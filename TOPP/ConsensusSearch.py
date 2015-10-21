"""
Searches for peptide fragments within the MS2 spectra.
Especially peptide-ion and peptide+HexNAc occurence.
Ions are assumed to be singly charged.

""" 

import sys
import glyxsuite

def searchMassInSpectrum(mass,tolerance,spectrum):
    for peak in spectrum:
        if abs(peak.x - mass) < tolerance:
            return 1
    return 0
    
def calcChargedMass(singlyChargedMass,charge):
    mass = singlyChargedMass+(charge-1)*glyxsuite.masses.MASS["H"]
    return mass/float(charge)

def main(options):
    
    # parse parameters
    tolerance = float(options.tolerance)
    ionthreshold = float(options.ionthreshold)
    
    # load analysis file
    glyxXMLFile = glyxsuite.io.GlyxXMLFile()
    glyxXMLFile.readFromFile(options.inGlyML)
    
    scoredSpectra = {}
    for spectrum in glyxXMLFile.spectra:
        scoredSpectra[spectrum.getNativeId()] = spectrum
    
    features = {}
    for feature in glyxXMLFile.features:
        features[feature.getId()] = feature

    keep = []

    for hit in glyxXMLFile.glycoModHits:

        feature = features[hit.featureID]
        for charge in range(1,feature.getCharge()):
            pepIon = hit.peptide.mass+glyxsuite.masses.MASS["H+"]
            pepGlcNAcIon = pepIon+glyxsuite.masses.GLYCAN["HEXNAC"]
            pepNH3 = pepIon-glyxsuite.masses.MASS["N"] - 3*glyxsuite.masses.MASS["H"]
            
            # calc charged mass
            pepIon = calcChargedMass(pepIon,charge)
            pepGlcNAcIon = calcChargedMass(pepGlcNAcIon,charge)
            pepNH3 = calcChargedMass(pepNH3,charge)

            # search for hits in spectra
            consensusSpectrum = feature.consensus
            foundA = searchMassInSpectrum(pepIon,tolerance,consensusSpectrum)
            foundB = searchMassInSpectrum(pepGlcNAcIon,tolerance,consensusSpectrum)
            foundC = searchMassInSpectrum(pepNH3,tolerance,consensusSpectrum)

            hit.fragments = {}
            chargeName = "+("+str(charge)+"H+)"
            if foundA > 0:
                fragment = {}
                fragment["mass"] = pepIon
                fragment["sequence"] = hit.peptide.sequence+chargeName
                fragment["counts"] = foundA
                hit.fragments["peptide"+chargeName] = fragment
            if foundB > 0:
                fragment = {}
                fragment["mass"] = pepGlcNAcIon
                fragment["sequence"] = hit.peptide.sequence+"+HexNAC"+chargeName
                fragment["counts"] = foundB
                hit.fragments["peptide+HexNAc"+chargeName] = fragment
            if foundC > 0:
                fragment = {}
                fragment["mass"] = pepNH3
                fragment["sequence"] = hit.peptide.sequence+"-NH3"+chargeName
                fragment["counts"] = foundC
                hit.fragments["peptide-NH3"+chargeName] = fragment
        # search for peptide fragments
        p = hit.peptide
        fragmenthits = (None,{})
        for i in glyxsuite.fragmentation.getModificationVariants(p):
            
            pepvariant = p.copy()
            pepvariant.modifications = i
            fragments = glyxsuite.fragmentation.generatePeptideFragments(pepvariant)
            fhit = {}
            for fragmentkey in fragments:
                fragmentmass = fragments[fragmentkey][0]
                fragmentsequence = fragments[fragmentkey][1]
                spectrahits = searchMassInSpectrum(fragmentmass,tolerance,consensusSpectrum)
                if spectrahits > 0:
                    fhit[fragmentkey] = (fragmentmass,fragmentsequence,spectrahits)
                

            if len(fhit) > len(fragmenthits[1]):
                fragmenthits = (pepvariant,fhit)
        if fragmenthits[0] is not None:
            pepvariant,fhit = fragmenthits
            
            # write fragments to hit
            hit.peptide = pepvariant
            for fragmentname in fhit:
                fragment = {}
                fragment["mass"] = fhit[fragmentname][0]
                fragment["sequence"] = fhit[fragmentname][1]
                fragment["counts"] = fhit[fragmentname][2]
                hit.fragments[fragmentname] = fragment
        keep.append(hit)

    print "keeping " + str(len(keep)) + " glycopeptide hits from " + str(len(glyxXMLFile.glycoModHits))
    glyxXMLFile.glycoModHits = keep

    # write to output
    glyxXMLFile.writeToFile(options.outGlyML)
    print "done" 
    

def handle_args(argv=None):
    """ Handles input arguments """
    import argparse
    usage = "\nSearches for peptide evidence in HCD spectra"
    parser = argparse.ArgumentParser(description=usage)
    parser.add_argument("--inGlyML", dest="inGlyML",
                        help="glyML input")
    parser.add_argument("--outGlyML", dest="outGlyML",
                        help="glyML output")
    parser.add_argument("--tolerance", dest="tolerance",
                        help="Mass tolerance in th",
                        type=float)
    parser.add_argument("--ionthreshold", dest="ionthreshold",
                        help="Threshold for peptide ions",
                        type=int)
    if not argv:
        print "parameters", sys.argv[1:]
        args = parser.parse_args(sys.argv[1:])
    else:
        print "parameters", argv
        args = parser.parse_args(argv)
    return args

if __name__ == "__main__":
    main(handle_args())
