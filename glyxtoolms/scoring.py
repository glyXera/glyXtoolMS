import pyopenms
import glyxtoolms.io
import math
from lxml import etree as ET
import re



class IonSeriesCalculator(object):

    def __init__(self):
        self.masses = {}
        self.masses["h+"] = 1.00727
        self.masses["h2o"] = 18.01056
        self.masses["ch2o"] = 30.01056
        self.masses["hex"] = 180.06336
        self.masses["hexnac"] = 221.08996
        self.masses["fuc"] = 164.06846
        self.masses["neuac"] = 309.10596
        self.masses["neugc"] = 325.10086

        #self.masses["HexHexNAc"] = 383.14276
        #self.masses["HexNAcHexNeuAc"] = self.masses["HexNAc"]+self.masses["Hex"]+self.masses["NeuAc"]-self.masses["H2O"]
        #self.masses["HexNeuAc"] = self.masses["Hex"]+self.masses["NeuAc"]-self.masses["H2O"]

        self.glycans = {}

    def _appendMassList(self, name, mass):
        self.masses[name] = mass

    def addGlycan(self, name):
        # Current glycan structure: Hex1HexNAc1, Hex2HexNac1

        if name in self.glycans:
            return self.glycans[name]

        mass = self.masses["h2o"]
        for part in re.findall(r"[A-z]+\d+", name):
            start = re.search(r"\d+", part).start()
            sugar = part[:start].lower()
            amount = int(part[start:])
            if not sugar in self.masses:
                raise Exception("SugarName "+sugar+" is not defined!")
            mass += self.masses[sugar]-self.masses["h2o"]
        self.glycans[name] = mass
        return mass

    def hasGlycan(self, glycan):
        if glycan in self.masses:
            return True
        return False


    def calcSeries(self, glycan, precursorMass, precursorCharge, nrNeutrallosses, maxChargeOxoniumIon):

        series = {}
        glycanMass = self.glycans[glycan]
        ion = Ion(glycan, glycanMass-self.masses["h2o"]+self.masses["h+"], 1.0)
        series["OxoniumIon"] = ion

        #series["OxoniumIon"] = Ion(glycan+":OxoniumIon", glycanMass-self.masses["H2O"]+self.masses["H+"], 1.0)
        series["Fragment1"] = Ion(glycan+":Fragment1:", series["OxoniumIon"].mass-self.masses["h2o"], 1.0, series["OxoniumIon"])
        #series["Fragment2"] = Ion(glycan+":Fragment2:", series["OxoniumIon"].mass-2*self.masses["H2O"], series["Fragment1"])
        #series["Fragment3"] = Ion(glycan+":Fragment3:", series["OxoniumIon"].mass-2*self.masses["H2O"]-self.masses["CH2O"], series["Fragment2"])
        #series["Fragment4"] = Ion(glycan+":Fragment4:", series["OxoniumIon"].mass-self.masses["CH2O"], series["OxoniumIon"])
        #series["Fragment5"] = Ion(glycan+":Fragment5:", series["OxoniumIon"].mass-2*self.masses["CH2O"], series["Fragment4"])
        #series["Fragment6"] = Ion(glycan+":Fragment6:", series["OxoniumIon"].mass-2*self.masses["CH2O"]-self.masses["H2O"], series["Fragment5"])

        # multiple neutral losses

        for nr in range(1, nrNeutrallosses+1):
            series["Neutralloss"+str(nr)] = Ion(glycan+":Neutralloss"+str(nr), precursorMass-nr*(glycanMass-self.masses["h2o"])/float(precursorCharge), float(precursorCharge), series["OxoniumIon"])

        for oxCharge in range(1, maxChargeOxoniumIon+1):
            if precursorCharge > oxCharge:
                series["OxoniumLoss"+str(oxCharge)] = Ion(glycan+":OxoniumLoss"+str(oxCharge), (precursorMass*precursorCharge-oxCharge*series["OxoniumIon"].mass)/float((precursorCharge-oxCharge)), float(oxCharge), series["OxoniumIon"])

        return series


