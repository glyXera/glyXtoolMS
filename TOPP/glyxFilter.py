"""
Uses Filter on MS2 spectra to identify glycopeptide features

Input: - Filter parameters
       - mzml File with picked MS2 spectra
       - feature file with MS1 features

"""

import sys
import math
import itertools
import datetime

import glyxsuite
import pyopenms

class Peak(object):
    """  Stores all relevant information to make the scoring on the spectrum

        Input: mass and intensity
    """

    def __init__(self, mass, intensity):
        self.mass = mass
        self.intensity = intensity
        self.normedIntensity = 0
        self.intensityPercent = 0
        self.ionname = None
        self.rank = 0

class Score(glyxsuite.io.GlyxXMLSpectrum, object):
    """ Glyxfilter scoring class

    Usage:  a) initialize Score with information about the
               spectrum: id, rt, precurosr mass and charge
            b) add peaks from the original spectrum via
               addPeak(mass, intensity)
            c) run peak ranking via makeRanking()
            d) normalize peak intensities via normIntensity()
            e) run scoring via
                makeScoring(oxoniumIons, ionthreshold, tolerance)

                oxoniumIons is a dict with the name as key, and
                a dict as value containing
                {"mass":00, "charge":0, "depends": other oxonium ion"}

    Result: after scoring the score value can be read via the function
                getLogScore()
    """
    def __init__(self, nativeId, spectrumRT, precursorMass, precursorCharge, precursorIntensity, feature):
        """ initialize Score with information about the spectrum
            Input: id, rt, precursor mass and charge """

        super(Score, self).__init__()
        self.nativeId = nativeId
        self.rt = spectrumRT
        self.precursorCharge = precursorCharge
        self.precursorMass = precursorMass
        self.precursorIntensity = precursorIntensity
        self.intensity_sum = 0
        self.highest_intensity = 0
        self.peaks = []
        self.logScore = 10
        self.oxoniumIons = []
        self.oxoniumLosses = []
        self.neutralLosses = []
        self.feature = feature

    def addPeak(self, mass, intensity):
        """ add a spectrum peak to the scoring with its mass and intensity
            Input: mass, intensity """
        p = Peak(mass, intensity)
        if intensity > self.highest_intensity:
            self.highest_intensity = intensity
        self.intensity_sum += intensity
        self.peaks.append(p)
        return p

    def normIntensity(self):
        """ norm all peaks to the sum of the spectrum intensity
            Input: None """
        for peak in self.peaks:
            peak.normedIntensity = peak.intensity/float(self.intensity_sum)
            peak.intensityPercent = peak.intensity/float(self.highest_intensity)*100

    def makeRanking(self):
        """ rank all peaks accoring to their intensity
            Input: None """
        intensitySort = [(p.intensity, p) for p in self.peaks]
        intensitySort.sort(reverse=True)
        for i, pair in enumerate(intensitySort):
            p = pair[1]
            p.rank = i+1

    def makeScoring(self, oxoniumIons, ionthreshold, tolerance):
        """Runs scoring function on the previously added peaks
           Input: oxoniumIons, ionthreshold(float), tolerance(float)
            oxoniumIons is a dict with the name as key, and
            a dict as value containing
            {"mass":00, "charge":0, "depends": other oxonium ion"}"""
        
        # find oxonium ions
        foundOxoniumIons = {}
        for peak in self.peaks:
            if peak.intensity < ionthreshold:
                continue
            for oxname in oxoniumIons:
                if abs(peak.mass - oxoniumIons[oxname]["mass"]) < tolerance:
                    foundOxoniumIons[oxname] = foundOxoniumIons.get(oxname, []) + [peak]

        # count if at least 2 oxoniumions are found
        if len(foundOxoniumIons) < 2:
            return

        # check dependencies of oxoniumions
        todelete = set()
        for oxname in foundOxoniumIons:
            if not "depends" in oxoniumIons[oxname]:
                continue
            for dependency in oxoniumIons[oxname]["depends"]:
                if dependency not in foundOxoniumIons:
                    todelete.add(oxname)

        # delete unfullfilled dependencies
        for oxname in todelete:
            foundOxoniumIons.pop(oxname)

        # count if at least 2 oxoniumions are found
        if len(foundOxoniumIons) < 2:
            return

        self.oxoniumIons = []
        self.oxoniumLosses = []
        
        for oxname in foundOxoniumIons:
            highest = max([peak for peak in foundOxoniumIons[oxname]],
                          key=lambda x: x.intensity)
            highest.ionname = oxname
            self.oxoniumIons.append(highest)

        # Look for oxonium losses and neutra losses
        oxoniumLosses = {}
        for peak, oxname in itertools.product(self.peaks,
                                              oxoniumIons):
            if peak.intensity < ionthreshold:
                continue
            mzOx = oxoniumIons[oxname]["mass"]
            chargeOx = oxoniumIons[oxname]["charge"]

            if chargeOx >= self.precursorCharge:
                continue

            mz_loss = ((self.precursorMass*self.precursorCharge-mzOx*chargeOx)/
                       (self.precursorCharge-chargeOx))

            if abs(mz_loss - peak.mass) < tolerance:
                oxoniumLosses[oxname] = oxoniumLosses.get(oxname, []) +[peak]

        for oxname in oxoniumLosses:
            highest = max([peak for peak in oxoniumLosses[oxname]],
                          key=lambda x: x.intensity)
            highest.ionname = "Loss: "+oxname
            self.oxoniumLosses.append(highest)
            

        scorevalue = 0
        for peak in self.oxoniumIons+self.oxoniumLosses:
            self.addIon("", peak.ionname, peak.mass, peak.intensityPercent)
            scorevalue += peak.normedIntensity/peak.rank
            
        if scorevalue > 0:
            scorevalue = -math.log10(scorevalue)
        else:
            scorevalue = 10
        self.setLogScore(scorevalue)

