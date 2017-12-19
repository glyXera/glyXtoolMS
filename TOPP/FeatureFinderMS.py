"""

find a feature to the given peak position within a picked mzML file

""" 
import glyxtoolms
import math
import pyopenms
import sys
import time

# precalculate patterns


def findPattern(monomass, charge, peaks, tolerance):
    # make assumtion about Nr of peaks that should occour
    sumP = 0
    pattern = glyxtoolms.masses.calcIsotopicPatternFromMass(monomass*charge,10)
    for N,p in pattern:
        if sumP > 0.99:
            break
        sumP += p

    candidates = []
    for e in range(0,N):
        mass = monomass + e*glyxtoolms.masses.MASS["H+"]/charge
        # find highest peak
        highest = None
        for peak in peaks:
            if peak.getMZ() < mass-tolerance:
                continue
            if peak.getMZ() > mass+tolerance:
                break
            if highest == None or highest.getIntensity() < peak.getIntensity():
                highest = peak
        if highest == None:
            highest = pyopenms.Peak1D()
            highest.setMZ(mass)
            highest.setIntensity(0.0)
        candidates.append(highest)
    if len(candidates) < 2:
        return None
    sumIntensity = sum([p.getIntensity() for p in candidates])
    if sumIntensity == 0:
        return None
    # calculate pattern
    #pattern = glyxtoolms.masses.calcIsotopicPatternFromMass(monomass*charge,len(candidates))
    pattern = pattern[:len(candidates)]
    sumP = sum([b for a,b in pattern])
    
    
    error = 0
    x = []
    y = []
    estimate = []
    for a,b in pattern:
        intensity_est = b*sumIntensity
        try:
            intensity_exp = candidates[a].getIntensity()
        except:
            print pattern, candidates
            raise Exception("foo")
        x.append(candidates[a].getMZ())
        y.append(intensity_exp)
        estimate.append(intensity_est)
        error += (intensity_est-intensity_exp)**2
    error = math.sqrt(error)
    error = error / sumIntensity*100
    result = {}
    result["error"] = error
    result["mass"] = monomass
    result["x"] = x
    result["y"] = y
    result["estimate"] = estimate
    result["sum"] = sumIntensity
    result["charge"] = charge
    return result

def findMonoIsotopicPeak(mz_org, charge, spec1, tolerance, precursorshift, mswindow):

    # calculate isotopic pattern
    peaks = []
    near = []
    # locate highest peak within location
    for peak in spec1:
        if peak.getMZ() < mz_org-mswindow:
            continue
        if peak.getMZ() > mz_org+mswindow:
            break
        if abs(peak.getMZ()-mz_org) < precursorshift:
            near.append(peak)
        peaks.append(peak)
    mz_candidates = [mz_org]
    if len(near) > 0:
        best = max(near, key=lambda p:p.getIntensity())
        #best2 = min(near, key=lambda p:abs(p.getMZ()-mz_org))
        mz_candidates.append(best.getMZ())

    # find which isotope mz is
    results = []
    for mz in mz_candidates:
        for charge in range(1,5): # TODO: open as parameter
            for i in range(-6,6):
                # calculate possible monoisotopes
                monomass = mz + i*glyxtoolms.masses.MASS["H+"]/charge
                result = findPattern(monomass, charge, peaks, tolerance)
                if result == None:
                    continue
                # check that pattern encloses mz_org
                isInPattern = False
                for x in result["x"]:
                    if abs(x-mz_org) < tolerance:
                        isInPattern = True
                        break
                minMZ = min(result["x"])-tolerance
                maxMZ = max(result["x"])+tolerance
                if minMZ < mz_org < maxMZ and isInPattern == True and sum(result["y"]) > 0:
                    results.append(result)
    return peaks, results


class Link:
    
    def __init__(self, rt, result):
        self.rt = rt
        self.mz = result["mass"]
        self.charge = result["charge"]
        self.result = result
        self.near = set()
        self.feature = None
        self.peaks = []
        self.nativeId = ""
        