class Ion(object):
    def __init__(self, name, mass, charge, parent=None):
        self.name = name
        self.charge = charge
        self.mass = mass
        self.counts = 0
        self.parent = parent
        self.peaks = []
        self.inverseRank = 0
        self.score = 0

    def addPeak(self, peak):
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


class Peak(object):

    def __init__(self, mass, intensity):
        self.mass = mass
        self.intensity = intensity
        self.normedIntensity = 0
        self.ionname = None
        self.rank = 0

class Score(object):

    def __init__(self, glycan):
        self.glycan = glycan
        self.ions = {}
        self.score = 0

    def addIon(self, ion):
        self.ions[ion.name] = ion

    def calcScores(self):
        self.score = 0
        for name in self.ions:
            self.score += self.ions[name].calcIonScore()


class SpectrumGlyxScore(glyxtoolms.io.GlyxXMLSpectrum):

    def __init__(self, nativeId, spectrumRT, precursorMass, precursorCharge, nrNeutrallosses, maxChargeOxoniumIon):

        self.nativeId = nativeId
        self.rt = spectrumRT
        self.precursorCharge = precursorCharge
        self.precursorMass = precursorMass
        self.nrNeutrallosses = nrNeutrallosses
        self.maxChargeOxoniumIon = maxChargeOxoniumIon
        self.ionCount = 0
        self.highestPeakIntensity = 0
        self.peaks = []
        self.totalIntensity = 0
        self.glycanScores = {}
        self.logScore = 10

    def addPeak(self, mass, intensity):
        p = Peak(mass, intensity)
        self.ionCount += intensity
        if intensity > self.highestPeakIntensity:
            self.highestPeakIntensity = intensity
        else:
            pass
        self.peaks.append(p)
        return p

    def normIntensity(self):
        for peak in self.peaks:
            peak.normedIntensity = peak.intensity/float(self.ionCount)

    def makeRanking(self):
        intensitySort = [(p.intensity, p) for p in self.peaks]
        intensitySort.sort(reverse=True)
        for i, pair in enumerate(intensitySort):
            p = pair[1]
            p.rank = i+1

    def findGlycanScore(self, seriesCalculator, glycan, massDelta, intensityThreshold=0):
        glycanSeries = seriesCalculator.calcSeries(glycan, self.precursorMass, self.precursorCharge, self.nrNeutrallosses, self.maxChargeOxoniumIon)
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

    def reevaluateScores(self, massDelta):
        count = 0
        masses = {"Hex":162.052, "HexNAc":203.079, "Fuc":146.058, "NeuAc":291.095}
        for glycan in self.glycanScores:
            score = self.glycanScores[glycan]
            for ionname in score.ions:
                ion = score.ions[ionname]
                for peak in self.peaks:
                    for newGlycan in masses:
                        distance = masses[newGlycan]/float(ion.charge)
                        if abs(abs(ion.mass-distance)-peak.mass) < massDelta:
                            count += 1
        return count

    def calcTotalScore(self, scoreThreshold):
        maxScore = 0
        self.ions = {} # For XML Output of ions
        for glycan in self.glycanScores:
            glycanScore = self.glycanScores[glycan]
            if glycanScore.score > maxScore:
                maxScore = glycanScore.score
            if glycanScore.score == 0:
                continue
            for ionname in glycanScore.ions:
                ion = glycanScore.ions[ionname]
                # get highest peak
                highest = ion.peaks[0]
                for peak in ion.peaks:
                    if peak.intensity > highest.intensity:
                        highest = peak
                self.addIon(glycan, ionname, highest.mass, highest.intensity)
        self.logScore = 10
        if maxScore > 0:
            self.logScore = -math.log(maxScore)/math.log(10)
        if self.reevaluateScores(0.2) == 0:
            self.logScore += 0.1
        if self.logScore < scoreThreshold:
            self.isGlycopeptide = True
        else:
            self.isGlycopeptide = False
        return self.logScore
