 
from Tkinter import *
import ttk

lastx, lasty = 0, 0

def xy(event):
    global lastx, lasty
    lastx, lasty = event.x, event.y

def addRuler(event):
    lastx, lasty = event.x, event.y
    canvas.delete("ruler")
    canvas.create_line((lastx, lasty, event.x, event.y),fill="red",tags=("ruler"))



def changeRuler(event):
    x1,y1,x2,y2 = canvas.coords("ruler")
    x2,y2 = event.x, event.y
    canvas.coords("ruler",(x1,y1,x2,y2))


root = Tk()
root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)

canvas = Canvas(root)
canvas.grid(column=0, row=0, sticky=(N, W, E, S))
canvas.bind("<Button-1>", addRuler)
canvas.bind("<B1-Motion>", changeRuler)

root.mainloop()
