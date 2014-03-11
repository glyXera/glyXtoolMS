import pyopenms
import math
import sys
from lxml import etree as ET
import datetime


class IonSeriesCalculator:

    def __init__(self):
        self.masses = {}
        self.masses["H+"] = 1.00727
        self.masses["H2O"] = 18.01056
        self.masses["CH2O"] = 30.01056
        self.masses["Hex"] = 180.06336
        self.masses["HexNAc"] = 221.08996
        self.masses["Fuc"] = 164.06846
        self.masses["NeuAc"] = 309.10596
        self.masses["NeuGc"] = 325.10086
        self.masses["HexHexNAc"] = 383.14276
        self.masses["HexNAcHexNeuAc"] = self.masses["HexNAc"]+self.masses["Hex"]+self.masses["NeuAc"]-self.masses["H2O"]
        self.masses["HexNeuAc"] = self.masses["Hex"]+self.masses["NeuAc"]-self.masses["H2O"]

    def _appendMassList(self,name,mass):
        self.masses[name] = mass

    def hasGlycan(self,glycan):
        if glycan in self.masses:
            return True
        return False


    def calcSeries(self,glycan,precursorMass, precursorCharge, nrNeutrallosses,maxChargeOxoniumIon):
        
        series = {}
        glycanMass = self.masses[glycan]
        series["OxoniumIon"] = Ion(glycan+":OxoniumIon",glycanMass-self.masses["H2O"]+self.masses["H+"])
        series["Fragment1"] = Ion(glycan+":Fragment1:",series["OxoniumIon"].mass-self.masses["H2O"],series["OxoniumIon"])
        series["Fragment2"] = Ion(glycan+":Fragment2:",series["OxoniumIon"].mass-2*self.masses["H2O"],series["Fragment1"])
        series["Fragment3"] = Ion(glycan+":Fragment3:",series["OxoniumIon"].mass-2*self.masses["H2O"]-self.masses["CH2O"],series["Fragment2"])
        series["Fragment4"] = Ion(glycan+":Fragment4:",series["OxoniumIon"].mass-self.masses["CH2O"],series["OxoniumIon"])
        series["Fragment5"] = Ion(glycan+":Fragment5:",series["OxoniumIon"].mass-2*self.masses["CH2O"],series["Fragment4"])
        series["Fragment6"] = Ion(glycan+":Fragment6:",series["OxoniumIon"].mass-2*self.masses["CH2O"]-self.masses["H2O"],series["Fragment5"])
        
        # multiple neutral losses
        for nr in range(1,nrNeutrallosses+1):
            series["Neutralloss"+str(nr)] = Ion(glycan+":Neutralloss"+str(nr),precursorMass-(glycanMass-self.masses["H2O"])/float(precursorCharge),series["OxoniumIon"])

        for oxCharge in range(1,maxChargeOxoniumIon+1):
            if precursorCharge > oxCharge:
                series["OxoniumLoss"+str(oxCharge)] = Ion(glycan+":OxoniumLoss"+str(oxCharge),(precursorMass*precursorCharge-oxCharge*series["OxoniumIon"].mass)/float((precursorCharge-oxCharge)),series["OxoniumIon"])
        return series


class Ion:
    def __init__(self,name,mass,parent=None):
        self.name = name
        self.mass = mass
        self.counts = 0
        self.parent = parent
        self.peaks = []
        self.inverseRank = 0
        self.score = 0
    
    def addPeak(self,peak):
        self.counts += peak.normedIntensity
        self.inverseRank += 1/float(peak.rank)
        self.peaks.append(peak)

    def calcIonScore(self):
        self.score = self.counts*self.inverseRank
        parent = self.parent
        while parent:
            self.score *= parent.inverseRank
            parent = parent.parent
        if self.score <= 0:
            for peak in self.peaks:
                peak.ionname = None
        return self.score        


class Peak:
    
    def __init__(self,mass,intensity):
        self.mass = mass
        self.intensity = intensity
        self.normedIntensity = 0
        self.ionname = None
        self.rank = 0

class Score:

    def __init__(self,glycan):
        self.glycan = glycan
        self.ions = {}
        self.score = 0

    def addIon(self,ion):
        self.ions[ion.name] = ion

    def calcScores(self):
        self.score = 0
        for name in self.ions:
            self.score += self.ions[name].calcIonScore()


