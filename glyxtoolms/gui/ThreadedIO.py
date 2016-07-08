import Queue
import threading

class ThreadedIO(object):

    def __init__(self):
        self.queue = Queue.Queue()
        self.running = False
        self.result = None
        self.thread = None


    def updateExternal(self):
        self.running = False
        raise Exception("Overwrite this function!")

    def checkQueue(self):
        if self.running == False:
            self.updateExternal(running=True)
            return
        if self.queue.empty() == True:
            self.updateExternal(running=True)
            ct = threading.Timer(1, self.checkQueue, args=())
            ct.deamon = True
            ct.start()
        else:
            self.running = False
            self.result = self.queue.get()
            self.updateExternal(running=False)

    def start(self):
        try:
            self.thread = threading.Thread(target=self.threadedAction, args=())
            self.running = True
            self.thread.start()
            self.checkQueue()
        except:
            self.running = False # stop checkQueue()
            self.queue.put("error")
            raise


    def threadedAction(self):
        self.queue.put("result")
        self.running = False
        raise Exception("Overwrite this function!")
