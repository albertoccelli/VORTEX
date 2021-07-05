#/.venv/bin/python

from source.testloop import Test
from source.testloop import splash

splash()

try:
    t = Test()
    t.recorder.record(10)

except KeyboardInterrupt:
    print("Goodbye")
