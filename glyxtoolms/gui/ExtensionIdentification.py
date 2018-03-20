import ttk
import Tkinter

from glyxtoolms.gui import IdentificationStatsFrame
from glyxtoolms.gui import PeptideCoverageFrame
from glyxtoolms.gui import ConsensusSpectrumFrame

class ExtensionIdentification(ttk.Labelframe):

    def __init__(self, master, model, text):
        ttk.Labelframe.__init__(self, master=master, text=text)
        self.master = master
        self.model = model

        panedWindow = Tkinter.PanedWindow(self,orient="vertical")
        panedWindow.pack(fill="both", expand=1)
        panedWindow.config(sashwidth=10)
        panedWindow.config(opaqueresize=False)
        panedWindow.config(sashrelief="raised")
        panedWindow.columnconfigure(0,weight=1)
        panedWindow.rowconfigure(0,weight=1)
        panedWindow.rowconfigure(1,weight=0)
        panedWindow.rowconfigure(2,weight=1)

        errorFrame = ttk.Labelframe(panedWindow, text="Identification errors")
        errorView = IdentificationStatsFrame.IdentificationStatsFrame(errorFrame,
                                                                      model)
        errorView.pack(expand=True, fill="both")

        peptideFrame = ttk.Labelframe(panedWindow, text="Peptide")
        peptideView = PeptideCoverageFrame.PeptideCoverageFrame(peptideFrame,
                                                                model)
        peptideView.pack(expand=True, fill="both")

        consensusFrame = ttk.Labelframe(panedWindow, text="Consensus-Spectrum")
        consensusView = ConsensusSpectrumFrame.ConsensusSpectrumFrame(consensusFrame,
                                                                      model)
        consensusView.pack(expand=True, fill="both")

        # add panels to panedWindow
        panedWindow.add(errorFrame)
        panedWindow.add(peptideFrame)
        panedWindow.add(consensusFrame)

        panedWindow.paneconfigure(errorFrame, stretch="last")
        panedWindow.paneconfigure(peptideFrame, stretch="middle")
        panedWindow.paneconfigure(consensusFrame, stretch="first")
