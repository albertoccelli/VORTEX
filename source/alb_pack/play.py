"""PyAudio Example: Play a wave file."""

import pyaudio
import wave
import sys
from scipy.io.wavfile import read, write
from matplotlib import pyplot as plt

def playWav(filename):
    '''
    Plays a wav file.
    '''
    CHUNK = 1024
    wf = wave.open(filename, 'rb')

    # instantiate PyAudio (1)
    p = pyaudio.PyAudio()

    # open stream (2)
    stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                    channels=wf.getnchannels(),
                    rate=wf.getframerate(),
                    output=True)

    # read data
    data = wf.readframes(CHUNK)
    
    # play stream (3)
    while len(data) > 0:
        stream.write(data)
        data = wf.readframes(CHUNK)

    # stop stream (4)
    stream.stop_stream()
    stream.close()

    # close PyAudio (5)
    p.terminate()
    return


def playData(data, fs):
    '''
    Plays a data array (in the numpy format).
    '''
    
    CHUNK = 1024
    # instantiate PyAudio (1)
    p = pyaudio.PyAudio()

    # open stream (2)
    nChannels = data.ndim
    
    if data.dtype == "int16":
        dFormat = 8
    elif data.dtype == "int8":
        dFormat = 16
    elif data.dtype == "int24":
        dFormat = 4
    elif data.dtype == "int32":
        dFormat = 2
    elif data.dtype == "float32":
        dFormat = 1

    #convert data in a format suitable for pyaudio
    nData = []
    for i in range(len(data)):
        try:
            nData.append((data[i][0])&0xff)
            nData.append((data[i][0]>>8)&0xff)
            nData.append((data[i][1])&0xff)
            nData.append((data[i][1]>>8)&0xff)
        except IndexError:
            nData.append((data[i])&0xff)
            nData.append((data[i]>>8)&0xff)            
        
    stream = p.open(format = dFormat,
                    channels=nChannels,
                    rate=fs,
                    output=True)
    
    nData = bytes(nData)
    CHUNK = CHUNK*2
    nFrames = int(len(nData)/CHUNK)+1
    
    for i in range(int(nFrames)):
        stream.write(nData[i*CHUNK:((i+1)*CHUNK)])

    # stop stream (4)
    stream.stop_stream()
    stream.close()
    # close PyAudio (5)
    p.terminate()
    return 

if __name__=="__main__":


    audiofile = "test_sounds/pink.wav"
    #read from wav
    print("Playing audio from wav file")
    playWav(audiofile)
    '''
    #read from array
    print("Playing audio from data")
    fs, data1 = read(audiofile)
    playData(data1, fs)
    '''
