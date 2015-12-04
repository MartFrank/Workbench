from .labelcombobox import *
from .labelradiobutton import *
from .scrolledlistbox import *
from .scrolledtreeview import *
from .labelentry import *
from .buttonbox import *
from .scrolledcanvas import *
from .scrolledtext import *
from .tree import *
from .datechooser import *
<<<<<<< HEAD
#~ from .printer import *
from .radioselect import *
#~ from .Dial import *
#~ from .ImageLabel import *
#~ from .BarChart import *
=======
#from .printer import *
from .radioselect import *
#from .Dial import *
#from .ImageLabel import *
#from .BarChart import *
>>>>>>> origin/master

def alignlabels(widgets):
    
    length = 0
    
    for w in widgets:
        l = len(w.label["text"])
        if l > length:
            length = l
    for w in widgets:
        w.label.config(width=length)
