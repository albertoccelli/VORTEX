import pyaudio  # record
import wave  # write to wav
import os
import struct
import math
import time
import numpy as np
from scipy.io.wavfile import read, write
import threading
from time import sleep

if __name__ != "__main__":
    from .play import playWav, playData
    from .alb_pack.dsp import getRms


def clear_console():
    command = 'clear'
    if os.name in ('nt', 'dos'):  # If Machine is running on Windows, use cls
        command = 'cls'
    os.system(command)


class Recorder:
    def __init__(self):
        self.threshold = -960
        self.chunk = 1024
        self.bits = 16
        self.channels = 1
        self.MAX_TIMEOUT = 30
        self.normalize = (1 / (2 ** (self.bits - 1)))
        self.data = []
        # check the proper sample format
        while True:
            if self.bits == 8:
                self.sample_format = pyaudio.paInt8
                break
            elif self.bits == 16:
                self.sample_format = pyaudio.paInt16
                break
            elif self.bits == 24:
                self.sample_format = pyaudio.paInt24
                break
            elif self.bits == 32:
                self.sample_format = pyaudio.paInt32
                break
            else:
                self.bits = int(input("Please select a valid sample format (8, 16, 24 or 32)"))
        # default device
        p = pyaudio.PyAudio()
        self.deviceIn = p.get_default_input_device_info().get("index")
        self.deviceOut = p.get_default_output_device_info().get("index")
        self.channels = p.get_device_info_by_index(self.deviceIn)["maxInputChannels"]
        p.terminate()
        # not calibrated by default 
        self.calibrated = []
        self.correction = []
        for i in range(self.channels):
            self.correction.append([])
            self.calibrated.append(False)

        # get audio info
        devinfo = self.get_device_info()
        # default sample rate
        self.fs = 44100
        self.available_inputs = devinfo.get("inputs")
        self.available_outputs = devinfo.get("outputs")

    def set_device(self, io, index):
        if io == "input":
            if index in self.available_inputs:
                self.deviceIn = index
        elif io == "output":
            if index in self.available_inputs:
                self.deviceOut = index
        return

    def get_device_info(self):
        """
        Returns a dictionary containing the information about the default input and output devices, along with all the
        available devices currently connected.

        Example:
        >>> information = get_device_info()
        >>> default_device_index = info.get("default_input").get("index")
        """
        # stored data into the recorder
        self.data = []
        # open the stream
        p = pyaudio.PyAudio()
        # get number of connected devices
        info = p.get_host_api_info_by_index(0)
        numdevices = info.get('deviceCount')
        devicesin = []
        devicesout = []
        # determine if each device is a input or output
        for i in range(0, numdevices):
            if p.get_device_info_by_host_api_device_index(0, i).get('maxInputChannels') > 0:
                print("INPUT: %d - %s" % (i, p.get_device_info_by_host_api_device_index(0, i).get('name')))
                devicesin.append(p.get_device_info_by_host_api_device_index(0, i))

            if p.get_device_info_by_host_api_device_index(0, i).get('maxOutputChannels') > 0:
                print("OUTPUT: %d - %s" % (i, p.get_device_info_by_host_api_device_index(0, i).get('name')))
                devicesout.append(p.get_device_info_by_host_api_device_index(0, i))

        print("\n--> Selected INPUT device: %d - %s" % (self.deviceIn, devicesin[self.deviceIn].get("name")))
        print("<-- Selected OUTPUT device: %d - %s" % (self.deviceOut, devicesout[self.deviceIn].get("name")))
        # create dictionary with default device and available devices
        audioinfo = {'inputs': devicesin,
                     'outputs': devicesout,
                     }
        # close stream
        p.terminate()
        return audioinfo

    def calibrate(self, channel, reference=94, timerec=10):
        """
        Calibrate the microphone to have a direct conversion from dBFS to dBSPL.

        This is done separately for each channel. Specify it in the function arguments.

        The use of a 94dBSPL (1kHz) calibrator is strongly advised. Otherwise, please
        specify another reference value.
        """

        # recording time
        minutes = int((timerec / 60)) % 60
        hours = int((timerec / 3600))
        seconds = timerec - 3600 * hours - 60 * minutes

        c_path_short = os.getcwd()
        tree = c_path_short.split("\\")
        if len(c_path_short) > 40:
            c_dir = (tree[0] + "\\" + tree[1] + "\\...\\" + tree[-2])
        else:
            c_dir = c_path_short

        # dialog
        clear_console()
        print("Calibrating (94dBSPL):")
        print("")
        print("-------------------------------------------------------------------")
        print("-------------------------------------------------------------------")
        print("- Sample format...................%d bits" % self.bits)
        print("- Sampling frequency..............%d Hz" % self.fs)
        print("- Samples per buffer..............%d samples" % self.chunk)
        print("- Recording time (hh:mm:ss).......%02d:%02d:%02d" % (hours, minutes, seconds))
        print("- Channel:........................%d" % channel)
        print("- Working directory...............%s" % c_dir)
        print("-------------------------------------------------------------------")
        print("-------------------------------------------------------------------")
        print("")
        try:
            input("Place the microphone into the calibrator and press ENTER to calibrate (CTRL+C to cancel)")
        except KeyboardInterrupt:
            print("Calibration canceled!")
            return
        # instantiate stream
        p = pyaudio.PyAudio()  # create an interface to PortAudio API

        stream = p.open(format=self.sample_format,
                        channels=self.channels,
                        rate=self.fs,
                        frames_per_buffer=self.chunk,
                        input_device_index=self.deviceIn,
                        input=True)
        frames = []  # initialize array to store frames

        # The actual recording
        current = time.time()
        maxtime = time.time() + timerec
        sum_squares_global = 0.0
        print("\nCalibrating...")
        while current <= maxtime:
            try:
                audio_data = stream.read(self.chunk)
                count = len(audio_data) / 2
                data_format = "%dh" % count
                shorts = struct.unpack(data_format, audio_data)

                shorts_array = []
                for i in range(self.channels):
                    shorts_array.append([])

                # get intensity
                for sample in range(len(shorts)):
                    shorts_array[sample % self.channels].append(shorts[sample])

                rms = []
                for i in range(len(shorts_array)):
                    sum_squares = 0.0
                    for sample in shorts_array[i]:
                        n = sample * self.normalize
                        sum_squares += n * n
                        if i == channel:
                            sum_squares_global = sum_squares
                    rms.append(
                        round(20 * math.log10(math.pow((sum_squares / self.chunk), 0.5)) + 20 * math.log10(2 ** 0.5),
                              2))
                frames.append(audio_data)
                current = time.time()
            except KeyboardInterrupt:
                print("\nRecording stopped")
                break
        rms_global = round(
            20 * math.log10(math.pow((sum_squares_global / self.chunk), 0.5)) + 20 * math.log10(2 ** 0.5), 2)

        # Stop and close the stream 
        stream.stop_stream()
        stream.close()
        # Terminate the portaudio interface
        p.terminate()

        wf = wave.open("temp.wav", 'wb')
        wf.setnchannels(self.channels)
        wf.setsampwidth(p.get_sample_size(self.sample_format))
        wf.setframerate(self.fs)
        wf.writeframes(b''.join(frames))
        wf.close()
        print('... done!')
        _, audio_data = read("temp.wav")
        os.remove("temp.wav")
        audio_data = audio_data[:, channel]
        self.calibrated[channel] = True  # microphone calibrated
        self.correction[channel] = reference - getRms(audio_data)  # correction factor
        print("Power = %sdBFS\ndBSPL/dBFS = %0.2f" % (rms_global, self.correction[channel]))
        return audio_data

    def play_and_record(self, filename):
        """
        Record while playing 
        """
        fs, filedata = read(filename)
        seconds = len(filedata)/fs
        play = threading.Thread(target=playWav, args = (filename,))
        play.start()
        sleep(0.2)
        self.record(seconds)
        return self.data

    def record(self, seconds, channel=0, device_index=None, threshold=None):
        clear_console()
        if device_index is None:
            device_index = self.deviceIn
        if threshold is None:
            threshold = self.threshold
        print("Threshold value: %f" % threshold)
        # instantiate stream
        p = pyaudio.PyAudio()  # create an interface to PortAudio API
        stream = p.open(format=self.sample_format,
                        channels=self.channels,
                        rate=self.fs,
                        frames_per_buffer=self.chunk,
                        input_device_index=self.deviceIn,
                        input=True)
        print("Recording with device %s" % self.deviceIn)
        frames = []  # initialize array to store frames

        # The actual recording
        started = False
        # print("Waiting for speech over the threshold...")
        current = time.time()
        timeout = 5
        end = time.time() + timeout
        maxtime = time.time() + seconds
        while current <= maxtime:
            try:
                audio_data = stream.read(self.chunk)
                count = len(audio_data) / 2
                data_format = "%dh" % count
                shorts = struct.unpack(data_format, audio_data)

                shorts_array = []
                for i in range(self.channels):
                    shorts_array.append([])

                # get intensity
                for sample in range(len(shorts)):
                    shorts_array[sample % self.channels].append(shorts[sample])

                rms = []
                for i in range(len(shorts_array)):
                    sum_squares = 0.0
                    for sample in shorts_array[i]:
                        n = sample * self.normalize
                        sum_squares += n * n
                    rms.append(
                        round(20 * math.log10(math.pow((sum_squares / self.chunk), 0.5)) + 20 * math.log10(2 ** 0.5),
                              2))

                # detects sounds over the threshold
                if rms[channel] > self.threshold:
                    end = time.time() + timeout
                    if not started:
                        started = True
                        maxtime = time.time() + seconds
                        print("\nRecording...\n")
                current = time.time()

                if started:
                    for i in range(len(rms)):
                        if self.calibrated[i]:
                            pass
                            # print("%0.2f dBSPL\t"%(rms[i]+self.correction[i]), end = ' ')
                        else:
                            pass
                            # print("%0.2f dBFS\t"%(rms[i]), end = ' ')
                    # print("\n")
                    frames.append(audio_data)
                if current >= end:
                    print("Silence TIMEOUT")
                    break

            except KeyboardInterrupt:
                print("\nRecording stopped")
                break

        # Stop and close the stream
        stream.stop_stream()
        stream.close()
        # Terminate the portaudio interface
        p.terminate()

        # write recorded data into an array
        if len(frames) > 0:
            wf = wave.open("temp.wav", 'wb')
            wf.setnchannels(self.channels)
            wf.setsampwidth(p.get_sample_size(self.sample_format))
            wf.setframerate(self.fs)
            wf.writeframes(b''.join(frames))
            wf.close()
            print('... done!')
            _, self.data = read("temp.wav")
            os.remove("temp.wav")
            # self.data = self.data[:,0]
            return self.data

        else:
            print("No audio recorded!")
            return 0

    def save(self, filename="output.wav"):
        write(filename, self.fs, np.array(self.data))
        return

    def play(self):
        """
        Reproduces the last recorded data.
        """
        if len(self.data) > 0:
            playData(self.data, self.fs, )
        else:
            print("\nNo data to play! Record something first")
        return


