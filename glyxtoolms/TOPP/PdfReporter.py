# Tool for generating excel data
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle, TA_CENTER
from reportlab.lib.units import inch, mm
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph, Table, SimpleDocTemplate, Spacer,TableStyle
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.lib import colors

from PyPDF2 import PdfFileReader, PdfFileWriter

import glyxtoolms
import math
import re
import sys
import os


def getSpectrum(exp,nativeId):
    msmsSpec = None
    msSpec = None
    index = int(nativeId.split("=")[-1])-1
    msmsSpec = exp[index]
    try:
        assert msmsSpec.getNativeID() == nativeId
        assert msmsSpec.getMSLevel() == 2
    except:
        for index,s in enumerate(exp):
            if s.getNativeID() == nativeId:
                assert s.getMSLevel() == 2
                msmsSpec = s
                break
    # find precursor spectrum
    while index > 0:
        index -= 1
        s = exp[index]
        if s.getMSLevel() == 1:
            msSpec = s
            break
    return msSpec,msmsSpec

def findScale(start, end, NrScales):
    diff = abs(end-start)/NrScales
    exp = math.floor(math.log(diff)/math.log(10))
    base = 10**exp
    nr = diff/base
    if nr < 0 or nr >= 10:
        raise Exception("error in scaling")
    # choose nearest scale of [1, 2, 2.5, 5]
    scales = [1, 2, 2.5, 5]
    sortNr = [(abs(s-nr), s) for s in scales]
    sortNr.sort()
    diff = sortNr[0][1]*base

    startAxis = math.floor(start/diff)*diff
    endAxis = math.ceil(end/diff)*diff
    return startAxis, endAxis, diff, exp
    
def shortNr(nr, exp):
    # shorten nr if precision is necessary
    if exp <= 0:
        return round(nr, int(-exp+1))
    if exp > 4:
        e = int(math.floor(math.log(nr)/math.log(10)))
        b = round(nr/float(10**e), 4)
        return str(b)+"E"+str(e)
    return int(nr)

