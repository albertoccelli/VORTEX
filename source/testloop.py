# default libraries
import os
import time
# user interface
import tkinter as tk
from datetime import datetime
from time import sleep
from tkinter import filedialog

import numpy as np
from scipy.io.wavfile import read

from .ABC_weighting import a_weight
# custom libraries
from .alb_pack.dsp import get_rms, add_gain, SaturationError
from .configure import load_list
from .play import play_data
from .recorder import Recorder

root = tk.Tk()
root.wm_attributes("-topmost", 1)
root.withdraw()

cPath = os.getcwd()

_langDict = {"ARW": "Arabic",
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


def clear_console():
    command = 'clear'
    if os.name in ('nt', 'dos'):  # If Machine is running on Windows, use cls
        command = 'cls'
    os.system(command)


def splash():
    _show_image("./utilities/logo.txt")
    print("\n++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
    print("+                                                                                        +")
    print("+                   VoRTEx v0.2.3a - Voice Recognition Test Execution                    +")
    print("+                                                                                        +")
    print("+                             'From testers, for testers'                                +")
    print("+                                                                                        +")
    print("+                               albertoccelli@gmail.com                                  +")
    print("+                       https://github.com/albertoccelli/VoRTEx                          +")
    print("+                                                                                        +")
    print("++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++\n")
    return


def _show_image(txt):
    with open(txt, "r") as f:
        for line in f.readlines():
            print(line, end="")
            sleep(0.01)
    return


def _now():
    """
    Returns the current date and time.
    """
    now_time = datetime.now().strftime('%Y/%m/%d_%H:%M:%S.%f')[:-3]
    return now_time


def _log(event, log_name="test_status.log"):
    """
    Log every test event with a timestamp.
    """
    with open(log_name, "a", encoding="utf-16") as r:
        r.write(_now() + "\t")
        r.write(event + "\n")
    return


def show_dirs(path):
    directories = []
    for name in os.listdir(path):
        if os.path.isdir(os.path.join(path, name)):
            directories.append(name)
    return directories


# noinspection SpellCheckingInspection
def lombard(noise):
    """
    The noise is expressed in dBSPL
    """
    if 50 < noise < 77:
        lombard_gain = 0.3 * (noise - 50)
    elif noise > 77:
        lombard_gain = 8
    else:
        lombard_gain = 0
    return lombard_gain


# noinspection SpellCheckingInspection
class Test:

    def __init__(self):
        # declare the attributes of the test
        self.wPath = "."  # The current working path of the selected test
        self.testName = ""
        # default paths
        self.calibDir = "utilities/calibration/"
        self.databaseDir = "database/"
        self.testDir = "vr_tests/"
        self.phrasesPath = "phrases/"  # The path of the audio files
        self.configfile = ""  # The configuration file of the current test
        self.listfile = ""  # The list file for the command database
        self.lang = "ITA"  # The language used for the test
        # status of the test
        self.begun = False  # Has the test already started?
        self.completed = False  # Has the test been completed?
        self.status = 0  # The test number we should start from. If the test is new, then the status is 0.
        self.results = {}  # A list containing the test results
        self.mCalibrated = False  # Is the mouth calibrated?
        self.mouth_calibration = 0  # The gain value for the mouth to reach 94dBSPL
        self.gain = 0  # The gain value for the mouth to reach 94dBSPL
        self.failed = []  # List of failed tests
        self.noise = 0  # RMS value of the background noise
        # open the sound recorder for calibration and translation
        print("------------------------------------------------------------------")
        print("Opening sound recorder\n")
        self.recorder = Recorder()
        print("\nChannels: %d" % self.recorder.channels)
        # set 2 channels 
        self.recorder.channels = 2
        # channel assignment
        # output
        self.mouthChannel = 0
        self.noiseChannel = 1
        # input
        self.micChannel = 0
        self.earChannel = 1
        # choose whether to create a new test or open a existing one
        option = int(input("\nDo you want to: \n1)start a new test\n2) open an existing one\n-->"))
        if option == 1:
            self.new()
        elif option == 2:
            self.resume()

        self.logname = "%s/testlog.log" % self.wPath

    def detectgenders(self, lang):
        """
        For the selected language, detects if both male and female voice are available,
        based on the folders on the "phrases" directory.
        """
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
            print("\tLANGUAGE: %s" % self.lang)
            print("\tSTARTED: %s" % self.begun)
            print("\tCOMPLETED: %s" % self.completed)
            print("------------------------------------------------------------------")
            try:
                if self.begun:
                    input(
                        "Do you want to continue with this test? (ENTER to continue, CTRL+C to cancel and choose "
                        "another one)")
                else:
                    input("Press ENTER to continue")
                break
            except KeyboardInterrupt:
                self.resume()

    def resume(self, path=None):
        if path is None:
            tests = show_dirs(self.testDir)
            if len(tests) == 0:
                print("No tests found! Let's start a new one")
                self.new()
                return
            else:
                print("\nWhich test do you want to resume? \n")
                for i in range(len(tests)):
                    print("\t%02d) %s ----> created: %s" % (i + 1,
                                                            tests[i],
                                                            time.strftime('%Y/%m/%d at %H:%M:%S',
                                                                          time.gmtime(os.path.getmtime(
                                                                              self.testDir + tests[i])))))
                print("\n\t%02d) browse..." % (len(tests) + 1))
                choice = int(input("-->"))
                if choice == len(tests) + 1:
                    # choose the test directory with a dialog
                    self.wPath = filedialog.askdirectory(title="Choose a test to resume",
                                                         initialdir=self.testDir)
                else:
                    self.wPath = self.testDir + tests[choice - 1]
                self.testName = self.wPath.split("/")[-1]
                if self.wPath == "":
                    print("Never mind, let's start from scratch")
                    self.new()
                    return
        else:
            self.wPath = path
        self.configfile = "%s/config.cfg" % self.wPath  # the configuration file's path
        self.load_conf()  # retrieve the paths and test status from the configuration file
        self._configure_list()  # get the test configuration (languages, lists) from the listfile
        self.getstatus()
        return

    def new(self, testname=None):
        if testname is None:
            # self.testname = simpledialog.askstring("New test",
            # "Choose a fancy name for this new vr test").replace(" ","_")
            self.testName = input("\nCreating a new test...! Please choose a fancy name for it!\n-->")
        else:
            self.testName = testname
        self.wPath = "%s%s" % (self.testDir, self.testName)  # this will be your new working directory
        try:
            os.mkdir(self.wPath)  # create a new directory for the test
            self.configfile = "%s/config.cfg" % self.wPath
            print("Creating test (%s)" % self.wPath)
            # select the proper list file with the command lists
            self.listfile = filedialog.askopenfilename(title="Choose the list file for the test",
                                                       filetypes=[("Voice Recognition Test List files", "*.vrtl"),
                                                                  ("All files", "*")],
                                                       initialdir=self.databaseDir)
            self._configure_list()  # get the command database (languages, lists) from the list file
            print("\n\nChoose the language to be used in the test among the following:\n")
            for i in range(len(self.langs)):
                print("\t%02d) %s" % (i + 1, _langDict[self.langs[i]]))
            langindex = int(input("\n-->"))
            self.lang = self.langs[langindex - 1]  # the language used in this test
            print("\nYou have chosen: %s\n" % self.lang)

            # detects whether male and female voices are available
            langpath = self.lang
            g = 0
            for i in os.listdir(self.database["AUDIOPATH"]):
                if self.lang in i:
                    g += 1
            if g == 2:
                response = input(
                    "Male (m) and female (f) voices are available. Which one do you want to test?\n-->").lower()
                while True:
                    if response == "m":
                        langpath = self.lang + "_M"
                        break
                    elif response == "f":
                        langpath = self.lang + "_F"
                        break
                    else:
                        response = input("Invalid input! Please choose between m and f.\n-->")
            self.phrasesPath = self.database["AUDIOPATH"] + langpath  # build the path for the speech files
            self.save_conf()  # save the configuration into the cfg file
            return
        except FileExistsError:
            # n_testname = simpledialog.askstring("New test",
            #                                   "The test '%s' already exists :(
            #                                   \nPlease choose another name or press enter to resume the selected one
            #                                   \n-->"%self.testname).replace(" ","_")
            n_testname = input(
                "The directory '%s' already exists :( \nPlease choose another name or press enter to resume the "
                "selected one\n-->" % self.testName)
            if str(n_testname) == "":
                print("Resuming...")
                self.resume(self.wPath)
            else:
                self.new(n_testname)
        return

    def _configure_list(self):
        """
        Opens the database file and converts it into a dictionary form suitable for the test.

        test = {"LANG1" = [[], [], [], []],
                "LANG2" = [[], [], [], []],
                ecc...
                }
        """
        self.database = load_list(self.listfile)  # create the test sequence dictionary from the vrtl file
        self.langs = []  # list of the currently supported languages
        for k in self.database.keys():
            if k != "preconditions" and k != "expected" and k != "AUDIOPATH":
                self.langs.append(k)
        for lang in self.langs:
            if len(self.database[lang]) > 157:  # detects if natural language is available
                self.langs.append(lang + "_NLU")
                self.database[lang + "_NLU"] = self.database[lang][157:]
                self.database[lang] = self.database[lang][0:157]
        self.langs.sort()
        return

    def save_conf(self):
        """
        Writes the test attributes (including the current progress) into the config file, along
        with information regarding the .vrtl file used for the test.
        """
        with open(self.configfile, "w", encoding="utf-16") as r:
            r.write("@YODA\n")
            r.write("@CONFIGURATION\n")
            r.write("LISTFILE=%s\n" % self.listfile)
            r.write("MOUTH_CALIBRATED=%s\n" % self.mCalibrated)
            r.write("MOUTH_CORRECTION=%s\n" % self.mouth_calibration)
            r.write("MIC_CALIBRATED=%s\n" % self.recorder.calibrated)
            r.write("MIC_DBFSTODBSPL=%s\n" % self.recorder.correction)
            r.write("PHRASESPATH=%s\n" % self.phrasesPath)
            r.write("LANG=%s\n" % self.lang)
            r.write("\n")
            # save progress
            r.write("@PROGRESS\n")
            r.write("STARTED=%s\n" % self.begun)
            r.write("STATUS=%s\n" % self.status)
            r.write("COMPLETED=%s\n" % self.completed)
            r.write("RESULTS=%s\n" % self.results)

    def load_conf(self):
        """
        Reads the configuration file for the selected test

        """
        with open(self.configfile, "r", encoding="utf-16") as r:
            # CHECK INTEGRITY
            healthy = False
            for line in r.readlines():
                if "@YODA" in line:
                    healthy = True
        with open(self.configfile, "r", encoding="utf-16") as r:
            if healthy:
                for line in r.readlines():
                    # read configuration
                    if "STARTED" in line:
                        self.begun = eval(line.split("=")[-1])
                        print(line.split("=")[-1])
                    elif "STATUS" in line:
                        self.status = int(line.split("=")[-1])
                    elif "COMPLETED" in line:
                        self.completed = eval(line.split("=")[-1])
                    elif "RESULTS" in line:
                        self.results = eval(line.split("=")[-1])
                    elif "LISTFILE" in line:
                        self.listfile = str(line.split("=")[-1].replace("\n", ""))
                    elif "PHRASESPATH" in line:
                        self.phrasesPath = str(line.split("=")[-1].replace("\n", ""))
                    elif "LANG" in line:
                        self.lang = str(line.split("=")[-1]).replace("\n", "")
            else:
                print("\n==================================================================")
                print("!!!CONFIGURATION FILE CORRUPTED!!!")
                print("\n==================================================================")
        return

    @staticmethod
    def activate_mic(mode=1):
        """
        Function to activate the vehicle's microphone for the voice recognition.
        Modes:
        1 - Manual
        2 - Reproduce wake word (to be chosen among the audio files)
        3 - Send PTT can message
        """
        if mode == 1:
            input("Press PTT")
        else:
            input("Mode not implemented. Falling back to 1")
        return

    def play_command(self, cid):
        """
        Plays the command based on the current test language and on the command ID.
        """
        filename = self.phrasesPath + "/" + self.lang + "_" + str(cid) + ".wav"
        print(filename)
        fs, data = read(filename)
        if self.mCalibrated:
            while True:
                total_gain = lombard(self.noise) + self.gain
                print("Adjusting gain (%0.2fdB)" % total_gain)
                try:
                    data = add_gain(data, total_gain)
                    break
                except SaturationError:
                    a = input(
                        "Cannot increase the volume of the wave file. Do you want to increase the amplifier volume "
                        "and redo the mouth calibration? (y/n to keep the max gain value possible).\n-->")
                    if str(a) == "y":
                        self.calibrate_mouth()
                    else:
                        break
        play_data(data, fs)
        return

    def calibrate_mic(self):
        """
        Calibrates the microphone so that it expresses values in dBSPL
        """
        self.recorder.calibrate(self.micChannel)
        return

    def calibrate_ear(self):
        """
        Calibrates Oscar's ear so that it expresses values in dBSPL
        """
        self.recorder.calibrate(channel=self.earChannel, reference=92.1)
        return

    def calibrate_mouth(self, reference=94):
        max_attempts = 5
        if self.recorder.calibrated:  # microphone has to be calibrated first
            # measure the RMS value of the calibration file
            c_file = self.calibDir + "FRF.wav"
            c_fs, c_data = read(c_file)
            c_data_gain = add_gain(c_data, self.gain)
            recorded = self.recorder.play_and_record(c_data_gain, c_fs)[:, self.micChannel]
            recorded_dbspl = get_rms(recorded) + self.recorder.correction[self.micChannel]
            print("Mouth RMS: %0.1fdBSPL\tdelta = %0.2f" % (recorded_dbspl, (reference - recorded_dbspl)))
            attempt = 0
            while abs(reference - recorded_dbspl) > 0.5:
                attempt += 1
                # add gain and record again until the intensity is close to 94dBSPL
                self.gain = reference - recorded_dbspl
                try:
                    c_data_gain = add_gain(c_data, self.gain)
                    print("Gain: %0.1fdB" % self.gain)
                    recorded = self.recorder.play_and_record(c_data_gain, c_fs)[:, self.micChannel]
                    recorded_dbspl = get_rms(recorded) + self.recorder.correction[self.micChannel]
                except SaturationError:
                    input("Cannot automatically increase the volume. Please manually increase the volume from "
                          "the amplifier knob and press ENTER to continue\n-->")
                    self.calibrate_mouth()
                    break
                if attempt == max_attempts:
                    break
            print("Calibration completed: %0.1fdB added" % self.gain)
            self.mCalibrated = True
        return self.gain

    def test(self, test, testid, translate=False):
        """
        Run a single test.
        """
        expected = []
        # test = self.database[self.lang]
        try:
            precs = self.database["preconditions"]  # if available, imports the array for the preconditions
            expected = self.database["expected"]  # and for the expected behaviour of the radio
            print("Preconditions:\n%s\n" % (precs[testid - 1].replace("\n", "")))
        except KeyError:
            pass
        _log("=========================== TEST #%03d ===========================" % testid, self.logname)
        while True:
            for test_index in range(len(test[testid - 1])):
                # reading database, splits commands into command id and phrase
                cid = test[testid - 1][test_index].split("\t")[0]
                command = test[testid - 1][test_index].split("\t")[1].replace("\n", "")
                exp = expected[testid - 1][test_index].replace("\n", "")
                if cid == "000":
                    self.activate_mic(1)  # activate the infotainment microphone for the voice recognition
                    # (1: manual, 2: wake word, 3: automatic)
                    _log("MIC_ACTIVATED", self.logname)
                else:
                    print("Reproducing %s_%s.wav - '%s'" % (self.lang, cid, command))
                    try:
                        self.play_command(cid)  # the mouth reproduces the command (after adjusting the gain, if wanted)
                    except Exception as e:
                        print("ERROR: %s" % e)
                    _log("OSCAR: <<%s>> (%s_%s.wav)" % (command, self.lang, cid), self.logname)
                    try:
                        print("\nExpected behaviour --> %s\n" % exp)
                    except NameError:
                        pass
                    # PLACE HERE THE FUNCTION TO LISTEN TO THE RADIO RESPONSE
                    response = "[Answer]"
                    if translate:
                        translation = "Translation"
                        _log("RADIO: <<%s>> - <<%s>>" % (response, translation), self.logname)
                    else:
                        _log("RADIO: <<%s>>" % response, self.logname)
                    if test_index + 1 < len(test[testid - 1]):
                        pass
                        input("==> Press ENTER to proceed with next step\n")
            result = str(input("Result: 1(passed), 0(failed), r(repeat)\n-->"))
            self.status += 1  # status updated
            if result != "r":
                if result == "0":
                    _log("END_TEST #%03d: FAILED" % testid, self.logname)
                elif result == "1":
                    _log("END_TEST #%03d: PASSED" % testid, self.logname)
                else:
                    result = str(input("INVALID INPUT: 1(passed), 0(failed), r(repeat)\n-->"))
                self.save_conf()
                break
            else:  # repeats test
                _log("REPEATING", self.logname)
        try:
            # at the end of the selected test, writes the results into a array
            self.results[str(testid)].append(result)
        except KeyError:
            self.results[str(testid)] = []
            self.results[str(testid)].append(result)

        return result

    def execution(self, translate=False):
        """
        Execute the whole test routine for the chosen language.

        If the test has already started, resume it.
        """
        clear_console()
        # Test begins
        preconditions = []
        expected = []
        if not self.begun:
            # start test from 0
            print("\n==================================================================")
            print("Beginning test... Press ENTER when you are ready")
            print("------------------------------------------------------------------")
            input("-->")
            _log("MAY THE FORCE BE WITH YOU", self.logname)  # the first line of the log file
            self.results = {}
            self.begun = True
        else:
            # resume the test
            print("==================================================================")
            print("Resuming test from %d... Press ENTER when you are ready" % (self.status + 1))
            print("------------------------------------------------------------------")
            input("-->")
            _log("WELCOME BACK", self.logname)

        # takes just the commands for the chosen language
        test = self.database[self.lang]
        try:  # if available, imports the array for the preconditions and expected behaviour
            preconditions = self.database["preconditions"]
            expected = self.database["expected"]
        except KeyError:
            pass
        _log("SELECTED LANGUAGE: %s - %s" % (self.lang, _langDict[self.lang]), self.logname)
        if self.recorder.calibrated[self.earChannel]:
            print("Listening to ambiance noise...\n")
            self.listen_noise()
            input("Press ENTER to continue\n-->")
        i = 0
        try:
            for i in range(self.status, len(test)):
                clear_console()
                print("------------------------------------------------------------------")
                print("%s: TEST %d OUT OF %d\n" % (_langDict[self.lang], i + 1, len(test)))  # test number counter
                print("------------------------------------------------------------------\n")
                try:
                    print("Preconditions:\n%s\n" % (preconditions[i].replace("\n", "")))
                except NameError:
                    pass
                _log("=========================== TEST #%03d ===========================" % (i + 1), self.logname)
                while True:
                    for test_index in range(len(test[i])):
                        cid = test[i][test_index].split("\t")[
                            0]  # reading database, splits commands into command id and phrase
                        command = test[i][test_index].split("\t")[1].replace("\n", "")
                        exp = expected[i][test_index].replace("\n", "")
                        if cid == "000":
                            self.activate_mic(1)  # activate the infotainment microphone for the voice recognition
                            # (1: manual, 2: wake word, 3: automatic)
                            _log("MIC_ACTIVATED", self.logname)
                        else:
                            print("Reproducing %s_%s.wav - '%s'" % (self.lang, cid, command))
                            try:
                                self.play_command(
                                    cid)  # the mouth reproduces the command (after adjusting the gain, if wanted)
                            except Exception as e:
                                print("ERROR: %s" % e)
                            _log("OSCAR: <<%s>> (%s_%s.wav)" % (command, self.lang, cid), self.logname)
                            try:
                                print("\nExpected behaviour --> %s\n" % exp)
                            except NameError:
                                pass
                            # PLACE HERE THE FUNCTION TO LISTEN TO THE RADIO RESPONSE
                            response = "[Answer]"
                            if translate:
                                translation = "Translation"
                                _log("RADIO: <<%s>> - <<%s>>" % (response, translation), self.logname)
                            else:
                                _log("RADIO: <<%s>>" % response, self.logname)
                            if test_index + 1 < len(test[i]):
                                pass
                                input("==> Press ENTER to proceed with next step\n")
                    result = str(input("Result: 1(passed), 0(failed), r(repeat)\n-->"))
                    print(result)
                    self.status += 1  # status updated
                    if result != "r":
                        if result == "0":
                            _log("END_TEST #%03d: FAILED" % (i + 1), self.logname)
                            self.failed.append(i + 1)
                        elif result == "1":
                            _log("END_TEST #%03d: PASSED" % (i + 1), self.logname)
                        else:
                            result = str(input("INVALID INPUT: 1(passed), 0(failed), r(repeat)\n-->"))
                        break
                    else:  # repeats test
                        _log("REPEATING", self.logname)
                try:
                    # at the end of the selected test, writes the results into a array
                    self.results[str(i + 1)].append(result)
                except KeyError:
                    self.results[str(i + 1)] = []
                    self.results[str(i + 1)].append(result)
                print("DONE")
            print("------------------------------------------------------------------")
            print("TEST COMPLETED")
            _log("TEST_STATUS: COMPLETED", self.logname)
            self.completed = True
            self.status = 0
            self.save_conf()  # save current progress of the test

        except KeyboardInterrupt:
            print("------------------------------------------------------------------")
            print("Test aborted! Saving...")
            self.completed = False
            _log("TEST_INTERRUPTED", self.logname)
            self.status = i
            _log("TEST_STATUS: %03d" % self.status, self.logname)
            self.save_conf()  # save current progress of the test

        except Exception as e:
            print("------------------------------------------------------------------")
            print("Test aborted due to a error (%s)! Saving..." % e)
            self.completed = False
            _log("ERROR %s" % e, self.logname)
            self.status = i
            _log("TEST_STATUS: %03d" % self.status, self.logname)
            self.save_conf()  # save current progress of the test

        # calculate the score and display it
        score = 0
        scores = []
        for i in range(len(self.results)):
            scores.append(max(self.results[str(i + 1)]))
        for i in scores:
            score += int(i)
        try:
            score = 100 * score / len(scores)
        except ZeroDivisionError:
            score = 0
        _log("TEST_RESULT: %d%%" % score, self.logname)
        print("------------------------------------------------------------------")
        print("Results: %d%%" % score)
        print("------------------------------------------------------------------")
        self.save_conf()
        return self.status

    def listen_noise(self, seconds=3):
        noise = self.recorder.record(seconds)[:, 1]
        noise_w = a_weight(noise, self.recorder.fs).astype(np.int16)
        self.noise = get_rms(noise_w) + self.recorder.correction[1]
        input("\nNoise intensity: %0.2fdBA\nThe gain due to lombard effect is %0.2fdB\n-->" % (
            self.noise, lombard(self.noise)))
        return self.noise

    def print_report(self):
        """
        Print the results in a csv file suitable for the analysis with Excel.
        """
        report_file = "%s/report.csv" % self.wPath
        print("\nSaving test results into %s...\n" % report_file)
        with open(report_file, "w", encoding="utf-16") as r:
            r.write("LANGUAGE: %s\n" % self.lang)
            r.write("TEST N.\tRESULT\n")
            for i in range(len(self.results)):
                r.write("%s\t %s\n" % (i + 1, self.results[i]))
        return


if __name__ == "__main__":
    # show splash screen
    splash()
    # declare a new test
    t = Test()
    # execute test
    t.execution()