class Feature:
    def __init__(self):
        self.ms2 = []
        self.charge = 0
        self.error = 0
        self.mz = 0.0
        self.rt = 0.0
        self.rtLow = 0.0
        self.rtHigh = 0.0
        self.mzLow = 0.0
        self.mzHigh = 0.0
        self.pattern = {}
                
    def extendRTDomain(self, ms1, tolerance, cutoff=20.0, maxRTspan=10000):
        
        # get highest spectrum as origin
        msBest = max(self.ms2, key = lambda ms: ms.result["sum"])
        self.rt = msBest.rt1
        normedIntensities = []
        sumIntensityBest = sum(msBest.result["y"])
        for mz, signal in zip(msBest.result["x"], msBest.result["y"]):
            normedIntensities.append(signal/sumIntensityBest)
        # get minimum and maximum rt from linked precursors
        minRT = min([link.rt1 for link in self.ms2])
        self.rtLow = minRT
        maxRT = max([link.rt for link in self.ms2])
        self.rtHigh = maxRT
        # find starting index
        for start,spec in enumerate(ms1):
            if spec.getNativeID() == msBest.nativeId:
                break
        assert spec.getNativeID() == msBest.nativeId
        i = start+1
        self.pattern = {}
        while i > 0:
            i -= 1
            spec = ms1[i]
            intensities = []
            for e, mz in enumerate(msBest.result["x"]):
                sumInt = 0
                sumMz = 0
                for peak in spec:
                    if peak.getMZ() < mz-tolerance:
                        continue
                    if peak.getMZ() > mz+tolerance:
                        break
                    sumInt += peak.getIntensity()
                    sumMz += peak.getMZ()*peak.getIntensity()
                intensities.append(sumInt)
                if sumInt > 0:
                    sumMz = sumMz/sumInt
                    self.pattern[e] = [(spec.getRT(), sumMz, sumInt)]+self.pattern.get(e, [])
                else:
                    self.pattern[e] = [(spec.getRT(), mz, 0)]+self.pattern.get(e, [])
                
            # calculate error
            sumIntensity = sum(intensities)
            err = 0
            for a,b in zip(intensities, normedIntensities):
                err += (b*sumIntensity - a)**2
            if sumIntensity > 0:
                err = math.sqrt(err) / sumIntensity * 100
            else:
                err = 100
            if spec.getRT() < self.rtLow:
                self.rtLow = spec.getRT()
            if sumIntensity < sumIntensityBest/cutoff:
                break
                
            if err > 35: # TODO: Handle spray loss spectra
                break
                
        i = start-1
        while i < len(ms1)-1:
            i += 1
            spec = ms1[i]
            intensities = []
            for e, mz in enumerate(msBest.result["x"]):
                sumInt = 0
                sumMz = 0
                for peak in spec:
                    if peak.getMZ() < mz-tolerance:
                        continue
                    if peak.getMZ() > mz+tolerance:
                        break
                        
                    sumInt += peak.getIntensity()
                    sumMz += peak.getMZ()*peak.getIntensity()
                intensities.append(sumInt)
                if sumInt > 0:
                    sumMz = sumMz/sumInt
                    self.pattern[e] = self.pattern.get(e, []) + [(spec.getRT(), sumMz, sumInt)]
                else:
                    self.pattern[e] = self.pattern.get(e, []) + [(spec.getRT(), mz, 0)]
            # calculate error
            sumIntensity = sum(intensities)
            err = 0
            for a,b in zip(intensities, normedIntensities):
                err += (b*sumIntensity - a)**2
            if sumIntensity > 0:
                err = math.sqrt(err) / sumIntensity * 100
            else:
                err = 100
            if spec.getRT() > self.rtHigh:
                self.rtHigh = spec.getRT()
            if sumIntensity < sumIntensityBest/cutoff:
                break
            if err > 35:
                break
        
            

