

from tkinter import *
from tkinter.ttk import *
from Moggs import *


class Bar:
    def __init__(self, canvas, origin, size, color):
        self.canvas = canvas
        self.x = origin[0]
        self.y = origin[1]
        self.width = size[0]
        self.height = size[1]
        self.color = color
        self.bar = self.canvas.create_rectangle(self.x, self.y, self.x+self.width, self.y+self.height, fill = self.color)        
        
class BarChart:
    def __init__(self, canvas, origin, data, title=""):
        self.canvas = canvas
        self.x = origin[0]
        self.y = origin[1]
        
        gap = 5
        
        
        ## get extents
        self.labels = []
        rows = len(data)
        minv = 0
        maxv = 100
        for row in data:
            if row[1] < minv:
                minv = row[1]
            if row[1] > maxv:
                maxv = row[1]
            
            hl = HorizontalLabel(row[0])
            self.labels.append((hl, row[1]))
            
            
        ## draw labels first ?
        y = self.y
        for lab, d in self.labels:
            i = self.canvas.create_image(self.x, y, image=lab, anchor = "ne")
            x = self.canvas.bbox(i)[2]
            bar = Bar(self.canvas, (x + gap, y), (d, lab.height()), "red")
            y =y + lab.height() + gap
        
if __name__=="__main__":

    root= Tk()
    canvas = Canvas(root)
    canvas.pack()
            
    #~ b1 = Bar(canvas, (20, 20), (100, 10), "red")
    #~ b2 = Bar(canvas, (20, 40), (90, 10), "green")
    #~ b3 = Bar(canvas, (20, 60), (60, 10), "yellow")
    
    d = (
        ("Martin", 39),
        ("Julia", 32),
        ("Cameron", 14),
        ("Jack", 12),
        )
    
    bc = BarChart(canvas, (150, 150), d)


    root.mainloop()