def parseOxoniumIons(options):
    """ Create oxonium ion list used for the spectrum scoring
        Uses information from the options parameter:
        options.hasSial = "True" -> adds sialic acid containing oxoniumions
        options.hasFucose = "True" -> adds fucose containing oxoniumions

        Additional oxoniumions can be included via options.oxoniumions
        with each oxiniumion separated by ', '
        Each oxoniumion has to look like this'(NeuAc)1(H2O)-1(H+)1' """
    oxoniumIons = {}

    oxoniumIons['(HexNAc)1(H+)1'] = {'charge':1, 'depends':['(HexNAc)1(H2O)-1(H+)1']}
    oxoniumIons['(HexNAc)1(H2O)-1(H+)1'] = {'charge':1, 'depends':['(HexNAc)1(H+)1']}

    oxoniumIons['(Hex)1(H+)1'] = {'charge':1, 'depends':['(Hex)1(H2O)-1(H+)1']}
    oxoniumIons['(Hex)1(H2O)-1(H+)1'] = {'charge':1, 'depends':['(Hex)1(H+)1']}

    oxoniumIons['(HexNAc)1(Hex)1(H+)1'] = {'charge':1}

    # N-Glycan core
    oxoniumIons['(HexNAc)1(Hex)2(H+)1'] = {'charge':1}

    # Sialic acid
    if options.hasSial == "true":
        oxoniumIons['(NeuAc)1(H+)1'] = {'charge':1, 'depends':['(NeuAc)1(H2O)-1(H+)1']}
        oxoniumIons['(NeuAc)1(H2O)-1(H+)1'] = {'charge':1, 'depends':['(NeuAc)1(H+)1']}

        oxoniumIons['(Hex)1(HexNAc)1(NeuAc)1(H+)1'] = {'charge':1, 'depends':['(NeuAc)1(H+)1']}
        oxoniumIons['(Hex)2(HexNAc)1(NeuAc)1(H+)1'] = {'charge':1, 'depends':['(NeuAc)1(H+)1']}

    # Fucose
    if options.hasFucose == "true":
        oxoniumIons['(dHex)1(H+)1'] = {'charge':1, 'depends':['(dHex)1(H2O)-1(H+)1']}
        oxoniumIons['(dHex)1(H2O)-1(H+)1'] = {'charge':1, 'depends':['(dHex)1(H+)1']}
        oxoniumIons['(HexNAc)1(Hex)1(dHex)1(H+)1'] = {'charge':1, 'depends':['(Hex)1(H+)1']}

    # Fucose and Sialic acid
    if options.hasSial == "true" and options.hasFucose == "true":
        oxoniumIons['(Hex)1(HexNAc)1(NeuAc)1(dHex)1(H+)1'
                   ] = {'charge':1,
                        'depends':['(NeuAc)1(H+)1', '(dHex)1(H+)1']}

    for name in oxoniumIons:
        oxoniumIons[name]["mass"] = glyxsuite.masses.calcIonMass(name)[0]
    if len(options.oxoniumions) > 0:
        for name in list(set(options.oxoniumions.split(","))):
            mass, charge = glyxsuite.masses.calcIonMass(name)
            oxoniumIons[name] = {}
            oxoniumIons[name]["mass"] = mass
            oxoniumIons[name]["charge"] = charge
    return oxoniumIons


