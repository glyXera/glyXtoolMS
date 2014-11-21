import time
import threading
from multiprocessing import Process,Queue

def request(q):
    if q.empty() == True:
        threading.Timer(1, request, args=(q,) ).start()
    else:
        print q.get()

def loooooong(q):
    print "do stuff"
    time.sleep(5)
    print "finished"
    running = False
    q.put("blah")

       
q = Queue()

t = Process(target=loooooong, args=(q,))
t.start()

# start periodic request of new stuff
threading.Timer(1, request,args=(q,)).start()
#print q.get()
#t.join()