class Spectrum(object):
    
    def __init__(self,canvas,posx1,posy1,posx2,posy2):
        
        self.canvas = canvas
        
        self.posx1 = posx1
        self.posy1 = posy1
        self.posx2 = posx2
        self.posy2 = posy2
        
        self.m_mz = 1
        self.b_mz = 0
        
        self.m_int = 1
        self.b_int = 0
        
        self.mz1 = 0
        self.mz2 = 2000
        self.int1 = 0
        self.int2 = 10000
        self.setXAxis(self.mz1,self.mz2)
        self.setYAxis(self.int1,self.int2)
        #self.canvas.rect(self.posx1,self.posy1,self.posx2-self.posx1,self.posy2-self.posy1)

    def setXAxis(self,mz1,mz2):
        self.mz1 = mz1
        self.mz2 = mz2
        
        self.m_mz = (self.posx2-self.posx1)/float((mz2-mz1))
        self.b_mz = self.posx1-self.m_mz*mz1
        
    def setYAxis(self,int1,int2):
        self.int1 = int1
        self.int2 = int2
        
        self.m_int = (self.posy2-self.posy1)/float((int2-int1))
        self.b_int = self.posy1-self.m_int*int1
        
    def X(self,mz):
        return self.m_mz*mz+self.b_mz
        
    def Y(self,intens):
        return self.m_int*intens+self.b_int
        
    def draw(self, hit):
        
        def determineFragmentOrder(fragments):
            ranking = []
            for f in fragments:
                count = f.name.count("+")+f.name.count("-")*2
                if len(f.isotopes) == 0:
                    count += 3
                count += f.charge
                ranking.append((count,-f.peak.y,f))
            ranking = sorted(ranking)
            return [f for rank,intensity,f in ranking]
                
        
        startMZ,endMZ,diffMZ,expMZ = findScale(0, max([p.x for p in hit.feature.consensus]),8)
        startInt,endInt,diffInt,expInt = findScale(0, max([p.y for p in hit.feature.consensus]),8)
        self.setXAxis(startMZ,endMZ)
        self.setYAxis(startInt,endInt)
        self.ticksMZ = (startMZ,endMZ,diffMZ,expMZ)
        self.ticksInt = (startInt,endInt,diffInt,expInt)
        
        self.canvas.setLineWidth(0.1)
        
        order = ['PEPTIDEION', 'GLYCOPEPTIDEION', 'OXONIUMION','BION','YION', 'CION','ZION', 'IMMONIUMION']
        drawOrder = []
        fragmentPeaks = {}
        types = {}
        for f in hit.fragments.values():
            types[f.typ] = types.get(f.typ,[]) + [f]
            f.isotopes = set()
        for typ in order:
            #for f in sorted(types.get(typ,[]),key=lambda f:f.peak.y,reverse=True):
            for f in determineFragmentOrder(types.get(typ,[])):
                if not f.peak in fragmentPeaks:
                    drawOrder.append(f)
                    fragmentPeaks[f.peak] = f

        fragmentColors = {'PEPTIDEION':"green", 'GLYCOPEPTIDEION':"green", 'OXONIUMION':"red",'BION':"blue",'YION':"blue",'CION':"blue",'ZION':"blue", 'IMMONIUMION':"yellow"}
        
        # link isotopes
        for f in types.get("ISOTOPE",[]):
            for parentname in f.parents:
                parent = hit.fragments[parentname]
                parent.isotopes.add(f)
        
        annotationBoxes = []
        drawnPeaks = []
        # draw fragments first
        for f in drawOrder:
            color = fragmentColors[f.typ]
            text = f.name+"\n"+str(round(f.peak.x,2))
            self.drawPeak(f.peak,color,text,annotationBoxes)
            drawnPeaks.append(f.peak)
            
        # draw isotopes
        for f in drawOrder:
            color = fragmentColors[f.typ]
            for isotope in f.isotopes:
                if isotope.peak in drawnPeaks:
                    continue
                #text = isotope.name+"\n"+str(round(f.peak.x,2))
                text = str(round(isotope.peak.x,2))
                self.drawPeak(isotope.peak,color,text,annotationBoxes)
                drawnPeaks.append(isotope.peak)
            
        # draw remaining peaks
        for peak in sorted(hit.feature.consensus,key=lambda p:p.y,reverse=True):
            if peak in drawnPeaks:
                continue
            self.drawPeak(peak,"black",str(round(peak.x,2)),annotationBoxes)
            drawnPeaks.append(peak)

        self.drawAxis()
        
    def drawAxis(self):

        
        self.canvas.setStrokeColor("black")
        self.canvas.setLineWidth(1)

        self.canvas.line(self.X(self.mz1),self.Y(self.int1),self.X(self.mz1),self.Y(self.int2))
        self.canvas.drawCentredString(self.X(self.mz1), self.Y(self.int2)+4, "Intensity")
        self.canvas.line(self.X(self.mz1),self.Y(self.int1),self.X(self.mz2),self.Y(self.int1))
        self.canvas.drawString(self.X(self.mz2)+2, self.Y(self.int1)-1, "m/z")
        # draw arrow heads
        self.canvas.line(self.X(self.mz1),self.Y(self.int2),self.X(self.mz1)-5,self.Y(self.int2)-5)
        self.canvas.line(self.X(self.mz1),self.Y(self.int2),self.X(self.mz1)+5,self.Y(self.int2)-5)
        self.canvas.line(self.X(self.mz2),self.Y(self.int1),self.X(self.mz2)-5,self.Y(self.int1)-5)
        self.canvas.line(self.X(self.mz2),self.Y(self.int1),self.X(self.mz2)-5,self.Y(self.int1)+5)
        
        fontSize = 5
        self.canvas.setFont("Courier", fontSize)
        # draw x-tick
        start,end,diff,exp = self.ticksMZ
        y = self.Y(self.int1)
        while start < end:
            if start > self.mz1 and start < self.mz2:
                x = self.X(start)
                self.canvas.drawCentredString(x, y-fontSize-6, str(shortNr(start, exp)))
                self.canvas.line(x,y,x,y-4)
            start += diff
        # draw y-tick
        start,end,diff,exp = self.ticksInt
        x = self.X(self.mz1)
        while start < end:
            if start > self.int1 and start < self.int2:
                y = self.Y(start)
                self.canvas.drawRightString(x-6, y-fontSize/2.0+1, str(shortNr(start, exp)))
                self.canvas.line(x,y,x-4,y)
            start += diff

    def drawPeak(self,peak,color,text,annotationBoxes,debug=False):
        text = text.split("\n")
        self.canvas.setStrokeColor(color)
        
        self.canvas.line(self.X(peak.x),self.Y(0),self.X(peak.x),self.Y(peak.y))
        fontSize = 5
        self.canvas.setFont("Courier", fontSize)
        #annotationDimensions = [0,len(text)*(fontSize+2)]
        boxHeight = fontSize
        x,y = self.X(peak.x), self.Y(peak.y)
        # get dimensions
        newAnnotations = []
        for i,part in enumerate(text[::-1]):
            boxWidth = stringWidth(part, "Courier", fontSize)
            box = [x-boxWidth/2.0,y+i*boxHeight+2,x+boxWidth/2.0,y+(i+1)*boxHeight+2]
            # check if box is intersecting something
            isIntersecting = False
            for drawn in annotationBoxes:
                isIntersecting = not (box[2] < drawn[0] or box[0] > drawn[2] or box[3] < drawn[1] or box[1] > drawn[3])
                if isIntersecting == True:
                    if debug:
                        print box, "intersecting",drawn
                    break
            if isIntersecting == False:
                self.canvas.drawCentredString(x, y+i*fontSize+2, part)
                #self.canvas.rect(x-boxWidth/2.0,y+i*boxHeight+2,boxWidth,boxHeight)
                newAnnotations.append(box)
        annotationBoxes += newAnnotations


