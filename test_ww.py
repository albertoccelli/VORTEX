from source.play import play_wav
from source.recorder import Recorder
from time import sleep
from source.dsp import get_rms

ww = "phrases/harman/DUN/DUN_000.wav"
cancel = "phrases/harman/DUN/DUN_999.wav"

ntests = 190
issued = 10
recognized = 10
'''
for i in range(ntests):
    while True:
        input("TEST %s - Press ENTER to reproduce WW" % (i+1))
        issued+=1
        play_wav(ww)
        res = input("Recognized? (0/1)")
        if res == '':
            play_wav(cancel)
            recognized+=1
            print("Rate: %s/%s\n" % (recognized,issued))
            break
    
'''

class MyRec(Recorder):
    def __init__(self):
        super(MyRec, self).__init__()
        self.activated = False
        self.waiting_for_mic = False

    def on_negative_edge(self):
        if self.waiting_for_mic == True:
            print("MIC ACTIVATED")
            self.activated = True
            raise KeyboardInterrupt
    
    def on_positive_edge(self):
        pass

r = MyRec()

r.record(seconds = 10, channel = 0, monitor = True)


r.soglia = get_rms(r.data)[0]-15
print("Treshold: %sdBFS" % r.soglia)
while True:
    r.record(4, channel = 0, monitor = False)
    if r.rms > r.soglia:
        break

recognized = 0
issued = 0

r.activated = False
for i in range(ntests):
    print("Test n. %s" % (i+1))
    while True:
        r.record(4, channel = 0, monitor = False)
        if r.rms > r.soglia:
            break
    while True:
        r.activated = False
        print("Wakeword")
        r.waiting_for_mic = True
        play_wav(ww)
        issued+=1
        r.record(2, channel = 0, monitor = False)
        if r.activated == True or r.rms < r.soglia:
            recognized+=1
            print("Cancel")
            play_wav(cancel)
            sleep(3)
            r.waiting_for_mic = False
            break
        else:
            print("Mic not activated, trying again...")
    print("Recognized/Issued: %s/%s" % (recognized, issued))
