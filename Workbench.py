#
#
import sqlite3 as sqldb
from Moggs import *
from tkinter import filedialog

import os
import shutil
import sys
import glob
import pprint


class Workbench(Tk):
    def __init__(self):
        Tk.__init__(self)
        self.title("SQL Workbench")

        # toolbar
        self.toolbar = Buttonbox(self)
        self.toolbar.add("SQL Pad", command=self.sqlPad)
        self.toolbar.add("Exit", command=self.exit)
        self.toolbar.alignbuttons()
        self.toolbar.pack(side = "top", fill = "x", expand = "no")
       
        # main frame
        mainFrame = Frame(self)
        mainFrame.pack(side = "top", fill = "both", expand = "yes", padx=4)
            
        # left frame
        lFrame = Frame(mainFrame)
        lFrame.pack(side = "left", fill = "y", expand = "no", padx=4)

        # middle frame
        mFrame = Frame(mainFrame)
        mFrame.pack(side = "left", fill = "both", expand = "yes", padx=4)
        self.mFrame = mFrame
        # right frame
        rFrame = Frame(mainFrame)
        rFrame.pack(side = "left", fill = "y", expand = "no", padx=4)

        b = Button(rFrame, text = "New Table", command=self.newTable)
        b.pack()
        b = Button(rFrame, text = "Edit Table", command=self.editTable)
        b.pack()
        b = Button(rFrame, text = "Drop Table", command=self.dropTable)
        b.pack()
        b = Button(rFrame, text = "Load Data", command=self.loadData)
        b.pack()
        b = Button(rFrame, text = "View Data", command=self.viewData)
        b.pack()

        # status bar
        self.statusBar = LabelEntry(self)
        self.statusBar.pack(side = "top", fill = "x", expand = "no")

        # connection manager
        self.connectionManager = ConnectionManager(lFrame, parent=self)
        self.connectionManager.pack(side = "top", fill = "both", expand = "yes")
        
        # work area
        self.workArea = ScrolledCanvas(mFrame)
        self.workArea.pack(side = "top", fill = "both", expand = "yes")
        self.workArea.oldactive = None ## which object is selected

    def sqlPad(self):
        if self.connection:
            pad = SQLScratchPad(self.connection)


    def clearWorkArea(self):
        """remove all items from canvas!"""
        self.workArea.delete("all")

    def listTables(self):
        self.clearWorkArea()
        sql = "SELECT name FROM sqlite_master WHERE type='table';"
        tables = self.executeFetchall(sql)
        self.populateWorkArea(tables)
        
        
    def populateWorkArea(self, tables):
        Y = 10
        X = 10
        W = 50
        H = 70
        for row in tables:
            tableName = row[0]
            # create table object
            tab = Table(self.workArea, tableName, X, Y, W, H)
            # arrange them all
            x1, y1, x2, y2 = self.workArea.bbox("all")
            X = X + W + 15
            if X >= 600:
                X = 10
                Y = y2 + 2
            self.workArea.tag_bind(tableName, "<1>", TagBinder(self.workArea, tableName))
                
                
    def dropTable(self):
        # get table name & description for 'active' / selected table
        if self.workArea.oldactive:
            tn = self.workArea.oldactive
            sql = "drop table %s" %tn
            self.execute(sql)
            self.commit()
            self.workArea.oldactive = None
            self.listTables()

    def editTable(self):
        """show the table editor"""
        # get table name & description for 'active' / selected table
        if self.workArea.oldactive:
            tn = self.workArea.oldactive
            sql = "PRAGMA table_info([%s])" %tn
            td = self.executeFetchall(sql)
            te = TableEditor(self, tableName=tn, tableDesc=td)
           
            
    def newTable(self):
        """show the table editor"""
        te = TableEditor(self)
        
    def exit(self):
        """Close the main window and withdraw it (clean up)"""
        self.quit()
        self.withdraw()


    def execute(self, sql):
        cur = self.connection.cursor()
        cur.execute(sql)

    def executeFetchall(self, sql):
        cur = self.connection.cursor()
        cur.execute(sql)
        return cur.fetchall()


    def commit(self):
        self.connection.commit()

    def viewData(self):
        if self.workArea.oldactive:
            tn = self.workArea.oldactive
            sql = "PRAGMA table_info([%s])" %tn
            tdesc = self.executeFetchall(sql)
            sql = "select * from %s" %(tn)
            tdata = self.executeFetchall(sql)
            DataEditor(self, tableDesc = tdesc, tableData = tdata)
        
    def loadData(self):
        ## load the data from a csv file into selected table
        ## data MUST match table & be in correct column order!
        if self.workArea.oldactive:
            tn = self.workArea.oldactive
            filename = filedialog.askopenfilename()
            if filename:
                fin = open(filename)
                for row in fin:
                    #~ row_data = eval(line) ## SUPER DANGEROUS, SERIOUSLY!
                    
                    ## SQL INJECTION ATTACK WAITING TO HAPPEN
                    sql = "insert into %s values (%s)" %(tn, row)
                    print(sql)
                    self.execute(sql)
                    self.commit()
                

