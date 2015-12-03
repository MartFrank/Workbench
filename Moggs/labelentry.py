from tkinter import *
from tkinter.ttk import *


class LabelEntry(Frame):
    def __init__(self, parent, text="", value=""):
        Frame.__init__(self, parent)
        
        self.label = Label(self, text = text)
        self.label.pack(side = "left")
        
        self.value = StringVar()
        
        self.entry = Entry(self, textvariable = self.value)
        self.entry.pack(side = "left", expand = "yes", fill = "x")
        
        
        self.set(value)
        
    def set(self, value):
        self.value.set(value)
        
    def get(self):
        return self.value.get()
        
