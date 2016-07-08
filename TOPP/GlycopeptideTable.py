""""
Generates the possible glycopeptide masses from a peptide list and a glycan list.

""" 

def handle_args(argv=None):
    import argparse
    usage = "\nFile Glycan composition builder"
    parser = argparse.ArgumentParser(description=usage)
    parser.add_argument("--inGlycan", dest="infileGlycan",help="File input Glycan composition file .txt")
    parser.add_argument("--inPeptide", dest="infilePeptide",help="File input Glycopeptide file .xml")    
    parser.add_argument("--out", dest="outfile",help="File output as .xls file")
    parser.add_argument("--chargeRange", dest="chargeRange",help="Chargerange to test")
                
    if not argv:
        args = parser.parse_args(sys.argv[1:])
    else:
        args = parser.parse_args(argv)
    return args

def parseComposition(comp):
    string = ""
    names = {"DHEX":"F","HEX":"H","HEXNAC":"HN","NEUAC":"NA","NEUGC":"NG"}
    for match in re.findall("[A-z]+\d+",comp):
        unit = re.search("[A-z]+",match).group()
        amount = int(re.search("\d+",match).group())
        if amount == 0:
            continue
        string += names[unit] + str(amount)
    return string

def main(options):
    print "parsing input parameters"

    # charge range
    minCharge,maxCharge = map(int,options.chargeRange.split(":"))
    # Peptide file
    pepFile = glyxtoolms.io.XMLPeptideFile()
    pepFile.loadFromFile(options.infilePeptide)
    # Glycan file
    glycans = []
    glycanFile = file(options.infileGlycan,"r")
    for line in glycanFile:
        glycan = glyxtoolms.lib.Glycan(line[:-1])
        glycans.append((glycan.mass,glycan))
    glycanFile.close()

    # sort glycan file for faster comparison
    glycans.sort()

    print "starting generation"
    data = {}
    comps = set()
    for peptide in pepFile.peptides:
        for glycanmass, glycan in glycans:
            comp = glycan.composition
            comps.add(comp)
            seq = peptide.toString()
            if not seq in data:
                data[seq] = {}
                
            mass = peptide.mass+glycanmass+glyxtoolms.masses.MASS["H+"]
            chargestates = []
            for charge in range(minCharge,maxCharge+1):
                ionmass = (mass + glyxtoolms.masses.MASS["H+"]*charge)/charge
                chargestates.append("{}({})".format(str(round(ionmass,1)),str(charge)))
            data[seq][comp] = ";".join(chargestates)
                
    print "writing output"
    # write output
    comps = sorted(list(comps))

    wb = xlwt.Workbook()
    ws0 = wb.add_sheet("Resultstable")

    # write header
    for col,comp in enumerate(["Peptides"]+comps):
        ws0.write(0,col,parseComposition(comp))
    row = 0
    for seq in data:
        row += 1
        # write sequence
        ws0.write(row,0,seq)
        col = 0
        for comp in comps:
            col += 1
            if comp in data[seq]:
                ws0.write(row,col,data[seq][comp])
                
    wb.save(options.outfile)
    print "done"
    return

import sys
import glyxtoolms
from itertools import product
import xlwt
import re

if __name__ == "__main__":
    options = handle_args()
    main(options)
 
