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
    """print "loading experiment"
    exp = pyopenms.MSExperiment()
    fh = pyopenms.FileHandler()
    fh.loadExperiment(options.infile,exp)
    print "loading finnished"          """

    # Initialize IonSeriesCalculator
    seriesCalc = glyxsuite.scoring.IonSeriesCalculator()
    """# check validity of each glycan
    for glycan in glycans:
        if not seriesCalc.hasGlycan(glycan):
            print "Cannot find glycan in SeriesCalculator, Aborting!"
            return
"""
    # add glycans to IonSeriesCalculator
    print "adding glycans:"
    for glycan in glycans:
        print glycan, seriesCalc.addGlycan(glycan)

    # initialize output xml file
    xmlRoot = ET.Element("glyxXML")
    xmlParameters = ET.SubElement(xmlRoot,"parameters")
    xmlSpectra = ET.SubElement(xmlRoot,"spectra")

    # write search parameters
    xmlParametersDate = ET.SubElement(xmlParameters,"timestamp")
    xmlParametersDate.text = str(datetime.datetime.today())

    xmlParametersGlycans = ET.SubElement(xmlParameters,"glycans")
    for glycan in glycans:
        xmlParametersGlycan = ET.SubElement(xmlParametersGlycans,"glycan")
        xmlParametersGlycan.text = glycan
    xmlParametersTol = ET.SubElement(xmlParameters,"tolerance")
    xmlParametersTol.text = str(options.tol)

    xmlParametersIonthreshold = ET.SubElement(xmlParameters,"ionthreshold")
    xmlParametersIonthreshold.text = str(options.ionthreshold)

    xmlParametersNeutral = ET.SubElement(xmlParameters,"nrNeutrallosses")
    xmlParametersNeutral.text = str(options.nrNeutralloss)

    xmlParametersOxionCharge = ET.SubElement(xmlParameters,"maxOxoniumionCharge")
    xmlParametersOxionCharge.text = str(options.chargeOxIon)

    xmlParametersScorethreshold = ET.SubElement(xmlParameters,"scorethreshold")
    xmlParametersScorethreshold.text = str(options.scorethreshold)


    # score each spectrum
    lowQualtiySpectra = 0
    skippedSingleCharged = 0
    for spec in exp:
        if spec.getMSLevel() != 2:
            continue
        if spec.size() == 0:
            continue
        # create spectrum
        for precursor in spec.getPrecursors(): # Multiple precurors will make native spectrum id nonunique!
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

            logScore = s.calcTotalScore()
            s.logScore = logScore
            s.makeXMLOutput(xmlSpectra)

    print "skipped "+str(lowQualtiySpectra)+" low quality spectra"
    print "skipped "+str(skippedSingleCharged)+" singly charged spectra"
    print "writing outputfile"
    xmlTree = ET.ElementTree(xmlRoot)
    f = file(options.outfile,"w")
    f.write(ET.tostring(xmlTree,pretty_print=True))
    f.close()
                    

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
