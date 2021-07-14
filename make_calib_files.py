#/.venv/bin/python
import os
from scipy.io.wavfile import read, write
import numpy as np
wpathini = "phrases/harman/"

folders = []
for i in os.listdir(wpathini):
    if os.path.isdir(wpathini+i):
        folders.append(i)

treshold = 100

for folder in folders:

    wpath = wpathini + folder + "/"

    files = []
    for i in os.listdir(wpath):
        if i.split(".")[-1]=="wav":
            files.append(wpath+i)

    pdata = np.array([])
    j = 0
    print("Writing calibration file for %s... "%folder, end = '')
    while True:
        file = files[j]
        fs, data = read(file)
        # cut silence at the beginning and at the end
        for i in range(len(data)):
            if abs(data[1]) > treshold and abs(data[-1]) > treshold:
                break
            else:
                if abs(data[1]) < treshold:
                    data = data[1:]
                if abs(data[-1]) < treshold:
                    data = data[:-1]
        data = np.concatenate((pdata, data))
        # if the obtained file is longer than 30s, break the loop
        length = len(data)/fs
        if length>30: break
        pdata = data
        j+=1
        
    len(data)
    print("done!")
    write("utilities/calibration/%s.wav"%folder, fs, data.astype(np.int16))
