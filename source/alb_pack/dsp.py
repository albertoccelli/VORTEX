#!/usr/bin/env python3
import numpy as np
from scipy import signal
from scipy.fft import rfft, rfftfreq


class SaturationError(Exception):
    pass


def bandpass(data, lc, hc, fs, order = 5):
    '''
    OLD
    nyq = fs/2
    low = lc/nyq
    b, a = signal.butter(order, low, btype = "low")
    filtered = signal.lfilter(b, a, data)
    return filtered
    '''
    pass

    
def peak(data, lc, hc, fs, order = 5):
    '''
    OLD
    nyq = fs/2
    low = lc/nyq
    b, a = signal.butter(order, low, btype = "low")
    filtered = signal.lfilter(b, a, data)
    return filtered
    '''
    
    

# 1 octave bands
octave1Freq = [31, 63, 125, 250, 500, 1000, 2000, 4000, 8000, 16000]

down1 = []

for i in range(len(octave1Freq)):
    down1.append(octave1Freq[i]/(2**(1/2)))    

up1 = []



def Scale(fftdatax, fftdatay, scale=3):
    '''
    Performs octave scaling over a FFT spectruma analysis. Currently only 1/3 octave is supported.

    Example:
    >>> scaledF, scaledY = Scale(F, Y)

    '''

    # nominal frequencies array
    octave13Freq = [16, 20, 25, 31, 40, 50, 63, 80,
                100, 125, 160, 200, 250, 315, 400, 500, 630, 800,
                1000, 1250, 1600, 2000, 2500, 3150, 4000, 5000, 6300, 8000,
                10000, 12500, 16000, 20000]
    g = []
    gx = []
    scaledSpectrum = []
    matrix = []
    matrixUp = []
    matrixDown = []

    # determine n of bands based on the FFT size
    fftsize = (len(fftdatax)-1)*2
    if fftsize == 32:
        nBands = 3
    elif fftsize == 64:
        nBands = 6
    elif fftsize == 128:
        nBands = 10
    elif fftsize == 256:
        nBands = 13
    elif fftsize == 512:
        nBands = 16
    elif fftsize == 1024:
        nBands = 19
    elif fftsize == 2048:
        nBands = 22
    elif fftsize == 4096:
        nBands = 25
    elif fftsize == 8192:
        nBands = 28
    elif fftsize == 16384:
        nBands = 31
    elif fftsize == 32768:
        nBands = 34
    elif fftsize == 65536:
        nBands = 36

    # real frequencies array
    for i in range(44-nBands-1,44):
        matrix.append(10**(0.1*i))
        matrixDown.append((10**(0.1*i))/(10**0.05))
        matrixUp.append((10**(0.1*i))*(10**0.05))
    scaledFreq = octave13Freq[-nBands-1:]

    for i in range(len(fftdatax)):
        for j in range(len(matrix)):
            b = 0          
            if fftdatax[i] < matrixUp[j] and fftdatax[i] > matrixDown[j]:
                # define weighting matrix
                gterm = 1 + (((fftdatax[i])/matrix[j]-matrix[j]/fftdatax[i])*(1.507*scale))**6
                g.append((fftdatay[i]**2/gterm))
                gx.append(fftdatax[i])
                
    for j in range(len(matrix)):
        b = 0
        for i in range(len(g)):
            if gx[i] < matrixUp[j] and gx[i] > matrixDown[j]:
                b+=g[i]
        b = np.sqrt(b)
        scaledSpectrum.append(b)
        
    return scaledFreq, scaledSpectrum


def Fft(data, fftsize = 8192, sample_rate = 44100, window = "hanning", scaling = None, weighting = None): #WORK IN PROGRESS
    '''
    Compute fast fourier transform with choosen fft size and windowing. Returns fft array
    along with frequency array. If desired, a 1/3 octave scaling could be implemented.

    Example:
    >>> X, F = Fft(x, fftsize=8192, window = "hanning", scaling = "1")

    '''
    # normalize signal
    data = data/np.iinfo(data.dtype).max
    # calculate rms power
    rms = 0
    for i in data:
        rms=rms+(i*i)
    #print(rms)
    rms = ((rms/len(data))**(0.5))*(2**0.5)
    rmsdb = (20*np.log10(rms))
    print("RMS POWER: %.3f (%.2f dBFS)"%(rms, rmsdb))
    N = len(data)
    fftsize = int(fftsize)
    #choose window
    if window == "hanning":
        w = np.hanning(fftsize)
    elif window == "bartlett":
        w = np.bartlett(fftsize)
    elif window == "blackman":
        w = np.blackman(fftsize)
    elif window == "hamming":
        w = np.hamming(fftsize)
    elif window == "bartlett":
        w = np.bartlett(fftsize)

    frames = int(N/fftsize)+1
    print("\nFFT size: %d"%fftsize)
    print("Frequency resolution: %.2fHz"%(sample_rate/fftsize))    
    print("\nLength of the audio file: %d points"%len(data))
    print("Number of frames: %d"%frames)
    print("Number of 0 points: %d\n"%((frames*fftsize)-len(data)))

    # 0 padding
    coda =[] 
    for i in range((frames*fftsize)-len(data)):
        coda.append(0)
    coda = np.array(coda)
    data = np.concatenate((data, coda))

    # compute FFT (average spectrum)
    yf = []    
    for i in range(int(N/fftsize)+1):
        yf.append(rfft(w*data[fftsize*i:fftsize*(i+1)]))
    xf = rfftfreq(fftsize, 1 / sample_rate)
    yftot = np.abs(yf[0])
    for j in range(len(yf)-1):
        yftot+=np.abs(yf[j+1])
    yftot =(yftot)/(len(yf))

    # scale y axis
    yftot = 4*yftot/fftsize
    if scaling == "13octave":
        xf, yftot = Scale(xf, yftot, 3)
    yftot = 20*np.log10(yftot)
    
    return xf, yftot


