#/.venv/bin/python

from source.testloop import Test
from source.testloop import splash
import os
import warnings
warnings.filterwarnings('ignore')

# user interface
import tkinter as tk
from tkinter import messagebox

root = tk.Tk()
root.withdraw()

splash()

try:
    t = Test()
    MsgBox = tk.messagebox.askquestion ('Calibration','Do you want to calibrate the microphone and the mouth?',icon = 'warning')
    if MsgBox == 'yes':
        t.calibrateMic()    # calibration of the measurement microphone
        t.calibrateMouth()  # calibration of the mouth
    t.execution()           # execute test
    if t.completed == True:
        messagebox.showinfo(t.testname,"Test completed!")
        t.printReport()         # create csv file with results
        ("Report printed!")
    else:
        messagebox.showinfo(t.testname,"Test interrupted")

except KeyboardInterrupt:
    print("Goodbye")
