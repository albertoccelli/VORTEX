#/.venv/bin/python

from source.testloop import Test
from source.testloop import splash
from source.play import playWav
from source.recorder import Recorder
from threading import Thread

splash()

try:
    t = Test()
    input("\nPress ENTER TO CONTINUE")
    t.recordTreshold(15)
    t.execution()

except KeyboardInterrupt:
    print("Goodbye")
