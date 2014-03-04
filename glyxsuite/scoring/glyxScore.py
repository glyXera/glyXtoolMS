import pyopenms


class IonMassSeriesCalculator:

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


    def calcSeries(self,glycan):
        
        series = {}
        glycanMass = self.masses[glycan]
        series["OxoniumIon"] = Ion(glycan+":OxoniumIon",glycanMasss-self.masses["H2O"]+self.masses["H+"])
        series["Fragment1"] = Ion(glycan+":Fragment1:",series["OxoniumIon"].mass-self.masses["H2O"],series["OxoniumIon"])
        series["Fragment2"] = Ion(glycan+":Fragment2:",series["OxoniumIon"].mass-2*self.masses["H2O"],series["Fragment1"])
        series["Fragment3"] = Ion(glycan+":Fragment3:",series["OxoniumIon"].mass-2*self.masses["H2O"]-self.masses["CH2O"],series["Fragment2"])
        series["Fragment4"] = Ion(glycan+":Fragment4:",series["OxoniumIon"].mass-self.masses["CH2O"],series["OxoniumIon"])
        series["Fragment5"] = Ion(glycan+":Fragment5:",series["OxoniumIon"].mass-2*self.masses["CH2O"],series["Fragment4"])
        series["Fragment6"] = Ion(glycan+":Fragment6:",series["OxoniumIon"].mass-2*self.masses["CH2O"]-self.masses["H2O"],series["Fragment5"])
        
        # multiple neutral losses
        for nr in range(1,nrNeutrallosses+1):
            series["Neutralloss"+str(nr)] = Ion(name+":Neutralloss"+str(nr),precursorMass-(sugarMass-self.masses["H2O"])/float(precursorCharge),series["OxoniumIon"])

        for oxCharge in range(1,maxChargeOxoniumIon+1):
            if precursorCharge > oxCharge:
                series["OxoniumLoss"+str(oxCharge)] = Ion(name+":OxoniumLoss"+str(oxCharge),(precursorMass*precursorCharge-oxCharge*series["OxoniumIon"].mass)/float((precursorCharge-oxCharge)),series["OxoniumIon"])
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

    def calcScore(self):
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

class Spectrum:

    def __init__(self,spectrumId):
        self.spectrumId = spectrumId
        self.spectrumIntensity = 0
        self.rt = 0.0
        self.charge = 0
        self.peaks = []
        self.totalIntensity = 0
        self.nr = -1
        

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

    def findGlycanScore(self,glycanseries,precursorMass, precursorCharge,massDelta,intensityThreshold=0):
        for ionname in glycanSeries:
            ion = glycanSeries[ionname]
            massTh = ion.mass
            for peak in self.peaks:
                if peak.intensity >= intensityThreshold and peak.mass >= massTh-massDelta and peak.mass <= massTh+delta:
                    ion.addPeak(peak)
                    peak.ionname = ion.name

def main(options):
    print "parsing glycan parameters:"
    glycans = options.glycanlist.split(" ")

    print "loading experiment"
    exp = pyopenms.MSExperiment()
    outExp = pyopenms.MSExperiment()
    fh = pyopenms.FileHandler()
    fh.loadExperiment(options.infile,exp)
    print "loading finnished"          

    # score each spectrum
    for spec in exp:
        if spec.getMSLevel() != 2:
            continue
        # create spectrum
        s = Spectrum(spec.getNativeId())
        for peak in spec:
            s.addPeak(peak.getMZ(),peak.getIntensity())
                    

def handle_args():
    import argparse
    usage = "\nGlycopeptide Scoringtool for lowresolution MS/MS spectra"
    parser = argparse.ArgumentParser(description=usage)
    parser.add_argument("--in", dest="infile",help="File input")
    parser.add_argument("--glycans", dest="glycanlist",help="Possible glycans as list")
    args = parser.parse_args(sys.argv[1:])
    return args

if __name__ == "__main__":
    options = handle_args()
    main(options)
