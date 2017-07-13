# Tool for reevaluating possible peptide candidates based on reported glycosylation sites gathered by GlycoDomainViewer
# Input: Peptide xml file, Possible precursor tool: GlycopeptideDigest Tool
# Output: Peptide xml file, without peptides with no reported glycosylation site

import glyxtoolms
import time

import urllib2
import json
import sys

def getAuthToken():
    response = urllib2.urlopen('https://glycodomain.glycomics.ku.dk/api/login')
    html = response.read()
    html_parsed = json.loads(html)
    AUTH_TOKEN = html_parsed['id_token']
    return AUTH_TOKEN

def getGlycoSylationSites(fastaID, AUTH_TOKEN) :
    # parse uniprotID from fasta identifier
    uniprotID = fastaID.split("|")[1]
    request_url = 'https://glycodomain.glycomics.ku.dk/api/data/latest/combined/'+uniprotID
    headers = {'Authorization': 'Bearer '+ AUTH_TOKEN}

    req = urllib2.Request(request_url, headers=headers)
    response = urllib2.urlopen(req)
    the_page = response.read()
    page_parsed = json.loads(the_page)

    # collect sites
    sites = {}
    data = page_parsed["data"]
    if len(data) == 0:
        return None
    for dataset in data:
        for modification in dataset["data"]:
            if "sites" in modification:
                for site, modtype in modification["sites"]:
                    if "GlcNAc" in modtype or "HexNAc" in modtype:
                        sites[site] = sites.get(site, []) + [modtype]
    return sites

def handle_args(argv=None):
    import argparse
    usage = "\nFile GlycoDomainViewer Filter. Removes peptides with no known glycosylation site."
    parser = argparse.ArgumentParser(description=usage)
    parser.add_argument("--in", dest="infile",help="File input - peptide .xml file")
    parser.add_argument("--out", dest="outfile",help="File output - peptide .xml file")                
    if not argv:
        args = parser.parse_args(sys.argv[1:])
    else:
        args = parser.parse_args(argv)
    return args

def main(options):

    f = glyxtoolms.io.XMLPeptideFile()
    f.loadFromFile(options.infile)

    # get authtoken
    print "getting AUTH_TOKEN"
    auth = getAuthToken()
    # collect glycosylation sites

    print "collecting glycoslyation sites"
    prot = {}
    for fastaID in f.parameters.proteins:
        prot[fastaID] = getGlycoSylationSites(fastaID, auth)
        time.sleep(0.5)

    print "start filtering"
    glycoSites = {}
    # filter peptide
    filtered_peptides = []
    for peptide in f.peptides:
        current_sites = prot.get(peptide.proteinID, None)
        if current_sites == None: # cannot find protein (e.g non-human), so keep it
            filtered_peptides.append(peptide)
            continue
        # collect peptide sites
        pep_sites = []
        for pos, typ in peptide.glycosylationSites:
            if pos+1 in current_sites:
                pep_sites.append((pos, typ))
                glycoSites[peptide.proteinID] = glycoSites.get(peptide.proteinID, set())
                glycoSites[peptide.proteinID].add((pos, typ)) 
        if len(pep_sites) > 0:
            peptide.glycosylationSites = pep_sites
            filtered_peptides.append(peptide)
    print "Removed " + str(len(f.peptides) - len(filtered_peptides)) + " from " + str(len(f.peptides)) + " peptides. Keeping " + str(len(filtered_peptides)) + "!"
    f.peptides = filtered_peptides
    f.writeToFile(options.outfile)
    print glycoSites
if __name__ == "__main__":
    options = handle_args()
    main(options)
 