class Header(object):
    
    def __init__(self,canvas,posx1,posy1,posx2,posy2):
        self.canvas = canvas
        self.posx1 = posx1
        self.posy1 = posy1
        self.posx2 = posx2
        self.posy2 = posy2
        self.style = getSampleStyleSheet()["Normal"]
        #self.canvas.rect(self.posx1,self.posy1,self.posx2-self.posx1,self.posy2-self.posy1)
        
    def draw(self,hit, fragTyp):
        font = "Courier"
        fontSize = 10
        labels = []
        labels.append("Peptide: ")
        labels.append("Glycan: ")
        labels.append("Spectrum type: ")
        labels.append("Percursor mass: ")
        labels.append("Precursor charge: ")
        labels.append("Precursor RT: ")
        labels.append("Precursor Error: ")
        labels.append("Proteins: ")
        labels.append("Glycosylation Sites: ")
        labels.append("Explained by: ")
        labels.append("Peptide mass: ")
        labels.append("Glycan mass: ")
        labels.append("Scans: ")
        labels.append("Score: ")
        labels.append("Explained Intensity: ")
        
        offset = 0
        for line in labels:
            w = stringWidth(line, font, fontSize)
            if w > offset:
                offset = w
        
        textobject = self.canvas.beginText(self.posx1, self.posy2)
        textobject.setFont(font, fontSize)
        for line in labels:
            textobject.textLine(line)
        self.canvas.drawText(textobject)
        
        
        if "explainedByPeptideInference" in hit.tags:
            comment = "infered by precursor mass"
        elif "explainedByProteinInference" in hit.tags:
            comment = "infered from the existence of the protein"
        elif "explainedByETD" in hit.tags and "explainedByHCD" in hit.tags:
            comment = "HCD and ETD"
        elif "explainedByETD" in hit.tags:
            comment = "ETD"
        else:
            comment = "HCD"
        
        
        values = []
        values.append("")
        values.append(hit.glycan.toString())
        values.append(fragTyp)
        values.append(str(round(hit.feature.getMZ(),4)))
        values.append(str(hit.feature.getCharge()))
        values.append(str(round(hit.feature.getRT()/60.0,2)) + " min")
        mz = (hit.peptide.mass+hit.glycan.mass+glyxtoolms.masses.MASS["H+"]*hit.feature.getCharge())/hit.feature.getCharge()
        values.append(str(round(glyxtoolms.lib.calcMassError(mz,hit.feature.getMZ(),"ppm"),2)) + " ppm / " + str(round(hit.feature.getMZ()-mz,4)) + " Da")
        values.append(", ".join(hit.proteins))
        values.append(", ".join([typ+str(pos) for pos,typ in sorted(hit.peptide.glycosylationSites)]))
        values.append(comment)
        values.append(str(round(hit.peptide.mass,4)))
        values.append(str(round(hit.glycan.mass,4)))
        values.append(",".join(["scan="+s.getNativeId().split("=")[-1] for s in hit.feature.spectra]))
        if fragTyp == "ETD":
            score = hit.toolValues.get("etdScore2",0.0)
        else:
            score = hit.toolValues.get("hcdScore2",0.0)
        values.append(str(round(abs(score),2)))
        if fragTyp == "ETD":
            explainedInt = hit.toolValues.get("explainedETD",0.0)
        else:
            explainedInt = hit.toolValues.get("explainedHCD",0.0)
        values.append(str(round(abs(explainedInt*100),2))+"%")
        
        textobject = self.canvas.beginText(self.posx1+offset, self.posy2)
        textobject.setFont(font, fontSize)
        for line in values:
            textobject.textLine(line)
        self.canvas.drawText(textobject)
        
        # draw peptide sequence
        textobject = self.canvas.beginText(self.posx1+offset, self.posy2)
        textobject.setFont(font, fontSize)

        glycosites = [pos-hit.peptide.start for pos,typ in hit.peptide.glycosylationSites]
        mods = {}
        for m in hit.peptide.modifications:
             mods[m.position] = m

        for pos,amino in enumerate(hit.peptide.sequence):
            if pos in glycosites:
                textobject.setFillColor(colors.red)
            else:
                textobject.setFillColor(colors.black)
            textobject.textOut(amino)
            if pos in mods:
                for s in "("+mods[pos].name+")":
                    textobject.textOut(s)
        self.canvas.drawText(textobject)
        
