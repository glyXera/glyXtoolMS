from nose.tools import *
from glyxsuite.scoring.glyxScore import *

def setup():
    print "SETUP!"

def teardown():
    print "TEAR DOWN!"

def test_class_Peak():
    p = Peak(100,123.5)
    
def test_class_Ion():

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
    s = Spectrum("spectrum")
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




