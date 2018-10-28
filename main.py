import multiprocessing
import psutil
from facerec import cameras, processing, tracking
from tkinter import *
import tkinter as tk
import tkinter.font as tkFont
import tkinter.ttk as ttk
import sys
import threading
from multiprocessing import Process
import RefreshingList as RL
import json
import time

#------------------------------------------------------------

root = tk.Tk()
listbox = None
Start = None

def makeGUI():
    global root, Start
    root.title("Attendence")
    root.minsize(width=300, height=350)
    root.maxsize(width=400, height=500)

    Start = Button(root, text="Start", command=run)
    Start.pack(side = BOTTOM, pady = 25, anchor=CENTER)

    root.mainloop()

def run():
    filename = 'Attendence ' + time.strftime("%m.%d") + '.json'
    with open(filename, 'w') as outfile:
        json.dump({}, outfile, sort_keys=True, indent=4)
    startTable()
    Process(target=startRec).start()

def startTable():
    global root
    global listbox
    global Start


    listbox = RL.MultiColumnListbox()
    root.update()
    root.after(1000,lambda: listbox.refresh(False))
    threading.Thread(target=listbox.doStuff).start()
    Start['state'] = "disabled"

#-------------------------------------------------------------

def startRec():
    image_queue = multiprocessing.Queue(1)
    face_pairs_queue = multiprocessing.Queue(8)

    for _ in range(3):
        worker = processing.FaceDetectionWorker.new_process(image_queue, face_pairs_queue)
        worker.start()
        process = psutil.Process(pid=worker.pid)

        if hasattr(process, 'cpu_affinity'):
            cpu_list = process.cpu_affinity()
            process.cpu_affinity(cpu_list[0: len(cpu_list) - 1])
        else:
            process.nice(process.nice() + 1)

    tracking.FaceRecognitionWorker.new_process(face_pairs_queue).start()
    camera = cameras.CvCamera()
    while True:
        output = camera.capture()
        image_queue.put(output)

#-------------------------------------------------------------

if __name__ == '__main__':
    makeGUI()
