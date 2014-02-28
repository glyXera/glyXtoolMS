import pyopenms

def main(options):
    print "parsing glycan parameters:"
    sugars = options.glycanlist.split(" ")

    print "loading experiment"
    exp = pyopenms.MSExperiment()
    outExp = pyopenms.MSExperiment()
    fh = pyopenms.FileHandler()
    fh.loadExperiment(options.infile,exp)

    print "loading finnished"


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
