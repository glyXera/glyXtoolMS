import Tkinter


class Checkbutton(Tkinter.Checkbutton):

    def __init__(self, master, text="", variable=None, command=None):
        Tkinter.Checkbutton.__init__(self, master, text=text, variable=variable, command=command)
        #self.config(bg="#d9d9d9")
        #self.config(activebackground="#d9d9d9")
        #self.config(highlightcolor="#d9d9d9")
        #self.config(highlightbackground="#d9d9d9")

class Radiobutton(Tkinter.Radiobutton):

    def __init__(self, master, text="", variable=None, value=None):
        Tkinter.Radiobutton.__init__(self, master, text=text, variable=variable, value=value)
        #self.config(bg="#d9d9d9")
        #self.config(activebackground="#d9d9d9")
        #self.config(highlightcolor="#d9d9d9")
        #self.config(highlightbackground="#d9d9d9")

class Label(Tkinter.Label):
    def __init__(self, *arg, **args):
        Tkinter.Label.__init__(self, *arg, **args)
        #self.config(bg="#d9d9d9")

