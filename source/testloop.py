# default libraries
import sys
from scipy.io.wavfile import read, write
import numpy as np
import time
from time import sleep
from datetime import datetime
import os
from . ABC_weighting import A_weight

# user interface
import tkinter as tk
from tkinter import Tk, Label, Button, Radiobutton, IntVar
from tkinter import simpledialog
from tkinter import messagebox
from tkinter import filedialog
from tkinter.ttk import Progressbar

# custom libraries
from . alb_pack.resample import resample
from . alb_pack.add_noise import addNoise
from . alb_pack.dsp import getRms, addGain, SaturationError
from . play import playWav, playData
from . recorder import Recorder
from . configure import saveList, loadList
from . tts import say

root = tk.Tk()
root.wm_attributes("-topmost", 1)
root.withdraw()

cPath = os.getcwd()

langDict = {"ARW": "Arabic",
            "CHC": "Chinese",
            "DUN": "Dutch",
            "ENG": "English (UK)",
            "ENA": "English (Australia)",
            "ENI": "English (India)",
            "ENU": "English (USA)",
            "FRF": "French (France)",
            "FRC": "French (Canada)",
            "GED": "German",
            "GED_NLU": "German (Natural language)",
            "ITA": "Italian",
            "ITA_NLU": "Italian (Natural language)",
            "JPJ": "Japanese",
            "KRK": "Korean",
            "PLP": "Polish",
            "PTP": "Portuguese (Portugal)",
            "PTB": "Portuguese (Brazil)",
            "RUR": "Russian",
            "SPE": "Spanish (Spain)",
            "SPM": "Spanish (Mexico)",
            "TRT": "Turkish"
            }
def clearConsole():
    command = 'clear'
    if os.name in ('nt', 'dos'):  # If Machine is running on Windows, use cls
        command = 'cls'
    os.system(command)

