from tkinter import *
from tkinter.ttk import *


class RadioSelect(Frame):
    def __init__(self, parent):
        Frame.__init__(self, parent)
        self.variable = StringVar()
        
        
    def set(self, value):
        self.variable.set(value)
        
    def get(self):
        return self.variable.get()
        
        
    def add(self, text, value=""):
        rb = Radiobutton(self, text=text, value=value, variable=self.variable)
        rb.pack(side="left")