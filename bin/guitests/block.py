import time
import threading
import _longwait
import cython
import sys

def longWait():
    print "sleep"
    #longwait.busy_sleep(100000000)
    time.sleep(5)
    print "wakeup"
    
def longWaitCpython():
    print "sleep"
    _longwait.wasteTime()
    print "wakeup"    
    
def shortWait(N):
    if N > 0:
        print "running"
        time.sleep(1)
        shortWait(N-1)
    else:
        print "stopped"
        
        
    
# run two threads, one     

# a) start periodic thread
tShort = threading.Thread(target=shortWait,args=(10,))
tShort.start()

# b) start long thread
tLong = threading.Thread(target=longWaitCpython,args=())
tLong.start()
 
