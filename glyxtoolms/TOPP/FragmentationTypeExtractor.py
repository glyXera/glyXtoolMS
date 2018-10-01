import pyopenms

# FragmentationTypeExtractor, extract fragmentation type spectra into a new file.

def getSpectrumType(spectrum,lookup):
    if spectrum.getMSLevel() == 1:
        return "MS1"
    else:
        p = spectrum.getPrecursors()[0]
        return "-".join([lookup.get(x,"?") for x in sorted(p.getActivationMethods())])

def handle_args(argv=None):
    import argparse
    usage = "\FragmentationTypeExtractor, split mass spectromery files with alternating fragmentation techniques into separate files"
    parser = argparse.ArgumentParser(description=usage)
    parser.add_argument("--in", dest="infile",help="File input - Original file")
    parser.add_argument("--out", dest="outfile",help="File output")
    parser.add_argument("--extractType", dest="extractType",help="Extract type")
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
    
    print "getting fragment spectra types:"
    fragmentationTypes = {}
    for s in exp:
        if s.getMSLevel() != 1:
            typ = getSpectrumType(s,lookup)
            fragmentationTypes[typ] = fragmentationTypes.get(typ,0) +1
    print "found the following spectra types:"
    for typ in fragmentationTypes:
        print "typ '" + typ +"' with " + str(fragmentationTypes[typ]) + " spectra"
            
    print "extracting all "+str(fragmentationTypes.get(options.extractType,0))+" spectra with type " + options.extractType 
    
    expNew = pyopenms.MSExperiment()
    for s in exp:
        if s.getMSLevel() == 1 or getSpectrumType(s,lookup) == options.extractType:
            expNew.addSpectrum(s)

    print "saving file"
    mzFile = pyopenms.MzMLFile()
    fileoptions = mzFile.getOptions()
    fileoptions.setCompression(True)
    mzFile.setOptions(fileoptions)
    
    mzFile.store(options.outfile,expNew)

    print "finished"


import pyopenms
import sys
import os

if __name__ == "__main__":
    options = handle_args()
    main(options)
