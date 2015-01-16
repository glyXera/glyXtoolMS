import ttk
import Tkinter

class ExtensionScoring(ttk.Labelframe):
    
    def __init__(self,master,model,text):
        ttk.Labelframe.__init__(self,master=master,text=text)
        self.master = master
        self.model = model 
        
        #self.b = Tkinter.Button(self,text=text)
        #self.b.grid()
