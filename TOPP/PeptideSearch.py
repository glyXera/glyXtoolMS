"""
Searches for peptide fragments within the MS2 spectra.
Especially peptide-ion and peptide+HexNAc occurence.
Ions are assumed to be singly charged.

""" 

import sys
import glyxtoolms

def countMassInSpectra(mass,tolerance,spectra):
    count = 0
    for spectrum in spectra:
        for peak in spectrum:
            if abs(peak.getMZ() - mass) < tolerance:
                count += 1
                break
    return count

def main(options):
    
    # parse parameters
    tolerance = float(options.tolerance)
    ionthreshold = float(options.ionthreshold)
    
    # load analysis file
    glyxXMLFile = glyxtoolms.io.GlyxXMLFile()
    glyxXMLFile.readFromFile(options.inGlyML)
    
    # loading mzML file
    exp = glyxtoolms.lib.openOpenMSExperiment(options.inMZML)

    rawSpectra = {}
    for spectrum in exp:
        rawSpectra[spectrum.getNativeID()] = spectrum
    
    scoredSpectra = {}
    for spectrum in glyxXMLFile.spectra:
        scoredSpectra[spectrum.getNativeId()] = spectrum
    
    features = {}
    for feature in glyxXMLFile.features:
        features[feature.getId()] = feature

    keep = []

    for hit in glyxXMLFile.glycoModHits:

        feature = features[hit.featureID]
            
        pepIon = hit.peptide.mass+glyxtoolms.masses.MASS["H+"]
        pepGlcNAcIon = pepIon+glyxtoolms.masses.GLYCAN["HEXNAC"]
        pepNH3 = pepIon-glyxtoolms.masses.MASS["N"] - 3*glyxtoolms.masses.MASS["H"]

        # search for hits in spectra
        foundA = 0
        foundB = 0
        spectraList = []
        for spectrumID in feature.getSpectraIds():
            if scoredSpectra[spectrumID].getLogScore() > 2.5:
                continue
            spectraList.append(rawSpectra[spectrumID])
            
        foundA = countMassInSpectra(pepIon,tolerance,spectraList)
        foundB = countMassInSpectra(pepGlcNAcIon,tolerance,spectraList)
        foundC = countMassInSpectra(pepNH3,tolerance,spectraList)
        
        if foundA + foundB + foundC == 0:
            continue
        hit.fragments = {}
        if foundA > 0:
            fragment = {}
            fragment["mass"] = pepIon
            fragment["sequence"] = hit.peptide.sequence
            fragment["counts"] = foundA
            hit.fragments["peptide"] = fragment
        if foundB > 0:
            fragment = {}
            fragment["mass"] = pepGlcNAcIon
            fragment["sequence"] = hit.peptide.sequence+"+HexNAC"
            fragment["counts"] = foundB
            hit.fragments["peptide+HexNAc"] = fragment
        if foundC > 0:
            fragment = {}
            fragment["mass"] = pepNH3
            fragment["sequence"] = hit.peptide.sequence+"-NH3"
            fragment["counts"] = foundC
            hit.fragments["peptide-NH3"] = fragment
        # search for peptide fragments
        p = hit.peptide
        fragmenthits = (None,{})
        for i in glyxtoolms.fragmentation.getModificationVariants(p):
            
            pepvariant = p.copy()
            pepvariant.modifications = i
            fragments = glyxtoolms.fragmentation.generatePeptideFragments(pepvariant)
            fhit = {}
            for fragmentkey in fragments:
                fragmentmass = fragments[fragmentkey][0]
                fragmentsequence = fragments[fragmentkey][1]
                spectrahits = countMassInSpectra(fragmentmass,tolerance,spectraList)
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
    parser.add_argument("--inMZML", dest="inMZML",
                        help="mzML file input")
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
