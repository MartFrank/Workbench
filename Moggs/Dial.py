

from tkinter import *
from tkinter.ttk import *
from Moggs import *





class Dial:
    def __init__(self, canvas, origin, size, value, thresholds=(75, 90), reverse=False):
        """Dial
        
        Draw a 0-100% horizontal dial on given canvas
            canvas = tkinter canvas like object
            origin = (x,y)
            size = (width, height)
            value = in the range of 0 - 100
            
        dial background colour changes from green to yellow at 75% then to red at 90%
        """
        self.canvas = canvas
        self.x = origin[0]
        self.y = origin[1]
        self.width = size[0]
        self.height = size[1]
        self.value = value
        self.reverse = reverse
        self.thresholds = thresholds
        
        self.dial = canvas.create_arc(self.x, self.y-self.height, self.x+self.width, self.y+self.height, start=0, extent=180)
        
        canvas.create_text(self.x - 3, self.y, text="0%", anchor="e")
        canvas.create_text(self.x+self.width + 3, self.y, text="100%", anchor="w")
        canvas.create_text(self.x+(self.width/2.0), self.y-self.height, text="50%", anchor="s")
        
        
        ## value text in center of dial
        self.text = canvas.create_text(self.x+(self.width/2.0), self.y-(self.height/2), text="%s%%" %self.value, anchor="center")
       
        
        self.arrow = canvas.create_arc(self.x+10, self.y-self.height+10, self.x+self.width-10, self.y+self.height-10, start=180 - (self.value*1.8), extent=0)
        
                
    def update(self, value):
        self.value = value
        self.canvas.itemconfigure(self.text, text="%3.2f%%" %self.value)
        self.canvas.itemconfigure(self.arrow, start=180-(self.value*1.8))
        
        if self.reverse:
            fill = "red"
            if self.value > self.thresholds[0]:
                fill="yellow"
            if self.value > self.thresholds[1]:
                fill = "green"
        else:
            fill = "green"
            if self.value > self.thresholds[0]:
                fill="yellow"
            if self.value > self.thresholds[1]:
                fill = "red"
        
        self.canvas.itemconfigure(self.dial, fill=fill)
        
        



if __name__=="__main__":

    root= Tk()
    canvas = Canvas(root)
    canvas.pack()
            
    d = Dial(canvas, (30, 100), (100, 50), 50)


    START = 0
    d.update(START)
    
    def move(event):
        global START
        START = START + 1
        d.update(START)
        
    root.bind("<Return>", move)




    root.mainloop()
