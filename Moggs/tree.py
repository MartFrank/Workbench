
# http://www.magicnet.net/~gcash/tree.py

# highly optimized tkinter tree control
# by Charles E. "Gene" Cash (gcash@magicnet.net)
#
# 98/12/02 CEC started
# 99/??/?? CEC release to comp.lang.python.announce
#
# to do:
# add working "busy" cursor
# make paste more general
# drag'n'drop support
# add good ideas from win95's tree common control
            

## scrolledcanvas & associated stuff by Martin Franklin


from tkinter import *
from tkinter.ttk import *
from .scrolledcanvas import *

import os

# this is initialized later, after Tkinter is started
open_icon=None

#------------------------------------------------------------------------------
# cut'n'paste helper object

class Cut_Object:
    def __init__(self, node=None, id=None, state=None):
        self.node=node
        self.full_id=id
        self.state=state

#------------------------------------------------------------------------------
# tree node helper class
class Node:
    # initialization creates node, draws it, and binds mouseclicks
    def __init__(self, parent, name, id, closed_icon, open_icon, x, y,
                 parentwidget):
        # lots of things to remember
        # immediate parent node
        self.parent=parent
        # name displayed on the label
        self.name=name
        # internal name used to manipulate things
        self.id=id
        # bitmaps to be displayed
        self.open_icon=open_icon
        self.closed_icon=closed_icon
        # tree widget we belong to
        self.widget=parentwidget
        # our list of child nodes
        self.subnodes=[]
        # cheap mutex spinlock
        self.spinlock=0
        # closed to start with
        self.open_flag=0

        # draw horizontal connecting lines
        if self.widget.lineflag:
            self.line=self.widget.create_line(x-self.widget.distx, y, x, y)

        # draw approprate image
        if self.open_flag:
            self.symbol=self.widget.create_image(x, y, image=self.open_icon)
        else:
            self.symbol=self.widget.create_image(x, y, image=self.closed_icon)

        # add label
        self.label=self.widget.create_text(x+self.widget.textoff, y,
                                           text=self.name, justify='left',
                                           anchor='w')

        # single-click to expand/collapse
        cmd=self.widget.tag_bind(self.symbol, '<1>', self.click)

        # call customization hook
        if self.widget.init_hook:
            self.widget.init_hook(self)

    def __repr__(self):
        return 'Node: %s  Parent: %s  (%d children)' % \
               (self.name, self.parent.name, len(self.subnodes))

    # recursively delete subtree & clean up cyclic references
    def _delete(self):
        for i in self.subnodes:
            if i.open_flag and i.subnodes:
                # delete vertical connecting line
                if self.widget.lineflag:
                    self.widget.delete(i.tree)

            # delete node's subtree, if any
            i._delete()

            # the following unbinding hassle is because tkinter
            # keeps a callback reference for each binding
            # so if we want things GC'd...
            for j in (i.symbol, i.label):
                for k in self.widget.tag_bind(j):
                    self.widget.tag_unbind(j, k)


            # delete widgets from canvas
            self.widget.delete(i.symbol, i.label)
            if self.widget.lineflag:
                self.widget.delete(i.line)

            # break cyclic reference
            i.parent=None

        # move cursor if it's in deleted subtree
        if self.widget.pos in self.subnodes:
            self.widget.move_cursor(self)

        # now subnodes will be properly garbage collected
        self.subnodes=[]

    # move everything below current icon, to make room for subtree
    # using the magic of item tags
    def _tagmove(self, dist):
        # mark everything below current node as movable
        bbox1=self.widget.bbox(self.widget.root.symbol, self.label)
        bbox2=self.widget.bbox('all')
        self.widget.dtag('move')
        self.widget.addtag('move', 'overlapping',
                           bbox2[0], bbox1[3], bbox2[2], bbox2[3])

        # untag cursor & node so they don't get moved too
        # this has to be done under Tk on X11
        self.widget.dtag(self.widget.cursor_box, 'move')
        self.widget.dtag(self.symbol, 'move')
        self.widget.dtag(self.label, 'move')

        # now do the move of all the tagged objects
        self.widget.move('move', 0, dist)

        # fix up connecting lines
        if self.widget.lineflag:
            n=self
            while n:
                if len(n.subnodes):
                    # position of current icon
                    x1, y1=self.widget.coords(n.symbol)
                    # position of last node in subtree
                    x2, y2=self.widget.coords(n.subnodes[-1:][0].symbol)
                    self.widget.coords(n.tree, x1, y1, x1, y2)
                n=n.parent

    # return list of subnodes that are expanded (not including self)
    # only includes unique leaf nodes (e.g. /home and /home/root won't
    # both be included) so expand() doesn't get called unnecessarily
    # thank $DEITY for Dr. Dutton's Data Structures classes at UCF!
    def expanded(self):
        # push initial node into stack
        stack=[(self, (self.id,))]
        list=[]
        while stack:
            # pop from stack
            p, i=stack[-1:][0]
            del stack[-1:]
            # flag to discard non-unique sub paths
            flag=1
            # check all children
            for n in p.subnodes:
                # if expanded, push onto stack
                if n.open_flag:
                    flag=0
                    stack.append(n, i+(n.id,))
            # if we reached end of path, add to list
            if flag:
                list.append(i[1:])
        return list

    # get full name, including names of all parents
    def full_id(self):
        if self.parent:
            return self.parent.full_id()+(self.id,)
        else:
            return (self.id,)

    # expanding/collapsing folders
    def toggle_state(self, state=None):
        if state == None:
            # toggle to other state
            state = not self.open_flag
        else:
            # are we already in the state we want to be?
            if (not state) == (not self.open_flag):
                return

        # not re-entrant
        # acquire mutex
        while self.spinlock:
            pass
        self.spinlock=1

        # call customization hook
        if self.widget.before_hook:
            self.widget.before_hook(self)

        # if we're closed, expand & draw our subtrees
        if not self.open_flag:
            if self.widget.expand_hook:
                self.widget.expand_hook(self)
            self.open_flag=1
            self.widget.itemconfig(self.symbol, image=self.open_icon)

            # get contents of subdirectory or whatever
            contents=self.widget.get_contents(self)

            # move stuff to make room
            self._tagmove(self.widget.disty*len(contents))

            # now draw subtree
            self.subnodes=[]
            # get current position of icon
            x, y=self.widget.coords(self.symbol)
            yp=y
            for i in contents:
                # add new subnodes, they'll draw themselves
                yp=yp+self.widget.disty
                self.subnodes.append(Node(self, i[0], i[1], i[2], i[3],
                                          x+self.widget.distx, yp,
                                          self.widget))

            # the vertical line spanning the subtree
            if self.subnodes and self.widget.lineflag:
                self.tree=self.widget.create_line(x, y,
                                     x, y+self.widget.disty*len(self.subnodes))
                self.widget._canvas.lower(self.tree, self.symbol)
                #~ self.widget.lower(self.tree, self.symbol)

        # if we're open, collapse and delete subtrees
        elif self.open_flag:
            if self.widget.collapse_hook:
                self.widget.collapse_hook(self)
            self.open_flag=0
            self.widget.itemconfig(self.symbol, image=self.closed_icon)

            # if we have any children
            if self.subnodes:
                # recursively delete subtree icons
                self._delete()

                # delete vertical line
                if self.widget.lineflag:
                    self.widget.delete(self.tree)

                # find next (vertically-speaking) node
                n=self
                while n.parent:
                    # position of next sibling in parent's list
                    i=n.parent.subnodes.index(n)+1
                    if i < len(n.parent.subnodes):
                        n=n.parent.subnodes[i]
                        break
                    n=n.parent

                if n.parent:
                    # move everything up so that distance to next subnode is
                    # correct
                    x1, y1=self.widget.coords(self.symbol)
                    x2, y2=self.widget.coords(n.symbol)
                    dist=y2-y1-self.widget.disty
                    self._tagmove(-dist)

        # update scroll region for new size
        self.widget.reset()

        # call customization hook
        if self.widget.after_hook:
            self.widget.after_hook(self)

        # release mutex
        self.spinlock=0

    # expand this subnode
    # doesn't have to exist, it expands what part of the path DOES exist
    def expand(self, dirs):
        # if collapsed, then expand
        self.toggle_state(1)

        # find next subnode
        if dirs:
            for n in self.subnodes:
                if n.id == dirs[0]:
                    n.expand(dirs[1:])
                    break

    # handle mouse clicks by moving cursor and toggling folder state
    def click(self, event):
        self.widget.move_cursor(self)
        # is it expandable!!!!
        if not self.open_icon:
            #~ print('Its a file!')
            pass
        else:
            self.toggle_state()

    # cut a node and it's subtree
    def cut(self):
        # remember what was expanded, so we can re-expand on paste
        expand_list=self._expanded()
        if not self.open_flag:
            expand_list=None

        id=self.full_id()

        # collapse
        self.toggle_state(1)

        # delete from tree
        if self.parent:
            # move cursor safely out of the way
            if self.widget.pos == self:
                self.widget.prev()

            if len(self.parent.subnodes) == 1:
                # delete vertical connecting line
                # if we're the only child
                if self.widget.lineflag:
                    self.widget.delete(self.parent.tree)

            # delete from parent's list of children
            self.parent.subnodes.remove(self)

        # move rest of tree up
        self._tagmove(-self.widget.disty)

        # break cyclic reference
        self.parent=None

        # see _delete() for why we have to do this
        for j in (self.symbol, self.label):
            for k in self.widget.tag_bind(j):
                self.widget.tag_unbind(j, k)

        # delete from canvas
        self.widget.delete(self.symbol, self.label)
        if self.widget.lineflag:
            self.widget.delete(self.line)

        # update scrollbar for new height
        self.widget.resizescrollregion()

        # returns a "cut_object"
        co=Cut_Object(self, id, expand_list)

        # call customization hook
        if self.widget.cut_hook:
            self.widget.cut_hook(co)

        return co

    # insert a "cut object" at the proper place
    # option:
    # 1 - insert as 1st child
    # 2 - insert after last child
    # 3 - insert as next sibling
    def paste(self, co, option=1):
        # call customization hook
        # this usually does the actual cut'n'paste on the underlying
        # data structure
        if self.widget.paste_hook:
            # if it returns false, it wasn't successful
            if self.widget.paste_hook(co):
                return

        # expand if necessary
        if option == 1 or option == 2:
            self.toggle_state(2)

        # make subnode list the right size for _tagmove()
        if option == 1:
            self.subnodes.insert(0, None)
            i=0
        elif option == 2:
            self.subnodes.append(None)
            i=-1
        elif option == 3:
            i=self.parent.subnodes.index(self)+1
            self.parent.subnodes.insert(i, None)

        # move rest of tree down
        self._tagmove(self.widget.disty)

        # place new node
        x, y=self.widget.coords(self.symbol)
        if option == 1 or option == 2:
            x=x+self.widget.distx
        y=y+self.widget.disty

        # create node
        if option == 1 or option == 2:
            parent=self
        elif option == 3:
            parent=self.parent
        n=Node(parent, co.node.name, co.node.id, co.node.open_flag,
               co.node.icon, x, y, self.widget)

        # insert into tree
        if option == 1 or option == 2:
            self.subnodes[i]=n
        elif option == 3:
            # insert as next sibling
            self.parent.subnodes[i]=n

        # expand children to the same state as original cut tree
        if co.state:
            n.expand(co.state)

    # return next lower visible node
    def __next__(self):
        n=self
        if n.subnodes:
            # if you can go right, do so
            return n.subnodes[0]
        while n.parent:
            # move to next sibling
            i=n.parent.subnodes.index(n)+1
            if i < len(n.parent.subnodes):
                return n.parent.subnodes[i]
            # if no siblings, move to parent's sibling
            n=n.parent
        # we're at bottom
        return self

    # return next higher visible node
    def prev(self):
        n=self
        if n.parent:
            # move to previous sibling
            i=n.parent.subnodes.index(n)-1
            if i >= 0:
                # move to last child
                n=n.parent.subnodes[i]
                while n.subnodes:
                    n=n.subnodes[-1]
            else:
                # punt if there's no previous sibling
                if n.parent:
                    n=n.parent
        return n

