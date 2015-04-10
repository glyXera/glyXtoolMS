from nose.tools import *
import glyxsuite
import os
import shutil

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
    exp = glyxsuite.lib.openOpenMSExperiment("data/msExample.mzML")
    assert exp.size() == 7
    spectrum = exp[0]

    d = glyxsuite.deconvolution.Deconvolution(max_charge=4,
                                            mz_tolerance=0.15, 
                                            intensity_tolerance=0.5)
                                            
    # add peaks
    for peak in spectrum:
        d.addPeak(peak.getMZ(),peak.getIntensity())
        
    assert len(d.peaklist) == 1234
    
    deconvolutedPeaks = d.deconvolute(4,50) 

    assert len(deconvolutedPeaks) == 50
    
    p = d.peaklist[0]
    
    assert p.charge == 2
    assert p.isotope == 0
    assert p.right.isotope == 1
