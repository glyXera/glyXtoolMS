import Tkinter

class TagEditorWindow(Tkinter.Toplevel):

    def __init__(self, master, model, tagparents):
        Tkinter.Toplevel.__init__(self, master=master)
        self.master = master
        self.title("Edit Tags")
        self.config(bg="#d9d9d9")
        self.model = model
        self.tagparents = tagparents
