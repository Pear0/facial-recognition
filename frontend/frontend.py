'''
Here the TreeView widget is configured as a multi-column listbox
with adjustable column width and column-header-click sorting.
'''
from tkinter import *
import tkinter as tk
import tkinter.font as tkFont
import tkinter.ttk as ttk
import RefreshingList as RL
import threading

root = tk.Tk()
listbox = None

def start():
    global root
    global listbox
    listbox = RL.MultiColumnListbox()
    root.update()
    root.after(1000,lambda: listbox.refresh(False))
    threading.Thread(target=listbox.doStuff).start()


def StartButton():
    start()

def init():
    global root

    root.title("Attendence")
    #root.resizable(width=False, height=False)
    root.minsize(width=300, height=350)
    root.maxsize(width=400, height=500)

    Start = Button(root, text="Start", command=StartButton)
    Start.pack(side = BOTTOM, pady = 25, anchor=CENTER)

    root.mainloop()

init()