def main(options):
    """ Scores a given mzML file with a given featurefile """

    oxoniumIons = parseOxoniumIons(options)
    print "------oxoniumIonList-----"
    for key in oxoniumIons:
        print key, "\t", oxoniumIons[key]

    # set parameters
    skippedSingleCharged = 0
    tolerance = float(options.tolerance)
    ionthreshold = float(options.ionthreshold)
    scorethreshold = float(options.scorethreshold)


    # loading feature file
    print "loading feature file"
    fm = pyopenms.FeatureMap()
    fh = pyopenms.FeatureXMLFile()
    if options.inFeature != None:
        fh.load(options.inFeature, fm)

    allFeatures = {}
    for feature in fm:
        f = glyxsuite.io.GlyxXMLFeature()
        f.setId(feature.getUniqueId())
        hull = feature.getConvexHull().getBoundingBox()
        minRT, minMZ = hull.minPosition()
        maxRT, maxMZ = hull.maxPosition()
        f.setBoundingBox(minRT, maxRT, minMZ, maxMZ)
        f.setIntensity(feature.getIntensity())
        f.setRT(feature.getRT())
        f.setMZ(feature.getMZ())
        f.setCharge(feature.getCharge())
        allFeatures[feature.getUniqueId()] = f

    # loading mzML file
    exp = glyxsuite.lib.openOpenMSExperiment(options.inMZML)


    # initialize output xml file
    glyxXMLFile = glyxsuite.io.GlyxXMLFile()
    parameters = glyxXMLFile.parameters
    parameters.setTimestamp(str(datetime.datetime.today()))
    source = exp.getSourceFiles()[0]
    parameters.setSourceFilePath(options.inMZML) # TODO: Feature file path?
    parameters.setSourceFileChecksum(source.getChecksum())

    parameters.setMassTolerance(str(options.tolerance))
    parameters.setIonThreshold(str(options.ionthreshold))
    parameters.setNrNeutrallosses(str(0))
    parameters.setMaxOxoniumCharge(str(1))
    parameters.setScoreThreshold(str(options.scorethreshold))

    
    keepFeatures = set()
    ms2Spectra = {}
    collectedScores = {}
    for spec in exp:
        if spec.getMSLevel() != 2:
            continue
        ms2Spectra[spec.getNativeID()] = spec
        # check if spectrum lies within a feature
        precursor = spec.getPrecursors()[0] # Multiple precurors currently not handled!
        rt = spec.getRT()
        mz = precursor.getMZ()
        charge = precursor.getCharge()
        intensity = precursor.getIntensity()
        if spec.size() == 0:
            continue
        # create list of all possible scores
        scores = []

        singleCharged = True # check if only single charges would be possible
        if charge != 1:
            score = Score(spec.getNativeID(), rt, mz, charge, intensity, None)
            scores.append(score)
            singleCharged = False


        #if charge == 1:
        #    skippedSingleCharged += 1
        #    continue

        # find all scores with possible features
        for feature in allFeatures.values():
            minRT, maxRT, minMZ, maxMZ = feature.getBoundingBox()
            if minRT > spec.getRT() or spec.getRT() > maxRT:
                continue
            if minMZ > precursor.getMZ() or precursor.getMZ() > maxMZ+tolerance:
                continue
            rt = feature.getRT()
            mz = feature.getMZ()
            charge = feature.getCharge()
            if charge != 1:
                score = Score(spec.getNativeID(), rt, mz, charge, intensity, feature)
                scores.append(score)
                singleCharged = False
        
        if singleCharged == True:
            skippedSingleCharged += 1
            continue
        
        if len(scores) == 0:
            continue
        
        # run all possible scores
        bestScore = scores[0]
        for score in scores:
            # add peaks from spectrum
            for peak in spec:
                score.addPeak(peak.getMZ(), peak.getIntensity())
            # rank peaks
            score.makeRanking()

            # normalize
            score.normIntensity()

            # make scoring
            score.makeScoring(oxoniumIons, ionthreshold, tolerance)
            
            if score.getLogScore() < scorethreshold:
                score.setIsGlycopeptide(True)
            # replace bestScore if it is featureless or keep best Score
            if score.feature != None and bestScore.feature == None:
                bestScore = score
            elif score.getLogScore() < bestScore.getLogScore():
                bestScore = score
        collectedScores[bestScore.getNativeId()] = bestScore
        
    print "skipped", skippedSingleCharged, " single charged spectra"
    print "writing outputfile"
    
    featureNr = 0
    for key in collectedScores:
        score = collectedScores[key]
        glyxXMLFile.spectra.append(score)
        if score.feature is None:
            # generate new feature
            f = glyxsuite.io.GlyxXMLFeature()
            featureNr += 1
            f.setId("own"+str(featureNr))
            minRT = score.rt
            maxRT = score.rt
            minMZ = score.precursorMass
            maxMZ = minMZ+1/float(score.precursorCharge)*3 # TODO: handle other Adducts
            f.setBoundingBox(minRT, maxRT, minMZ, maxMZ)
            f.setIntensity(score.precursorIntensity)
            f.setRT(score.rt)
            f.setMZ(score.precursorMass)
            f.setCharge(score.precursorCharge)
            score.feature = f
            allFeatures[f.getId()] = f
            
        score.feature.spectraIds.append(score.getNativeId())
        if score.getLogScore() < scorethreshold:
            keepFeatures.add(score.feature.getId())

    # write features
    for key in keepFeatures:
        # generate consensus spectra
        feature = allFeatures[key]
        # collect all spectra
        spectra = []
        for nativeID in feature.spectraIds:
            peaks = ms2Spectra[nativeID].get_peaks()
            if hasattr(peaks, "shape"):
                spectra.append(peaks)
            else:
                mzArray, intensArray = peaks
                spectra.append(zip(mzArray, intensArray))
        if len(spectra) == 1:
            minSpecCount = 1
        else:
            minSpecCount = 2
        keep,notkeep,underThreshold = glyxsuite.consensus.generateConsensusSpectrum(spectra,minSpecCount=minSpecCount)
        feature.consensus = keep
        glyxXMLFile.features.append(feature)

    glyxXMLFile.writeToFile(options.outGlyML)

