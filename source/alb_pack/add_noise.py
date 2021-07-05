from scipy.io.wavfile import read, write
import numpy as np
from . resample import resample
import matplotlib.pyplot as plt



def addNoise(sound, noise, fs):
    '''
    Add noise data to sound data.
    Before processing the audios, make sure to have properly resampled the files.
    '''

    fadein = 0.2
    fadeout = 0.2

    noise = noise[0:len(sound)]

    #ramp up
    rampin = []
    for i in range(round(fadein*fs)):
        rampin.append(-1/(fadein*fs)+(i+1)/(fadein*fs))
    #ramp down
    rampout = []
    for i in range(round(fadeout*fs)):
        rampout.append(-1/(fadeout*fs)+(i+1)/(fadeout*fs))
    rampout.reverse()

    #apply rampin
    for i in range(len(rampin)):
        noise[i] = noise[i]*rampin[i]
    #apply rampout
    for i in range(len(rampin)):
        noise[-(len(rampin)) + i] = noise[-(len(rampin)) + i]*rampout[i]
    total = noise+sound
    
    return total



if __name__ == "__main__":

    sound, fs = read("prova")
    resample("noises/Noise5.wav")
    noise, fsnoise = read("noises/Noise5.wav")

    total = addNoise(sound, noise)

    write("prova_and_noise.wav", fs, total.astype(voice.dtype))
    
