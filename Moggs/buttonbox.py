from tkinter import *
from tkinter.ttk import *


class Buttonbox(Frame):
    def __init__(self, parent):
        Frame.__init__(self, parent)
        self.buttons = []
        self.max_length = 0
        
        
        
        
    def add(self, text, command = None):
        if len(text) > self.max_length:
            self.max_length = len(text)
            
        b = Button(self, text = text, command=command)
        b.pack(side = "left", expand = "yes")
        self.buttons.append(b)
        
        
    def alignbuttons(self):
        for b in self.buttons:
            b.config(width = self.max_length)
