from matplotlib import pyplot as plt
class Histogram:
    
    def __init__(self,binwidth):
        print "version 1.0"
        self.bins = {}
        self.colors = {}
        self.binwidth = float(binwidth)
        self.maxValue = 0

    def addSeries(self,series,label="",color="black"):
        if not label in self.bins:
            self.bins[label] = {}
        self.colors[label] = color
        for x in series:
            b = int(x/self.binwidth)
            if not b in self.bins[label]:
                self.bins[label][b] = 0
            self.bins[label][b] += 1
            if self.bins[label][b] > self.maxValue:
                self.maxValue = self.bins[label][b]

    def ploth(self,order=None,axis=None):
        if not order:
            order = self.bins.keys()        
        leftStart = {}
        for label in order:
            bottom = []
            width = []
            left = []
            for b in self.bins[label]:
                if not b in leftStart:
                    leftStart[b] = 0
                bottom.append(b*self.binwidth)
                width.append(self.bins[label][b])
                left.append(leftStart[b])
                leftStart[b] += self.bins[label][b]
            if axis:
                axis.barh(bottom,width,height=self.binwidth,left=left,label=label,color=color)
            else:
                plt.barh(bottom,width,height=self.binwidth,left=left,label=label,color=color)

    def plot(self,order=None,axis=None):
        if not order:
            order = self.bins.keys()        
        bottomStart = {}
        for label in order:
            bottom = []
            height = []
            left = []
            if not label in self.bins:
                continue
            for b in self.bins[label]:
                if not b in bottomStart:
                    bottomStart[b] = 0
                left.append(b*self.binwidth)
                height.append(self.bins[label][b])
                bottom.append(bottomStart[b])
                bottomStart[b] += self.bins[label][b]
            if axis:
                axis.bar(left,height,width=self.binwidth,bottom=bottom,label=label,color=self.colors[label])
            else:
                plt.bar(left,height,width=self.binwidth,bottom=bottom,label=label,color=self.colors[label]) 

"""
h = Histogram(0.2)
h.addSeries([1,2,3],label="label1",color=color)
h.plot(axis=plt,order=["label1"])
plt.show()
"""
