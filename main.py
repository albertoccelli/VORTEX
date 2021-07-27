# /.venv/bin/python
import os

from source.testloop import Test, splash
from source.cli_tools import clear_console
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
    '''
    if t.completed > 0 and not t.running:
        q = input("Test appears have completed %s round(s)! Want to start a new one?\n-->" % t.completed)
        if q.lower() == "y":
            pass
    '''

    if not t.recorder.calibrated[t.micChannel] or not t.recorder.calibrated[t.earChannel]:
        MsgBox = tk.messagebox.askyesno('Calibration', 'Do you want to calibrate the microphones?',
                                        icon='question')
    else:
        MsgBox = tk.messagebox.askyesno('Calibration', 'Do you want to calibrate the microphones?'
                                                       '(Press "No" to proceed with the previously saved '
                                                       'calibration)',
                                        icon='question')
    if MsgBox:
        # calibration of measurement microphone
        clear_console()
        print("Calibrating measurement microphone\n")
        t.calibrate_mic()
        input("\nPress ENTER to proceed...\n-->")
        # calibration of Oscar's ear
        clear_console()
        print("Calibrating artificial ear\n")
        t.calibrate_ear()
        input("\nPress ENTER to proceed...\n-->")
        # calibration of artificial mouth
        clear_console()
        t.save_settings()

    if not t.mCalibrated:
        MsgBox = tk.messagebox.askyesno('Calibration', 'Do you want to calibrate the mouth?',
                                        icon='question')
    else:
        MsgBox = tk.messagebox.askyesno('Calibration', 'Do you want to calibrate the mouth?'
                                                       '(Advised if the language has changed.'
                                                       'Press "No" to proceed with the previously saved '
                                                       'calibration.)',
                                        icon='question')
    if MsgBox:
        clear_console()
        print("------------------------------------------------------------------")
        input("Calibrating mouth: please place the measurement microphone at the MRP and press ENTER\n-->")
        t.calibrate_mouth()  # calibration of the mouth
        input("\nPress ENTER to proceed...\n-->")
        t.save_settings()

    clear_console()
    t.mic_mode = int(input("Please choose the microphone activation mode:\n"
                           "1) Manual (Push To Talk from the steering wheel\n"
                           "2) Wake-word\n"
                           "-->"))
    if not t.running:
        t.status = int(input("From which test do you want to start??\n-->"))-1
    t.execution()  # execute test
    if t.completed > 0 and not t.running:
        messagebox.showinfo(t.testName, "Test completed!")
        t.print_report()  # create csv file with results
        "Report printed!"
    else:
        messagebox.showinfo(t.testName, "Test interrupted")
    t.print_report()
    os.system("")
    pass
    '''
        else:
            q2 = input("Print the report before quitting?\n-->")
            if q2.lower == "y":
                t.print_report()
    '''
except KeyboardInterrupt:
    print("Goodbye")
