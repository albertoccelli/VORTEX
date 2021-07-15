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
        if MsgBox:
            # calibration of measurement microphone
            if not t.recorder.calibrated[t.micChannel]:
                clear_console()
                print("Calibrating measurement microphone\n")
                t.calibrate_mic()
                input("\nPress ENTER to proceed...\n-->")
            # calibration of Oscar's ear
            if not t.recorder.calibrated[t.earChannel]:
                clear_console()
                print("Calibrating artificial ear\n")
                t.calibrate_ear()
                input("\nPress ENTER to proceed...\n-->")
            # calibration of artificial mouth
            clear_console()
            input("Calibrating mouth: please place the measurement microphone at the MRP and press ENTER\n-->")
            t.calibrate_mouth()  # calibration of the mouth
            input("\nPress ENTER to proceed...\n-->")
    t.execution()  # execute test
    if t.completed:
        messagebox.showinfo(t.testName, "Test completed!")
        t.print_report()  # create csv file with results
        "Report printed!"
    else:
        messagebox.showinfo(t.testName, "Test interrupted")

except KeyboardInterrupt:
    print("Goodbye")
