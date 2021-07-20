import pyaudio                          #record
import wave                             #write to wav
import os
import struct
import math
import time
from scipy.io.wavfile import read, write

class Recorder():
    
    def __init__(self):
        self.threshold = -96
        self.chunk = 1024
        self.bits = 16
        self.channels = 2
        self.MAX_TIMEOUT = 30
        self.normalize = (1/(2**(self.bits-1)))
        
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
        p.terminate()
        # get audio info
        devinfo = self.getDeviceInfo()
        # default sample rate
        self.fs = 44100
        print("Current sample rate: %d"%self.fs)
        self.available_inputs = devinfo.get("inputs")
        # not calibrated by default 
        self.calibration = False
        self.correction = False
        

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
        >>> info = get_device_info()
        >>> default_device_index = info.get("default_input").get("index")
        

        '''
        
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
        print("\n<-- Selected OUTPUT device: %d - %s"%(self.device, devicesout[self.device].get("name")))
        # create dictionary with default device and available devices
        audioinfo = {'inputs': devicesin,
                     'outputs': devicesout,
                     }
        # close stream
        p.terminate()

        return audioinfo

    '''
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
        input("Be quiet (press ENTER to continue)")
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
    '''
        
    def calibrate(self, reference = 94, timerec = 10, widget = None):
        '''
        Calibrate the microphone to have a direct conversion from dBFS to dBSPL.
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
        print("- Working directory...............%s"%cDir)
        print("-------------------------------------------------------------------")
        print("-------------------------------------------------------------------")
        print("")
        input("Place the microphone into the calibrator and press ENTER to calibrate")

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
        while current <= maxtime:
            try:
                data = stream.read(self.chunk)
                count = len(data)/2
                format = "%dh" %(count)
                shorts = struct.unpack(format, data)
                
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
        self.correction = reference - average
        print("Average intensity: %f"%average)
        print("Correction parameter: %f\n\nYou can now remove the microphone from the calibrator"%self.correction)
        input("---------------------------------------------------")
        self.calibration = True
        
        return self.correction, frames

    
    def record(self, seconds, filename = "temp.wav", threshold = None):
        if threshold == None:
            pass
        # recording time
        minutes = int((seconds/60))%60
        hours = int((seconds/3600))
        seconds = seconds - 3600*hours - 60*minutes
        cPath = os.getcwd()
        cPathShort = cPath +"\\"+filename
        tree = cPathShort.split("\\")
        if len(cPath)>40:
            cDir = (tree[0]+"\\"+tree[1]+"\...\\"+tree[-2])
            cPathShort = (cDir+"\\"+tree[-1])

        #instantiate stream
        p = pyaudio.PyAudio() # create an interface to PortAudio API
        stream = p.open(format=self.sample_format,
                        channels=self.channels,
                        rate=self.fs,
                        frames_per_buffer = self.chunk,
                        input_device_index = self.device,
                        input=True)

        frames = [] # initialize array to store frames

        # The actual recording
        
        started = False
        print("Waiting for speech over the threshold...")
        current = time.time()
        timeout = 5
        MAX_TIMEOUT = 30
        end = time.time()+timeout
        maxtime = time.time()+MAX_TIMEOUT
        while current <= maxtime:
            try:
                data = stream.read(self.chunk)
                count = len(data)/2
                format = "%dh" %(count)
                shorts = struct.unpack(format, data)
                
                # get intensity
                sum_squares = 0.0
                for sample in shorts:
                    n = sample * self.normalize
                    sum_squares += n * n
                rms = round(20*math.log10(math.pow(sum_squares / count, 0.5)))
                
                # detects sounds over the threshold
                if rms > self.threshold:
                    end = time.time()+timeout
                    if not started:
                        started = True
                        print("/nTriggered/n")
                current = time.time()

                if started:
                    if self.calibration:
                        print("%f dBSPL"%(rms+self.correction))
                    else:
                        print("%f dBFS"%(rms))
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
        
        # save the output file as WAV
        if len(frames)>0:
            print('\nSaving file %s' %cPathShort)
            wf = wave.open(filename, 'wb')
            wf.setnchannels(self.channels)
            wf.setsampwidth(p.get_sample_size(self.sample_format))
            wf.setframerate(self.fs)
            wf.writeframes(b''.join(frames))
            wf.close()
            print('... done!')
            # open wav as data
            _, data = read(filename)
            return data
        
        else:
            print("No audio recorded!")
            return 0

               
def getDeviceInfo():
    '''
    Returns a dictionary containing the information about the default input and output devices, along with all the
    available devices currently connected.

    Example:
    >>> info = get_device_info()
    >>> default_device_index = info.get("default_input").get("index")
    

    '''
    
    # open the stream
    p = pyaudio.PyAudio()
    # get number of connected devices
    info = p.get_host_api_info_by_index(0)
    numdevices = info.get('deviceCount')
    devicesin = []
    devicesout = []
    nchannels = []
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

    r = Recorder()
    rec = r.record(30)