class SequenceCoverage(object):
    
    def __init__(self,canvas,posx1,posy1,posx2,posy2):
        self.canvas = canvas
        self.posx1 = posx1
        self.posy1 = posy1
        self.posx2 = posx2
        self.posy2 = posy2
        #self.canvas.rect(self.posx1,self.posy1,self.posx2-self.posx1,self.posy2-self.posy1)
        
    def determineSequenceCoverage(self, hit):
        show = []
        for f in hit.fragments.values():
            if f.charge > 2:
                continue
            if f.typ not in ['BION','YION','CION','ZION']:
                continue
            if "-" in f.name:
                continue
            if "+" in f.name[:-3]:
                if not "+HexNAc1(" in f.name and not "+"+hit.glycan.toString()+"(" in f.name:
                    continue
            f.hasIsotop = f.name+"/1" in hit.fragments
            show.append(f)
            
        # parse series and position
        series = {}
        for f in show:
            nr = int(re.search("(^.|\*)\d+",f.name).group()[1:])
            hasGlycan = "+" in f.name[:-3]
            series[f.typ] = series.get(f.typ, {})
            series[f.typ][nr] = series[f.typ].get(nr,False)
            if hasGlycan == True:
                series[f.typ][nr] = True
        return series
        
    def draw(self,hit):
        width = self.posx2-self.posx1
        height = self.posy2-self.posy1
        sequence = hit.peptide.toString()
        
        ionSeries = self.determineSequenceCoverage(hit)
        
        # get right fontsize
        fontSize = 5
        font = "Courier"
        while True:
            fontSize += 1
            if fontSize*2 > height:
                break
            textWidth = stringWidth(sequence, font, fontSize)
            if textWidth > width:
                break
        fontSize -= 0
        self.canvas.setFont(font, fontSize)
        # draw peptide sequence
        textobject = self.canvas.beginText((self.posx1+self.posx2-textWidth)/2.0, self.posy1+height/2.0-fontSize/2)
        textobject.setFont(font, fontSize)

        glycosites = [pos-hit.peptide.start for pos,typ in hit.peptide.glycosylationSites]
        mods = {}
        for m in hit.peptide.modifications:
             mods[m.position] = m
        self.canvas.setFont("Courier", fontSize/4) # font for ion series
        for pos,amino in enumerate(hit.peptide.sequence):
            if pos in glycosites:
                textobject.setFillColor(colors.red)
            else:
                textobject.setFillColor(colors.black)
            # y and z series
            yzPos = len(hit.peptide.sequence)-pos
            if yzPos in ionSeries.get("YION",{}) or yzPos in ionSeries.get("ZION",{}):
                if yzPos in ionSeries.get("YION",{}):
                    name = "y"
                    hasGlycan = ionSeries["YION"][yzPos]
                else:
                    name = "z"
                    hasGlycan = ionSeries["ZION"][yzPos]
                if hasGlycan == True:
                    self.canvas.setDash(2,2)
                else:
                    self.canvas.setDash()
                x = textobject.getX()
                y = textobject.getY()
                self.canvas.line(x,y+fontSize/3.0,x,y+fontSize)
                self.canvas.line(x,y+fontSize,x+6,y+fontSize)
                
                self.canvas.drawCentredString(x+3, y+fontSize+2, name+str(yzPos))

            textobject.textOut(amino)
            if pos in mods:
                for s in "("+mods[pos].name+")":
                    textobject.textOut(s)
            ## b and c series
            bcPos = pos+1
            if bcPos in ionSeries.get("BION",{}) or bcPos in ionSeries.get("CION",{}):
                if bcPos in ionSeries.get("BION",{}):
                    name = "b"
                    hasGlycan = ionSeries["BION"][bcPos]
                else:
                    name = "c"
                    hasGlycan = ionSeries["CION"][bcPos]
                if hasGlycan == True:
                    self.canvas.setDash(2,2)
                else:
                    self.canvas.setDash()
                x = textobject.getX()
                y = textobject.getY()
                self.canvas.line(x,y+fontSize/3.0,x,y-fontSize/3)
                self.canvas.line(x-6,y-fontSize/3,x,y-fontSize/3)
                self.canvas.drawCentredString(x-3, y-fontSize/3-fontSize/4, name+str(bcPos))
        self.canvas.setDash() # reset dash
        self.canvas.drawText(textobject)
        
