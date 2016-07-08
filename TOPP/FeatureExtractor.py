# Tool for combining a featureXML file with a glyxML file - Extracts all glycopeptide features under a given threshold


#  in1: glyxML analysis file
#  in2: featureXML file
# out1: glyML analysis file with appended features
# out2: featureXML file only containing glycopeptide features

def handle_args(argv=None):
    import argparse
    usage = "\nFile Glycopeptide Feature extractor tool"
    parser = argparse.ArgumentParser(description=usage)
    parser.add_argument("--inFeature", dest="infileFeature",help="File input - featureXML file")
    parser.add_argument("--inAnalysis", dest="infileAnalysis",help="File input glyXML analysis file")
    #parser.add_argument("--outFeature", dest="outfileFeature",help="File output Feature file")
    parser.add_argument("--out", dest="outfile",help="File output Analysis file")
    parser.add_argument("--logscore", dest="logscore",help="score cutoff for glycopeptides")
    parser.add_argument("--keepSingleCharged", dest="keepSingleCharged",help="Keep or dismiss singly charged features")
    parser.add_argument("--checkPrecursorCharge", dest="checkPrecursorCharge",help="Check if precursor charge is identical to feature charge")
    if not argv:
        args = parser.parse_args(sys.argv[1:])
    else:
        args = parser.parse_args(argv)
    return args


def main(options):
    
    print "loading feature file"
    fm = pyopenms.FeatureMap()
    fh = pyopenms.FeatureXMLFile()
    fh.load(options.infileFeature,fm)
    
    print "loading analysis file"
    glyML = glyxtoolms.io.GlyxXMLFile()
    glyML.readFromFile(options.infileAnalysis)
    
    # reset features
    glyML.features = []
    print "loading finnished"          
    
    # initiate new Featuremap or Glycopeptidefeatures
    fi = pyopenms.FeatureMap()
    spectra = {}
    for feature in fm:
        if options.keepSingleCharged == "false" and feature.getCharge() == 1:
            continue
        hull = feature.getConvexHull().getBoundingBox()
        minRT,minMZ = hull.minPosition()
        maxRT,maxMZ = hull.maxPosition()
        spectraHits = []
        for spectrum in glyML.spectra:
            spectrumKey = spectrum.getNativeId()
            if not spectrumKey in spectra:
                spectra[spectrumKey] = 0 # no glycopeptide
            if spectrum.getLogScore() > float(options.logscore):
                continue
            rt = spectrum.getRT()
            mz = spectrum.getPrecursorMass()
            if spectra[spectrumKey] < 1:
                spectra[spectrumKey] = 1 # no feature
            if minRT > rt or rt > maxRT:
                continue
            if minMZ > mz or mz > maxMZ:
                continue
            if feature.getCharge() != spectrum.getPrecursorCharge():
                if spectra[spectrumKey] < 2:
                    spectra[spectrumKey] = 2 # wrong spectrum charge
                if options.checkPrecursorCharge == "true":
                    continue
            if spectra[spectrumKey] < 3:
                spectra[spectrumKey] = 3 # hit
            spectraHits.append(spectrum.getNativeId())
        if len(spectraHits) == 0:
            continue
            

            
        # create glyxMLFeature
        glyxFeature = glyxtoolms.io.GlyxXMLFeature()
        glyxFeature.setId(feature.getUniqueId())
        glyxFeature.setRT(feature.getRT())
        glyxFeature.setMZ(feature.getMZ())
        glyxFeature.setIntensity(feature.getIntensity())
        glyxFeature.setCharge(feature.getCharge())
        glyxFeature.setBoundingBox(minRT,maxRT,minMZ,maxMZ)
        for spectrumId in spectraHits:
            glyxFeature.addSpectrumId(spectrumId)
        
        glyML.addFeature(glyxFeature)
        
        # add feature to featuremap
        fi.push_back(feature)
        pass
    
    
    # count spectra hits
    noGlyco = 0
    noFeature = 0
    wrongCharge = 0
    hit = 0
    for spectrumKey in spectra:
        if spectra[spectrumKey] == 0:
            noGlyco += 1
        elif spectra[spectrumKey] == 1:
            noFeature += 1
        elif spectra[spectrumKey] == 2:
            wrongCharge += 1
        else:
            hit += 1
    print noGlyco, " spectra are no glycopeptide"
    print noFeature, " spectra lay outside of any feature"
    if options.checkPrecursorCharge == "true":
        print wrongCharge, " spectra have a different charge than their feature and are ignored"
    else:
        print wrongCharge, " spectra have a different charge than their feature but are still used"
    print hit, " spectra are in a feature with right charge"
            
        
    # write glyML file
    print "writing Analysis file to ",options.outfile
    glyML.writeToFile(options.outfile)
    
    # write feature file
    """print "writing Feature file to ",options.outfileFeature
    fi.setDataProcessing(fm.getDataProcessing())
    fi.ensureUniqueId()
    fh.store(options.outfileFeature,fi)
    """
    print "finished"


import sys
import pyopenms
import glyxtoolms

if __name__ == "__main__":
    options = handle_args()
    main(options)
