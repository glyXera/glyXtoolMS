import pyopenms

# Tool for picking profile spectra, spectra already in centroided format will not be processed further.

def getSpectrumType(spectrum,lookup):
    if spectrum.getMSLevel() == 1:
        return "MS1"
    else:
        p = spectrum.getPrecursors()[0]
        return "-".join([lookup.get(x,"?") for x in sorted(p.getActivationMethods())])

def percentile75(l):
    l = sorted(l)
    N = len(l)
    return l[int(N*0.75)]

def continousSpectrumCheck(spectrum):
    # get ten first datapoints if availabe
    diff = []
    N = 20
    N = min(N,spectrum.size())
    for i in range(0,N-1):
        diff.append(spectrum[i+1].getMZ() - spectrum[i].getMZ())
    return percentile75(diff) < 1.0



def handle_args(argv=None):
    import argparse
    usage = "\nPeakpickerHighRes, robust against already centroided spectra"
    parser = argparse.ArgumentParser(description=usage)
    parser.add_argument("--in", dest="infile",help="File input - Original file")
    parser.add_argument("--out", dest="outfile",help="File output")
    if not argv:
        args = parser.parse_args(sys.argv[1:])
    else:
        args = parser.parse_args(argv)
    return args


def main(options):
    
    # generate fragmentationtype lookup
    lookup = {}
    methods = pyopenms.ActivationMethod()
    for attr in dir(methods):
        value = getattr(methods,attr)
        if isinstance(value,int):
            lookup[value] = attr
    
    print "loading MS Experiment "
    exp = pyopenms.MSExperiment()
    fh = pyopenms.FileHandler()
    fh.loadExperiment(options.infile,exp)
    
    print "checking spectra types:"
    fragmentationTypes = {}
    for s in exp:
        typ = getSpectrumType(s,lookup)
        cont = continousSpectrumCheck(s)
        fragmentationTypes[typ] = fragmentationTypes.get(typ, [] ) + [cont]


    isContinousSpectrum = {}
    for typ in fragmentationTypes:
        check = percentile75(fragmentationTypes[typ])
        isContinousSpectrum[typ] = check
        if check == True:
            print "\t" + typ + " has continous spectra data"
        else:
            print "\t" + typ + " has centroided spectra data"

    print "picking spectra"
    expNew = pyopenms.MSExperiment()
    picker = pyopenms.PeakPickerHiRes()
    for s in exp:
        typ = getSpectrumType(s,lookup)
        if isContinousSpectrum[typ] == True:
            newSpec = pyopenms.MSSpectrum()
            picker.pick(s,newSpec)
            expNew.addSpectrum(newSpec)
        else:
            expNew.addSpectrum(s)
    
    print "saving file to ",options.outfile
    mzFile = pyopenms.MzMLFile()
    fileoptions = mzFile.getOptions()
    fileoptions.setCompression(True)
    mzFile.setOptions(fileoptions)
    mzFile.store(options.outfile,expNew)
    print "finished"


import pyopenms
import sys

if __name__ == "__main__":
    options = handle_args()
    main(options)