def sortSpectra(exp):
    """ Sort MS1 and MS2 spectra into separate lists"""
    ms1 = []
    ms2 = []
    for spec in exp:
        if spec.getMSLevel() == 1:
            if spec.isSorted() == False:
                spec.sortByPosition()
            ms1.append(spec)
        elif spec.getMSLevel() == 2:
            p = spec.getPrecursors()[0]
            ms2.append((p.getMZ(), spec, ms1[-1]))
    return ms1, ms2

def handle_args(argv=None):
    import argparse
    usage = "\nFeaturefinder using MS2 spectra as seeds"
    parser = argparse.ArgumentParser(description=usage)
    parser.add_argument("--inMZML", dest="infile",help="File input - Picked mzML file")
    parser.add_argument("--outFeature", dest="outfile",help="Featurefile output")
    parser.add_argument("--tolerance", dest="tolerance",help="Mass tolerance in Dalton")
    parser.add_argument("--mswindow", dest="mswindow",help="Precursor mass window")
    parser.add_argument("--precursorshift", dest="precursorshift",help="Allowed precursor mass shift to search best precursor candidate")
    parser.add_argument("--rtwindow", dest="rtwindow",help="RT range of an eluting peak in seconds")
    
    if not argv:
        args = parser.parse_args(sys.argv[1:])
    else:
        args = parser.parse_args(argv)
    return args

def timed(s, starttime):
    print "["+str(int(time.time()-starttime))+" sec] " + s

