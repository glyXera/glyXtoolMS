from threading import Thread
import threading
import ttk
import pyopenms
import time
import glyxsuite
from Tkinter import *




def openThis():
    path = '/afs/mpi-magdeburg.mpg.de/data/bpt/bptglycan/DATA_EXCHANGE/Terry/GlyxMSuite/AMAZON/CID/20140904_TNK_FET_TA_A8001_BA1_01_3142/20140904_TNK_FET_TA_A8001_BA1_01_3142_20140922.mzML'
    t = Thread(target=openmzMLFile, args=(path,))
    t.start()
    print threading.current_thread().name
    print t.name

def hello():
    print "hello"

def openmzMLFile(path):
    print "loading"
    print "new", threading.current_thread().name
    f = file(path,"r")
    exp = f.read()
    f.close()
    #exp = pyopenms.MSExperiment()
    #fh = pyopenms.MzMLFile()
    #fh.load(path,exp)
    
    print "fin"
       
    
"""    
def runGui():
    master = Tk()
    b = Button(master, text="hi", command=hello)
    b.pack()
    c = Button(master, text="open", command=openThis)
    c.pack()

    mainloop()
        
    
# start gui in thread
gt = Thread(target=runGui, args=())
gt.start() 
    
"""

openThis()
for i in range(0,5):
    print i