class ConnectionManager(Frame):
    def __init__(self, cont, parent=None):
        Frame.__init__(self, cont)
        self.parent = parent
        
        l = Label(self, text = "Choose Connection:")
        l.pack(fill = "x")
        
        self.databaseName = LabelCombobox(self, text = "Database Name")
        self.databaseName.pack(fill = "x")

        # testing
        self.databaseName.set("moggs.dbf")

        
        b = Button(self, text = "Connect", command = self.connect)
        b.pack()
        
        # populate databaeName
        self.populateDatabaseName()
        
        
    def connect(self):
        self.parent.statusBar.set("")
        
        self.backupDatabase()
        
        try:
            self.connection = sqldb.connect(self.databaseName.get())
        except Exception as ex:
            self.parent.statusBar.set("%s" %str(ex))
        else:
            self.parent.connection = self.connection # fudge?
            self.parent.statusBar.set("Connected to %s" %self.databaseName.get())
            self.parent.listTables()
            
    def populateDatabaseName(self):
        filenames = glob.glob("*.dbf")
        filenames.sort()
        self.databaseName.setlist(filenames)
        
    def backupDatabase(self):
        dbname = self.databaseName.get()
        shutil.copyfile(dbname, dbname.replace(".dbf", ".bak"))
        
        
class DataEditor(Toplevel):
    def __init__(self, parent=None, tableName="", tableDesc=None, tableData=None):
        Toplevel.__init__(self)
        self.title("Data Viewer Table : %s" %tableName)
        self.parent = parent
        
        self.dataEditor = ScrolledTreeview(self, show="headings")
        self.dataEditor.pack(fill="both", expand="yes")
        cols = []
        for row in tableDesc:
            cols.append(row[1])
        self.dataEditor["columns"] = cols
        for col in cols:
            self.dataEditor.heading(col, text=col)
        
        for row in tableData:
            #~ print(row)
            self.dataEditor.insert("", "end", values=row)
            
        
        
class TableEditor(Toplevel):
    def __init__(self, parent=None, tableName="", tableDesc=None):
        Toplevel.__init__(self)
        self.title("Edit Table : %s" %tableName)

        self.parent = parent
        
        self.tableColumns = []
        
        # toolbar
        bb = Buttonbox(self)
        bb.add("Add", command=self.addRow)
        bb.add("Save", command=self.saveTable)
        bb.pack(fill="x")

        # table name
        self.tableName = LabelEntry(self, text = "Table Name")
        self.tableName.set(tableName)
        self.tableName.pack(fill = "x")
        
        # load in the table description create a row per column
        # populate the rows with the table description
        # unless new table (tableData=None) in which case
        # create one empty row
        if tableDesc:
            for col in tableDesc:
                row = TableColumn(self)
                self.tableColumns.append(row)
                row.pack()
                row.colName.set(col[1])
                row.dataType.set(col[2])
                null = col[3]
                dflt = col[4]
                pk = col[5]
                if pk:
                    row.dataConst.set("PRIMARY KEY")
                else:
                    if null:
                        row.dataConst.set("NOT NULL")
        else:
            row = TableColumn(self)
            self.tableColumns.append(row)
            row.pack()
        
        


    def saveTable(self):
        # drop the table first (very destructive!)
        sql = "drop table %s" %(self.tableName.get())
        #~ print(sql)
        try:
            self.parent.execute(sql)
            self.parent.commit()
        except:
            pass # really...?
        
        # construct the create table sql
        sql = """create table %s (""" %(self.tableName.get())
        for row in self.tableColumns:
            sql = sql + row.getSQL()
            sql = sql + ","
        sql = sql[:-1] + ")"
        #~ print(sql)
        self.parent.execute(sql)
        self.parent.commit()
        self.parent.listTables()
        self.withdraw()

    def addRow(self):
        row = TableColumn(self)
        self.tableColumns.append(row)
        row.pack()
        
    def deleteRow(self):
        pass
        
        
