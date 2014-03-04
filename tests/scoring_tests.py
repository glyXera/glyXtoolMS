from nose.tools import *
from glyxsuite.scoring.glyxScore import *

def setup():
    print "SETUP!"

def teardown():
    print "TEAR DOWN!"

def test_basic():
    print "I RAN!"

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


