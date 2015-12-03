from tkinter import *
from tkinter.ttk import *

import calendar
import time
import collections


class Datechooser(Frame):
    def __init__(self, parent, data=[], default="", command=None, label_text=""):
        Frame.__init__(self, parent)
        self.command = command
        
        self.variable=StringVar()
        
        self.label = Label(self, text=label_text)
        self.label.pack(side="left")
        self.entry=Entry(self, textvariable=self.variable)
        self.entry.pack(side="left", fill="x", expand="yes")
        self.entry.bind("<ButtonRelease-1>", self.hideList)
        self.entry.bind("<Return>", self.invoke)
        
        
        self.button=Button(self, command=self.buttonCommand)
        self.button.pack(side="left")
        self.createButtonImage()
        
        self.popup=Toplevel(self)
        self.popup.interior=Frame(self.popup)
        self.popup.interior.pack(fill="both", expand="yes")
        self.popup.withdraw()
        self.popup.overrideredirect(1)
        self.popup.hideList = self.hideList
        self.popup.setentry = self.setentry
        
        self.listbox=DateSelector(self.popup)
        self.listbox.pack(fill="both", expand="yes")
        self.listbox.visible = 0
        parent.winfo_toplevel().bind("<Configure>", self.reconfigure)
        
    def createButtonImage(self):
        width=self.entry.winfo_reqheight()-4
        height=width
        self.image=PhotoImage(width=width, height=height)
        for row in range(3, height-3, 1):
            for col in range(int(row/1.75), width-int(row/1.75), 1):
                self.image.put("black", (col, row))
        self.button["image"]=self.image
        
    def get(self):
        return self.variable.get()
            
    def getentry(self):
        return self.variable.get()
        
    def setentry(self, value):
        self.variable.set(value)
                
    def buttonCommand(self):
        if self.listbox.visible:
            self.hideList(None)
        else:
            self.showList()
                
    def invoke(self, *event):
        if isinstance(self.command, collections.Callable):
            self.command(self.getentry())
        
        
        
    def reconfigure(self, event):
        if self.listbox.visible:
            self.hideList(event)
            self.showList()
        
    def hideList(self, *event):
        self.listbox.visible = 0
        self.popup.withdraw()
        
    def showList(self):
        self.listbox.visible = 1
        self.update()
        x = self.entry.winfo_rootx()
        y = self.entry.winfo_rooty() + self.entry.winfo_height()
        w = self.entry.winfo_width() + self.button.winfo_width()
        h =  self.listbox.winfo_height()
        sh = self.winfo_screenheight()
        if y + h > sh and y > sh / 2:
            y = self.entry.winfo_rooty() - h
        self.popup.interior.configure(width=w)
        self.popup.update()
        self.popup.geometry('+%d+%d' % (x, y))
        self.popup.deiconify()
        self.popup.tkraise()
        self.listbox.focus_set()
        
    
class DateSelector(Frame):
    def __init__(self, parent):
        Frame.__init__(self, parent)
        self.parent = parent
        today = time.localtime(time.time())
        self.year = today[0]
        self.month = today[1]
        self.thisYear = today[0]
        self.thisMonth = today[1]
        self.day = today[2]
        
        
        self.monthYear = MonthYearSelector(self, year=self.year, 
            month=self.month, command=self.gridMonth)
        self.monthYear.grid(row=0, columnspan=7)
        self.gridMonth("%s - %d" %(self.year, self.month))
        
        
        
    def gridMonth(self, stuff):
        
        year, month = self.monthYear.get()
        self.year = year
        self.month = month
        
        row = 1
        col = 0
        cal = calendar.monthcalendar(year, month)
        
        for dname in "MTWTFSS":
            l=Label(self, text=dname, width=2)
            l.grid(row=row, column=col)
            col=col+1
        
        row = 2
        col = 0
        
        
        for w in cal:
            for d in w:
                if d:
                    b=Button(self, text=d, width=2,
                        command=lambda self=self, day=d: self.returnDay(day))
                    b.grid(row=row, column=col)
                    if col>4:
                        b.config()
                    if d==self.day and self.year==self.thisYear and self.month==self.thisMonth:
                        b.config()
                        
                    
                col=col+1
            row=row+1
            col=0
        
        
    def returnDay(self, day):
        self.parent.setentry("%d/%s/%d" %(day, calendar.month_name[self.month], self.year))
        self.parent.hideList()
        
    
    
class MonthYearSelector(Frame):
    def __init__(self, parent, year=1973, month=5, command=None):
        Frame.__init__(self, parent)
        self.parent = parent
        self.year = year
        self.month = month
        
        l = []
        for year in range(1970, 2030, 1):
            for month in calendar.month_name:
                if month:
                    l.append("%d - %s" %(year, month))
                    
        self.counter = StringVar()
        counter = Combobox(self, values=l, textvariable = self.counter)
        counter.bind('<<ComboboxSelected>>', command)
        
        counter.pack(fill="x")
        self.set(self.year, self.month)
        
        
    def set(self, year, month):
        self.counter.set("%d - %s" %(year, calendar.month_name[month]))
        
        
    def get(self):
        year, month = self.counter.get().split(" - ")
        month = list(calendar.month_name).index(month)
        year = int(year)
        
        return year, month
    
    
if __name__=="__main__":
    root=Tk()
    def printit(thing):
        print(thing)
    
    cb=Datechooser(root)
    cb.pack(fill="x")
    root.mainloop()


