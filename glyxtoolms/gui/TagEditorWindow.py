import Tkinter
import ttk
import glyxtoolms

class TagEditorWindow(Tkinter.Toplevel):

    def __init__(self, master, model, tagparents,updateTagsView):
        Tkinter.Toplevel.__init__(self, master=master)
        self.master = master
        self.title("Edit Tags")
        self.config(bg="#d9d9d9")
        self.model = model
        self.updateTagsView = updateTagsView

        self.tagContainer = {}
        for tagparent in tagparents:
            self.tagContainer[tagparent] = set(tagparent.tags)
        self.allTags = set(self.model.currentAnalysis.analysis.all_tags)
        self.tagVars = {}
        self.editedTags = set()
        w = 600
        h = 300
        #self.minsize(w,h)

        self.maxCol = 5

        # collect tags
        self.tagCopy = {}


        frameAddTag = ttk.Labelframe(self, text="Add Tag")
        self.frameTags = ttk.Labelframe(self, text="Tags")
        frameButtons = Tkinter.Frame(self)
        frameAddTag.grid(row=0, column=0, sticky="NSEW")
        self.frameTags.grid(row=1, column=0, sticky="NSEW")
        frameButtons.grid(row=2, column=0, sticky="NSEW")

        self.entryContent = Tkinter.StringVar()
        entry = Tkinter.Entry(frameAddTag,textvariable=self.entryContent)
        entry.config(bg="white")
        buttonEntry = Tkinter.Button(frameAddTag, text="Add", command=self.addTag)
        entry.grid(row=0, column=0, sticky="NSEW")
        buttonEntry.grid(row=0, column=1)

        buttonCancel = Tkinter.Button(frameButtons, text="Cancel",command=self.pressedCancel)
        buttonOK = Tkinter.Button(frameButtons, text="OK",command=self.pressedOK)
        buttonCancel.grid(row=0, column=0)
        buttonOK.grid(row=0, column=1)
        self.paintTags()

    def addTag(self):
        text = self.entryContent.get()
        if text == "":
            return
        for tagContent in self.tagContainer.values():
            tagContent.add(text)
        self.allTags.add(text)
        self.entryContent.set("")
        self.editedTags.add(text)
        self.paintTags()

    def paintTags(self):
        for button in self.frameTags.children.values():
            button.destroy()
        self.tagVars = {}
        col = 0
        frame = Tkinter.Frame(self.frameTags)
        frame.pack(side="top")
        maxLength = 40
        for tag in sorted(self.allTags):
            N = 0
            for tagContent in self.tagContainer.values():
                if tag in tagContent:
                    N += 1
            var = Tkinter.IntVar()
            button = Tkinter.Checkbutton(frame,text=tag,variable=var)
            if N == 0:
                var.set(0)
                button.config(selectcolor="white")
            elif N == len(self.tagContainer.values()):
                var.set(1)
                button.config(selectcolor="white")
            else:
                var.set(1)
                button.config(selectcolor="red")
            self.tagVars[tag] = (var,button)
            var.trace("w", lambda a,b,c,d=tag: self.tagToggled(d))
            button.pack(side="left")
            col += len(tag)+4
            if col >= maxLength:
                col = 0
                frame = Tkinter.Frame(self.frameTags)
                frame.pack(side="top")

    def tagToggled(self, tag):
        var,button = self.tagVars[tag]
        button.config(selectcolor="white")
        self.editedTags.add(tag)
        if var.get() == 0:
            for tagContent in self.tagContainer.values():
                if tag in tagContent:
                     tagContent.remove(tag)
        else:
            for tagContent in self.tagContainer.values():
                tagContent.add(tag)

    def pressedOK(self):
        for tag in self.editedTags:
            var,button = self.tagVars[tag]
            value = var.get()
            for tagparent in self.tagContainer:
                if value == 0 and tag in tagparent.tags:
                    tagparent.tags.remove(tag)
                elif value == 1:
                    tagparent.tags.add(tag)
        self.destroy()
        # collect tags
        self.model.currentAnalysis.analysis.collect_tags()
        self.model.collect_tags()
        # update view
        self.updateTagsView()

    def pressedCancel(self):
        self.destroy()