def main(options):
    starttime = time.time()
    tolerance = float(options.tolerance)
    precursorshift = float(options.precursorshift)
    mswindow = float(options.mswindow)
    rtwindow = float(options.rtwindow)
    
    # load file
    timed("loading experiment",starttime)
    exp = glyxtoolms.lib.openOpenMSExperiment(options.infile)
    # assure sorted spectra
    exp.sortSpectra()
    timed("sort spectra",starttime)
    ms1, ms2 = sortSpectra(exp)

    links = []
    noresult = 0
    
    timed("finding precursors " + str(len(ms2)),starttime)
    for mz, spec2, spec1 in ms2:
        charge = spec2.getPrecursors()[0].getCharge()
        if charge == 0:
            charge = 1
        peaks, results = findMonoIsotopicPeak(mz, charge, spec1, tolerance, precursorshift, mswindow)
        if len(results) == 0:
            noresult += 1
            continue
        
        best = min(results, key = lambda r: r["mass"]*r["error"]/r["sum"]**2)
        rt = spec2.getRT()
        link = Link(rt, best)
        link.rt1 = spec1.getRT()
        link.nativeId = spec1.getNativeID()
        link.peaks = peaks
        links.append(link)

    print "could not find suitable starting pattern for ", noresult, "spectra from ", len(ms2) 
    timed("group precursors",starttime)
    # group precursors
    for l1 in links:
        for l2 in links:
            if l1.charge != l2.charge:
                continue
            if abs(l1.mz - l2.mz) > tolerance:
                continue
            if abs(l1.rt - l2.rt) > rtwindow:
                continue
            l1.near.add(l2)
    timed("group into features",starttime)
    # group into features
    features = []
    while True:
        # find link without feature
        working = set()
        for link in links:
            if link.feature == None:
                working.add(link)
                break
        if len(working) == 0:
            break
        feature = Feature()
        features.append(feature)
        while len(working) > 0:
            current = working.pop()
            current.feature = feature
            feature.ms2.append(current)
            for link in current.near:
                if link.feature == None:
                    working.add(link)

    timed("calculate precursor positions",starttime)
    # calculate mz and charge of feature
    for feature in features:
        feature.mz = sum([l.mz for l in feature.ms2])/len(feature.ms2)
        feature.charge = feature.ms2[0].charge
        # get lowest error
        feature.error = min([l.result["error"] for l in feature.ms2])
        feature.extendRTDomain(ms1, tolerance)
        # calculate dimensions
        masses = [l.result["x"][-1] for l in feature.ms2]
        feature.mzLow = feature.mz
        feature.mzHigh = max(masses)
            
    timed("merge features",starttime)
    # check features against each other
    # remove feature if mzLow is within other feature and rtLow and rtHigh within too
    todelete = set()
    for f1 in features:
        for f2 in features:
            if f1 == f2:
                continue
            if abs(f1.mz-f2.mz) > tolerance:
                continue
            if not (f1.mzLow <= f2.mzLow <= f1.mzHigh):
                continue
            if not (f1.rtLow <= f2.rtLow <= f1.rtHigh):
                continue
            if not (f1.rtLow <= f2.rtHigh <= f1.rtHigh):
                continue
            todelete.add(f2)
    for f in todelete:
        features.remove(f)

    newfeatures = set()
    # merge features
    for f1 in features:
        if f1.rtHigh == 0.0:
            print "zero", "f1" ,[ms.rt for ms in f1.ms2]
        for f2 in features:
            if f1 == f2:
                continue
            if abs(f1.mzLow - f2.mzLow) > tolerance:
                continue
            if f1.charge != f2.charge:
                continue
            if not((f1.rtLow <= f2.rtLow <= f1.rtHigh) or abs(f2.rtLow - f1.rtHigh) < 30):
                continue
            todelete.add(f1)
            todelete.add(f2)
            
            # create new feature
            newf = Feature()
            newf.error = min((f1.error, f2.error))
            newf.mz = min((f1.mz, f2.mz))
            newf.mzLow = min((f1.mzLow, f2.mzLow))
            newf.mzHigh= max((f1.mzHigh, f2.mzHigh))
            newf.rtLow = min((f1.rtLow, f2.rtLow))
            newf.rtHigh= max((f1.rtHigh, f2.rtHigh))
            if newf.rtHigh == 0.0:
                print "zero", "newf"
            newf.ms2 = sorted(set(f1.ms2).union(set(f2.ms2)),key=lambda ms: ms.rt)
            newf.rt = (f1.rt+ f2.rt)/2.0
            newfeatures.add(newf)

    features += list(newfeatures)     
    
    timed("write featuremap",starttime)
    fm = pyopenms.FeatureMap()
    N = 0
    for feature in features:
        # calc bounding boxes from pattern
        f = pyopenms.Feature()
        f.ensureUniqueId()
        f.setRT(feature.rt)
        f.setMZ(feature.mz)
        f.setCharge(feature.charge)
        hulls = []
        sumIntensity = 0
        for i in feature.pattern:
            pattern = feature.pattern[i]
            minRT = feature.rtLow-1 # eliminate rounding error by adding a rt tolerance
            maxRT = feature.rtHigh+1
            #minRT = min([p[0] for p in pattern])
            #maxRT = max([p[0] for p in pattern])
            minMZ = min([p[1] for p in pattern])-tolerance
            maxMZ = max([p[1] for p in pattern])+tolerance
            sumIntensity += sum([p[2] for p in pattern])
            h = pyopenms.ConvexHull2D()
            h.addPoint([minRT,minMZ])
            h.addPoint([maxRT,minMZ])
            h.addPoint([maxRT,maxMZ])
            h.addPoint([minRT,maxMZ])
            hulls.append(h)
        f.setConvexHulls(hulls)
        f.getConvexHull().expandToBoundingBox()
        f.setIntensity(sumIntensity)
        f.setOverallQuality(feature.error)
        
        # check if boundingbox is fullfilles
        h = f.getConvexHull()
        b = h.getBoundingBox()
        minRT, minMZ = b.minPosition()
        maxRT, maxMZ = b.maxPosition()

        if sumIntensity == 0:
            N += 1
            continue
        if charge == 0:
            N += 1
            continue
        fm.push_back(f)
    print "ignoring ", N, " features that have no peaks or a charge of 0"
    fxml = pyopenms.FeatureXMLFile()
    fxml.store(options.outfile, fm)
 

if __name__ == "__main__":
    options = handle_args()
    main(options)
