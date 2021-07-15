# /.venv/bin/python

from source.testloop import Test, splash, clear_console
import warnings
# user interface
import tkinter as tk
from tkinter import messagebox

warnings.filterwarnings('ignore')

root = tk.Tk()
root.withdraw()

splash()
input("Press ENTER to begin")
clear_console()

try:
    t = Test()
    if not t.mCalibrated:
        MsgBox = tk.messagebox.askyesno('Calibration', 'Do you want to calibrate the microphones and the mouth?',
                                        icon='question')
        print(MsgBox)
        if MsgBox:
            if not t.recorder.calibrated[t.micChannel]:
                t.calibrate_mic()  # calibration of the measurement microphone
            if not t.recorder.calibrated[t.earChannel]:
                t.calibrate_ear()  # calibration of Oscar's ear
            input("\nPlace the measurement microphone at the MRP and press ENTER to continue\n-->")
            t.calibrate_mouth()  # calibration of the mouth
    t.execution()  # execute test
    if t.completed:
        messagebox.showinfo(t.testName, "Test completed!")
        t.print_report()  # create csv file with results
        "Report printed!"
    else:
        messagebox.showinfo(t.testName, "Test interrupted")

except KeyboardInterrupt:
    print("Goodbye")
