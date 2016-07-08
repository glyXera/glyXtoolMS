"""
Function to generate a consensus spectrum from a set of spectra

"""

import glyxtoolms

class Peak(glyxtoolms.io.GlyxXMLConsensusPeak, object):

    def __init__(self, x, y, spectrum):
        super(Peak, self).__init__(x, y)
        self.spectrum = spectrum
        self.neighbors = []
        self.graph = None
        self.subpeaks = []

class Graph(object):

    def __init__(self):
        self.vertices = []

    def plot(self, color, text=False):
        for v in self.vertices:
            plt.plot((v.x, v.x), (0, v.y), color=color)
            if text == True:
                plt.text(v.x, v.y, v.spectrum)

    def separate(self, tolerance):
        allPeaks = sorted(self.vertices, key=lambda p: p.x)
        while True:
            # search minimum Distance
            mini = None
            for i in range(0, len(allPeaks)-1):
                p1 = allPeaks[i]
                p2 = allPeaks[i+1]
                #if p1.spectrum != -1 and p1.spectrum == p2.spectrum:
                #    continue
                diff = p2.x-p1.x
                if diff < tolerance:
                    if mini == None or diff < mini[0]:
                        mini = (diff, p1, p2, i)
            if mini == None:
                break
            # generate new peak
            diff, p1, p2, i = mini
            x = (p1.x*p1.y+p2.x*p2.y)/float(p1.y+p2.y)
            y = p1.y+p2.y
            peak = Peak(x, y, -1)
            if p1.spectrum != -1:
                peak.subpeaks.append(p1)
            else:
                peak.subpeaks += p1.subpeaks
            if p2.spectrum != -1:
                peak.subpeaks.append(p2)
            else:
                peak.subpeaks += p2.subpeaks
            allPeaks.pop(i)
            allPeaks.pop(i)
            allPeaks.insert(i, peak)
        return allPeaks



def generateConsensusSpectrum(spectra, tolerance=0.1, minSpecCount=2, keepRange=0, keepAmount=5):

    allPeaks = []
    i = 0
    for spec in spectra:
        for x, y in spec:
            p = Peak(x, y, i)
            allPeaks.append(p)
        i += 1

    allPeaks = sorted(allPeaks, key=lambda p: p.x)

    delete = []
    # search neighbours
    for i in range(0, len(allPeaks)):
        p1 = allPeaks[i]
        m1 = p1.x
        t1 = p1.spectrum
        neighbors = []
        e = i
        while e > 0:
            e -= 1
            p2 = allPeaks[e]
            m2 = p2.x
            t2 = p2.spectrum
            if t2 == t1:
                break
            diff = abs(m1-m2)
            if diff > tolerance:
                break
            if diff < tolerance:
                neighbors.append(p2)

        e = i
        while e < len(allPeaks)-1:
            e += 1
            p2 = allPeaks[e]
            m2 = p2.x
            t2 = p2.spectrum
            if t2 == t1:
                break
            diff = abs(m1-m2)
            if diff > tolerance:
                break
            if diff < tolerance:
                neighbors.append(p2)

        allPeaks[i].neighbors = neighbors

    # find connected graphs
    graphs = []
    while True:
        # find peak without graph
        start = None
        for s in allPeaks:
            if s.graph == None:
                start = s
                break
        if start == None:
            break
        working = [start]
        graph = Graph()
        while len(working) > 0:
            current = working.pop()
            graph.vertices.append(current)
            current.graph = graph
            for s in current.neighbors:
                if s.graph == None:
                    s.graph = graph
                    working.append(s)
        graphs.append(graph)


    # search single peaks
    underThreshold = []
    overThreshold = []
    for g in graphs:
        for p in g.separate(tolerance):
            # introduce peak scaling
            nSpectra = len(set([v.spectrum for v in p.subpeaks]))
            pi = nSpectra/float(len(spectra))
            scale = 0.95 + 0.05 * (1+pi)**5
            p.y = p.y*scale

            if len(p.subpeaks)+1 < minSpecCount:
                underThreshold.append(p)
            else:
                overThreshold.append(p)

    # sort b after increasing intensity

    sort = sorted(overThreshold, key=lambda v: v.y)
    keep = []
    notkeep = []
    if keepRange == 0:
        return overThreshold, [], underThreshold

    for i in range(0, len(sort)):
        p1 = sort[i]
        N = 0
        for e in range(i+1, len(sort)):
            p2 = sort[e]
            if abs(p1.x-p2.x) < keepRange:
                N += 1
            if N > keepAmount:
                break
        if N <= keepAmount:
            keep.append(p1)
        else:
            notkeep.append(p1)

    return keep, notkeep, underThreshold