def splash():
    showImage("./utilities/logo.txt")
    print("\n++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
    print("+                                                                        +")
    print("+           VoRTEx v0.2.2a - Voice Recognition Test Execution            +")
    print("+                                                                        +")
    print("+                       albertoccelli@gmail.com                          +")
    print("+               https://github.com/albertoccelli/VoRTEx                  +")
    print("+                                                                        +")
    print("++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++\n")
    return


def showImage(txt):
    with open(txt, "r") as f:
        for l in f.readlines():
            print(l, end = "")
            sleep(0.01)
    return


def now():
    '''
    Returns the current date and time.
    '''
    now = datetime.now().strftime('%Y/%m/%d_%H:%M:%S.%f')[:-3]
    return now


def log(event, logname = "test_status.log"):
    '''
    Log every test event with a timestamp.
    '''
    with open(logname, "a", encoding = "utf-16") as r:
        r.write(now()+"\t")
        r.write(event+"\n")
    return


def showDirs(path):
    directories = []
    for name in os.listdir(path):
        if os.path.isdir(os.path.join(path, name)):
            directories.append(name)
    return directories


def lombard(noise):
    '''
    The noise is expressed in dBSPL
    '''
    if noise > 50 and noise < 77:
        lombard_gain = 0.3 * (noise-50)
    elif noise < 50:
        lombard_gain = 0
    elif noise > 77:
        lombard_gain = 8
    return lombard_gain




class Test():
    
    def __init__(self):
        # declare the attributes of the test
        self.wPath              = "."                                       # The current working path of the selected test
        self.testname           = ""
        #default paths
        self.databaseDir        = "database/"
        self.testDir            = "vr_tests/"       
        self.phrasesPath        = "phrases/"                                # The path of the audio files
        self.configfile         = ""                                        # The configuration file of the current test
        self.listfile           = ""                                        # The list file for the command database
        self.lang               = "ITA"                                     # The language used for the test
        # status of the test
        self.begun              = False                                     # Has the test already started?
        self.completed          = False                                     # Has the test been completed?
        self.status             = 0                                         # The test number we should start from. If the test is new, then the status is 0.
        self.results            = {}                                        # A list containing the test results
        self.mCalibrated        = False                                     # Is the mouth calibrated?
        self.mouthCalibration   = 0                                         # correction parameter binding the rms dBFS intensity of the audio file to the dBSPL value
        self.failed             = []
        self.noise              = 0
        
        # open the sound recorder for the radio feedback translation
        print("------------------------------------------------------------------")
        print("Opening sound recorder\n")
        self.recorder = Recorder()
        # set 2 channels 
        self.recorder.channels = 2
        # channel assignment
        # output
        self.mouthChannel = 0
        self.noiseChannel = 1
        #input
        self.micChannel = 0
        self.earChannel = 1
        
        # choose whether to create a new test or open a existing one
        option = int(input("\n\nDo you want: \nto start a new test (1) \nor open an existing one? (2)\n-->"))
        if option == 1:
            self.new()        
        elif option == 2:
            self.resume()

        self.logname = "%s/testlog.log"%self.wPath
        
        # store attributes
        self.attributes = {"CONFIGFILE": self.configfile,
                           "LISTFILE": self.listfile,
                           "LANGUAGE": self.lang,
                           "STARTED": self.begun,
                           "COMPLETED": self.completed,
                           "STATUS": self.status,
                           "RESULTS": self.results}
        

        
    def detectGenders(self, lang):
        '''
        For the selected language, detects if both male and female voice are available,
        based on the folders on the "phrases" directory.
        '''
        path = self.phrasesPath
        languages = []
        for i in os.listdir(path):
            if lang in i:
                languages.append(i)
        return len(languages)
                
    
        
    def getstatus(self):
        # print the status of the test and ask for confirmation
        while True:
            print("\n------------------------------------------------------------------")
            print("---------------------STATUS OF THE TEST---------------------------")
            print("------------------------------------------------------------------")
            print("\tLANGUAGE: %s"  %self.lang)
            print("\tSTARTED: %s"   %self.begun)
            print("\tCOMPLETED: %s" %self.completed)
            print("------------------------------------------------------------------")
            try:
                if self.begun:
                    input("Do you want to continue with this test? (ENTER to continue, CTRL+C to cancel and choose another one)")
                else:
                    input("Press ENTER to continue")
                break
            except KeyboardInterrupt:
                self.resume()

        
    def resume(self, path = None):
        if path == None:
            tests = showDirs(self.testDir)
            if len(tests) == 0:
                print("No tests found! Let's start a new one")
                self.new()
                return
            else:
                print("\nWhich test do you want to resume? \n")
                for i in range(len(tests)):
                    print("\t%02d) %s ----> created: %s"%(i+1, tests[i], time.strftime('%Y/%m/%d at %H:%M:%S', time.gmtime(os.path.getmtime(self.testDir + tests[i])))))
                print("\n\t%02d) browse..."%(len(tests)+1))
                choice = int(input("-->"))
                if choice == len(tests)+1:
                    self.wPath = filedialog.askdirectory(title = "Choose a test to resume", initialdir = self.testDir)              # choose the test directory with a dialog
                else:
                    self.wPath = self.testDir+tests[choice-1]
                self.testname = self.wPath.split("/")[-1]
                if self.wPath == "":
                    print("Never mind, let's start from scratch")
                    self.new()
                    return
        else:
            self.wPath = path
        self.configfile = "%s/config.cfg"%self.wPath                        # the configuration file's path 
        self.loadConf()                                                     # retrieve the paths and test status from the configuration file   
        self.configureList()                                                # get the test configuration (languages, lists) from the listfile    
        self.getstatus()
        return

    
    def new(self, testname=None):
        if testname == None:
            #self.testname = simpledialog.askstring("New test", "Choose a fancy name for this new vr test").replace(" ","_")
            self.testname = input("\nCreating a new test...! Please choose a fancy name for it!\n-->")
        else:
            self.testname = testname
        self.wPath = "%s%s"%(self.testDir, self.testname)                   # this will be your new working directory
        try:
            os.mkdir(self.wPath)                                            # create a new directory for the test
            self.configfile = "%s/config.cfg"%self.wPath
            print("Creating test (%s)"%self.wPath)
            self.listfile = filedialog.askopenfilename(title = "Choose the list file for the test",
                                                       filetypes = [("Voice Recognition Test List files","*.vrtl"),("All files", "*")],
                                                       initialdir = self.databaseDir) # select the proper list file with the command lists
            self.configureList()                                            # get the command database (languages, lists) from the list file
            print("\n\nChoose the language to be used in the test among the following:\n")
            for i in range(len(self.langs)):
                print("\t%02d) %s"%(i+1, langDict[self.langs[i]]))
            langindex = int(input("\n-->"))
            self.lang = self.langs[langindex-1]                             # the language used in this test
            print("\nYou have chosen: %s\n"%self.lang)
            
            # detects wether male and female voices are available
            langpath = self.lang
            g = 0
            for i in os.listdir(self.database["AUDIOPATH"]):
                if self.lang in i:
                    g+=1
            if g == 2:
                response = input("Male (m) and female (f) voices are availabe. Which one do you want to test?\n-->").lower()
                while True:
                    if response == "m":
                        langpath = self.lang+"_M"
                        break
                    elif response == "f":
                        langpath = self.lang+"_F"
                        break
                    else:
                        response = input("Invalid input! Please choose between m and f.\n-->")
            self.phrasesPath = self.database["AUDIOPATH"] + langpath        # build the path for the speech files
            self.saveConf()                                                 # save the configuration into the cfg file
            return
        except FileExistsError:
            #nTestname = simpledialog.askstring("New test",
            #                                   "The test '%s' already exists :( \nPlease choose another name or press enter to resume the selected one\n-->"%self.testname).replace(" ","_")
            nTestname = input("The directory '%s' already exists :( \nPlease choose another name or press enter to resume the selected one\n-->"%self.testname)
            if str(nTestname)=="":
                print("Resuming...")
                self.resume(self.wPath)
            else:self.new(nTestname)
        return 
    
        
    def configureList(self):
        '''
        1. Opens the database file and converts it into a dictionary form suitable for the test.

        test = {"LANG1" = [[], [], [], []],
                "LANG2" = [[], [], [], []],
                ecc...
                }
        '''
        self.database = loadList(self.listfile)                             # create the test sequence dictionary from the vrtl file
        self.langs = []                                                     # list of the currently supported languages
        for k in self.database.keys():
            if k != "preconditions" and k != "expected" and k!= "AUDIOPATH":
                self.langs.append(k)
        for l in self.langs:
            if len(self.database[l]) > 157:                                 # detects if natural language is available
                self.langs.append(l+"_NLU")
                self.database[l+"_NLU"]=self.database[l][157:]
                self.database[l] = self.database[l][0:157]
        self.langs.sort()         
        return


    def saveConf(self):
        '''
        Writes the test attributes (including the current progress) into the config file, along
        with information regarding the .vrtl file used for the test. 
        '''
        with open(self.configfile, "w", encoding = "utf-16") as r:
            r.write("@YODA\n")
            r.write("@CONFIGURATION\n")
            r.write("LISTFILE=%s\n"%self.listfile)
            r.write("MOUTH_CALIBRATED=%s\n"%self.mCalibrated)
            r.write("MOUTH_CORRECTION=%s\n"%self.mouthCalibration)
            r.write("MIC_CALIBRATED=%s\n"%self.recorder.calibrated)
            r.write("MIC_DBFSTODBSPL=%s\n"%self.recorder.correction)
            r.write("PHRASESPATH=%s\n"%self.phrasesPath)
            r.write("LANG=%s\n"%self.lang)
            r.write("\n")
            # save progress
            r.write("@PROGRESS\n")
            r.write("STARTED=%s\n"%self.begun)
            r.write("STATUS=%s\n"%self.status)
            r.write("COMPLETED=%s\n"%self.completed)
            r.write("RESULTS=%s\n"%self.results)
            
    
    def loadConf(self):
        '''
        Reads the configuration file for the selected test
        
        '''
        with open(self.configfile, "r", encoding = "utf-16") as r:
            #CHECK INTEGRITY
            healty = False
            for l in r.readlines():
                if "@YODA" in l:
                    healty = True
        with open(self.configfile, "r", encoding = "utf-16") as r:        
            if healty:
                for l in r.readlines():
                    # read configuration
                    if "STARTED" in l:
                        self.begun = eval(l.split("=")[-1])
                        print(l.split("=")[-1])
                    elif "STATUS" in l:
                        self.status = int(l.split("=")[-1])
                    elif "COMPLETED" in l:
                        self.completed = eval(l.split("=")[-1])
                    elif "RESULTS" in l:
                        self.results = eval(l.split("=")[-1])
                    elif "LISTFILE" in l:
                        self.listfile = str(l.split("=")[-1].replace("\n", ""))
                    elif "PHRASESPATH" in l:
                        self.phrasesPath = str(l.split("=")[-1].replace("\n", ""))
                    elif "LANG" in l:
                        self.lang = str(l.split("=")[-1]).replace("\n","")
            else:
                print("\n==================================================================")
                print("!!!CONFIGURATION FILE CORRUPTED!!!")
                print("\n==================================================================")
        return
            

    def activateMic(self, mode = 1):
        '''
        Function to acrivate the vehicle's microphone for the voice recognition.
        
        Modes:

        1 - Manual
        2 - Reproduce wakeword (to be chosen among the audio files)
        3 - Send PTT can message
        '''
        if mode == 1:
            pass
            input("Press PTT")
        return 


    def playCommand(self, cid):
        '''
        Plays the command based on the current test language and on the command ID.
        '''
        filename = self.phrasesPath+"/"+self.lang+"_"+str(cid)+".wav"
        print(filename)
        fs, data = read(filename)
        if self.mCalibrated:
            while True:
                commandRms = getRms(data) + self.mouthCalibration               # The estimated dBSPL level of the mouth
                delta = 94 - commandRms + lombard(self.noise)
                print("Adjusting gain (%0.2fdB)"%delta)
                print("RMS: %0.2fdBFS\t-->\t%0.2fdBSPL"%(getRms(data), commandRms))
                try:
                    data = addGain(data, delta)
                    break
                except SaturationError:
                    a = input("Cannot increase the volume of the wave file. Do you want to increase the amplifier volume and redo the mouth calibration? (y/n to keep the max gain value possible).\n-->")
                    if str(a) == "y":
                        self.calibrateMouth()
                    else:break
        playData(data, fs, deviceOutIndex = 4)
        return


    def calibrateMic(self):
        '''
        Calibrates the microphone so that it expresses values in dBSPL
        '''
        self.recorder.calibrate(self.micChannel)
        return

    
    def calibrateEar(self):
        '''
        Calibrates Oscar's ear so that it expresses values in dBSPL
        '''
        self.recorder.calibrate(channel = self.earChannel, reference = 92.1)
        return


    def calibrateMouth(self):
        if self.recorder.calibrated:                                        # microphone has to be calibrated first
            cFile = "utilities\calibration.wav"
            fs, played = read(cFile)
            rmsdBFS = getRms(played)
            #recorded = self.recorder.playAndRecord(played, fs)
            recordedRms = float(input("Open the session file 'calibration.ses' with Audition. Record the mouth output and measure the average RMS power.\nInsert here the dBFS value and press ENTER\n-->"))
            rmsdBSPL = recordedRms + self.recorder.correction[self.micChannel]
            self.mouthCalibration = rmsdBSPL - rmsdBFS
            self.mCalibrated = True
            print("File audio RMS: %0.2fdBFS\t-->\t%0.2fdBSPL\nMouth dSPL/dBFS: %0.2f\n"%(rmsdBFS, rmsdBSPL, self.mouthCalibration))
        return self.mouthCalibration
    

    def test(self, testid, translate = False):
        '''
        Run a single test.
        '''
        test = self.database[self.lang]
        try:
            preconditions = self.database["preconditions"]                              # if available, imports the array for the preconditions
            expected = self.database["expected"]                                        # and for the expected behaviour of the radio
            print("Preconditions:\n%s\n"%(preconditions[testid-1].replace("\n", ""))) 
        except: pass
        log("=========================== TEST #%03d ==========================="%(testid), self.logname)
        while True: 
            for t in range(len(test[testid-1])):
                cid = test[testid-1][t].split("\t")[0]                                 # reading database, splits commands into command id and phrase
                command = test[testid-1][t].split("\t")[1].replace("\n","")
                exp = expected[testid-1][t].replace("\n","")
                if cid == "000":
                    self.activateMic(1)                                         # activate the infotainment microphone for the voice recognition
                                                                                            # (1: manual, 2: wakeword, 3: automatic)
                    log("MIC_ACTIVATED", self.logname)
                else:
                    print("Reproducing %s_%s.wav - '%s'"%(self.lang, cid, command))
                    try:
                        self.playCommand(cid)                                   # the mouth reproduces the command (after adjusting the gain, if wanted)
                    except Exception as e:
                        print("ERROR: %s"%e)
                    log("OSCAR: <<%s>> (%s_%s.wav)"%(command, self.lang, cid), self.logname)                        
                    try:
                        print("\nExpected behaviour --> %s\n"%exp)
                    except:
                        pass
                    # PLACE HERE THE FUNCTION TO LISTEN TO THE RADIO RESPONSE
                    response = "[Answer]"
                    if translate:
                        translation = "Translation"
                        log("RADIO: <<%s>> - <<%s>>"%(response, translation), self.logname)
                    else:
                        log("RADIO: <<%s>>"%(response), self.logname)
                    if t+1 < len(test[testid-1]):
                        pass
                        input("==> Press ENTER to proceed with next step\n")
            result = str(input("Result: 1(passed), 0(failed), r(repeat)\n-->"))
            self.status +=1     # status updated
            if result != "r":
                if result == "0":
                    log("END_TEST #%03d: FAILED"%(testid), self.logname)
                elif result == "1":
                    log("END_TEST #%03d: PASSED"%(testid), self.logname)
                else:
                    result = str(input("INVALID INPUT: 1(passed), 0(failed), r(repeat)\n-->"))                      
                break
                self.saveConf()
            else:               # repeats test
                log("REPEATING", self.logname)  
        self.results[testid].append(result) # at the end of the selected test, writes the results into a array
        
        return result
        
        
    
    def execution(self, translate = False):
        '''
        Execute the whole test routine for the chosen language.
        
        If the test has already started, resume it.
        '''
        #Test begins
        if not self.begun:
            # start test from 0
            print("\n==================================================================")
            print("Beginning test... Press ENTER when you are ready")
            print("------------------------------------------------------------------")
            input("-->")
            log("MAY THE FORCE BE WITH YOU", self.logname)                                  # the first line of the log file
            self.results = {}                             
            self.begun = True
        else:
            # resumes the test
            print("==================================================================")
            print("Resuming test from %d... Press ENTER when you are ready"%(self.status+1))
            print("------------------------------------------------------------------")
            input("-->")
            log("WELCOME BACK", self.logname)
        if True:
            test = self.database[self.lang]                                                 # takes just the commands for the choosen language
            try:
                preconditions = self.database["preconditions"]                              # if available, imports the array for the preconditions
                expected = self.database["expected"]                                        # and for the expected behaviour of the radio
            except: pass
            log("SELECTED LANGUAGE: %s - %s"%(self.lang, langDict[self.lang]), self.logname)
            if self.recorder.calibrated[self.earChannel]:
                print("Listening to ambiance noise...\n")
                self.listenNoise()
                input("Press ENTER to continue\n-->")
            try:
                for i in range(self.status, len(test)):
                    clearConsole()
                    print("------------------------------------------------------------------")
                    print("%s: TEST %d OUT OF %d\n"%(langDict[self.lang], i+1, len(test)))  # test number counter
                    print("------------------------------------------------------------------\n")
                    try:
                        print("Preconditions:\n%s\n"%(preconditions[i].replace("\n", ""))) 
                    except:pass
                    log("=========================== TEST #%03d ==========================="%(i+1), self.logname)
                    while True: 
                        for t in range(len(test[i])):
                            cid = test[i][t].split("\t")[0]                                 # reading database, splits commands into command id and phrase
                            command = test[i][t].split("\t")[1].replace("\n","")
                            exp = expected[i][t].replace("\n","")
                            if cid == "000":
                                self.activateMic(1)                                         # activate the infotainment microphone for the voice recognition
                                                                                            # (1: manual, 2: wakeword, 3: automatic)
                                log("MIC_ACTIVATED", self.logname)
                            else:
                                print("Reproducing %s_%s.wav - '%s'"%(self.lang, cid, command))
                                try:
                                    self.playCommand(cid)                                   # the mouth reproduces the command (after adjusting the gain, if wanted)
                                except Exception as e:
                                    print("ERROR: %s"%e)
                                log("OSCAR: <<%s>> (%s_%s.wav)"%(command, self.lang, cid), self.logname)                        
                                try:
                                    print("\nExpected behaviour --> %s\n"%exp)
                                except: pass
                                # PLACE HERE THE FUNCTION TO LISTEN TO THE RADIO RESPONSE
                                response = "[Answer]"
                                if translate:
                                    translation = "Translation"
                                    log("RADIO: <<%s>> - <<%s>>"%(response, translation), self.logname)
                                else:
                                    log("RADIO: <<%s>>"%(response), self.logname)
                                if t+1 < len(test[i]):
                                    pass
                                    input("==> Press ENTER to proceed with next step\n")
                        result = str(input("Result: 1(passed), 0(failed), r(repeat)\n-->"))
                        self.status +=1                                                     # status updated
                        if result != "r":
                            if result == "0":
                                log("END_TEST #%03d: FAILED"%(i+1), self.logname)
                                self.failed.append(i+1)
                            elif result == "1":
                                log("END_TEST #%03d: PASSED"%(i+1), self.logname)
                            else:
                                result = str(input("INVALID INPUT: 1(passed), 0(failed), r(repeat)\n-->"))                      
                            break
                            self.saveConf()
                        else:                                                               # repeats test
                            log("REPEATING", self.logname)
                    try:
                        self.results[str(i+1)].append(result) # at the end of the selected test, writes the results into a array
                    except:
                        self.results[str(i+1)] = []
                        self.results[str(i+1)].append(result)
                print("------------------------------------------------------------------")
                print("TEST COMPLETED")
                log("TEST_STATUS: COMPLETED", self.logname)
                self.completed = True
                self.status = 0
                self.saveConf()                                                             # save current progress of the test

            except KeyboardInterrupt:
                print("------------------------------------------------------------------")
                print("Test aborted! Saving...")
                self.completed = False
                log("TEST_INTERRUPTED", self.logname)
                self.status = i
                log("TEST_STATUS: %03d"%self.status, self.logname)
                self.saveConf()     # save current progress of the test
            
            except Exception as e:
                print("------------------------------------------------------------------")
                print("Test aborted due to a error (%s)! Saving..."%e)
                self.completed = False
                log("ERROR %s"%e, self.logname)
                self.status = i
                log("TEST_STATUS: %03d"%self.status, self.logname)
                self.saveConf()     # save current progress of the test

            #calculate the score and display it
            score = 0
            scores = []
            for i in range(len(self.results)):
                scores.append(max(self.results[str(i+1)]))
            for i in scores:
                score+=int(i)
            try:
                score = 100*score/len(scores)
            except ZeroDivisionError:
                score = 0
            log("TEST_RESULT: %d%%"%score, self.logname)
            print("------------------------------------------------------------------")
            print("Results: %d%%"%score)
            print("------------------------------------------------------------------")
            self.saveConf()
            return self.status

    def listenNoise(self, seconds = 3):
        noise = self.recorder.record(seconds)[:,1]
        noise_w = A_weight(noise, self.recorder.fs).astype(np.int16)
        self.noise = getRms(noise_w) + self.recorder.correction[1]
        input("\nNoise intensity: %0.2fdBA\nThe gain due to lombard effect is %0.2fdB\n-->"%(self.noise, lombard(self.noise)))
        return self.noise


    def printReport(self):
        '''
        Print the results in a csv file suitable for the analysis with Excel.
        '''
        reportFile = "%s/report.csv"%self.wPath
        print("\nSaving test results into %s...\n"%reportFile)
        with open(reportFile, "w", encoding = "utf-16") as r:
            r.write("LANGUAGE: %s\n"%self.lang)
            r.write("TEST N.\tRESULT\n")
            for i in range(len(self.results)):
                r.write("%s\t %s\n"%(i+1, self.results[i]))
        return
            
        

if __name__ == "__main__":

    # show splash screen
    splash()
    # declare a new test
    t = Test()
    #execute test
    t.execution()
