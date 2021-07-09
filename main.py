#/.venv/bin/python

from source.testloop import Test
from source.testloop import splash
import os
import warnings
warnings.filterwarnings('ignore')

splash()

try:
    t = Test()
    if (input("\nDo you want to calibrate microphone and mouth? (y/n)\n-->")).lower() == "y":
        t.calibrateMic()    # calibration of the measurement microphone
        t.calibrateMouth()  # calibration of the mouth
    t.execution()           # execute test
    input("\nPress ENTER TO CONTINUE")
    t.printReport()         # create csv file with results
    ("Report printed!")

except KeyboardInterrupt:
    print("Goodbye")
