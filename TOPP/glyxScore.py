import glyxsuite
from lxml import etree as ET
import sys
import datetime

def main(options):
    print "parsing glycan parameters:"
    glycans = options.glycanlist.split(" ")
    if options.glycanlistOpt != "None":
        glycans  += options.glycanlistOpt.split(",")
    glycans = list(set(glycans))
    print "glycanlist: ",glycans

    exp = glyxsuite.lib.openOpenMSExperiment(options.infile)

    # Initialize IonSeriesCalculator
    seriesCalc = glyxsuite.scoring.IonSeriesCalculator()

    # add glycans to IonSeriesCalculator
    print "adding glycans:"
    for glycan in glycans:
        print glycan, seriesCalc.addGlycan(glycan)

    # initialize output xml file
    glyxXMLFile = glyxsuite.io.GlyxXMLFile()
    parameters = glyxXMLFile.parameters
    parameters.setTimestamp(str(datetime.datetime.today()))
    source = exp.getSourceFiles()[0]
    parameters.setSourceFilePath(options.infile)
    parameters.setSourceFileChecksum(source.getChecksum())

    # write search parameters
    for glycan in glycans:
        parameters.addGlycan(glycan)
        
    parameters.setMassTolerance(str(options.tol))
    parameters.setIonThreshold(str(options.ionthreshold))
    parameters.setNrNeutrallosses(str(options.nrNeutralloss))
    parameters.setMaxOxoniumCharge(str(options.chargeOxIon))
    parameters.setScoreThreshold(str(options.scorethreshold))

    # score each spectrum
    lowQualtiySpectra = 0
    skippedSingleCharged = 0
    for spec in exp:
        if spec.getMSLevel() != 2:
            continue
        if spec.size() == 0:
            continue
        # create spectrum
        precursor = spec.getPrecursors()[0] # Multiple precurors currently not handled!
        s = glyxsuite.scoring.SpectrumGlyxScore(spec.getNativeID(),
                                                spec.getRT(),
                                                precursor.getMZ(),
                                                precursor.getCharge(),
                                                int(options.nrNeutralloss),
                                                int(options.chargeOxIon))
        logScore = 10
        if s.precursorCharge > 1:
            for peak in spec:
                s.addPeak(peak.getMZ(),peak.getIntensity())
            # check ionthreshold
            #if s.spectrumIntensity/float(spec.size()) >= float(options.ionthreshold):
            if s.highestPeakIntensity > float(options.ionthreshold):
                # make Ranking
                s.makeRanking()
                s.normIntensity()
                for glycan in glycans:
                    #s.findGlycanScore(seriesCalc, glycan, float(options.tol), float(options.ionthreshold))
                    s.findGlycanScore(seriesCalc, glycan, float(options.tol), 0)
            else:
                lowQualtiySpectra += 1
        else:
            skippedSingleCharged += 1

        logScore = s.calcTotalScore(float(options.scorethreshold))
        glyxXMLFile.spectra.append(s)
        #s.makeXMLOutput(xmlSpectra)

    print "skipped "+str(lowQualtiySpectra)+" low quality spectra"
    print "skipped "+str(skippedSingleCharged)+" singly charged spectra"
    print "writing outputfile"
    glyxXMLFile.writeToFile(options.outfile)
    #xmlTree = ET.ElementTree(xmlRoot)
    #f = file(options.outfile,"w")
    #f.write(ET.tostring(xmlTree,pretty_print=True))
    #f.close()
                    

def handle_args(argv=None):
    import argparse
    usage = "\nGlycopeptide Scoringtool for lowresolution MS/MS spectra"
    parser = argparse.ArgumentParser(description=usage)
    parser.add_argument("--in", dest="infile",help="File input")
    parser.add_argument("--out", dest="outfile",help="File output")
    parser.add_argument("--glycans", dest="glycanlist",help="Possible glycans as list")
    parser.add_argument("--glycansOpt", dest="glycanlistOpt",help="Possible glycans as commaseparated strings")
    parser.add_argument("--tol", dest="tol",help="Mass tolerance in th",type=float)
    parser.add_argument("--ionthreshold", dest="ionthreshold",help="Threshold for reporter ions", type=int)
    parser.add_argument("--nrNeutralloss", dest="nrNeutralloss",help="Possible nr of Neutrallosses (default: 1)",type=int)
    parser.add_argument("--chargeOxIon", dest="chargeOxIon",help="maximum charge of oxonium ions (default: 4)",type=int)
    parser.add_argument("--scorethreshold", dest="scorethreshold",help="Score threshold for identifying glycopeptide spectra",type=float)
    if not argv:
        args = parser.parse_args(sys.argv[1:])
    else:
        args = parser.parse_args(argv)
    return args

if __name__ == "__main__":
    options = handle_args()
    main(options)
