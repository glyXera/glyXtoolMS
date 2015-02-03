import ttk
import Tkinter
import TwoDView

class ExtensionFeature(ttk.Labelframe):
    
    def __init__(self,master,model,text):
        ttk.Labelframe.__init__(self,master=master,text=text)
        self.master = master
        self.model = model
        twoDFrame = ttk.Labelframe(self,text="Precursor Chromatogram")
        twoDFrame.grid(row=0,column=0)
        twoDView = TwoDView.TwoDView(twoDFrame,model,height=450,width=500)
        twoDView.pack()


