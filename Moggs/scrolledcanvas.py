## based on standard libraru 'turtle' ScrolledCanvas
## with additional scrollbar stuff from Pmw




from tkinter import *
from tkinter.ttk import *
from turtle import *

import types


## helper functions for Scrolled Canvas, to forward Canvas-methods
## to ScrolledCanvas class

def __methodDict(cls, _dict):
    """helper function for Scrolled Canvas"""
    baseList = list(cls.__bases__)
    baseList.reverse()
    for _super in baseList:
        __methodDict(_super, _dict)
    for key, value in cls.__dict__.items():
        if type(value) == types.FunctionType:
            _dict[key] = value

def __methods(cls):
    """helper function for Scrolled Canvas"""
    _dict = {}
    __methodDict(cls, _dict)
    return _dict.keys()

__stringBody = (
    'def %(method)s(self, *args, **kw): return ' +
    'self.%(attribute)s.%(method)s(*args, **kw)')

def __forwardmethods(fromClass, toClass, toPart, exclude = ()):
    ### MANY CHANGES ###
    _dict_1 = {}
    __methodDict(toClass, _dict_1)
    _dict = {}
    mfc = __methods(fromClass)
    for ex in _dict_1.keys():
        if ex[:1] == '_' or ex[-1:] == '_' or ex in exclude or ex in mfc:
            pass
        else:
            _dict[ex] = _dict_1[ex]

    for method, func in _dict.items():
        d = {'method': method, 'func': func}
        if isinstance(toPart, str):
            execString = \
                __stringBody % {'method' : method, 'attribute' : toPart}
        exec(execString, d)
        setattr(fromClass, method, d[method])   ### NEWU!




class ScrolledCanvas(Frame):
    def __init__(self, master, width=500, height=350,
                                          canvwidth=600, canvheight=500):
        Frame.__init__(self, master, width=width, height=height)
        self._rootwindow = self.winfo_toplevel()
        self.width, self.height = width, height
        self.canvwidth, self.canvheight = canvwidth, canvheight
        self.bg = "white"
        self._canvas = Canvas(master, width=width, height=height,
                                 bg=self.bg, relief=SUNKEN, borderwidth=2)
        self.hscroll = Scrollbar(master, command=self._canvas.xview,
                                    orient=HORIZONTAL)
        self.vscroll = Scrollbar(master, command=self._canvas.yview)
        self._canvas.configure(xscrollcommand=self.hscroll.set,
                               yscrollcommand=self.vscroll.set)
        self.rowconfigure(0, weight=1, minsize=0)
        self.columnconfigure(0, weight=1, minsize=0)
        self._canvas.grid(padx=1, in_ = self, pady=1, row=0,
                column=0, rowspan=1, columnspan=1, sticky='news')
        self.vscroll.grid(padx=1, in_ = self, pady=1, row=0,
                column=1, rowspan=1, columnspan=1, sticky='news')
        self.hscroll.grid(padx=1, in_ = self, pady=1, row=1,
                column=0, rowspan=1, columnspan=1, sticky='news')
        self._rootwindow.bind('<Configure>', self.onResize)
        self.after_idle(self.reset)

    def reset(self):
        self.onResize(1)




    def onResize(self, event):
        """self-explanatory"""
        self.update()
        try:
            region = self._canvas.bbox('all')
        except:
            return
        if region is not None:
            region = (region[0] , region[1], region[2], region[3])
            self._canvas.configure(scrollregion = region)
            
    def bbox(self, *args):
        """ 'forward' method, which canvas itself has inherited...
        """
        return self._canvas.bbox(*args)

    def cget(self, *args, **kwargs):
        """ 'forward' method, which canvas itself has inherited...
        """
        return self._canvas.cget(*args, **kwargs)

    def config(self, *args, **kwargs):
        """ 'forward' method, which canvas itself has inherited...
        """
        self._canvas.config(*args, **kwargs)

    def bind(self, *args, **kwargs):
        """ 'forward' method, which canvas itself has inherited...
        """
        self._canvas.bind(*args, **kwargs)

    def unbind(self, *args, **kwargs):
        """ 'forward' method, which canvas itself has inherited...
        """
        self._canvas.unbind(*args, **kwargs)

    def focus_force(self):
        """ 'forward' method, which canvas itself has inherited...
        """
        self._canvas.focus_force()

__forwardmethods(ScrolledCanvas, Canvas, '_canvas')
