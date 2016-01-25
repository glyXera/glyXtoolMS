# Tool for Building conglomerate raw mzML files.
#e.g  continous MS1 + line spectra MS2


# a) in1: Keeps all as it is
# b) in2: replaces one specified MSLevel with its own





def handle_args(argv=None):
    import argparse
    usage = "\nFile Merger Tool for using different MSLevel types"
    parser = argparse.ArgumentParser(description=usage)
    parser.add_argument("--inOriginal", dest="infileOriginal",help="File input - Original file")
    parser.add_argument("--inReplace", dest="infileReplace",help="File input with spectra that replace alle original spectra with the given MS Level")
    parser.add_argument("--out", dest="outfile",help="File output")
    parser.add_argument("--MSLevel", dest="MSLevel",help="MS Level to replace")
    if not argv:
        args = parser.parse_args(sys.argv[1:])
    else:
        args = parser.parse_args(argv)
    return args


def main(options):
    
    print "loading original MS Experiment "
    exp1 = pyopenms.MSExperiment()
    fh = pyopenms.FileHandler()
    fh.loadExperiment(options.infileOriginal,exp1)
    print "loading replacement MS Experiment"
    exp2 = pyopenms.MSExperiment()
    fh.loadExperiment(options.infileReplace,exp2)
    print "loading finnished"          


    replaceLevel = 2

    err = 0
    if exp1.size() != exp2.size():
        print "different spectra count, aborting"
        return


    expNew = pyopenms.MSExperiment()
    
    i = -1
    dis = []
    for spec in exp1:
        i += 1
        if spec.getMSLevel() != replaceLevel:
            expNew.addSpectrum(spec)
            continue
        else:
            pass

        #find spectrum
        specNew = exp2[i]
        if str(spec.getRT()) != str(specNew.getRT()):
            err += 1
            print spec.getRT() , specNew.getRT()
            continue
        if spec.getMSLevel() != specNew.getMSLevel():
            err += 1
            print spec.getMSLevel() , specNew.getMSLevel()
            continue

        expNew.addSpectrum(specNew)

    print "skipped ",err, "spectra due to discrepancies"
    
    del exp1
    del exp2
    
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