def handle_args(argv=None):
    """ Handles input arguments """
    import argparse
    usage = "\nGlycopeptide Scoringtool for highresolution MS/MS spectra"
    parser = argparse.ArgumentParser(description=usage)
    parser.add_argument("--inMZML", dest="inMZML",
                        help="mzML file input")
    parser.add_argument("--inFeature", dest="inFeature", nargs='?',
                        help="feature file input")
    parser.add_argument("--outGlyML", dest="outGlyML",
                        help="glyML output")
    parser.add_argument("--checkNGlycan", dest="checkNGlycan",
                        help="Checks for oxoniumion 528 m/z indicative for N-Glycosylation")
    parser.add_argument("--hasFucose", dest="hasFucose",
                        help="include oxoniumions indicative for fucosylation")
    parser.add_argument("--hasSial", dest="hasSial",
                        help="include oxoniumions indicative for sialisation")
    parser.add_argument("--oxoniumions", dest="oxoniumions",
                        nargs='?', const="",
                        help="Additional oxoniumions as comma separated strings")
    parser.add_argument("--tolerance", dest="tolerance",
                        help="Mass tolerance in th",
                        type=float)
    parser.add_argument("--ionthreshold", dest="ionthreshold",
                        help="Threshold for reporter ions",
                        type=int)
    parser.add_argument("--scorethreshold", dest="scorethreshold",
                        help="Score threshold for identifying glycopeptide spectra",
                        type=float)
    
    if not argv:
        args = parser.parse_args(sys.argv[1:])
    else:
        args = parser.parse_args(argv)
    return args

if __name__ == "__main__":
    main(handle_args())