def get_device_info():
    """
    Returns a dictionary containing the information about the default input and output devices, along with all the
    available devices currently connected.

    Example:
    >>> information = get_device_info()
    >>> default_device_index = info.get("default_input").get("index")


    """

    # open the stream
    p = pyaudio.PyAudio()
    # get number of connected devices
    info = p.get_host_api_info_by_index(0)
    numdevices = info.get('deviceCount')
    devicesin = []
    devicesout = []
    nchannels = []
    # determine if each device is a input or output
    for i in range(0, numdevices):
        if p.get_device_info_by_host_api_device_index(0, i).get('maxInputChannels') > 0:
            print("Input Device id ", i, " - ", p.get_device_info_by_host_api_device_index(0, i).get('name'),
                  " - N. Channels: ", p.get_device_info_by_host_api_device_index(0, i).get('maxInputChannels'))
            devicesin.append("INPUT: %s" % p.get_device_info_by_host_api_device_index(0, i).get('name'))
            nchannels.append(p.get_device_info_by_host_api_device_index(0, i).get('maxInputChannels'))
        if p.get_device_info_by_host_api_device_index(0, i).get('maxOutputChannels') > 0:
            print("Output Device id ", i, " - ", p.get_device_info_by_host_api_device_index(0, i).get('name'),
                  " - N. Channels: ", p.get_device_info_by_host_api_device_index(0, i).get('maxOutputChannels'))
            devicesout.append("OUTPUT: %s" % p.get_device_info_by_host_api_device_index(0, i).get('name'))
            nchannels.append(p.get_device_info_by_host_api_device_index(0, i).get('maxInputChannels'))

    # create dictionary with default device and available devices
    audioinfo = {'default_input': p.get_default_input_device_info(),
                 'default_output': p.get_default_output_device_info(),
                 'inputs': devicesin,
                 'outputs': devicesout,
                 }
    # close stream
    p.terminate()

    return audioinfo


if __name__ == "__main__":
    from play import playWav, playData
    from alb_pack.dsp import getRms

    r = Recorder()

    r.fs, data = read("test.wav")
    playData(data, r.fs, 5)
    # rec = r.playAndRecord(data, r.fs)
    # d = r.calibrate(1)