class ReportIndex(object):
    """"""
 
    #----------------------------------------------------------------------
    def __init__(self):
        """Constructor"""
        self.width, self.height = A4
        self.styles = getSampleStyleSheet()
    
    def debug(self):
        style = ParagraphStyle(name = 'fbfj', fontName = 'Courier', fontSize = 10)
        anchorname = "page3.html#0"
        return Paragraph('<a href = '+anchorname+'>Jump</a>',style)
 
    #----------------------------------------------------------------------
    def run(self,pdfname):
        """
        Run the report
        """
        
        self.doc = SimpleDocTemplate(pdfname)
        self.story = []

        self.story.append(self.debug())
        
 
        self.doc.build(self.story)


########################################################################
class IdentificationReport(object):
    """"""
 
    #----------------------------------------------------------------------
    def __init__(self,hit,fragTyp):
        """Constructor"""
        self.width, self.height = A4
        self.styles = getSampleStyleSheet()
        self.hit = hit
        self.fragTyp = fragTyp
        self.spaceHeader = 60*mm
        self.spaceCoverage = 30*mm
        self.spaceSpectrum = 80*mm
        self.spacer = 10*mm
 
    #----------------------------------------------------------------------
    def run(self,pdfname):
        """
        Run the report
        """
        
        self.doc = SimpleDocTemplate(pdfname)
        self.story = []
        self.story.append(self.generateAnchor())
        self.story.append(Spacer(self.width, self.spaceHeader+self.spaceCoverage+self.spaceSpectrum+self.spacer))
        self.createFragmentIontable()
        self.story.append(self.debug())
        
 
        self.doc.build(self.story, onFirstPage=self.drawCanvas)
        
    def generateAnchor(self):
        style = ParagraphStyle(name = 'Header', fontName = 'Courier', fontSize = 0)
        anchorname = "page3.html#0"
        return Paragraph('<a name = '+anchorname+'></a>',style)
        
    def debug(self):
        style = ParagraphStyle(name = 'fbfj', fontName = 'Courier', fontSize = 10)
        anchorname = "page3.html#0"
        return Paragraph('<a href = '+anchorname+'>Jump</a>',style)
 
    #----------------------------------------------------------------------
    def drawCanvas(self, canvas, doc):
        """
        Create the header and the spectrum
        """
        y0 = self.height - 15*mm - self.spaceHeader
        y1 = self.height - 15*mm
        self.header = Header(canvas,15*mm,y0,self.width-15*mm,y1)
        self.header.draw(self.hit,self.fragTyp)
        
        y1 = y0
        y0 = y0-self.spaceCoverage     
        self.coverage = SequenceCoverage(canvas,15*mm,y0,self.width-15*mm,y1)
        self.coverage.draw(self.hit)
        
        y1 = y0-self.spacer
        y0 = y0-self.spaceSpectrum-self.spacer
        self.spectrum = Spectrum(canvas, 20*mm,y0,self.width-15*mm,y1)
        self.spectrum.draw(self.hit)
    
    #----------------------------------------------------------------------
    def createFragmentIontable(self):

        # generate fragment list
        fragmentList = {}
        for f in self.hit.fragments.values():
            #if f.charge == 1:
            #    continue
            
            if f.typ == 'ISOTOPE':
                continue
            f.hasIsotop = f.name+"/1" in self.hit.fragments
            fragmentList[f.typ] = fragmentList.get(f.typ, []) + [f]


        for typ in fragmentList:
            if typ in ['BION', 'YION','CION', 'ZION']:
                sortList = sorted([(int(re.search("(^.|\*)\d+",f.name).group()[1:]),f.name,f.charge,f) for f in fragmentList[typ]])
                fragmentList[typ] = [p for pos,name,charge,p in sortList]
            else:
                fragmentList[typ] = sorted(fragmentList[typ], key=lambda f:(f.mass,f.name))
            
        typs =[('IMMONIUMION',colors.red),('OXONIUMION',colors.red),('PEPTIDEION',colors.green),('GLYCOPEPTIDEION',colors.green),('BION',colors.blue), ('YION',colors.blue),('CION',colors.blue), ('ZION',colors.blue)]


        data = []
        data.append(["Ion name", "Ion type","Mass [Da]","Intensity\n[% highest]","z","has\nisotope", "Mass error\n[Da]", "Mass error\n[ppm]"])
        rowHeights = [6*mm]
        maxCount = max([p.y for p in self.hit.feature.consensus])
        colorIndizes = []
        row = 0
        rowstart = 0
        for typ,color in typs:
            for f in fragmentList.get(typ,[]):
                data.append([f.name,  typ, round(f.mass,4), round(f.peak.y/maxCount*100,2), f.charge, f.hasIsotop, round(f.peak.x-f.mass,4), round(glyxtoolms.lib.calcMassError(f.peak.x,f.mass,"ppm"),2)])
                rowHeights.append(3*mm)
                row += 1
            colorIndizes.append(('TEXTCOLOR', (0, rowstart+1), (-1, row), color))
            rowstart = row
            
        table=Table(data,rowHeights=rowHeights)
        table.setStyle(TableStyle([('FONTSIZE', (0, 0), (-1, -1), 5),
                                   ('ALIGN', (3, 0), (-1, -1), "CENTER")]+colorIndizes))

        self.story.append(table)