#------------------------------------------------------------------------------
# default routine to get contents of subtree
# supply this for a different type of app
# argument is the node object being expanded
# should return list of 4-tuples in the form:
# (label, unique identifier, closed icon, open icon)
# where:
#    label             - the name to be displayed
#    unique identifier - an internal fully unique name
#    closed icon       - PhotoImage of closed item
#    open icon         - PhotoImage of open item, or None if not openable
def get_contents(node):
    dirs=[]
    files=[]
    path=os.path.join(*node.full_id())
    for filename in os.listdir(path):
        full=os.path.join(path, filename)
        name=filename
        folder=0
        if os.path.isdir(full):
            # it's a directory
            folder=1
        elif not os.path.isfile(full):
            # but it's not a file
            name=name+' (special)'

        if os.path.islink(full):
            # it's a link
            name=name+' (link to '+os.readlink(full)+')'

        if folder:
            # it's a collapsed directory
            dirs.append((name, full, shut_icon, open_icon))
            #dirs.append((name, filename, shut_icon, open_icon))
        else:
            # it's not!!
            files.append((name, full, file_icon, None))
            #files.append((name, filename, file_icon, None))
    dirs.sort()
    files.sort()
    return dirs+files

#------------------------------------------------------------------------------
class Tree(ScrolledCanvas):
    def __init__(self, master, rootname, rootlabel=None, openicon=None,
                 shuticon=None, getcontents=get_contents, init=None,
                 before=None, after=None, cut=None, paste=None,
                 onexpand=None, oncollapse=None,
                 distx=15, disty=15, textoff=10, lineflag=1, **kw_args):

        global open_icon, shut_icon, file_icon
        
        
        #~ # Define the megawidget options.        
        #~ INITOPT = Pmw.INITOPT
        #~ optiondefs = (
            #~ ('borderframe',    0,            INITOPT),
            #~ ('canvasmargin',   0,            INITOPT),
            #~ ('hscrollmode',    'dynamic',    self._hscrollMode),
            #~ ('labelmargin',    0,            INITOPT),
            #~ ('labelpos',       None,         INITOPT),
            #~ ('scrollmargin',   2,            INITOPT),
            #~ ('usehullsize',    0,            INITOPT),
            #~ ('vscrollmode',    'dynamic',    self._vscrollMode),
        #~ )
        
        
        #~ self.defineoptions(kw_args, optiondefs)
        ScrolledCanvas.__init__(self, master)
        #~ self.initialiseoptions(TxTree)

        


        # default images (BASE64-encoded GIF files)
        # we have to delay initialization until Tk starts up or PhotoImage()
        # complains (otherwise I'd just put it up top)
        if open_icon == None:
            open_icon=PhotoImage(data="R0lGODlhFAAUAJEAANnZ2QEBAf///////yH5BAEAAAAALAAAAAAUABQAAAJFhI+py+3fSAgf8yJUk8SEjwkRQSF8TIpN8BEpPsHHo/hB8NEovhF8BIp/BB8pPhL8o/gYBN8oPhrBB4qPR/Axdbn9oSIFADs=")
            shut_icon=PhotoImage(data="R0lGODlhFAAUAJEAANnZ2QEBAf///////yH5BAEAAAAALAAAAAAUABQAAAJShI+py0wJ4WNeRBB8TIsICuFjAsUm+JgUn+AjUvwg+HgU3wg+GsU/go9A8Y/gI1B8I/hoFD8IPh7FJ/iIFJvgY0ZEEHxMiAiCj2kRqqqUUkqRAgA7")
            file_icon = PhotoImage(data="R0lGODlhFAAUAJEAANnZ2QEBAf///////yH5BAEAAAAALAAAAAAUABQAAAI7hI+py+0PozQkPsHHo/hG8BEoPhJ8pPhI8JHiI8FHio8EHyk+Enyk+EjwESi+EXw8ik/wMXW5/WGUhhQAOw==")
                
            self.open_icon=open_icon
            self.shut_icon=shut_icon
            self.file_icon=file_icon


        # function to return subnodes (not very much use w/o this)
        if not getcontents:
            raise ValueError('must have "get_contents" function')
        self.get_contents=getcontents
        # horizontal distance that subtrees are indented
        self.distx=distx
        # vertical distance between rows
        self.disty=disty
        # how far to offset text label
        self.textoff=textoff
        # called after new node initialization
        self.init_hook=init
        # called just before subtree expand/collapse
        self.before_hook=before
        # called on expand
        self.expand_hook=onexpand
        # called just after subtree expand/collapse
        self.after_hook=after
        # called on collapse
        self.collapse_hook=oncollapse
        # called at the end of the cut operation
        self.cut_hook=cut
        # called beginning of the paste operation
        self.paste_hook=paste
        # flag to display lines
        self.lineflag=lineflag

        # create root node to get the ball rolling
        if openicon:
            oi = openicon
        else:
            oi = open_icon
        if shuticon:
            si = shuticon
        else:
            si = shut_icon
        if rootlabel:
            self.root=Node(None, rootlabel, rootname, si, oi, 10, 10, self)
        else:
            self.root=Node(None, rootname, rootname, si, oi, 10, 10, self)

        # configure for scrollbar(s)
        self.reset()


        # add a cursor
        self.cursor_box=self.create_rectangle(0, 0, 0, 0)
        self.move_cursor(self.root)

        # make it easy to point to control
        self.bind('<Enter>', self.mousefocus)

        #
        # totally arbitrary yet hopefully intuitive default keybindings
        # stole 'em from ones used by microsoft tree control
        #
        # page-up/page-down
        self.bind('<Next>', self.pagedown)
        self.bind('<Prior>', self.pageup)

        # arrow-up/arrow-down
        self.bind('<Down>', self.next)
        self.bind('<Up>', self.prev)

        # arrow-left/arrow-right
        self.bind('<Left>', self.ascend)
        # (hold this down and you expand the entire tree)
        self.bind('<Right>', self.descend)

        # home/end
        self.bind('<Home>', self.first)
        self.bind('<End>', self.last)

        # space bar
        self.bind('<Key-space>', self.toggle)

    # scroll (in a series of nudges) so items are visible
    def see(self, *items):
        x1, y1, x2, y2=self.bbox(*items)
        while x2 > self.canvasx(0)+self.winfo_width():
            old=self.canvasx(0)
            self.xview('scroll', 1, 'units')
            # avoid endless loop if we can't scroll
            if old == self.canvasx(0):
                break
        while y2 > self.canvasy(0)+self.winfo_height():
            old=self.canvasy(0)
            self.yview('scroll', 1, 'units')
            if old == self.canvasy(0):
                break
        # done in this order to ensure upper-left of object is visible
        while x1 < self.canvasx(0):
            old=self.canvasx(0)
            self.xview('scroll', -1, 'units')
            if old == self.canvasx(0):
                break
        while y1 < self.canvasy(0):
            old=self.canvasy(0)
            self.yview('scroll', -1, 'units')
            if old == self.canvasy(0):
                break

    # move cursor to node
    def move_cursor(self, node):
        self.pos=node
        x1, y1, x2, y2=self.bbox(node.symbol, node.label)
        self.coords(self.cursor_box, x1-1, y1-1, x2+1, y2+1)
        self.see(node.symbol, node.label)

    # expand given path
    # note that the convention used in this program to identify a
    # particular node is to give a tuple listing it's id and parent ids
    # so you probably want to use os.path.split() a lot
    def expand(self, path):
        self.root.expand(path[1:])
        
    # soak up event argument when moused-over
    # could've used lambda but didn't...
    def mousefocus(self, event):
        self.focus_set()

    # open/close subtree
    def toggle(self, event=None):
        self.pos.toggle_state()

    # move to next lower visible node
    def next(self, event=None):
        self.move_cursor(next(self.pos))

    # move to next higher visible node
    def prev(self, event=None):
        self.move_cursor(self.pos.prev())

    # move to immediate parent
    def ascend(self, event=None):
        if self.pos.parent:
            # move to parent
            self.move_cursor(self.pos.parent)

    # move right, expanding as we go
    def descend(self, event=None):
        self.pos.toggle_state(1)
        if self.pos.subnodes:
            # move to first subnode
            self.move_cursor(self.pos.subnodes[0])
        else:
            # if no subnodes, move to next sibling
            next(self)

    # go to root
    def first(self, event=None):
        # move to root node
        self.move_cursor(self.root)

    # go to last visible node
    def last(self, event=None):
        # move to bottom-most node
        n=self.root
        while n.subnodes:
            n=n.subnodes[-1]
        self.move_cursor(n)

    # previous page
    def pageup(self, event=None):
        n=self.pos
        j=self.winfo_height()/self.disty
        for i in range(j-3):
            n=n.prev()
        self.yview('scroll', -1, 'pages')
        self.move_cursor(n)

    # next page
    def pagedown(self, event=None):
        n=self.pos
        j=self.winfo_height()/self.disty
        for i in range(j-3):
            n=next(n)
        self.yview('scroll', 1, 'pages')
        self.move_cursor(n)

#------------------------------------------------------------------------------
# the good 'ol test/demo code
if __name__ == '__main__':
    import sys


    root=Tk()
    root.title(os.path.basename(sys.argv[0]))
    tree=os.sep
    if sys.platform == 'win32':
        # we could call the root "My Computer" and mess with get_contents()
        # to return "A:", "B:", "C:", ... etc. as it's children, but that
        # would just be terminally cute and I'd have to shoot myself
        tree='C:'+os.sep

    # create the control
    t=TxTree(root, tree, rootlabel=tree)
    t.pack(fill='both', expand='yes')

    # we could do without this, but it's nice and friendly to have
    b=Button(root, text='Quit', command=root.quit)
    b.pack()
    # expand out our current directory
    # note that directory case in getcwd() under win32 is sometimes broken
    root.mainloop()
