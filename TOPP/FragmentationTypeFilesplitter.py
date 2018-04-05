import pyopenms

# FragmentationTypeFilesplitter, split mass spectromery files with alternating fragmentation techniques into separate files.

def getSpectrumType(spectrum,lookup):
    if spectrum.getMSLevel() == 1:
        return "MS1"
    else:
        p = spectrum.getPrecursors()[0]
        return "-".join([lookup.get(x,"?") for x in sorted(p.getActivationMethods())])

def handle_args(argv=None):
    import argparse
    usage = "\FragmentationTypeFilesplitter, split mass spectromery files with alternating fragmentation techniques into separate files"
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
    
    print "getting fragment spectra types:"
    fragmentationTypes = set()
    for s in exp:
        if s.getMSLevel() != 1:
            typ = getSpectrumType(s,lookup)
            fragmentationTypes.add(typ)

    # writing new files
    filepart, suffix = os.path.splitext(options.outfile)
    filenames = []
    for typ in fragmentationTypes:
        expNew = pyopenms.MSExperiment()
        for s in exp:
            if s.getMSLevel() == 1 or getSpectrumType(s,lookup) == typ:
                expNew.addSpectrum(s)

        print "saving file"
        mzFile = pyopenms.MzMLFile()
        fileoptions = mzFile.getOptions()
        fileoptions.setCompression(True)
        mzFile.setOptions(fileoptions)
        name = filepart+"_"+typ + ".mzML"
        filenames.append(name)
        mzFile.store(name,expNew)
        del expNew

    
    
    print "create zip file", options.outfile
    zipFile = zipfile.ZipFile(options.outfile, "w",allowZip64 = True)
    for name in filenames:
        zipFile.write(name, os.path.basename(name))
    zipFile.close()
    print "finished"


import pyopenms
import sys
import os
import zipfile

if __name__ == "__main__":
    options = handle_args()
    main(options)