def pdf_cat(input_paths, output_stream):
    input_streams = []
    try:
        for path in input_paths:
            input_streams.append(open(path, 'rb'))
        writer = PdfFileWriter()
        for reader in map(PdfFileReader, input_streams):
            for n in range(reader.getNumPages()):
                writer.addPage(reader.getPage(n))
        writer.write(output_stream)
    finally:
        for f in input_streams:
            f.close()
 
def generateSmallPdfs(analysisfile, pdffolder, fragTyp):
    
    print "reading in Analysis file ", analysisfile
    glyML = glyxtoolms.io.GlyxXMLFile()
    glyML.readFromFile(analysisfile)
    peptides = {}
    for hit in glyML.glycoModHits:
        #hit = glyML.glycoModHits[527]
        key = hit.feature.id+"-"+hit.peptide.toString()+"+"+hit.glycan.toString()
        if key not in peptides:
            peptides[key] = hit
            hit.proteins = {hit.peptide.proteinID}
        else:
            peptides[key].proteins.add(hit.peptide.proteinID)
        

    for hit in peptides.values():
        t = IdentificationReport(hit,fragTyp)
        t.run(os.path.join(pdffolder,hit.feature.id+"-"+hit.peptide.toString()+"+"+hit.glycan.toString()+".pdf"))
    return peptides

