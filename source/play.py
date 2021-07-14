import wave

import pyaudio


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
    data = wf.readframes(chunk)
    # play stream
    while len(data) > 0:
        stream.write(data)
        data = wf.readframes(chunk)
    # stop stream
    stream.stop_stream()
    stream.close()
    # close PyAudio
    p.terminate()
    return


def play_data(data, fs, device_out_index):
    """
    Plays a data array (in the numpy format).
    """
    chunk = 1024
    # instantiate PyAudio
    p = pyaudio.PyAudio()
    # open stream 
    n_channels = data.ndim
    if data.dtype == "int16":
        d_format = 8
    elif data.dtype == "int8":
        d_format = 16
    elif data.dtype == "int24":
        d_format = 4
    elif data.dtype == "int32":
        d_format = 2
    elif data.dtype == "float32":
        d_format = 1
    else:
        print("Invatid data type!")
        return
    # convert data in a format su-itable for pyaudio
    n_data = []
    for i in range(len(data)):
        try:  # if data is stereo
            n_data.append((data[i][0]) & 0xff)
            n_data.append((data[i][0] >> 8) & 0xff)
            n_data.append((data[i][1]) & 0xff)
            n_data.append((data[i][1] >> 8) & 0xff)
        except IndexError:
            n_data.append((data[i]) & 0xff)
            n_data.append((data[i] >> 8) & 0xff)
            # open stream
    stream = p.open(format=d_format,
                    channels=n_channels,
                    rate=fs,
                    output_device_index=device_out_index,
                    output=True)
    n_data = bytes(n_data)
    chunk = chunk * 2
    n_frames = int(len(n_data) / chunk) + 1
    for i in range(int(n_frames)):
        stream.write(n_data[i * chunk:((i + 1) * chunk)])
    # stop stream
    stream.stop_stream()
    stream.close()
    # close PyAudio
    p.terminate()
    return


if __name__ == "__main__":
    audiofile = "filtered_noise.wav"
    # read from wav
    print("Playing audio from wav file")
    play_wav(audiofile)
    '''
    #read from array
    print("Playing audio from data")
    fs, data1 = read(audiofile)
    play_data(data1, fs)
    '''
