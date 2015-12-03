


from tkinter import *
from tkinter.ttk import *
from Moggs import *
import win32print

import os
import sys

    

class Printer(Toplevel):    
    def __init__(self, parent, filelist=[], printer=None):
        Toplevel.__init__(self, parent)
        
        self.filelist=filelist
        self.parent=parent
        self.printer_list=[]
               
        ## biuld the print list 
        ## network printers first I think...?
        try:
            for p in win32print.EnumPrinters(win32print.PRINTER_ENUM_CONNECTIONS):
                self.printer_list.append(repr(p[2]).replace("'", ""))
        except:
            pass
            
        ## local printers?
        for p in win32print.EnumPrinters(win32print.PRINTER_ENUM_LOCAL):
            self.printer_list.append(str(p[2]))

        ## get and set the default printer
        self.default_printer=win32print.GetDefaultPrinter()
        
        
        if printer:
            self.default_printer=printer
        
        self.last_printer = self.default_printer
        
        lf = LabelFrame(self, text="Print")
        lf.pack(fill="both", expand="yes")
            
        
        self.printer = LabelCombobox(lf, text = "Printer")
        self.printer.set(self.default_printer)
        self.printer.setlist(self.printer_list)
        self.printer.pack(fill="x")
        
        bb = Buttonbox(self)
        bb.add("Ok", command=self.print_file)
        bb.add("Close", command=self.cancel)
        bb.pack(fill="both")
            
        
    def cancel(self):
        for file in self.filelist:
            os.remove(file)
        self.withdraw()
        

    def print_file(self):
        printer = win32print.OpenPrinter(self.printer.get())
        bytes=None
        for file in self.filelist:
            jid = win32print.StartDocPrinter(printer, 1, ('FamilyTree', None, 'RAW'))
            bytes = win32print.WritePrinter(printer, open(file, 'rb').read())
            win32print.EndDocPrinter(printer)
        win32print.ClosePrinter(printer)
        self.withdraw()


if __name__=="__main__":
    Printer(None, "", "").mainloop()


