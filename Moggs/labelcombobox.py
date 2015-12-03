from tkinter import *
from tkinter.ttk import *


class LabelCombobox(Frame):
    def __init__(self, parent, text="", values=(), value="", command=None):
        Frame.__init__(self, parent)
        
        self.command = command
        
        self.label = Label(self, text = text)
        self.label.pack(side = "left")
        
        self.value = StringVar()
        
        self.combobox = Combobox(self, textvariable = self.value)
        self.combobox.pack(side = "left", expand = "yes", fill = "x")
        self.combobox.bind("<<ComboboxSelected>>", self.selectcommand)
        
        self.set(value)
        self.setlist(values)
        
        
    def selectcommand(self, event):
        if callable(self.command):
            self.command()
        
        
    def set(self, value):
        self.value.set(value)
        
    def get(self):
        return self.value.get()
        
    def setlist(self, values):
        self.values = values
        self.combobox.config(values=self.values)
    
        
