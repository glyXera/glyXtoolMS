import glyxtoolms
import os
import shutil
import time

def setup():
    print "SETUP!"
    if os.path.exists("tempTest/"):
        shutil.rmtree("tempTest")
    os.mkdir("tempTest/")


def teardown():
    print "TEAR DOWN!"
    if os.path.exists("tempTest/"):
        shutil.rmtree("tempTest/")


def test_deconvolution():

    # open spectrum
    exp = glyxtoolms.lib.openOpenMSExperiment("data/msExample.mzML")
    assert exp.size() == 7
    spectrum = exp[0]

    d = glyxtoolms.deconvolution.Deconvolution(max_charge=4,
                                              mass_tolerance=0.15,
                                              intensity_tolerance=0.5)

    # add peaks
    for peak in spectrum:
        d.add_peak(peak.getMZ(), peak.getIntensity())

    assert len(d.peaklist) == 1234

    deconvolutedPeaks = d.deconvolute(4, 50)

    assert len(deconvolutedPeaks) == 50

    p = d.peaklist[0]

    assert p.charge == 2
    assert p.isotope == 0
    assert p.right.isotope == 1

def test_peptide_digest():

    # Protein
    protein = glyxtoolms.lib.Protein()
    protein.sequence = "AAACACAAAANASAARHGGGGGGKMGAH"
    proteinDigest = glyxtoolms.lib.ProteinDigest()

    proteinDigest.addModification("CYS_CAM")
    proteinDigest.addModification("MSO")

    proteinDigest.newDigest(protein)
    proteinDigest.add_tryptic_digest()
    peptides = proteinDigest.digest(1)
    glycopeptides = proteinDigest.findGlycopeptides(peptides,
                                                    True,
                                                    False)
    assert len(peptides) == 5
    peptidestrings = [pep.toString() for pep in peptides]
    glycopeptidestrings = [pep.toString() for pep in glycopeptides]
    print peptidestrings
    print glycopeptidestrings
    #assert "AAACAAAAANASAAR" in peptidestrings
    #assert "AAACAAAAANASAARHGGGGGGK" in peptidestrings
    #assert "HGGGGGGK" in peptidestrings
    #assert "HGGGGGGKMGAH" in peptidestrings
    #assert "MGAH" in peptidestrings
    #
    #assert len(glycopeptides) == 4
    #
    #glycopeptidestrings = [pep.toString() for pep in glycopeptides]
    #print glycopeptidestrings
    #assert "AAACAAAAANASAAR" in glycopeptidestrings
    #assert "AAACAAAAANASAAR Cys_CAM(-1)" in glycopeptidestrings
    #assert "AAACAAAAANASAARHGGGGGGK" in glycopeptidestrings
    #assert "AAACAAAAANASAARHGGGGGGK Cys_CAM(-1)" in glycopeptidestrings



def test_io():
    # create spectrum
    spectrum = glyxtoolms.io.GlyxXMLSpectrum()
    spectrum.nativeId = "spectrumID"
    spectrum.rt = 100.5
    spectrum.ionCount = 55
    spectrum.precursorMass = 1111.1
    spectrum.precursorCharge = 2
    spectrum.logScore = 1.3
    spectrum.addIon("Hex", "(Hex)1(H+)1", 163.059, 1234.5)
    spectrum.isGlycopeptide = True

    # create Feature
    feature = glyxtoolms.io.GlyxXMLFeature()
    feature.id = "featureID"
    feature.mz = 111.0
    feature.rt = 100.4
    feature.intensity = 121.0
    feature.charge = 2
    feature.setBoundingBox(95.0, 110.0, 109.0, 113.1)
    feature.addSpectrumId(spectrum.nativeId)
    # add consensus peaks
    feature.addConsensusPeak(1.0,4)
    feature.addConsensusPeak(2.0,3)

    # create peptide
    peptide = glyxtoolms.io.XMLPeptide()
    peptide.proteinID = "proteinID"
    peptide.sequence = "AAACAAAAANASAAR"
    peptide.start = 0
    peptide.end = 15
    peptide.mass = 1316.6255039999999
    peptide.addModification('CYS_CAM')
    peptide.glycosylationSites = [(9, 'N')]

    # create glycan
    glycan = glyxtoolms.io.XMLGlycan()
    glycan.composition = "HEX9HEXNAC5"
    glycan.mass = 1234.5

    # create glycomod hit
    hit = glyxtoolms.io.GlyxXMLGlycoModHit()
    hit.featureID = "featureID"
    hit.peptide = peptide
    hit.glycan = glycan
    hit.error = -0.01

    # create GlyxXMLFile
    f = glyxtoolms.io.GlyxXMLFile()
    f.spectra.append(spectrum)
    f.features.append(feature)
    f.glycoModHits.append(hit)

    # write parameters
    param = f.parameters
    param.setTimestamp(time.time())
    param.setMassTolerance(0.2)
    param.setIonThreshold(1000)
    param.setNrNeutrallosses(1)
    param.setMaxOxoniumCharge(2)
    param.setScoreThreshold(2.5)
    param.setGlycanList(["Hex", "HexNAc"])
    param.addGlycan("NeuAc")
    param.setSourceFileChecksum("md5")

    # write file
    f.writeToFile("tempTest/glyML.xml")

    # parse from file
    fparse = glyxtoolms.io.GlyxXMLFile()
    fparse.readFromFile("tempTest/glyML.xml")

    # check some paramters between the files
    assert len(fparse.spectra) == 1
    assert len(fparse.features) == 1
    assert len(fparse.glycoModHits) == 1
    newspectrum = fparse.spectra[0]
    #newfeature = fparse.features[0]
    #newhit = fparse.glycoModHits[0]
    assert newspectrum.isGlycopeptide == spectrum.isGlycopeptide