class TableColumn(Frame):
    def __init__(self, parent):
        Frame.__init__(self, parent)

        # column name
        self.colName = LabelEntry(self, text = "Column Name")
        self.colName.pack(side = "left")

        # column data type
        self.dataType = LabelCombobox(self, text = "Data Type")
        self.dataType.setlist(["INTEGER", "REAL", "TEXT", "BLOB"])
        self.dataType.pack(side = "left")

        # column constraints, PRIMARY KEY implies NOT NULL & UNIQUE
        self.dataConst = LabelCombobox(self, text = "Constraints")
        self.dataConst.setlist(["", "PRIMARY KEY", "UNIQUE", "NOT NULL", "UNIQUE, NOT NULL"])
        self.dataConst.pack(side = "left")

    def getSQL(self):
        cn = self.colName.get()
        dt = self.dataType.get()
        dc = self.dataConst.get()
        if dc:
            return "%s %s %s" %(cn, dt, dc)
        else:
            return "%s %s" %(cn, dt)

class Table:
    """object on canvas that represents a database table"""
    def __init__(self, canvas, tableName, X, Y, W, H):
        self.canvas = canvas
        self.name = tableName
        
        self.canvas.create_polygon(
            (X, Y),
            (X+W-10, Y),   # chopped
            (X+W, Y+H-60), # corner
            (X+W, Y+H),
            (X, Y+H),
            (X, Y),
            fill = "white",
            outline = "black",
            width = 2,
            tags = tableName,
            )
        # grid lines
        self.canvas.create_line(X + 5, Y + 20, X + W - 5, Y + 20, width = 2, tags=tableName)
        self.canvas.create_line(X + 5, Y + 30, X + W - 5, Y + 30, width = 2, tags=tableName)
        self.canvas.create_line(X + 5, Y + 40, X + W - 5, Y + 40, width = 2, tags=tableName)
        self.canvas.create_line(X + 5, Y + 50, X + W - 5, Y + 50, width = 2, tags=tableName)
        # grid lines
        self.canvas.create_line(X + 5, Y + 20, X + 5, Y + 50, width = 2, tags=tableName)
        self.canvas.create_line(X + 15, Y + 20, X + 15, Y + 50, width = 2, tags=tableName)
        self.canvas.create_line(X + 25, Y + 20, X + 25, Y + 50, width = 2, tags=tableName)
        self.canvas.create_line(X + 35, Y + 20, X + 35, Y + 50, width = 2, tags=tableName)
        self.canvas.create_line(X + 45, Y + 20, X + 45, Y + 50, width = 2, tags=tableName)
        
        # label
        self.canvas.create_text(X, Y+H, anchor = "nw", text = "%s" %tableName, font = "Courier 6", tags=tableName)
        
class TagBinder:
    def __init__(self, canvas, tag):
        self.canvas = canvas
        self.tag = tag
        
    def __call__(self, event):
        try:
            self.canvas.itemconfig(self.canvas.oldactive, outline="black")
        except:
            pass
        try:
            self.canvas.itemconfig(self.tag, outline="red")
        except:
            ## this is a real bad hack
            ## basically one of the items on the canvas does not suport "outline"
            ## this except catches that and stops changing colour
            ## happy accident means the outside shape is changed but nothing else!
            pass
        self.canvas.oldactive = self.tag
        
        
class SQLScratchPad(Toplevel):
    def __init__(self, connection):
        Toplevel.__init__(self)
        self.title("SQL Scratch Pad")
        
        self.connection = connection
        
        l = Label(self, text = "SQL Input")
        l.pack(fill="x")
        self.sqlInput = ScrolledText(self, height=3)
        self.sqlInput.pack(fill="both", expand="yes")
        
        bb = Buttonbox(self)
        bb.add("Execute", command=self.execute)
        bb.add("Execute & Fetch One", command=self.executeFetchone)
        bb.add("Execute & Fetch All", command=self.executeFetchall)
        bb.add("Close", command=self.withdraw)
        bb.alignbuttons()
        bb.pack(fill="x")
        
        
        l = Label(self, text = "Results...")
        l.pack(fill="x")
        self.sqlOutput = ScrolledText(self)
        self.sqlOutput.pack(fill="both", expand="yes")
        
    def log(self, text):
        self.sqlOutput.insert("end", "-------------------------------------\n")
        self.sqlOutput.insert("end", text)
        self.sqlOutput.insert("end", "\n-------------------------------------\n")
        self.sqlOutput.see("end")
        
    def execute(self):
        sql = self.sqlInput.gettext()
        cur = self.connection.cursor()
        cur.execute(sql)
        self.log("executed")
        
    def executeFetchone(self):
        sql = self.sqlInput.gettext()
        cur = self.connection.cursor()
        cur.execute(sql)
        self.log(pprint.pformat(cur.fetchone()))
        
    def executeFetchall(self):
        sql = self.sqlInput.gettext()
        cur = self.connection.cursor()
        cur.execute(sql)
        self.log(pprint.pformat(cur.fetchall()))
        
        
wb = Workbench()
wb.mainloop()
