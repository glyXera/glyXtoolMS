import ttk
import Tkinter
import IdentificationStatsFrame
import PeptideCoverageFrame
import ConsensusSpectrumFrame

class ExtensionIdentification(ttk.Labelframe):

    def __init__(self, master, model, text):
        ttk.Labelframe.__init__(self, master=master, text=text)
        self.master = master
        self.model = model

        errorFrame = ttk.Labelframe(self, text="Identification errors")
        errorFrame.grid(row=0, column=0, columnspan=2)

        errorView = IdentificationStatsFrame.IdentificationStatsFrame(errorFrame, model, height=200, width=800)
        errorView.grid(row=0, column=0)
        
        
        
        peptideFrame = ttk.Labelframe(self, text="Peptide")
        peptideFrame.grid(row=1, column=0, columnspan=2)

        peptideView = PeptideCoverageFrame.PeptideCoverageFrame(peptideFrame, model, height=200, width=800)
        peptideView.grid(row=0, column=0)


        consensusFrame = ttk.Labelframe(self, text="Consensus-Spectrum")
        consensusFrame.grid(row=2, column=0, columnspan=2)

        consensusView = ConsensusSpectrumFrame.ConsensusSpectrumFrame(consensusFrame, model, height=300, width=800)
        consensusView.grid(row=0, column=0)
