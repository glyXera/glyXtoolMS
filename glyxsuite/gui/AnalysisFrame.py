import ThreadedIO
import ttk 
from Tkinter import * 
import pyopenms
import tkFileDialog
import AddChromatogram
import tkMessageBox
import DataModel
import os

def treeview_sort_column(tv, col, reverse):    
    l = [(tv.set(k, col), k) for k in tv.get_children('')]
    l.sort(reverse=reverse)
    

    # rearrange items in sorted positions
    for index, (val, k) in enumerate(l):
        tv.move(k, '', index)
        
        # adjust tags
        taglist = list(tv.item(k,"tags"))
        if "oddrowFeature" in taglist:
            taglist.remove("oddrowFeature")
        if "evenrowFeature" in taglist:
            taglist.remove("evenrowFeature")
            
        if index%2 == 0:    
            taglist.append("evenrowFeature")
        else:
            taglist.append("oddrowFeature")
        tv.item(k,tags = taglist)        

    # reverse sort next time
    tv.heading(col, command=lambda: treeview_sort_column(tv, col, not reverse))


class AnalysisFrame(ttk.Frame):
    
    def __init__(self,master,model):
        ttk.Frame.__init__(self,master=master)
        self.master = master
        self.model = model
        
        scrollbar = Scrollbar(self)    
        self.tree = ttk.Treeview(self,yscrollcommand=scrollbar.set)
        
        columns = ("RT","Score","Peptide","Glycan")
        self.tree["columns"] =("RT","Score","Peptide","Glycan")
        
        for col in columns:
            self.tree.column(col,width=100)
            self.tree.heading(col, text=col, command=lambda col=col: treeview_sort_column(self.tree, col, False))
        
        self.tree.grid(row=1,column=0,sticky=(N, W, E, S))
        self.model.debug = self.tree
        
        scrollbar.grid(row=1,column=1,sticky=(N, W, E, S))
        scrollbar.config(command=self.tree.yview)
        
        
        # treeview style
        #self.tree.tag_configure('oddrow', background='orange')
        self.tree.tag_configure('oddrowFeature', background='Moccasin')
        self.tree.tag_configure('evenrowFeature', background='PeachPuff')
        
        self.tree.tag_configure('evenSpectrum', background='LightBlue')
        self.tree.tag_configure('oddSpectrum', background='SkyBlue')
        self.tree.bind("<<TreeviewSelect>>", self.clickedTree);
        
        
        
    def clickedTree(self,event):
        item = self.tree.selection()[0]
        print "clicked on ",item, 
        if not item in self.model.treeIds:
            return
        # get tag
        if self.tree.tag_has("feature", item):
            print "feature"
        elif self.tree.tag_has("spectrum", item):
            print "spectrum"
            s = self.model.treeIds[item]
            key = s.getNativeId()
            print key,len(self.model.spectra)
            if not key in self.model.spectra:
                print "no spectra found"
                return
            self.model.funcPaintSpectrum(self.model.spectra[key])
            
        else:
            print "unknown tag"


    