def pan(data, value):
    '''
    Regulate the amount of volume per channel.
    value range: [-100,100]

        -100 --> full left panning
        100  --> full right panning
        0    --> center panning
        
    '''
    #calculate the gain per channel
    angle = value*(45/100)
    if data.ndim == 2:
        data[:,0]=((2**0.5)/2)*(np.cos(angle)-np.sin(angle))*data[:,0]
        data[:,1]=((2**0.5)/2)*(np.cos(angle)+np.sin(angle))*data[:,1]
    return data       


def getRms(data):
    '''
    Returns RMS level of a signal (array) in dBFS. For a stereo signal, returns a 2-D array
    for RMS values for left and right channels respectively.
    
    '''
    norm = np.iinfo(data.dtype).max
    rms = 0
    for i in data:
        i = i/norm
        rms=rms+(i*i)
    rms = ((rms/len(data))**(0.5))*(2**0.5)
    rms = (20*np.log10(rms))
    return rms


def addGain(data, G):
    '''
    Adds gain (expressed in dB) to a signal.
    
    '''
    mpeak = max(abs(data))
    allowed_max = max_value = np.iinfo(data.dtype).max
    maxGain = allowed_max - mpeak
        
    if maxGain>G:
        gainLin = 10**(G/20)
        for d in range(len(data)):
            data[d] = int(data[d]*gainLin)
    else:
        raise SaturationError("Cannot add that much gain. Try to increase the amplifier volume instead!")
    return data


def monoToStereo(data):
    '''
    The function name explain it all...
    
    '''
    if data.ndim == 1:
        dataStereo = np.vstack((data,data)).T
        return dataStereo



def stereoToMono(data):
    '''
    The function name explain it all...
    
    '''
    dataMono = []
    if data.ndim == 2:
        dataMono = ((data[:,0]+data[:,1])/2).astype(data.dtype)
        return dataMono
    else:
        print("Signal is already mono.")
        return data
        

def splitChannels(data):
    '''
    Splits a stereo signal into two mono signals (left and right respectively).

    Example:
    >>> dataL, dataR = splitChannels(data)
    
    '''
    dataL = []
    dataR = []
    if len(data[0])==2: 
        dataL = data[:,0]
        dataR = data[:,1]
        return dataL, dataR
    else:
        print("Signal should be stereo.")
        return data


def cpbGraph(X, Y, bottom):
    plt.ylabel("Amplitude [dBFS]")
    plt.xlabel("Frequency [Hz]")
    plt.yticks(range(0, -bottom, int(-bottom/8)), range(bottom, 0, int(-bottom/8)))
    plt.xticks(range(len(Y)), X)
    plt.xticks(rotation = 45)
    plt.bar(range(len(Y)), -bottom+Y, align='center', width=0.9)
    plt.show()    
    


if __name__ == "__main__":

    from scipy.io.wavfile import read, write
    from matplotlib import pyplot as plt
    
    fs, noise = read("white.wav")
    x = np.arange(0, len(noise)/fs, 1/fs)
    noise_filt = bandpass(noise, 100, fs, order=5).astype(noise.dtype)
    
    F, Noise = Fft(noise_filt, fftsize=4096, sample_rate = fs)

    write("filtered_noise.wav", fs, noise)
    
    #export data into txt format
    with open("data.txt", "w") as f:
        for i in range(len(F)):
            f.write("%f\t%.10f\n"%(F[i], Noise[i]))

    minimum = -100


    
    
    #cpbGraph(F, Noise, minimum)
    plt.xscale("log")
    plt.ylim(-100, -10)
    plt.xlim(20, max(F))
    plt.plot(F, Noise)
    plt.show()
