from nose.tools import *
from glyxsuite.scoring.glyxScore import *
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

def test_class_Peak():
    p = Peak(100,123.5)
    
"""def test_class_Ion():

    s = Spectrum("spectrum")

    p1 = s.addPeak(100.1,200)
    p2 = s.addPeak(49.9,50)

    s.makeRanking()
    s.normIntensity()


    i1 = Ion("a",100)
    i2 = Ion("b",50,i1)

    i1.addPeak(p1)
    i2.addPeak(p2)

    i1.calcScore()
    i2.calcScore()
"""


def test_class_IonSeriesCalculator():
    
    seriesCalc = IonSeriesCalculator()
    seriesCalc._appendMassList("foo",1230)
    
    series = seriesCalc.calcSeries("NeuAc",1000,3,4,4)
    assert "Fragment5" in series
    fragment5 = series["Fragment5"]
    assert isinstance(fragment5,Ion)
    assert fragment5.mass == 232.08155
    assert fragment5.parent == series["Fragment4"]

 

def test_class_Spectrum():
    # create spectrum
    s = Spectrum("spectrum",1000,3,4,4)
    # add some peaks
    s.addPeak(100,50)
    s.addPeak(300,60)
    s.addPeak(500,.100)
    s.addPeak(700,.200)
    s.addPeak(900,.10)
    s.addPeak(1100,.80)
    s.addPeak(1300,.300)
    s.addPeak(1500,.200)
    s.addPeak(292.1,400) # NeuAC:Oxoniumion
    s.addPeak(274.1,.100) # NeuAc:Fragment1
    s.addPeak(1353.9,.200) # NeuAc:OxoniumLoss1: Precursormass 1000, Charge 3

    s.makeRanking()
    s.normIntensity()
    
    seriesCalc = IonSeriesCalculator()
    seriesCalc._appendMassList("foo",1230)
    
    scoreNeuAc = s.findGlycanScore(seriesCalc,"NeuAc", 0.2,0)
    scoreHex = s.findGlycanScore(seriesCalc,"Hex",0.2,0)
    return s.calcTotalScore()




def test_glyxScore_withRealData():
    # initialize Options
    infile = "data/msExample.mzML"
    outfile = "tempTest/out.xml"
    glycans = "NeuAc Hex HexNAc"
    tol = "0.5"
    ionthreshold = "0"
    nrNeutralloss = "4"
    chargeOxIon = "4"
    scorethreshold = "2.5"
    
    argv = ["--in",infile]
    argv += ["--out",outfile]
    argv += ["--glycans",glycans]
    argv += ["--tol",tol]
    argv += ["--ionthreshold",ionthreshold]
    argv += ["--nrNeutralloss",nrNeutralloss]
    argv += ["--chargeOxIon",chargeOxIon]
    argv += ["--scorethreshold",scorethreshold]
    
    options = handle_args(argv)
    
    assert options.tol == 0.5

    main(options)
    assert os.path.exists(outfile)
    
    # check existence of xml tags
    from lxml import etree as ET
    f = file(outfile,"r")
    root = ET.fromstring(f.read())
    f.close()
    
    
    assert root.find("parameters") != None
    assert root.find("spectra") != None
    spectra = root.find("spectra").findall("spectrum")
    assert len(spectra) == 5

    s = spectra[0]

    assert s.find("nativeId") != None
    assert s.find("precursor") != None
    assert s.find("logScore") != None
