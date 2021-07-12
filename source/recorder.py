import pyaudio                          #record
from pydub.playback import play
import wave                             #write to wav
import os
import struct
import math
import time
import numpy as np
from scipy.io.wavfile import read, write

if __name__ != "__main__":
    from . play import playWav, playData

class Recorder():
    
    def __init__(self):
        self.threshold = -960
        self.chunk = 1024
        self.bits = 16
        self.channels = 1
        self.MAX_TIMEOUT = 30
        self.normalize = (1/(2**(self.bits-1)))
        self.data = []
        # not calibrated by default 
        self.calibrated = False
        self.correction = False
        
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
        self.device = p.get_default_input_device_info().get("index")
        self.channels = p.get_device_info_by_index(self.device)["maxInputChannels"]
        p.terminate()
        # get audio info
        devinfo = self.getDeviceInfo()
        # default sample rate
        self.fs = 44100
        print("\nCurrent sample rate: %d Hz"%self.fs)
        self.available_inputs = devinfo.get("inputs")
        

    def setDevice(self, index):
        if index in self.available_inputs:
            self.device = index
            self.fs = 44100
        return
    

    def getDeviceInfo(self):
        '''
        Returns a dictionary containing the information about the default input and output devices, along with all the
        available devices currently connected.

        Example:
        >>> info = getDeviceInfo()
        >>> default_device_index = info.get("default_input").get("index")
        

        '''
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
        for i in range (0,numdevices):
                if p.get_device_info_by_host_api_device_index(0,i).get('maxInputChannels')>0:
                    print("INPUT: %d - %s"%(i, p.get_device_info_by_host_api_device_index(0,i).get('name')))
                    devicesin.append(p.get_device_info_by_host_api_device_index(0,i))
                
                if p.get_device_info_by_host_api_device_index(0,i).get('maxOutputChannels')>0:
                    print("OUTPUT: %d - %s"%(i, p.get_device_info_by_host_api_device_index(0,i).get('name')))
                    devicesout.append(p.get_device_info_by_host_api_device_index(0,i))
        
        print("\n--> Selected INPUT device: %d - %s"%(self.device, devicesin[self.device].get("name")))          
        print("<-- Selected OUTPUT device: %d - %s"%(self.device, devicesout[self.device].get("name")))
        # create dictionary with default device and available devices
        audioinfo = {'inputs': devicesin,
                     'outputs': devicesout,
                     }
        # close stream
        p.terminate()
        return audioinfo


    def calculate_threshold(self):
        timerec = 10
        #instantiate stream                                               
        p = pyaudio.PyAudio() # create an interface to PortAudio API
        stream = p.open(format=self.sample_format,
                        channels=self.channels,
                        rate=self.fs,
                        frames_per_buffer=self.chunk,
                        input_device_index = self.device,
                        input=True)

        frames = [] # initialize array to store frames
        
        # The actual recording
        current = time.time()
        maxtime = time.time()+self.MAX_TIMEOUT

        # Record background noise
        input("Be quiet (press ENTER to continue...)")
        while current <= maxtime:
            try:
                data = stream.read(chunk)
                count = len(data)/2
                format = "%dh" %(count)
                shorts = struct.unpack(format, data)
                
                # get intensity
                sum_squares = 0.0
                for sample in shorts:
                    n = sample * normalize
                    sum_squares += n * n
                rms = math.pow(sum_squares / count, 0.5)
                data = round(20*math.log10(rms), 6)
                print("%.2f dBFS"%data)
                frames.append(data)
                current = time.time()
            except KeyboardInterrupt:
                print("\nRecording stopped")
                break
            
        background = 0
        for i in range(len(frames)):
            background += frames[i]
        background = background/len(frames)
        print("Background noise: %.2f dBFS"%background)
        
        # Record talk volume
        input("Now talk (press ENTER to continue)")
        current = time.time()
        maxtime = time.time()+ 3

        while current <= maxtime:
            try:
                data = stream.read(chunk)
                count = len(data)/2
                format = "%dh" %(count)
                shorts = struct.unpack(format, data)
                
                # get intensity
                sum_squares = 0.0
                for sample in shorts:
                    n = sample * normalize
                    sum_squares += n * n
                rms = math.pow(sum_squares / count, 0.5)

                data = round(20*math.log10(rms), 6)
                print("%f dBFS"%data)
                frames.append(data)
                current = time.time()
                
            except KeyboardInterrupt:
                print("\nRecording stopped")
                break
            
        maximum = -100
        for i in range(len(frames)):
            if frames[i] >= maximum:
                maximum = frames[i]
        print("Max talk volume: %f dBFS"%maximum)

        # Stop and close the stream
        stream.stop_stream()
        stream.close()
        # Terminate the portaudio interface
        p.terminate()
        self.threshold = (maximum+background)/2
        input("Threshold: %.2f dBFS\nPress ENTER to continue..."%self.threshold)

        return self.threshold


    def calibrate(self, channel, reference = 94, timerec = 10, widget = None):
        '''
        Calibrate the microphone to have a direct conversion from dBFS to dBSPL.

        This is done separately for each channel. Specify it in the function arguments.
        
        The use of a 94dBSPL (1kHz) calibrator is strongly advised. Otherwise, please
        specify another reference value.
        '''
        
        # recording time
        minutes = int((timerec/60))%60
        hours = int((timerec/3600))
        seconds = timerec - 3600*hours - 60*minutes
        
        cPathShort = os.getcwd()
        tree = cPathShort.split("\\")
        if len(cPathShort)>40:
            cDir = (tree[0]+"\\"+tree[1]+"\...\\"+tree[-2])
            cPathShort = (cDir+"\\"+tree[-1])

        # dialog
        print("Calibrating (94dBSPL):")
        print("")
        print("-------------------------------------------------------------------")
        print("-------------------------------------------------------------------")
        print("- Sample format...................%d bits"%self.bits)
        print("- Sampling frequency..............%d Hz"%self.fs)
        print("- Samples per buffer..............%d samples"%self.chunk)
        print("- Recording time (hh:mm:ss).......%02d:%02d:%02d"%(hours,minutes,seconds))
        print("- Channel:........................%d"%channel)
        print("- Working directory...............%s"%cDir)
        print("-------------------------------------------------------------------")
        print("-------------------------------------------------------------------")
        print("")
        try:
            input("Place the microphone into the calibrator and press ENTER to calibrate (CTRL+C to cancel)")
        except KeyboardInterrupt:
            print("Calibration canceled!")
            return
        #instantiate stream
        p = pyaudio.PyAudio() # create an interface to PortAudio API

        stream = p.open(format=self.sample_format,
                        channels=self.channels,
                        rate=self.fs,
                        frames_per_buffer=self.chunk,
                        input_device_index = self.device,
                        input=True)

        frames = [] # initialize array to store frames

        # The actual recording
        
        current = time.time()
        maxtime = time.time()+timerec
        while current <= maxtime:
            try:
                data = stream.read(self.chunk)
                count = len(data)/2
                format = "%dh" %(count)
                shorts = struct.unpack(format, data)
                print(shorts)
                
                # get intensity
                sum_squares = 0.0
                for sample in shorts:
                    n = sample * self.normalize
                    sum_squares += n * n
                rms = math.pow(sum_squares / count, 0.5)

                data = round(20*math.log10(rms), 6)
                print("%.2f dBFS"%data)
                frames.append(data)
                current = time.time()
            except KeyboardInterrupt:
                print("\nRecording stopped")
                break

        # Stop and close the stream 
        stream.stop_stream()
        stream.close()
        # Terminate the portaudio interface
        p.terminate()
        
        average = 0
        for i in range(len(frames)):
            average += frames[i]
        average = average/len(frames)
        self.correction = reference - average   # sets correction parameter
        print("Average intensity: %f"%average)
        print("Correction parameter: %f\n\nYou can now remove the microphone from the calibrator"%self.correction)
        input("---------------------------------------------------")
        self.calibrated = True                  # microphone calibrated
        
        return self.correction, frames          


    def playAndRecord(self, data, fs, deviceIndex = None, threshold = None):
        CHUNK = 1024
        channels = 1
        
        #instantiate stream
        p = pyaudio.PyAudio() # create an interface to PortAudio API
        stream = p.open(format=self.sample_format,
                        channels=channels,
                        rate=self.fs,
                        frames_per_buffer = self.chunk,
                        input_device_index = deviceIndex,
                        output_device_index = 4,
                        input = True,
                        output = True)
        print("Recording with device %s"%deviceIndex)
        
        nData = []
        for i in range(len(data)):
            try: # if data is stereo
                nData.append((data[i][0])&0xff)
                nData.append((data[i][0]>>8)&0xff)
                nData.append((data[i][1])&0xff)
                nData.append((data[i][1]>>8)&0xff)
            except IndexError:
                nData.append((data[i])&0xff)
                nData.append((data[i]>>8)&0xff)
                
        nData = bytes(nData)
        CHUNK = CHUNK*2
        nFrames = int(len(nData)/CHUNK)+1
        
        frames = [] # initialize array to store frames
        print("Playing")
        for i in range(int(nFrames)):
            stream.write(nData[i*CHUNK:((i+1)*CHUNK)])
            dataRec = stream.read(self.chunk)
            frames.append(dataRec)
        print("Done")

        # Stop and close the stream
        stream.stop_stream()
        stream.close()
        # Terminate the portaudio interface
        p.terminate()
        
        # write recorded data into an array
        wf = wave.open("temp.wav", 'wb')
        wf.setnchannels(channels)
        wf.setsampwidth(p.get_sample_size(self.sample_format))
        wf.setframerate(self.fs)
        wf.writeframes(b''.join(frames))
        wf.close()
        print('... done!')
        _, self.data = read("temp.wav")
        os.remove("temp.wav")
        return self.data


    def recordTreshold(self, seconds, channel = 0, deviceIndex = None, threshold = None):
        if deviceIndex == None:
            deviceIndex = self.device
        if threshold == None:
            threshold = self.threshold
        print("Threshold value: %f"%self.threshold)
        #instantiate stream
        p = pyaudio.PyAudio() # create an interface to PortAudio API
        stream = p.open(format=self.sample_format,
                        channels=self.channels,
                        rate=self.fs,
                        frames_per_buffer = self.chunk,
                        input_device_index = deviceIndex,
                        input=True)
        print("Recording with device %s"%deviceIndex)
        frames = [] # initialize array to store frames

        # The actual recording
        started = False
        print("Waiting for speech over the threshold...")
        current = time.time()
        timeout = 5
        end = time.time()+timeout
        maxtime = time.time()+seconds
        while current <= maxtime:
            try:
                data = stream.read(self.chunk)
                self.testdata = data
                count = len(data)/2
                format = "%dh" %(count)
                shorts = struct.unpack(format, data)

                shorts_array = []
                for i in range(self.channels):
                    shorts_array.append([])
                
                # get intensity
                for sample in range(len(shorts)):
                    shorts_array[sample%self.channels].append(shorts[sample])

                rms = []
                for i in range(len(shorts_array)):
                    sum_squares = 0.0
                    for sample in shorts_array[i]:
                        n = sample * self.normalize
                        sum_squares += n * n
                    rms.append(round(20*math.log10(math.pow((sum_squares/self.chunk), 0.5))+20*math.log10(2**0.5), 2))
                
                # detects sounds over the threshold
                if rms[channel] > self.threshold:
                    end = time.time()+timeout
                    if not started:
                        started = True
                        maxtime = time.time() + seconds
                        print("\nTriggered\n")
                current = time.time()

                if started:
                    if self.calibrated:
                        for i in rms:
                            print("%0.2f dBSPL\t"%(i+self.correction), end = ' ')
                        print("\n")
                    else:
                        for i in rms:
                            print("%0.2f dBFS\t"%(i), end = ' ')
                        print("\n")
                    frames.append(data)
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
        if len(frames)>0:
            wf = wave.open("temp.wav", 'wb')
            wf.setnchannels(self.channels)
            wf.setsampwidth(p.get_sample_size(self.sample_format))
            wf.setframerate(self.fs)
            wf.writeframes(b''.join(frames))
            wf.close()
            print('... done!')
            _, self.data = read("temp.wav")
            os.remove("temp.wav")
            #self.data = self.data[:,0]
            return self.data
        
        else:
            print("No audio recorded!")
            return 0


    def save(self, filename = "output.wav"):
        write(filename, self.fs, self.data)
        return


    def play(self):
        '''
        Reproduces the last recorded data.
        '''
        if len(self.data)>0:
            playData(self.data, self.fs)
        else:
            print("\nNo data to play! Record something first")
        return
    
   
