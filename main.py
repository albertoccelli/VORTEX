#/.venv/bin/python

from source.testloop import Test
from source.testloop import splash

splash()

try:
    t = Test()
    input("\nPress ENTER TO CONTINUE")
    t.execution()

except KeyboardInterrupt:
    print("Goodbye")
