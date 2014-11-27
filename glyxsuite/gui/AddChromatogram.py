from Tkinter import *
from tkColorChooser import askcolor 

class AddChromatogram(Toplevel):
    
    def __init__(self,master,model):
        Toplevel.__init__(self,master=master)
        self.master = master
        self.title("New Chromatogram")
    
        self.model = model
        
        self.massrangeLow = StringVar()
        self.massrangeHigh = StringVar()
        massrangeLabel = Label(self,text="Massrange: ")
        massrangeLabel.grid(row=0,column=0,sticky=(N, W, E, S))
        
        # valid percent substitutions (from the Tk entry man page)
        # %d = Type of action (1=insert, 0=delete, -1 for others)
        # %i = index of char string to be inserted/deleted, or -1
        # %P = value of the entry if the edit is allowed
        # %s = value of entry prior to editing
        # %S = the text string being inserted or deleted, if any
        # %v = the type of validation that is currently set
        # %V = the type of validation that triggered the callback
        #      (key, focusin, focusout, forced)
        # %W = the tk name of the widget
        vcmd = (self.model.root.register(self.OnValidate), 
                '%d', '%i', '%P', '%s', '%S', '%v', '%V', '%W')
        
        
        #massrangeEntry = Entry(self, textvariable=self.massrange,validatecommand=vcmd)
        massrangeEntryLow = Entry(self,validate="key",validatecommand=vcmd,textvariable=self.massrangeLow)
        massrangeEntryHigh = Entry(self,validate="key",validatecommand=vcmd,textvariable=self.massrangeHigh)
        
        massrangeEntryLow.grid(row=0,column=1,sticky=(N, W, E, S))
        massrangeEntryHigh.grid(row=0,column=3,sticky=(N, W, E, S))
        
        Label(self,text="-").grid(row=0,column=2,sticky=(N, W, E, S))
        
        self.name = StringVar()
        nameLabel = Label(self,text="Name: ")
        nameEntry = Entry(self, textvariable=self.name)
        nameLabel.grid(row=1,column=0,sticky=(N, W, E, S))
        nameEntry.grid(row=1,column=1,columnspan=3,sticky=(N, W, E, S))        
        
        self.pickedColor = "black"
        self.colorChooser = Button(self,bg=self.pickedColor,activebackground=self.pickedColor)
        self.colorChooser.config(command=self.getColor)
        colorLabel = Label(self,text="Select Color")
        colorLabel.grid(row=2,column=0,sticky=(N, W, E, S))
        self.colorChooser.grid(row=2,column=1,columnspan=3,sticky=(N, W, E, S))
        
        
        self.mslevel = IntVar()
        levelFrame = LabelFrame(self)
        msLevel1 = Radiobutton(levelFrame, text="MS 1", variable=self.mslevel, value=1)
        msLevel1.pack()
        msLevel2 = Radiobutton(levelFrame, text="MS 2", variable=self.mslevel, value=2)
        msLevel2.pack()
        msLevel3 = Radiobutton(levelFrame, text="MS 3", variable=self.mslevel, value=3)
        msLevel3.pack()
        levelLabel = Label(self,text="MS Level: ")
        levelLabel.grid(row=3,column=0,sticky=(N, W, E, S))
        levelFrame.grid(row=3,column=1,columnspan=3,sticky=(N, W, E, S))
        msLevel1.invoke()
        
        buttonAdd = Button(self,text="Add Chromatogram",command=self.addChromatogram)
        buttonAdd.grid(row=4,column=1,sticky=(N, W, E, S))
        
        buttonCancel = Button(self,text="Close",command=self.destroy)
        buttonCancel.grid(row=4,column=3,sticky=(N, W, E, S))
        
        
    def OnValidate(self, d, i, P, s, S, v, V, W):
        # only allow if the string is lowercase
        if S == "." and P.count(".") == 1:
            return True
        if S.isdigit():
            return True
        return False
        
    def getColor(self):

        self.pickedColor = askcolor(self.pickedColor)[1]
        self.colorChooser.config(bg=self.pickedColor)
        self.colorChooser.config(activebackground=self.pickedColor)
        
        
    def addChromatogram(self):
        options = {}
        options["name"] = self.name.get()
        options["range"] = (self.massrangeLow.get(),self.massrangeHigh.get())
        options["color"] = self.pickedColor
        options["mslevel"] = self.mslevel.get()
        self.master.addChromatogram(options)
