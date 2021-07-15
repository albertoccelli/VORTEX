#!/usr/bin/env python3
import numpy as np
from scipy.fft import rfft, rfftfreq


class SaturationError(Exception):
    pass


'''
def bandpass(data, lc, hc, fs, order = 5):
    OLD
    nyq = fs/2
    low = lc/nyq
    b, a = signal.butter(order, low, btype = "low")
    filtered = signal.lfilter(b, a, data)
    return filtered
    pass

def peak(data, lc, hc, fs, order=5):
    
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
    down1.append(octave1Freq[i] / (2 ** (1 / 2)))

up1 = []


def scale(fftdatax, fftdatay, band_scale=3):
    """
    Performs octave scaling over a FFT spectruma analysis. Currently only 1/3 octave is supported.

    Example:
    >>> scaledF, scaledY = scale(fftdatax, fftdatay)

    """

    # nominal frequencies array
    octave13_freq = [16, 20, 25, 31, 40, 50, 63, 80,
                     100, 125, 160, 200, 250, 315, 400, 500, 630, 800,
                     1000, 1250, 1600, 2000, 2500, 3150, 4000, 5000, 6300, 8000,
                     10000, 12500, 16000, 20000]
    g = []
    gx = []
    scaled_spectrum = []
    matrix = []
    matrix_up = []
    matrix_down = []

    # determine n of bands based on the FFT size
    fftsize = (len(fftdatax) - 1) * 2
    if fftsize == 32:
        n_bands = 3
    elif fftsize == 64:
        n_bands = 6
    elif fftsize == 128:
        n_bands = 10
    elif fftsize == 256:
        n_bands = 13
    elif fftsize == 512:
        n_bands = 16
    elif fftsize == 1024:
        n_bands = 19
    elif fftsize == 2048:
        n_bands = 22
    elif fftsize == 4096:
        n_bands = 25
    elif fftsize == 8192:
        n_bands = 28
    elif fftsize == 16384:
        n_bands = 31
    elif fftsize == 32768:
        n_bands = 34
    elif fftsize == 65536:
        n_bands = 36
    else:
        n_bands = 25

    # real frequencies array
    for index in range(44 - n_bands - 1, 44):
        matrix.append(10 ** (0.1 * index))
        matrix_down.append((10 ** (0.1 * index)) / (10 ** 0.05))
        matrix_up.append((10 ** (0.1 * index)) * (10 ** 0.05))
    scaled_freq = octave13_freq[-n_bands - 1:]

    for index in range(len(fftdatax)):
        for j in range(len(matrix)):
            if matrix_up[j] > fftdatax[index] > matrix_down[j]:
                # define weighting matrix
                gterm = 1 + (((fftdatax[index]) / matrix[j] - matrix[j] / fftdatax[index]) * (1.507 * band_scale)) ** 6
                g.append((fftdatay[index] ** 2 / gterm))
                gx.append(fftdatax[index])

    for j in range(len(matrix)):
        b = 0
        for index in range(len(g)):
            if matrix_up[j] > gx[index] > matrix_down[j]:
                b += g[index]
        b = np.sqrt(b)
        scaled_spectrum.append(b)

    return scaled_freq, scaled_spectrum


def fft(data, fftsize=8192, sample_rate=44100, window="hanning", scaling=None):  # WORK IN PROGRESS
    """
    Compute fast fourier transform with choosen fft size and windowing. Returns fft array
    along with frequency array. If desired, a 1/3 octave scaling could be implemented.

    Example:
    >>> X, F = fft(x, fftsize=8192, window = "hanning", scaling = "1")

    """
    # normalize signal
    data = data / np.iinfo(data.dtype).max
    # calculate rms power
    rms = 0
    for d in data:
        rms = rms + (d * d)
    # print(rms)
    rms = ((rms / len(data)) ** 0.5) * (2 ** 0.5)
    rmsdb = (20 * np.log10(rms))
    print("RMS POWER: %.3f (%.2f dBFS)" % (rms, rmsdb))
    n = len(data)
    fftsize = int(fftsize)
    # choose window
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
    else:
        print("Invalid window type!")
        return

    frames = int(n / fftsize) + 1
    print("\nFFT size: %d" % fftsize)
    print("Frequency resolution: %.2fHz" % (sample_rate / fftsize))
    print("\nLength of the audio file: %d points" % len(data))
    print("Number of frames: %d" % frames)
    print("Number of 0 points: %d\n" % ((frames * fftsize) - len(data)))

    # 0 padding
    coda = []
    for d in range((frames * fftsize) - len(data)):
        coda.append(0)
    coda = np.array(coda)
    data = np.concatenate((data, coda))

    # compute FFT (average spectrum)
    yf = []
    for d in range(int(n / fftsize) + 1):
        yf.append(rfft(w * data[fftsize * d:fftsize * (d + 1)]))
    xf = rfftfreq(fftsize, 1 / sample_rate)
    yftot = np.abs(yf[0])
    for j in range(len(yf) - 1):
        yftot += np.abs(yf[j + 1])
    yftot = yftot / (len(yf))

    # scale y axis
    yftot = 4 * yftot / fftsize
    if scaling == "13octave":
        xf, yftot = scale(xf, yftot, 3)
    yftot = 20 * np.log10(yftot)

    return xf, yftot


def pan(data, value):
    """
    Regulate the amount of volume per channel.
    value range: [-100,100]

        -100 --> full left panning
        100  --> full right panning
        0    --> center panning

    """
    # calculate the gain per channel
    angle = value * (45 / 100)
    if data.ndim == 2:
        data[:, 0] = ((2 ** 0.5) / 2) * (np.cos(angle) - np.sin(angle)) * data[:, 0]
        data[:, 1] = ((2 ** 0.5) / 2) * (np.cos(angle) + np.sin(angle)) * data[:, 1]
    return data


def get_rms(data):
    """
    Returns RMS level of a signal (array) in dBFS. For a stereo signal, returns a 2-D array
    for RMS values for left and right channels respectively.

    """
    norm = np.iinfo(data.dtype).max
    rms = 0
    for d in data:
        d = d / norm
        rms = rms + (d * d)
    rms = ((rms / len(data)) ** 0.5) * (2 ** 0.5)
    rms = (20 * np.log10(rms))
    return rms


def add_gain(data, gain):
    """
    Adds gain (expressed in dB) to a signal.

    """
    mpeak = max(abs(data))
    max_gain = -(20 * np.log10(mpeak / np.iinfo(data.dtype).max))
    print("Peak: %0.2fdBFS" % -max_gain)

    if max_gain > gain:
        gain_lin = 10 ** (gain / 20)
        for d in range(len(data)):
            data[d] = int(data[d] * gain_lin)
    else:
        raise SaturationError("Cannot add that much gain. Try to increase the amplifier volume instead!")
    return data


def mono_to_stereo(data):
    """
    The function name explain it all...

    """
    if data.ndim == 1:
        data_stereo = np.vstack((data, data)).T
        return data_stereo


def stereo_to_mono(data):
    """
    The function name explain it all...

    """
    if data.ndim == 2:
        data_mono = ((data[:, 0] + data[:, 1]) / 2).astype(data.dtype)
        return data_mono
    else:
        print("Signal is already mono.")
        return data


def split_channels(data):
    """
    Splits a stereo signal into two mono signals (left and right respectively).

    Example:
    >>> data_left, data_right = split_channels(data)

    """
    if len(data[0]) == 2:
        data_l = data[:, 0]
        data_r = data[:, 1]
        return data_l, data_r
    else:
        print("Signal should be stereo.")
        return data


def cpb_graph(x_axis, y_axis, bottom):
    plt.ylabel("Amplitude [dBFS]")
    plt.xlabel("Frequency [Hz]")
    plt.yticks(range(0, -bottom, int(-bottom / 8)), range(bottom, 0, int(-bottom / 8)))
    plt.xticks(range(len(y_axis)), x_axis)
    plt.xticks(rotation=45)
    plt.bar(range(len(y_axis)), -bottom + y_axis, align='center', width=0.9)
    plt.show()


if __name__ == "__main__":
    from scipy.io.wavfile import read
    from matplotlib import pyplot as plt

    fs, noise = read("white.wav")
    x = np.arange(0, len(noise) / fs, 1 / fs)
