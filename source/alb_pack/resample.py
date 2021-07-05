import numpy as np
from scipy.io import wavfile
from scipy import interpolate



def resample(data_in, old_samplerate, new_samplerate):
    data_out = []
    if old_samplerate != NEW_SAMPLERATE:
        duration = data_in.shape[0] / old_samplerate

        time_old  = np.linspace(0, duration, data_in.shape[0])
        time_new  = np.linspace(0, duration, int(data_in.shape[0] * new_samplerate / old_samplerate))

        interpolator = interpolate.interp1d(time_old, data_in.T)
        data_out = interpolator(time_new).T
    
    return data_out


if __name__ == "__main__":

    NEW_SAMPLERATE = 44100

    fs, old_audio = wavfile.read("../prova.wav")
    new_audio = resampled_audio = resample(old_audio, fs, NEW_SAMPLERATE)
    
    wavfile.write("prova_resampled.wav", NEW_SAMPLERATE, np.round(new_audio).astype(old_audio.dtype))
