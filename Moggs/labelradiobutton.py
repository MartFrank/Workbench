from tkinter import *
from tkinter.ttk import *


class LabelRadiobutton(Frame):
    def __init__(self, parent, text="", values=(), value=""):
        Frame.__init__(self, parent)
        
        self.label = Label(self, text = text)
        self.label.pack(side = "left", fill="x")
        f = Frame(self)
        f.pack(side="left", expand = "yes", fill = "x")
        self.value = StringVar()
        
        for v in values:
            rb = Radiobutton(f, text=v, variable=self.value, value=v)
            rb.pack(side = "left")
        self.set(value)
        
    def set(self, value):
        self.value.set(value)
        
    def get(self):
        return self.value.get()
        