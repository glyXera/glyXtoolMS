import ttk
import Tkinter
import ChromatogramView
import SpectrumView
import PrecursorView

class ExtensionScoring(ttk.Labelframe):

    def __init__(self, master, model, text):
        ttk.Labelframe.__init__(self, master=master, text=text)
        self.master = master
        self.model = model
        chromFrame = ttk.Labelframe(self, text="Precursor Chromatogram")
        chromFrame.grid(row=0, column=0)
        #chromFrame.pack()
        chromView = ChromatogramView.ChromatogramView(chromFrame, model, height=300, width=400)
        chromView.pack()

        msFrame = ttk.Labelframe(self, text="Precursorspectrum")
        msFrame.grid(row=0, column=1)
        #msFrame.pack()
        msView = PrecursorView.PrecursorView(msFrame, model, height=300, width=400)
        msView.pack()

        msmsFrame = ttk.Labelframe(self, text="MS/MS Spectrum")
        #msmsFrame.pack()
        msmsFrame.grid(row=1, column=0, columnspan=2, sticky="S")
        msmsView = SpectrumView.SpectrumView(msmsFrame, model, height=300, width=800)
        msmsView.pack()

        self.rowconfigure(0, weight=0)
        self.rowconfigure(1, weight=1)
        self.columnconfigure(1, weight=1)
