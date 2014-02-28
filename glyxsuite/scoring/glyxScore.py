import pyopenms

class Peak:
    
    def __init__(self,mass,intensity):
        self.mass = mass
        self.intent = intensity

class Spectrum:

    def __init__(self,spectrumId):
        self.spectrumId = = spectrumId
        self.precursorMass = 0
        self.spectrumIntensity = 0
        self.rt = 0.0
        self.charge = 0
        self.peaks = []
        self.totalIntensity = 0
        self.nr = -1
        

    def addPeak(self,mass,intensity):
        p = Peak(mass,intensity)
        self.total += p.intent
        self.peaks.append(p)

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
