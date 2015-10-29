import ttk
import Tkinter

from glyxsuite.gui import TwoDView
from glyxsuite.gui import FeaturePrecursorView
from glyxsuite.gui import FeatureChromatogramView
from glyxsuite.gui import FeatureSpectrumView

class Notebook1(ttk.Frame):

    def __init__(self, master, model):
        ttk.Frame.__init__(self, master=master)
        self.master = master
        self.model = model

        #twoDFrame = ttk.Labelframe(self, text="Precursor Chromatogram")
        #twoDFrame.grid(row=0, column=0, columnspan=2)

        #twoDView = TwoDView.TwoDView(twoDFrame, model, height=450, width=500)
        #twoDView.grid(row=0, column=0)

        chromFrame = ttk.Labelframe(self, text="Precursor Chromatogram")
        chromFrame.grid(row=1, column=0)
        chromView = FeatureChromatogramView.ChromatogramView(chromFrame, model, height=300, width=400)
        chromView.grid(row=0, column=0)

        msFrame = ttk.Labelframe(self, text="Precursorspectrum")
        msFrame.grid(row=1, column=1)
        msView = FeaturePrecursorView.PrecursorView(msFrame, model, height=300, width=400)
        msView.grid(row=0, column=0)


class Notebook2(ttk.Frame):

    def __init__(self, master, model):
        ttk.Frame.__init__(self, master=master)
        self.master = master
        self.model = model

        msmsFrame = ttk.Labelframe(self, text="MS/MS Spectrum")
        msmsFrame.grid(row=0, column=0)
        msmsView = FeatureSpectrumView.SpectrumView(msmsFrame, model, height=300, width=800)
        msmsView.grid(row=0, column=0)

class ExtensionFeature(ttk.Labelframe):

    def __init__(self, master, model, text):
        ttk.Labelframe.__init__(self, master=master, text=text)
        self.master = master
        self.model = model

        twoDFrame = ttk.Labelframe(self, text="Precursor Chromatogram")
        twoDFrame.grid(row=0, column=0, columnspan=2)

        twoDView = TwoDView.TwoDView(twoDFrame, model, height=450, width=500)
        twoDView.grid(row=0, column=0)

        self.notebook = ttk.Notebook(self)
        self.notebook.grid(row=1, column=0)
        self.n1 = Notebook1(self.notebook, self.model)
        self.n2 = Notebook2(self.notebook, self.model)

        self.notebook.add(self.n1, text='Feature')
        self.notebook.add(self.n2, text='Spectruminformation')

        """
        chromFrame = ttk.Labelframe(self, text="Precursor Chromatogram")
        chromFrame.grid(row=1, column=0)
        chromView = FeatureChromatogramView.ChromatogramView(chromFrame, model, height=300, width=400)
        chromView.grid(row=0, column=0)

        msFrame = ttk.Labelframe(self, text="Precursorspectrum")
        msFrame.grid(row=1, column=1)
        msView = FeaturePrecursorView.PrecursorView(msFrame, model, height=300, width=400)
        msView.grid(row=0, column=0)
        """

        #self.notebook = ttk.Notebook(self)
        #self.notebook.grid(row=0, column=0)
        #self.n1 = Notebook1(self.notebook, self.model)
        #self.n2 = Notebook2(self.notebook, self.model)

        #self.notebook.add(self.n1, text='View 1')
        #self.notebook.add(self.n2, text='View 2')



        #msmsFrame = ttk.Labelframe(self, text="MS/MS Spectrum")
        #msmsFrame.grid(row=1, column=0, columnspan=2)
        #msmsView = SpectrumView.SpectrumView(msmsFrame, model, height=300, width=800)
        #msmsView.pack()


