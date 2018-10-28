from tkinter import *
import tkinter as tk
import tkinter.font as tkFont
import tkinter.ttk as ttk
import json
import time
import datetime

headers = ['#', 'Name', 'GTID'] #% of Meetings Attended

class MultiColumnListbox(object):
    """use a ttk.TreeView as a multicolumn ListBox"""

    def __init__(self):
        self.tree = None
        self._setup_widgets()
        self.refresh(True)

    def doStuff(self):
        while True:
            try:
                self.refresh(False)
                time.sleep(3)
            except:
                sys.exit()

    def _setup_widgets(self):
        s = "List of People at Today's Meeting"
        msg = ttk.Label(wraplength="4i", justify="left", anchor="n",
            padding=(10, 2, 10, 2), text=s)
        msg.pack(fill='x')

        s = str(datetime.datetime.now().date())
        msg = ttk.Label(wraplength="4i", justify="left", anchor="n",
            padding=(10, 2, 10, 2), text=s)
        msg.pack(fill='x')

        #b = Button(root, text="Refresh",  command= lambda: self.refresh(False))
        #b.pack()

        container = ttk.Frame(width = 380, height = 500, relief = SUNKEN)
        container.pack(fill = X, padx = 5 , pady = 5)
        # create a treeview with dual scrollbars
        self.tree = ttk.Treeview(columns=headers, show="headings")
        vsb = ttk.Scrollbar(orient="vertical",
            command=self.tree.yview)
        hsb = ttk.Scrollbar(orient="horizontal",
            command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set,
            xscrollcommand=hsb.set)
        self.tree.grid(column=0, row=0, sticky='nsew', in_=container)
        vsb.grid(column=1, row=0, sticky='ns', in_=container)
        hsb.grid(column=0, row=1, sticky='ew', in_=container)
        container.grid_columnconfigure(0, weight=1)
        container.grid_rowconfigure(0, weight=1)

    def sortby(tree, col, descending):
        """sort tree contents when a column header is clicked on"""
        # grab values to sort
        data = [(tree.set(child, col), child) \
            for child in tree.get_children('')]
        # if the data to be sorted is numeric change to float
        #data =  change_numeric(data)
        # now sort the data in place
        data.sort(reverse=descending)
        for ix, item in enumerate(data):
            tree.move(item[1], '', ix)
        # switch the heading so it will sort in the opposite direction
        tree.heading(col, command=lambda col=col: sortby(tree, col, \
            int(not descending)))

    def refresh(self, setColSize):
        self.tree.delete(*self.tree.get_children())
        filename = 'Attendence ' + time.strftime("%m.%d") + '.json'
        with open(filename) as f:
            jsonData = json.load(f)
        peopleList = list(jsonData.keys())
        data = [[0 for x in range(3)] for y in range(len(peopleList))]
        for i in range(len(peopleList)):
            data[i][0] = i+1
            data[i][1] = jsonData[peopleList[i]]['name']
            data[i][2] = jsonData[peopleList[i]]['id']
        for col in headers:
            self.tree.heading(col, text=col.title(),
                command=lambda c=col: sortby(self.tree, c, 0))
            # adjust the column's width to the header string
            if(setColSize):
                self.tree.column(col, width=tkFont.Font().measure(col.title()))

        for item in data:
            self.tree.insert('', 'end', values=item)
            # adjust column's width if necessary to fit each value
            for ix, val in enumerate(item):
                col_w = tkFont.Font().measure(val)
                if self.tree.column(headers[ix],width=None)<col_w:
                    self.tree.column(headers[ix], width=col_w)