def getInputFile(option):
    files = []
    if option:
        for mergepath in option:
            files += mergepath.split(" ")
    return files

class Args(object):
    
    def __init__(self):
        pass

def handle_args(argv=None):

    if not argv:
        argv = sys.argv[1:]
    args = Args()
    for part in " ".join(argv).split("--"):
        if len(part) == 0:
            continue
        sp = part.strip().split(" ")
        if len(sp) == 1:
            value = None
        elif len(sp) == 2:
            value = sp[1:][0]
        else:
            value = sp[1:]
        attr = sp[0]
        setattr(args, attr,value)
    return args

def deletePdfs(path):
    for name in os.listdir(path):
        if name.endswith(".pdf"):
            os.unlink(os.path.join(path,name))
    print "deleting ", path

def main(options):
    
    print "tmp ",options.tmp
    print "inMZML ",options.inMZML
    print "inETD ",options.inETD
    print "inHCD ",options.inHCD
    print "out ",options.out
    #print "etdIn", getInputFile(options.inETD)
    #print "hcdIn", getInputFile(options.inHCD)
    
    
    #exp = glyxtoolms.lib.openOpenMSExperiment(options.inMZML)
    #
    #print "reading in ETD Analysis file"
    #etdFile = glyxtoolms.io.GlyxXMLFile()
    #etdFile.readFromFile(options.inETD)
    #
    #print "reading in HCD Analysis file"
    #hcdFile = glyxtoolms.io.GlyxXMLFile()
    #hcdFile.readFromFile(options.inHCD)
    #
    #print "generate feature lookup"
    #featureLookup = {}
    #for feature in etdFile.features:
    #    featureLookup[feature.id] = [feature,None]
    #    
    #for feature in etdFile.features:
    #    featureLookup[feature.id] = featureLookup.get(feature.id,[None,None])
    #    featureLookup[feature.id][1] = feature
    #
    # generate folder structure
    folderReport = os.path.join(options.tmp,"glyxtool_pdfreport")
    folderSubpages = os.path.join(folderReport,"sub")
    folderHCD = os.path.join(folderReport,"hcd")
    folderETD = os.path.join(folderReport,"etd")
    # check if folder exists
    if not os.path.exists(folderReport):
        os.mkdir(folderReport)
        
    if not os.path.exists(folderSubpages):
        os.mkdir(folderSubpages)
    else:
        deletePdfs(folderSubpages)
        
    if not os.path.exists(folderHCD):
        os.mkdir(folderHCD)
    else:
        deletePdfs(folderHCD)
        
    if not os.path.exists(folderETD):
        os.mkdir(folderETD)
    else:
        deletePdfs(folderETD)

    peptides = {}
    if options.inHCD:
        peptidesHCD = generateSmallPdfs(options.inHCD,folderHCD,"HCD")
        for key in peptidesHCD:
            if not key in peptides:
                peptides[key] = peptidesHCD[key]
                
    if options.inETD:
        peptidesETD = generateSmallPdfs(options.inETD,folderETD,"ETD")
        for key in peptidesETD:
            if not key in peptides:
                peptides[key] = peptidesETD[key]
    
    print "generating reporting order"
    # group proteins
    proteinToProtein = {}
    proteinToPeptides  = {}
    for hit in peptides.values():
        hit.bestValue = max((hit.toolValues.get("etdScore2",0.0),hit.toolValues.get("hcdScore2",0.0)))
        for prot in hit.proteins:
            proteinToProtein[prot] = proteinToProtein.get(prot, set()).union(hit.proteins)
            proteinToPeptides[prot] = proteinToPeptides.get(prot, set()).union({hit})
    
    proteinKeys = {}
    for prot in proteinToProtein:
        key = "-".join(sorted(proteinToProtein[prot]))
        proteinKeys[key] = proteinKeys.get(key, []) + [prot]
        
    proteinGroupToPeptides = {}
    for protgroup in proteinKeys:
        for prot in proteinKeys[protgroup]:
            proteinGroupToPeptides[protgroup] = proteinGroupToPeptides.get(protgroup,set()).union(proteinToPeptides[prot])
    
    sortedProteinGroupToPeptides = []
    for protgroup in proteinGroupToPeptides:
        hits = proteinGroupToPeptides[protgroup]
        maxValue = max([hit.bestValue for hit in hits])
        sortedProteinGroupToPeptides.append((maxValue,protgroup))
    
    sortedLookupKeys = []
    for rank,protgroup in sorted(sortedProteinGroupToPeptides, reverse=True):
        pepsort = {}
        for hit in proteinGroupToPeptides[protgroup]:
            seq = hit.peptide.toString()
            pepsort[seq] = pepsort.get(seq,[])+[hit]
        for seq in sorted(pepsort, key=lambda seq: max([hit.bestValue for hit in pepsort[seq]]),reverse=True):
            for hit in sorted(pepsort[seq],key=lambda h:h.bestValue,reverse=True):
                key = hit.feature.id+"-"+hit.peptide.toString()+"+"+hit.glycan.toString()
                sortedLookupKeys.append(key)
    print "Nr of proteins: ", len(proteinGroupToPeptides)
    
    #print "generate index"
    #reportIndex = ReportIndex()
    #reportIndex.run("index.pdf")
    
    print "merge pdfs"
    input_paths = []
    for key in sortedLookupKeys:
        pathHCD = os.path.join(folderHCD,key+".pdf")
        if os.path.exists(pathHCD):
            input_paths.append(pathHCD)
        
        pathETD = os.path.join(folderETD,key+".pdf")
        if os.path.exists(pathETD):
            input_paths.append(pathETD)
    
    # chunk files
    chunksize = 100
    chunked = []
    for i in range(0,len(input_paths)/chunksize+1):
        chunk = input_paths[i*chunksize:(i+1)*chunksize]
        chunkfile = os.path.join(folderSubpages,str(i+1)+".pdf")
        f = file(chunkfile,"wb")
        pdf_cat(chunk, f)
        f.close()
        chunked.append(chunkfile)
    
    print "writing report pdf"
    f = file(options.out,"wb")
    pdf_cat(chunked, f)
    f.close()
    
    print "adding index"
    

    print "done"
    return

if __name__ == "__main__":
    options = handle_args()
    main(options)
