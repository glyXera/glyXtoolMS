import ttk

from glyxtoolms.gui import IdentificationStatsFrame
from glyxtoolms.gui import PeptideCoverageFrame
from glyxtoolms.gui import ConsensusSpectrumFrame

class ExtensionIdentification(ttk.Labelframe):

    def __init__(self, master, model, text):
        ttk.Labelframe.__init__(self, master=master, text=text)
        self.master = master
        self.model = model

        self.columnconfigure(0, minsize=200, weight=1)
        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        self.rowconfigure(2, weight=1)
        
        errorFrame = ttk.Labelframe(self, text="Identification errors")
        errorFrame.grid(row=0, column=0, columnspan=2, sticky="NWES")

        errorView = IdentificationStatsFrame.IdentificationStatsFrame(errorFrame,
                                                                      model,
                                                                      height=200,
                                                                      width=800)
        errorView.pack(expand=True, fill="both")


        peptideFrame = ttk.Labelframe(self, text="Peptide")
        peptideFrame.grid(row=1, column=0, columnspan=2, sticky="NWES")
        

        peptideView = PeptideCoverageFrame.PeptideCoverageFrame(peptideFrame,
                                                                model,
                                                                height=200,
                                                                width=200)
        peptideView.pack(expand=True, fill="both")


        consensusFrame = ttk.Labelframe(self, text="Consensus-Spectrum")
        consensusFrame.grid(row=2, column=0, columnspan=2, sticky="NWES")

        consensusView = ConsensusSpectrumFrame.ConsensusSpectrumFrame(consensusFrame,
                                                                      model,
                                                                      height=300,
                                                                      width=800)
        consensusView.pack(expand=True, fill="both")
