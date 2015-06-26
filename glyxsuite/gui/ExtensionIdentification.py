import ttk
import Tkinter
import IdentificationStatsFrame

class ExtensionIdentification(ttk.Labelframe):

    def __init__(self, master, model, text):
        ttk.Labelframe.__init__(self, master=master, text=text)
        self.master = master
        self.model = model

        frame = ttk.Labelframe(self, text="Identification errors")
        frame.grid(row=0, column=0, columnspan=2)

        view = IdentificationStatsFrame.IdentificationStatsFrame(frame, model, height=200, width=800)
        view.grid(row=0, column=0)



