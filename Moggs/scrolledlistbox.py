## based on scrolledtext from stad lib.
##

from tkinter import *
from tkinter.ttk import *
from tkinter.constants import RIGHT, LEFT, Y, BOTH

class ScrolledListbox(Listbox):
    def __init__(self, master=None, **kw):
        self.frame = Frame(master)
        self.vbar = Scrollbar(self.frame)
        self.vbar.pack(side=RIGHT, fill=Y)

        kw.update({'yscrollcommand': self.vbar.set})
        Listbox.__init__(self, self.frame, **kw)
        self.pack(side=LEFT, fill=BOTH, expand=True)
        self.vbar['command'] = self.yview

        # Copy geometry methods of self.frame without overriding Listbox
        # methods -- hack!
        list_meths = vars(Listbox).keys()
        methods = vars(Pack).keys() | vars(Grid).keys() | vars(Place).keys()
        methods = methods.difference(list_meths)

        for m in methods:
            if m[0] != '_' and m != 'config' and m != 'configure':
                setattr(self, m, getattr(self.frame, m))
        

    def setlist(self, l):
        ## clear the old list?
        self.delete("0", "end")
        ## insert everything
        for item in l:
            self.insert("end", item)

    def getcurselection(self):
        ids = self.curselection()
        selected = []
        for idx in ids:
            thing = self.get(idx)
            selected.append(thing)
        return selected


    def __str__(self):
        return str(self.frame)


