from nose.tools import *
from glyxsuite import scoring

def setup():
    print "SETUP!"

def teardown():
    print "TEAR DOWN!"

def test_basic():
    print "I RAN!"

def test_multiply():
    assert scoring.glyxScore.multiply(3,4) == 12

def test_blah():
    assert 1 == 2
