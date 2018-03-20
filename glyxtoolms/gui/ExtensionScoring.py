import ttk
import Tkinter

from glyxtoolms.gui import ChromatogramView
from glyxtoolms.gui import SpectrumView2

from glyxtoolms.gui import PrecursorView

class ExtensionScoring(ttk.Labelframe):

    def __init__(self, master, model, text):
        ttk.Labelframe.__init__(self, master=master, text=text)
        self.master = master
        self.model = model
        chromFrame = ttk.Labelframe(self, text="Precursor Chromatogram")
        chromFrame.grid(row=0, column=0, sticky="NWES")
        chromFrame.rowconfigure(0, weight=1)
        chromFrame.columnconfigure(0, weight=1)

        chromView = ChromatogramView.ChromatogramView(chromFrame, model)
        chromView.grid(row=0, column=0, sticky="NWES")

        msFrame = ttk.Labelframe(self, text="Precursorspectrum")
        msFrame.grid(row=0, column=1, sticky="NWES")
        msFrame.rowconfigure(0, weight=1)
        msFrame.columnconfigure(0, weight=1)

        msView = PrecursorView.PrecursorView(msFrame, model)
        msView.grid(row=0, column=0, sticky="NWES")

        msmsFrame = ttk.Labelframe(self, text="MS/MS Spectrum")
        msmsFrame.grid(row=1, column=0, columnspan=2, sticky="NWES")
        msmsFrame.rowconfigure(0, weight=1)
        msmsFrame.columnconfigure(0, weight=1)

        msmsView = SpectrumView2.SpectrumView(msmsFrame, model)
        msmsView.grid(row=0, column=0, sticky="NWES")

        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
