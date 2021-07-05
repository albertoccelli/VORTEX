#-------------------------------------------------------------------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------------------------------------------------------------------
#
# Name:             testloop.py
#
# Author: 	    Alberto Occelli
#		    albertoccelli@gmail.com
#		    a.occelli@reply.it
#	            occellialberto@telematicainformatica.it
#
# Version: 	    1.0
#
# Creation: 	    09/06/2021
#
# Last updated:     09/06/2021
#
# Changelog:	    0.0.1  - created
#                   0.0.9  - you now can interrupt a test and automatically resume it. Added configuration files
#
# Description:      test automation for the voice recognition performances. Automatically processes voice files
#                   by adding noise; pronounces all the commands
#
# To be added:      - GUI interface to enable the desired commands, languages and noises
#                   - add the acoustics of the microphones
#                   - calibration of the voices' levels
#                   - automatically activates vehicle's microphone
#                   - listening to vehicle's response and detecting answer
#                   - try to understand whether the command has been recognized or not
#                   - compile an output file with the test results
#
#
#-------------------------------------------------------------------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------------------------------------------------------------------

# default libraries
import sys
from scipy.io.wavfile import read, write
import numpy as np
import time
from time import sleep
from datetime import datetime
import os

# custom libraries
from . alb_pack.resample import resample
from . alb_pack.add_noise import addNoise
from . alb_pack.dsp import getRms, addGain
from . play import playWav, playData
from . recorder import Recorder
from . configure import saveList, loadList

import tkinter as tk
from tkinter import filedialog
from tkinter.ttk import Progressbar
    
root = tk.Tk()
root.wm_attributes("-topmost", 1)
root.withdraw()

cPath = os.getcwd()


