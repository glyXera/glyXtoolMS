from nose.tools import *
from glyxsuite import reporter

def setup():
    print "SETUP!"

def teardown():
    print "TEAR DOWN!"

def test_basic():
    print "I RAN!" 