def getDeviceInfo():
    '''
    Returns a dictionary containing the information about the default input and output devices, along with all the
    available devices currently connected.

    Example:
    >>> info = getDeviceInfo()
    >>> default_device_index = info.get("default_input").get("index")
    

    '''
    
    # open the stream
    p = pyaudio.PyAudio()
    # get number of connected devices
    info = p.get_host_api_info_by_index(0)
    numdevices = info.get('deviceCount')
    devicesin =     []
    devicesout =    []
    nchannels =     []
    # determine if each device is a input or output
    for i in range (0,numdevices):
            if p.get_device_info_by_host_api_device_index(0,i).get('maxInputChannels')>0:
                    print ("Input Device id ", i, " - ", p.get_device_info_by_host_api_device_index(0,i).get('name'), " - N. Channels: ", p.get_device_info_by_host_api_device_index(0,i).get('maxInputChannels'))
                    devicesin.append("INPUT: %s"%p.get_device_info_by_host_api_device_index(0,i).get('name'))
                    nchannels.append(p.get_device_info_by_host_api_device_index(0,i).get('maxInputChannels'))            
            if p.get_device_info_by_host_api_device_index(0,i).get('maxOutputChannels')>0:
                    print ("Output Device id ", i, " - ", p.get_device_info_by_host_api_device_index(0,i).get('name'), " - N. Channels: ", p.get_device_info_by_host_api_device_index(0,i).get('maxOutputChannels'))
                    devicesout.append("OUTPUT: %s"%p.get_device_info_by_host_api_device_index(0,i).get('name'))
                    nchannels.append(p.get_device_info_by_host_api_device_index(0,i).get('maxInputChannels'))
                    
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
    r = Recorder()

    r.fs, data = read("filtered_noise.wav")
    
    rec = r.playAndRecord(data, r.fs)