def splash():
    showImage("./utilities/logo.txt")
    print("\n++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
    print("+                                                                        +")
    print("+           VoRTEx v0.0.1 - Voice Recognition Test Execution             +")
    print("+                                                                        +")
    print("+                       albertoccelli@gmail.com                          +")
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


class Test():
    
    def __init__(self):
        self.wPath = "."                # The current working path of the selected test
        self.databaseDir =  "database/"
        self.testDir =      "vr_tests/"
        self.phrasesPath =  "phrases/"  # The path of the audio files
        # declare the attributes of the test
        self.configfile = ""            # The configuration file of the current test
        self.listfile = ""              # The list file for the command database
        self.lang = ""                  # The language used for the test
        self.begun = False              # Has the test already started?
        self.completed = False          # Has the test been completed?
        self.status = 0                 # The test number we should start from. If the test is new, then the status is 0.
        self.results = []               # A list containing the test results
        
        # choose whether to create a new test or open a existing one
        option = int(input("Do you want: \nto start a new test (1) \nor open an existing one? (2)\n-->"))
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
        
        # open the sound recorder for the radio feedback translation
        print("\n------------------------------------------------------------------")
        print("Opening sound recorder\n")
        self.recorder = Recorder()
        

    def getstatus(self):
        # print the status of the test and ask for confirmation
        while True:
            print("\n------------------------------------------------------------------")
            print("---------------------STATUS OF THE TEST---------------------------")
            print("------------------------------------------------------------------")
            print("\tLANGUAGE: %s"%self.lang)
            print("\tSTARTED: %s"%self.begun)
            print("\tCOMPLETED: %s"%self.completed)
            if self.begun:
                print("\tRESULTS:")
                for i in range(len(self.results)):
                    if int(self.results[i]) == 1:
                        print("\t\tTEST %03d: PASS"%(i+1))
                    elif int(self.results[i]) == 0:
                        print("\t\tTEST %03d: FAIL"%(i+1))
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
                if self.wPath == "":
                    print("Never mind, let's start from scratch")
                    self.new()
                    return
        else:
            self.wPath = path
        self.configfile = "%s/config.cfg"%self.wPath            # the configuration file's path 
        self.loadConf()                                         # retrieve the paths and test status from the configuration file   
        self.configureList()                                    # get the test configuration (languages, lists) from the listfile    
        self.getstatus()
        return

    
    def new(self, testname=None):
        if testname == None:
            testname = input("\nCreating a new test...! Please choose a fancy name for it!\n-->")
        self.wPath = "%s%s"%(self.testDir, testname.replace(" ","_"))     # this will be your new working directory
        try:
            os.mkdir(self.wPath)                                # create a new directory for the test
            self.configfile = "%s/config.cfg"%self.wPath
            print("Creating test (%s)"%self.wPath)
            self.listfile = filedialog.askopenfilename(title = "Choose the list file for the test",
                                                       filetypes = [("Voice Recognition Test List files","*.vrtl"),("All files", "*")],
                                                       initialdir = self.databaseDir) # select the proper list file with the command lists
            self.configureList()                                # get the command database (languages, lists) from the list file
            print("\n\nChoose the language to be used in the test among the following:\n")
            for i in range(len(self.langs)):
                print("\t%02d) %s"%(i+1, self.langs[i]))
            langindex = int(input("\n-->"))
            self.lang = self.langs[langindex-1]                 # the language used in this test
            print("\nYou have chosen: %s"%self.lang)
            self.phrasesPath = self.database["AUDIOPATH"] + self.lang     # build the path for the speech files
            self.saveConf()                                     # save the configuration into the cfg file
            return
        except FileExistsError:
            nTestname = input("The directory '%s' already exists :( \nPlease choose another name or press enter to resume the selected one\n-->"%testname)
            self.new(nTestname)
            #if str(nTestname)=="":
            #    self.resume("tests/%s"%(testname.replace(" ","_")))
        self.getstatus()
        return 
    
        
    def configureList(self):
        '''
        1. Opens the database file and converts it into a dictionary form suitable for the test.

        test = {"LANG1" = [[], [], [], []],
                "LANG2" = [[], [], [], []],
                ecc...
                }
        '''
        self.database = loadList(self.listfile)                 # create the test sequence dictionary from the vrtl file
        self.langs = []                                         # list of the currently supported languages
        for k in self.database.keys():
            if k != "preconditions" and k != "expected" and k!= "AUDIOPATH":
                self.langs.append(k)
        for l in self.langs:
            if len(self.database[l]) > 157:   #detects if natural language is available
                self.langs.append(l+"_NLU")
                self.database[l+"_NLU"]=self.database[l][157:]
                self.database[l] = self.database[l][0:156]
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
        Modes:

        1 - Manual
        2 - Reproduce wakeword (to be chosen among the audio files)
        3 - Send PTT can message
        '''
        if mode == 1:
            input("Press PTT")
        return 


    def playCommand(self, cid):
        filename = self.phrasesPath+"/"+self.lang+"_"+str(cid)+".wav"
        playWav(filename)
        return
    

    def execution(self, translate = False):
        '''
        Execute the test for the chosen language.

        If the test has already started, resume it.
        '''
        lang = self.lang
        #Test begins
        if not self.begun:
            # start test from 0
            print("\n==================================================================")
            print("Beginning test... Press ENTER when you are ready")
            print("------------------------------------------------------------------")
            input("-->")
            log("MAY THE FORCE BE WITH YOU", self.logname)      # the first line of the log file
            self.results = []                               
            self.begun = True
        else:
            # resumes the test
            print("==================================================================")
            print("Resuming test from %d... Press ENTER when you are ready"%(self.status+1))
            print("------------------------------------------------------------------")
            input("-->")
            log("WELCOME BACK", self.logname)
        if True:
            test = self.database[lang]                          # takes just the commands for the choosen language
            try:
                preconditions = self.database["preconditions"]  # if available, imports the array for the preconditions
                expected = self.database["expected"]            # and for the expected behaviour of the radio
            except: pass
            log("SELECTED LANGUAGE: %s"%lang, self.logname)
            try:
                for i in range(self.status, len(test)):
                    print("------------------------------------------------------------------")
                    print("\n%s: TEST %d OUT OF %d\n"%(lang, i+1, len(test)))   # test number counter
                    try:
                        print("Preconditions:\n%s\n"%(preconditions[i].replace("\n", ""))) 
                    except:pass
                    log("=========================== TEST #%03d ==========================="%(i+1), self.logname)
                    while True: 
                        for t in range(len(test[i])):
                            cid = test[i][t].split("\t")[0]
                            command = test[i][t].split("\t")[1].replace("\n","")
                            exp = expected[i][t].replace("\n","")
                            if cid == "000":
                                self.activateMic(1)  # activate the infotainment microphone for the voice recognition (1: manual, 2: wakeword, 3: automatic)
                                log("MIC_ACTIVATED", self.logname)
                            else:
                                # reproduce the vocal command
                                print("Reproducing %s_%s.wav - '%s'"%(lang, cid, command))
                                self.playCommand(cid)
                                # PLACE HERE THE FUNCTION TO REPRODUCE THE WAVE FILE
                                log("OSCAR: <<%s>> (%s_%s.wav)"%(command, lang, cid), self.logname)
                                print("Listen to the radio answer")                                
                                try:
                                    print("Expected behaviour --> %s\n"%exp)
                                except:
                                    pass
                                # PLACE HERE THE FUNCTION TO LISTEN TO THE RADIO RESPONSE
                                sleep(1)
                                response = "[Answer]"
                                if translate:
                                    translation = "Translation"
                                    log("RADIO: <<%s>> - <<%s>>"%(response, translation), self.logname)
                                else:
                                    log("RADIO: <<%s>>"%(response), self.logname)
                                input("Press ENTER to continue")
                        result = str(input("Result: 1(passed), 0(failed), r(repeat)\n"))
                        self.status +=1     # status updated
                        if result != "r":
                            if result == "0":
                                log("END_TEST #%03d: FAILED"%(i+1), self.logname)
                            elif result == "1":
                                log("END_TEST #%03d: PASSED"%(i+1), self.logname)
                            else:
                                log("END_TEST #%03d: FAILED"%(i+1), self.logname)
                                result = 0                            
                            break
                        else:       # repeats test
                            log("REPEATING", self.logname)  
                    self.results.append(result) # at the end of the selected test, writes the results into a array
                print("------------------------------------------------------------------")
                print("TEST COMPLETED")
                log("TEST_STATUS: COMPLETED", self.logname)
                self.completed = True
                self.status = 0
                self.saveConf()     # save current progress of the test

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
            for i in self.results:
                score+=int(i)
            try:
                score = 100*score/len(self.results)
            except ZeroDivisionError:
                score = 0
            log("TEST_RESULT: %d%%"%score, self.logname)
            print("------------------------------------------------------------------")
            print("Results: %d%%"%score)
            print("------------------------------------------------------------------")
            self.saveConf()
            return self.status


    def printReport(self):
        '''
        Print the results in a csv file suitable for the analysis with Excel.
        '''
        with open("%s/report.csv"%self.wpath, "w", encoding = "utf-16") as r:
            r.write("#LANGUAGE: %s"%self.lang)
            r.write("#TEST N.,\tRESULT")
            for i in range(len(self.results)):
                r.write("%s,\t %s"%(i+1, self.results[i]))
        return
            
        

if __name__ == "__main__":

    # show splash screen
    splash()
    # declare a new test
    t = Test()
    #execute test
    t.execution()
