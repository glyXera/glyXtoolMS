 
def openDialog():
    import Tkinter, tkFileDialog
    root = Tkinter.Tk()
    root.withdraw()

    file_path = tkFileDialog.askopenfilename()
    root.destroy()
    return file_path
