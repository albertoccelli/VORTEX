import math
import os
import struct
import threading
import time
import wave  # write to wav

import numpy as np
import pyaudio  # record
from scipy.io.wavfile import read, write

if __name__ != "__main__":
    from .cli_tools import print_square

if __name__ != "__main__":
    from .dsp import get_rms


def clear_console():
    command = 'clear'
    if os.name in ('nt', 'dos'):  # If Machine is running on Windows, use cls
        command = 'cls'
    os.system(command)


class RecordingInterrupt(Exception):
    pass


class Recorder:
    def __init__(self):
        self.timeout = 5
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
        self.devicesIn = []
        self.devicesOut = []
        self.channelsIn = p.get_device_info_by_index(self.deviceIn)["maxInputChannels"]
        self.channelsOut = p.get_device_info_by_index(self.deviceIn)["maxInputChannels"]
        self.channels = min(self.channelsOut, self.channelsIn)
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
        self.lowtreshold = -960
        self.hightreshold = 0
        self.soglia = 0
        self.rms = -960
        self._running = False
        self._is_saved = False

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
        >>> recorder = Recorder()
        >>> information = recorder.get_device_info()
        >>> default_device_index = info.get("default_input").get("index")
        """
        # stored data into the recorder
        self.devicesIn = []
        self.devicesOut = []

        self.data = []
        # open the stream
        p = pyaudio.PyAudio()
        # get number of connected devices
        info = p.get_host_api_info_by_index(0)
        numdevices = info.get('deviceCount')
        # determine if each device is a input or output
        for i in range(0, numdevices):
            if p.get_device_info_by_host_api_device_index(0, i).get('maxInputChannels') > 0:
                print("INPUT: %d - %s - %d "
                      "channel(s)" % (i,
                                      p.get_device_info_by_host_api_device_index(0, i).get('name'),
                                      p.get_device_info_by_host_api_device_index(0, i).get('maxInputChannels')))
                self.devicesIn.append(p.get_device_info_by_host_api_device_index(0, i))

            if p.get_device_info_by_host_api_device_index(0, i).get('maxOutputChannels') > 0:
                print("OUTPUT: %d - %s - %d "
                      "channel(s)" % (i,
                                      p.get_device_info_by_host_api_device_index(0, i).get('name'),
                                      p.get_device_info_by_host_api_device_index(0, i).get('maxOutputChannels')))
                self.devicesOut.append(p.get_device_info_by_host_api_device_index(0, i))

        print("\n--> Selected INPUT device: %d - %s" % (self.deviceIn, self.devicesIn[self.deviceIn].get("name")))
        print("<-- Selected OUTPUT device: %d - %s" % (self.deviceOut, self.devicesOut[self.deviceIn].get("name")))
        # create dictionary with default device and available devices
        audioinfo = {'inputs': self.devicesIn,
                     'outputs': self.devicesOut,
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
        print("Calibrating (%0.1fdBSPL):" % reference)
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
            print("Place the microphone into the calibrator and press ENTER to calibrate (CTRL+C to cancel)")
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
        print("\nCalibrating... ", end='')
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
                # print("\nRecording stopped")
                break
        rms_global = round(
            20 * math.log10(math.pow((sum_squares_global / self.chunk), 0.5)) + 20 * math.log10(2 ** 0.5), 2)

        # Stop and close the stream 
        stream.stop_stream()
        stream.close()
        # Terminate the portaudio interface
        p.terminate()

        wf = wave.open('temp.wav', 'wb')
        wf.setnchannels(self.channels)
        wf.setsampwidth(p.get_sample_size(self.sample_format))
        wf.setframerate(self.fs)
        wf.writeframes(b''.join(frames))
        wf.close()
        print('done!\n')
        _, audio_data = read('temp.wav')
        os.remove('temp.wav')
        audio_data = audio_data[:, channel]
        self.calibrated[channel] = True  # microphone calibrated
        self.correction[channel] = reference - get_rms(audio_data)  # correction factor
        print_square("Power      = %0.2fdBFS\n"
                     "dBSPL/dBFS = %0.2f" % (get_rms(audio_data), self.correction[channel]),
                     margin=[4, 4, 1, 1])
        return audio_data

    def play_and_record(self, audio_data, audio_fs):
        """
        Record while playing 
        """
        sem = threading.Semaphore()

        def _play_wav_semaphore(file):
            """
            Plays a wav file.
            """
            chunk = 1024
            wf = wave.open(file, 'rb')
            # instantiate PyAudio
            p = pyaudio.PyAudio()
            # open stream
            stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                            channels=wf.getnchannels(),
                            rate=wf.getframerate(),
                            output=True)
            # read data
            file_data = wf.readframes(chunk)
            # play stream
            acquiring = False
            print("\nPlaying...\n")
            while len(file_data) > 0:
                stream.write(file_data)
                if not acquiring:
                    # print("About to acquire")
                    sem.release()
                    # print("acquired")
                    acquiring = True
                file_data = wf.readframes(chunk)
            # stop stream
            stream.stop_stream()
            stream.close()
            # close PyAudio
            p.terminate()
            return

        def _record_semaphore(secs, channel=0):
            # print("Record before")
            sem.acquire()
            # print("Record after")
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
            started = False
            # print("Waiting for speech over the threshold...")
            current = time.time()
            timeout = 5
            end = time.time() + timeout
            maxtime = time.time() + secs
            while current <= maxtime:
                try:
                    rec_data = stream.read(self.chunk)
                    count = len(rec_data) / 2
                    data_format = "%dh" % count
                    shorts = struct.unpack(data_format, rec_data)

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
                            round(
                                20 * math.log10(math.pow((sum_squares / self.chunk), 0.5)) + 20 * math.log10(2 ** 0.5),
                                2))

                    # detects sounds over the threshold
                    if rms[channel] > self.threshold:
                        end = time.time() + timeout
                        if not started:
                            started = True
                            maxtime = time.time() + secs
                            print("Recording...\n")
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
                        frames.append(rec_data)
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
                wf = wave.open(".temp_out.wav", 'wb')
                wf.setnchannels(self.channels)
                wf.setsampwidth(p.get_sample_size(self.sample_format))
                wf.setframerate(self.fs)
                wf.writeframes(b''.join(frames))
                wf.close()
                print('... done!')
                _, self.data = read(".temp_out.wav")
                os.remove(".temp_out.wav")
                # self.data = self.data[]
                return self.data

            else:
                print("No audio recorded!")
                return 0

        write(".temp.wav", audio_fs, audio_data)
        seconds = len(audio_data) / audio_fs
        sem.acquire()
        play = threading.Thread(target=_play_wav_semaphore, args=(".temp.wav",))
        rec = threading.Thread(target=_record_semaphore, args=(seconds,))
        play.start()
        rec.start()
        play.join()
        rec.join()
        os.remove(".temp.wav")
        return self.data

    def save(self, filename="output.wav"):
        write(filename, self.fs, np.array(self.data))
        return

    def play(self):
        """
        Reproduces the last recorded data.
        """
        if len(self.data) > 0:
            play_data(self.data, self.fs)
        else:
            print("\nNo data to play! Record something first")
        return

    def record(self, seconds=None, channel=0, l_threshold=None, h_treshold=None, monitor=False):
        p_pow = -960
        if l_threshold is None and h_treshold is None:
            l_threshold = -960
            h_treshold = -960
            pass
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
        started = False
        # print("Waiting for speech over the threshold...")
        current = time.time()
        timeout = self.timeout
        end = time.time() + timeout
        if seconds is None:
            seconds = 10000
        maxtime = time.time() + seconds
        self._running = True
        self._is_saved = False
        while current <= maxtime and self._running:
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
                if rms[channel] > l_threshold:
                    end = time.time() + timeout
                    if not started:
                        started = True
                        maxtime = time.time() + seconds
                        print("\nRecording...")
                current = time.time()

                if started:
                    for i in range(len(rms)):
                        if monitor:
                            if self.calibrated[i]:
                                pass
                                # print("%0.2f dBSPL - %s\t"%(rms[i]+self.correction[i], soglia))
                            else:
                                pass
                                # print("%0.2f dBFS - %s\t"%(rms[i], soglia))
                    rms_tot = rms[channel]
                    self.rms = rms_tot
                    if monitor:
                        print(rms[channel])
                    if rms_tot > self.hightreshold and p_pow < self.hightreshold:
                        self.on_positive_edge()
                    elif rms_tot < self.lowtreshold and p_pow > self.lowtreshold:
                        self.on_negative_edge()
                    p_pow = rms_tot
                    # print("\n")
                    frames.append(audio_data)
                if current >= end:
                    self.on_timeout()


            except KeyboardInterrupt:
                print("\nRecording stopped")
                break

        print("RECORD ENDED")
        # Stop and close the stream
        stream.stop_stream()
        stream.close()
        # Terminate the portaudio interface
        p.terminate()

        # write recorded data into an array
        print("SAVING INTO RECORDER DATA")
        print(len(frames))
        if len(frames) > 0:
            wf = wave.open(".temp.wav", 'wb')
            wf.setnchannels(self.channels)
            wf.setsampwidth(p.get_sample_size(self.sample_format))
            wf.setframerate(self.fs)
            wf.writeframes(b''.join(frames))
            wf.close()
            print('...done!')
            _, self.data = read(".temp.wav")
            os.remove(".temp.wav")
            # self.data = self.data[:,0]
            self._is_saved = True
            return self.data

        else:
            print("No audio recorded!")
            return 0

    def on_timeout(self):
        print("TIMEOUT")
        pass

    def on_positive_edge(self):
        pass

    def on_negative_edge(self):
        pass

    def terminate(self):
        self._running = False
        print("Saving...")
        while not self._is_saved:
            pass
        print("Done!")


if __name__ == "__main__":
    from play import play_data
    from dsp import get_rms
    from cli_tools import print_square

    r = Recorder()
    r.timeout = 5
    r.record(30, l_threshold=-30, monitor=True)
    r.save("PROVA.wav")