class Spectrum:

    def __init__(self,spectrumId, precursorMass, precursorCharge, nrNeutrallosses, maxChargeOxoniumIon):
        self.spectrumId = spectrumId
        self.precursorCharge = precursorCharge
        self.precursorMass = precursorMass
        self.nrNeutrallosses = nrNeutrallosses
        self.maxChargeOxoniumIon = maxChargeOxoniumIon
        self.spectrumIntensity = 0
        self.peaks = []
        self.totalIntensity = 0
        self.glycanScores = {}
        self.logScore = 10
        
    def addPeak(self,mass,intensity):
        p = Peak(mass,intensity)
        self.spectrumIntensity += intensity
        self.peaks.append(p)
        return p

    def normIntensity(self):
        for peak in self.peaks:
            peak.normedIntensity = peak.intensity/float(self.spectrumIntensity)

    def makeRanking(self):
        intensitySort = [(p.intensity,p) for p in self.peaks]
        intensitySort.sort(reverse=True)
        for i,pair in enumerate(intensitySort):
            p = pair[1]
            p.rank = i+1

    def findGlycanScore(self,seriesCalculator,glycan,massDelta,intensityThreshold=0):
        glycanSeries = seriesCalculator.calcSeries(glycan,self.precursorMass,self.precursorCharge, self.nrNeutrallosses, self.maxChargeOxoniumIon)
        score = Score(glycan)
        for ionname in glycanSeries:
            ion = glycanSeries[ionname]
            massTh = ion.mass
            for peak in self.peaks:
                if peak.intensity >= intensityThreshold and peak.mass >= massTh-massDelta and peak.mass <= massTh+massDelta:
                    ion.addPeak(peak)
                    peak.ionname = ion.name
            if ion.counts > 0:
                score.addIon(ion)
        score.calcScores()
        if score.score > 0:
            self.glycanScores[glycan] = score
        return score


    def calcTotalScore(self):
        maxScore = 0
        for glycan in self.glycanScores:
            glycanScore = self.glycanScores[glycan]
            if glycanScore.score > maxScore:
                maxScore = glycanScore.score
        self.logScore = 10
        if maxScore > 0:
            self.logScore = -math.log(maxScore)/math.log(10)
        return self.logScore

    def makeXMLOutput(self,xmlSpectra):
        xmlSpectrum = ET.SubElement(xmlSpectra,"spectrum")
        xmlSpectrumNativeId = ET.SubElement(xmlSpectrum,"nativeId")
        xmlSpectrumNativeId.text = str(self.spectrumId)
        xmlPrecursor = ET.SubElement(xmlSpectrum,"precursor")
        xmlPrecursorMass = ET.SubElement(xmlPrecursor,"mass")
        xmlPrecursorMass.text = str(self.precursorMass)
        xmlPrecursorCharge = ET.SubElement(xmlPrecursor,"charge")
        xmlPrecursorCharge.text = str(self.precursorCharge)
        xmlTotalScore = ET.SubElement(xmlSpectrum,"logScore")
        xmlTotalScore.text = str(self.logScore)                
        

def main(options):
    print "parsing glycan parameters:"
    glycans = options.glycanlist.split(" ")

    print "loading experiment"
    exp = pyopenms.MSExperiment()
    fh = pyopenms.FileHandler()
    fh.loadExperiment(options.infile,exp)
    print "loading finnished"          

    # Initialize IonSeriesCalculator
    seriesCalc = IonSeriesCalculator()
    # check validity of each glycan
    for glycan in glycans:
        if not seriesCalc.hasGlycan(glycan):
            print "Cannot find glycan in SeriesCalculator, Aborting!"
            return

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
    for spec in exp:
        if spec.getMSLevel() != 2:
            continue
        # create spectrum
        for precursor in spec.getPrecursors(): # Multiple precurors will make native spectrum id nonunique!
            s = Spectrum(spec.getNativeID(),precursor.getMZ(),precursor.getCharge(),int(options.nrNeutralloss),int(options.chargeOxIon))
            logScore = 10
            if s.precursorCharge > 1:
                for peak in spec:
                    s.addPeak(peak.getMZ(),peak.getIntensity())
                # make Ranking
                s.makeRanking()
                s.normIntensity()
                for glycan in glycans:
                    s.findGlycanScore(seriesCalc, glycan, float(options.tol), float(options.ionthreshold))

            logScore = s.calcTotalScore()
            s.logScore = logScore
            s.makeXMLOutput(xmlSpectra)

            
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
