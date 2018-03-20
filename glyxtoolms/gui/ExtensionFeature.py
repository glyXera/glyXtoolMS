import ttk
import Tkinter

from glyxtoolms.gui import TwoDView
from glyxtoolms.gui import FeaturePrecursorView
from glyxtoolms.gui import FeatureChromatogramView
from glyxtoolms.gui import FeatureSpectrumView
from glyxtoolms.gui import ConsensusSpectrumFrame2

class Notebook1(ttk.Frame):

    def __init__(self, master, model):
        ttk.Frame.__init__(self, master=master)
        self.master = master
        self.model = model

        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)

        chromFrame = ttk.Labelframe(self, text="Precursor Chromatogram")
        chromFrame.grid(row=0, column=0, sticky="NWES")
        chromView = FeatureChromatogramView.FeatureChromatogramView(chromFrame, model)
        chromView.grid(row=0, column=0, sticky="NWES")
        chromFrame.columnconfigure(0, weight=1)
        chromFrame.rowconfigure(0, weight=1)

        msFrame = ttk.Labelframe(self, text="Precursorspectrum")
        msFrame.grid(row=0, column=1, sticky="NWES")
        msView = FeaturePrecursorView.PrecursorView(msFrame, model)
        msView.grid(row=0, column=0, sticky="NWES")
        msFrame.columnconfigure(0, weight=1)
        msFrame.rowconfigure(0, weight=1)




class Notebook2(ttk.Frame):

    def __init__(self, master, model):
        ttk.Frame.__init__(self, master=master)
        self.master = master
        self.model = model
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        msmsFrame = ttk.Labelframe(self, text="MS/MS Spectrum")
        msmsFrame.grid(row=0, column=0, sticky="NWES")
        msmsFrame.columnconfigure(0, weight=1)
        msmsFrame.rowconfigure(0, weight=1)
        msmsView = FeatureSpectrumView.FeatureSpectrumView(msmsFrame, model)
        msmsView.grid(row=0, column=0, sticky="NWES")

class Notebook3(ttk.Frame):

    def __init__(self, master, model):
        ttk.Frame.__init__(self, master=master)
        self.master = master
        self.model = model
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        consFrame = ttk.Labelframe(self, text="Consensusspectrum")
        consFrame.grid(row=0, column=0, sticky="NWES")
        consFrame.columnconfigure(0, weight=1)
        consFrame.rowconfigure(0, weight=1)
        consView = ConsensusSpectrumFrame2.ConsensusSpectrumFrame(consFrame, model)
        consView.grid(row=0, column=0, sticky="NWES")


class ExtensionFeature(ttk.Labelframe):

    def __init__(self, master, model, text):
        ttk.Labelframe.__init__(self, master=master, text=text)
        self.master = master
        self.model = model

        twoDFrame = ttk.Labelframe(self, text="Feature Map")
        twoDFrame.grid(row=0, column=0, sticky="NWES")
        twoDFrame.columnconfigure(0, weight=1)
        twoDFrame.rowconfigure(0, weight=1)

        twoDView = TwoDView.TwoDView(twoDFrame, model)
        twoDView.grid(row=0, column=0, sticky="NWES")

        self.notebook = ttk.Notebook(self)
        self.notebook.grid(row=1, column=0, sticky="NWES")
        self.n1 = Notebook1(self.notebook, self.model)
        self.n2 = Notebook2(self.notebook, self.model)
        self.n3 = Notebook3(self.notebook, self.model)

        self.notebook.add(self.n1, text='Feature')
        self.notebook.add(self.n2, text='Fragment Spectrum')
        self.notebook.add(self.n3, text='Consensus Spectrum')

        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)


