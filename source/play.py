import wave

import pyaudio
from scipy.io.wavfile import read, write
import os


def play_wav(filename):
    """
    Plays a wav file.
    """
    chunk = 1024
    wf = wave.open(filename, 'rb')
    # instantiate PyAudio
    p = pyaudio.PyAudio()
    # open stream
    stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                    channels=wf.getnchannels(),
                    rate=wf.getframerate(),
                    output=True)
    # read data
    wav_data = wf.readframes(chunk)
    # play stream
    print("Playing...")
    while len(wav_data) > 0:
        stream.write(wav_data)
        wav_data = wf.readframes(chunk)
    # stop stream
    stream.stop_stream()
    stream.close()
    # close PyAudio
    p.terminate()
    print("Stop!")
    return


def play_data(audio_data, audio_fs):
    """
    Plays a data array (in the numpy format).
    """
    # write to temporary wave file and reproduce it
    write("temp.wav", audio_fs, audio_data)
    play_wav("temp.wav")
    os.remove("temp.wav")
    return


if __name__ == "__main__":
    import time

    audiofile = "../utilities/calibration/FRF.wav"
    # read from wav
    print("Playing audio from wav file")
    time1 = time.time()
    fs, data = read(audiofile)
    # play_wav(audiofile)
    play_data(data, fs)
    time2 = time.time() - len(data) / fs
    print("Deltat = %0.2f" % (time2 - time1))
    '''
    #read from array
    print("Playing audio from data")
    fs, data1 = read(audiofile)
    play_data(data1, fs)
    '''
