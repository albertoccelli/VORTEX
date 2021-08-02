# TODO merge common tests and Natural Language ones

# default libraries
import os
import time
# user interface
import tkinter as tk
from datetime import datetime
from tkinter import filedialog
from msvcrt import getch

import random
import numpy as np
from scipy.io.wavfile import read, write

from .ABC_weighting import a_weight
# custom libraries
from .dsp import get_rms, add_gain, SaturationError
from .configure import load_list
from .play import play_data
from .recorder import Recorder
from .cli_tools import print_square, clear_console, show_image

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


def _abs_to_rel(path):
    """
    Convert path from absolute to relative
    """
    cwd = os.getcwd().replace("\\", "/")
    return path.split(cwd)[-1]


def splash():
    clear_console()
    show_image("./utilities/logo.txt")
    welcome = "VoRTEx v0.5.4a - Voice Recognition Test Execution\n" \
              "'From testers, for testers'\n" \
              "\n" \
              "Os: Windows\n" \
              "(c) Jul. 2021 - Alberto Occelli\n" \
              "email: albertoccelli@gmail.com\n" \
              "https://github.com/albertoccelli/VoRTEx"
    print_square(welcome, margin=[20, 20, 1, 1], centering="center")
    return


def _clr_tmp():
    try:
        os.remove("temp.wav")
    except FileNotFoundError:
        pass
    return


def _now():
    """
    Returns the current date and time.
    """
    now_time = datetime.now().strftime('%Y/%m/%d_%H:%M:%S')
    return now_time


def _log(event, log_time=None, log_name="test_status.log"):
    """
    Log every test event with a timestamp.
    """
    if log_time is None:
        log_time = _now()
    with open(log_name, "a", encoding="utf-16") as r:
        r.write(log_time + "\t")
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
        self.settingsDir = "settings/"  # the directory for the settings of the program
        self.settingsFile = "settings/settings.vcfg"
        self.databaseDir = "database/"
        self.testDir = "vr_tests/"
        self.phrasesPath = "phrases/"  # The path of the audio files
        self.lang = "ITA"  # The language used for the test (to be defined during the test configuration)
        self.nlu = True  # Is Natural Language enabled?
        self.mic_mode = 1  # how the infotainment microphone is activated: ptt(1), wakeword(2), can message(3)
        # status of the test
        self.issued_ww = 0  # How many times has the wakeword been pronounced
        self.recognized_ww = 0  # How many times has the wakeword been recognized
        self.running = False  # Is the test running?
        self.completed = 0  # How many times has the test been completed?
        self.status = 0  # The test number we should start from. If the test is new, then the status is 0.
        self.results = {}  # A list containing the test results
        self.mCalibrated = False  # Is the mouth calibrated?
        self.gain = 0  # The gain value for the mouth to reach 94dBSPL
        self.failed = []  # List of failed tests
        self.noise = 0  # RMS value of the background noise
        self.noise_radio = 0  # RMS value of the background noise plus the radio on
        self.testlist = []
        # open the sound recorder for calibration and translation
        clear_console()
        print("------------------------------------------------------------------")
        print("Opening sound recorder\n")
        self.recorder = Recorder()
        print("\nChannels: %d\n" % self.recorder.channels)
        # set 2 channels
        self.recorder.channels = 2
        # channel assignment
        # output
        self.mouthChannel = 0
        self.noiseChannel = 1
        # input
        self.micChannel = 0
        self.earChannel = 1
        print("------------------------------------------------------------------")
        try:
            self.load_settings()
            print("Loading VoRTEx settings... done!")
        except FileNotFoundError:
            print("Creating VoRTEx settings file... done!")
            with open(self.settingsFile, "w", encoding="utf-16"):
                pass
        # choose whether to create a new test or open a existing one
        print("------------------------------------------------------------------")
        while True:
            try:
                option = int(input("Do you want to: "
                                   "\n1) start a new test"
                                   "\n2) open an existing one"
                                   "\n3) modify the audio device settings"
                                   "\n?\n-->"))
                if option == 1:
                    clear_console()
                    self.new()
                    break
                elif option == 2:
                    clear_console()
                    self.resume()
                    break
                # TODO: add an option to modify the device settings
                elif option == 3:
                    input("Choosing input and output devices! (NOT IMPLEMENTED YET)")
                else:
                    print("Invalid input!\n")
            except ValueError:
                print("Invalid input!")
        self.logname = "%s/testlog.log" % self.wPath
        self.testlist = range(len(self.database[self.lang]))

    def save_settings(self):
        with open(self.settingsFile, "w", encoding="utf-16") as f:
            f.write("@YODA\n")
            f.write("@SETTINGS\n")
            f.write("MOUTH_CALIBRATED=%s\n" % self.mCalibrated)
            f.write("MOUTH_CORRECTION=%s\n" % self.gain)
            f.write("MIC_CALIBRATED=%s\n" % self.recorder.calibrated)
            f.write("MIC_DBFSTODBSPL=%s\n" % self.recorder.correction)
        return

    def load_settings(self):
        try:
            with open(self.settingsFile, "r", encoding="utf-16") as f:
                for line in f.readlines():
                    if "MOUTH_CALIBRATED" in line:
                        self.mCalibrated = eval(line.split("=")[-1])
                    elif "MOUTH_CORRECTION" in line:
                        self.gain = eval(line.split("=")[-1])
                    elif "MIC_CALIBRATED" in line:
                        self.recorder.calibrated = eval(line.split("=")[-1])
                    elif "MIC_DBFSTODBSPL" in line:
                        self.recorder.correction = eval(line.split("=")[-1])
        except FileNotFoundError:
            raise FileNotFoundError("Settings file not found!")
        return

    def _detectgenders(self, lang):
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
            print_square("LANGUAGE: %s\n"
                         "RUNNING: %s\n"
                         "STATUS: %s/%s\n"
                         "COMPLETED: %s" % (self.lang, self.running, self.status,
                                            len(self.database[self.lang]), self.completed),
                         margin=[5, 5, 1, 1],
                         title="TEST STATUS")
            try:
                if self.running:
                    input("Do you want to continue with this test? (ENTER to continue, CTRL+C to cancel and choose "
                          "another one) ")
                else:
                    input("Press ENTER to continue")
                break
            except KeyboardInterrupt:
                self.resume()

    def new(self, testname=None):
        print("------------------------------------------------------------------")
        if testname is None:
            # self.testname = simpledialog.askstring("New test",
            # "Choose a fancy name for this new vr test").replace(" ","_")
            self.testName = input("Creating a new test...! Please choose a fancy name for it!\n-->")
        else:
            self.testName = testname
        self.wPath = "%s%s" % (self.testDir, self.testName)  # this will be your new working directory
        try:
            os.mkdir(self.wPath)  # create a new directory for the test
            self.testfile = "%s/config.cfg" % self.wPath
            print("Creating test (%s)" % self.wPath)
            # select the proper list file with the command lists
            self.listfile = filedialog.askopenfilename(title="Choose the list file for the test",
                                                       filetypes=[("Voice Recognition Test List files", "*.vrtl"),
                                                                  ("All files", "*")],
                                                       initialdir=self.databaseDir)
            self.listfile = _abs_to_rel(self.listfile)
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
            print("Test length: %d" % len(self.database[self.lang]))
            if len(self.database[self.lang]) > 157:  # detects if natural language is available
                self.nlu = True
                input("Natural Language enabled! (Press ENTER to continue)")
            else:
                self.nlu = False
            self.phrasesPath = self.database["AUDIOPATH"] + langpath  # build the path for the speech files
            self.save_conf()  # save the configuration into the cfg file
            return
        except FileExistsError:
            n_testname = input(
                "The directory '%s' already exists :( \nPlease choose another name or press enter to resume the "
                "selected one\n-->" % self.testName)
            if str(n_testname) == "":
                print("Resuming...")
                self.resume(self.wPath)
            else:
                self.new(n_testname)
        return

    def resume(self, path=None):
        print("------------------------------------------------------------------")
        if path is None:
            tests = show_dirs(self.testDir)
            if len(tests) == 0:
                print("No tests found! Let's start a new one")
                self.new()
                return
            else:
                print("Which test do you want to resume? \n")
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
        self.testfile = "%s/config.cfg" % self.wPath  # the configuration file's path
        self.load_conf()  # retrieve the paths and test status from the configuration file
        self._configure_list()  # get the test configuration (languages, lists) from the listfile
        self.getstatus()
        return

    # save and load functions
    def _configure_list(self):
        """
        Opens the database file and converts it into a dictionary form suitable for the test.

        test = {"LANG1" = [[], [], [], []],
                "LANG2" = [[], [], [], []],
                ecc...
                }
        """
        self.database = load_list(
            os.getcwd().replace("\\", "/") + self.listfile)  # create the test sequence dictionary from the vrtl file
        self.langs = []  # list of the currently supported languages
        for k in self.database.keys():
            if k != "preconditions" and k != "expected" and k != "AUDIOPATH":
                self.langs.append(k)
        self.langs.sort()
        return

    def save_conf(self):
        """
        Writes the test attributes (including the current progress) into the config file, along with information
        regarding the .vrtl file used for the single test.
        """
        with open(self.testfile, "w", encoding="utf-16") as r:
            r.write("@YODA\n")
            r.write("@CONFIGURATION\n")
            r.write("LISTFILE=%s\n" % self.listfile)
            r.write("PHRASESPATH=%s\n" % self.phrasesPath)
            r.write("LANG=%s\n" % self.lang)
            r.write("NLU=%s\n" % self.nlu)
            r.write("\n")
            # save progress
            r.write("@PROGRESS\n")
            r.write("STARTED=%s\n" % self.running)
            r.write("STATUS=%s\n" % self.status)
            r.write("COMPLETED=%s\n" % self.completed)
            r.write("ISSUED_WW=%s\n" % self.issued_ww)
            r.write("RECOGNIZED_WW=%s\n" % self.recognized_ww)
            r.write("RESULTS=%s\n" % self.results)

    def load_conf(self):
        """
        Reads the configuration file for the selected test
        """
        with open(self.testfile, "r", encoding="utf-16") as r:
            # CHECK INTEGRITY
            healthy = False
            for line in r.readlines():
                if "@YODA" in line:
                    healthy = True
        with open(self.testfile, "r", encoding="utf-16") as r:
            if healthy:
                for line in r.readlines():
                    # read configuration
                    if "STARTED" in line:
                        self.running = eval(line.split("=")[-1])
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
                    elif "NLU" in line:
                        self.nlu = str(line.split("=")[-1]).replace("\n", "")
                    elif "ISSUED_WW" in line:
                        self.issued_ww = float(line.split("=")[-1].replace("\n", ""))
                    elif "RECOGNIZED_WW" in line:
                        self.recognized_ww = float(line.split("=")[-1].replace("\n", ""))
            else:
                print_square("!!! CONFIGURATION FILE CORRUPTED", centering="center")

    def _check_completed(self):
        lengths = []
        for i in list(self.results.keys()):
            lengths.append(len(self.results[i]))
        if len(self.results) == len(self.database[self.lang]):
            self.completed = min(lengths)
            if min(lengths) == max(lengths):
                self.running = False
        return self.running, self.completed

    def play_command(self, cid):
        """
        Plays the command based on the current test language and on the command ID.
        The gain is adjusted based on the mouth calibration (if made) and on the Lombard Effect (if a recording of the
        background noise has been performed).
        """
        filename = self.phrasesPath + "/" + self.lang + "_" + str(cid) + ".wav"
        fs, data = read(filename)
        if self.mCalibrated:
            while True:
                # wake word is pronounced with radio on
                if int(cid) == 0:
                    total_gain = lombard(self.noise_radio) + self.gain
                else:
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

    def activate_mic(self, mode=1):
        """
        Function to activate the vehicle's microphone for the voice recognition.
        Modes:
        1 - Manual
        2 - Reproduce wake word (to be chosen among the audio files)
        3 - Send PTT can message
        """
        if mode == 1:
            input("Press PTT")
        elif mode == 2:
            try:
                print_square("Hey Maserati!", centering="center")
                self.play_command("000")
            except FileNotFoundError:
                print("Mode not implemented. Falling back to 1")
                pass
        else:
            input("Mode not implemented. Falling back to 1")
        return

    def cancel(self, mode=1):
        """
        Function to cancel recognition prompt

        1 - Reproduce "cancel" command
        2 - Send PTT can message
        """
        if mode == 1:
            try:
                print_square("Cancel", centering="center")
                self.play_command("999")
            except FileNotFoundError:
                input("'Cancel' command not found. Please place it under the command id '999'.")
                pass
        else:
            input("Mode not implemented. Falling back to 1")
        return

    # calibration functions
    def _make_calibration_file(self, duration=30):
        """
        Randomly chooses several audio files from the phrases folder and join them until a unique file of a fixed
        duration is made. The file is suitable for the calibration of the artificial mouth.
        """
        treshold = 100
        files = []
        for i in os.listdir(self.phrasesPath):
            if i.split(".")[-1] == "wav":
                files.append(self.phrasesPath + "/" + i)
        pdata = np.array([])
        while True:
            file = files[random.randint(1, len(files))]
            fs, calib_data = read(file)
            # cut silence at the beginning and at the end
            for i in range(len(calib_data)):
                if abs(calib_data[1]) > treshold and abs(calib_data[-1]) > treshold:
                    break
                else:
                    if abs(calib_data[1]) < treshold:
                        calib_data = calib_data[1:]
                    if abs(calib_data[-1]) < treshold:
                        calib_data = calib_data[:-1]
            calib_data = np.concatenate((pdata, calib_data))
            # if the obtained file is longer than 30s, break the loop
            length = len(calib_data) / fs
            if length > duration:
                break
            pdata = calib_data
        len(calib_data)
        write(self.phrasesPath + "/calibration.wav", fs, calib_data.astype(np.int16))
        return fs, calib_data.astype(np.int16)

    def calibrate_mic(self):
        """
        Calibrates the microphone so that it expresses values in dBSPL.
        For that a 94dBSPL calibrator is mandatory.
        """
        self.recorder.calibrate(self.micChannel)
        self.recorder.save("%smic_calibration.wav" % self.settingsDir)
        self.recorder.save("%s/mic_calibration.wav" % self.wPath)
        self.save_conf()
        return

    def calibrate_ear(self):
        """
        Calibrates Oscar's ear so that it expresses values in dBSPL.
        For that a 94dBSPL calibrator is mandatory.
        """
        self.recorder.calibrate(channel=self.earChannel, reference=92.1)
        self.recorder.save("%sear_calibration.wav" % self.settingsDir)
        self.recorder.save("%s/ear_calibration.wav" % self.wPath)
        self.save_conf()
        return

    def calibrate_mouth(self, reference=94, max_attempts=6):
        """
        Reproduces a calibration file from the mouth, records it, measures its RMS power and, if needed, adjusts the
        gain and records again the calibration file.

        This operation is repeated until the RMS power is as close as possible to the nominal value of 94dBSPL.
        The number of maximum attempts can be decided and specified among the function's arguments.
        After the last attempt the last gain value is kept, whatever the difference between the RMS level and the
        nominal one is.
        """
        attempt = 1
        try:
            if self.recorder.calibrated:  # microphone has to be calibrated first
                print("Opening calibration file... ")
                try:
                    c_fs, c_data = read(self.phrasesPath + "/calibration.wav")
                except FileNotFoundError:
                    print("Calibration file not found! Creating a new one...", end='')
                    c_fs, c_data = self._make_calibration_file()
                print("done!")
                c_data_gain = add_gain(c_data, self.gain)
                recorded = self.recorder.play_and_record(c_data_gain, c_fs)[:, self.micChannel]
                recorded_dbspl = get_rms(recorded) + self.recorder.correction[self.micChannel]
                delta = reference - recorded_dbspl
                print_square("Target      = %0.2fdBSPL\n"
                             "Mouth RMS   = %0.2fdBSPL\n"
                             "delta       = %0.2fdB" % (reference, recorded_dbspl, -delta),
                             title="ATTEMPT %d of %d" % (attempt, max_attempts))
                while abs(delta) > 0.5:
                    attempt += 1
                    # add gain and record again until the intensity is close to 94dBSPL
                    self.gain = self.gain + delta
                    try:
                        print("\nApplying gain: %0.2fdB" % self.gain)
                        c_data_gain = add_gain(c_data, self.gain)
                        recorded = self.recorder.play_and_record(c_data_gain, c_fs)[:, self.micChannel]
                        recorded_dbspl = get_rms(recorded) + self.recorder.correction[self.micChannel]
                        delta = reference - recorded_dbspl
                        print_square("Target      = %0.2fdBSPL\n"
                                     "Mouth RMS   = %0.2fdBSPL\n"
                                     "delta       = %0.2fdB" % (reference, recorded_dbspl, -delta),
                                     title="ATTEMPT %d of %d" % (attempt, max_attempts))
                    except SaturationError:
                        input("Cannot automatically increase the volume. Please manually increase the volume from "
                              "the amplifier knob and press ENTER to continue\n-->")
                        self.gain = self.gain - delta
                        self.calibrate_mouth()
                        return
                    if attempt == max_attempts:
                        break
                print("Calibration completed: %0.2fdB added" % self.gain)
                self.recorder.data = self.recorder.data[:, self.micChannel]
                self.recorder.save("%smouth_calibration.wav" % self.settingsDir)
                self.recorder.save("%s/mouth_calibration.wav" % self.wPath)
                self.mCalibrated = True
                self.save_conf()
        except KeyboardInterrupt:
            print("Mouth calibration interrupted. Gain value: %0.2f" % self.gain)
            self.mCalibrated = True
            self.save_conf()
        return self.gain

    def listen_noise(self, seconds=5):
        # Only background noise
        input("\nMeasuring background noise with radio OFF. Press ENTER to continue.\n-->")
        noise = self.recorder.record(seconds)[:, 1]
        noise_w = a_weight(noise, self.recorder.fs).astype(np.int16)
        self.noise = get_rms(noise_w) + self.recorder.correction[1]
        print_square("Noise intensity: %0.2fdBA\nLombard effect: %0.2fdB"
                     % (self.noise, lombard(self.noise)), title="RADIO OFF")
        self.recorder.save("%s/noise_radio_off.wav" % self.wPath)
        # Background noise and radio on
        input("\nMeasuring background noise with radio ON. Press ENTER to continue.\n-->")
        noise = self.recorder.record(seconds)[:, 1]
        noise_w = a_weight(noise, self.recorder.fs).astype(np.int16)
        self.noise_radio = get_rms(noise_w) + self.recorder.correction[1]
        print_square("Noise intensity: %0.2fdBA\nLombard effect: %0.2fdB"
                     % (self.noise_radio, lombard(self.noise_radio)), title="RADIO ON")
        self.recorder.save("%s/noise_radio_on.wav" % self.wPath)
        return self.noise, self.noise_radio

    # functions for the actual test
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
        if not self.running:
            # start test from 0
            print_square("Beginning test... Press ENTER when you are ready")
            input("-->")
            _log("MAY THE FORCE BE WITH YOU", self.logname)  # the first line of the log file
            self.results = {}
            self.running = True
        else:
            # resume the test
            print_square("Resuming test from %d... Press ENTER when you are ready" % (self.status + 1))
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
            self.listen_noise()
            input("Press ENTER to continue\n-->")
        i = 0

        print("Testlist: ")
        input(self.testlist)

        try:
            for i in range(self.status, len(self.testlist)):
                clear_console()
                print_square("%s: TEST %d OUT OF %d" % (_langDict[self.lang], i + 1, len(self.testlist)))
                try:
                    input("Preconditions:\n%s\n\nPress ENTER\n-->"
                          % (preconditions[self.testlist[i]].replace("\n", "")))
                except NameError:
                    pass
                except IndexError:
                    print("No preconditions for NLU commands!")
                _log("=========================== TEST #%03d ==========================="
                     % (self.testlist[i] + 1), self.logname)
                while True:
                    for test_index in range(len(test[self.testlist[i]])):
                        cid = test[self.testlist[i]][test_index].split("\t")[
                            0]  # reading database, splits commands into command id and phrase
                        command = test[self.testlist[i]][test_index].split("\t")[1].replace("\n", "")
                        try:
                            next_command = test[self.testlist[i]][test_index + 1].split("\t")[1].replace("\n", "")
                        except IndexError:
                            next_command = "End"
                        try:
                            exp = expected[self.testlist[i]][test_index].replace("\n", "")
                        except IndexError:
                            exp = "None"
                        if cid == "000":
                            attempt = 0
                            max_attempts = 8
                            while True:
                                # activate the infotainment microphone for the voice recognition
                                # (1: manual, 2: wake word, 3: automatic)
                                self.activate_mic(self.mic_mode)
                                if self.mic_mode == 2:
                                    attempt += 1
                                    if attempt == max_attempts:
                                        print("\nWake word not recognized for %d times. Manually activate the MIC and"
                                              "press ENTER to continue...\n-->" % max_attempts)
                                        _log("WAKE WORD NOT RECOGNIZED. SWITCHING TO MANUAL MODE", self.logname)
                                        break
                                    _log("HEY MASERATI", self.logname)
                                    self.issued_ww += 1
                                print("Press ENTER to continue ('r' to repeat)\n-->", end="")
                                if getch().decode("utf-8") == 'r':
                                    print("\nRepeating...")
                                    _log("REPEATING WAKEWORD", self.logname)
                                else:
                                    _log("MIC_ACTIVATED", self.logname)
                                    self.recognized_ww += 1
                                    break
                        else:
                            try:
                                while True:
                                    print("\nReproducing %s_%s.wav - '%s'" % (self.lang, cid, command))
                                    try:
                                        # the mouth reproduces the command (after adjusting the gain, if wanted)
                                        self.play_command(cid)
                                    except Exception as e:
                                        print("ERROR: %s" % e)
                                    _log("OSCAR: <<%s>> (%s_%s.wav)" % (command, self.lang, cid), self.logname)
                                    try:
                                        print("Expected behaviour --> %s\n" % exp)
                                    except NameError:
                                        pass
                                    # PLACE HERE THE FUNCTION TO LISTEN TO THE RADIO RESPONSE
                                    response = "[Answer]"
                                    if translate:
                                        translation = "Translation"
                                        _log("RADIO: <<%s>> - <<%s>>" % (response, translation), self.logname)
                                    else:
                                        _log("RADIO: <<%s>>" % response, self.logname)
                                    if len(test[self.testlist[i]]) > 1:
                                        print("Press ENTER to proceed with next step (%s) or 'r' to repeat\n-->"
                                              % next_command)
                                        q = getch()
                                        if q.decode("utf-8") == "r":
                                            print("\n\nRepeating step...", end="")
                                            _log("REPEATING STEP", self.logname)
                                        else:
                                            break
                                    else:
                                        break
                            except KeyboardInterrupt:
                                _log("CANCEL", self.logname)
                                break
                    self.cancel(1)
                    result = str(input("\nResult: 1(passed), 0(failed), r(repeat all)\n-->"))
                    r_time = _now()
                    print(result)
                    self.status += 1  # status updated
                    if result != "r":
                        while True:
                            if result == "0":
                                _log("END_TEST #%03d: FAILED" % (i + 1), self.logname)
                                note = input("Write notes if needed: ")
                                if len(note) > 0:
                                    _log("NOTE #%03d: %s" % ((i + 1), note), self.logname)
                                result = "%s\t%s\t%s\t" % (result, note, r_time.replace("_", " "))
                                self.failed.append(i + 1)
                                input("(ENTER)-->")
                                break
                            elif result == "1":
                                _log("END_TEST #%03d: PASSED" % (i + 1), self.logname)
                                note = input("Write notes if needed: ")
                                if len(note) > 0:
                                    _log("NOTE #%03d: %s" % ((i + 1), note), self.logname)
                                result = "%s\t%s\t%s\t" % (result, note, r_time.replace("_", " "))
                                break
                            else:
                                # TODO: fix bug when answered "r"
                                result = str(input("INVALID INPUT: 1(passed), 0(failed), r(repeat all)\n-->"))
                        break
                    else:  # repeats test
                        _log("REPEATING", self.logname)
                    # cancels prompt
                    input("Press ENTER -->")
                try:
                    # at the end of the selected test, writes the results into a array
                    self.results[str(self.testlist[i] + 1)].append(result)
                except KeyError:
                    self.results[str(self.testlist[i] + 1)] = []
                    self.results[str(self.testlist[i] + 1)].append(result)
                self.save_conf()  # save current progress of the test
                self.running, self.completed = self._check_completed()
                if self.completed > 0 and not self.running:
                    self._complete()
        except KeyboardInterrupt:
            print("------------------------------------------------------------------")
            print("Test aborted! Saving...")
            _log("TEST_INTERRUPTED", self.logname)
            self.status = self.testlist[i]
            _log("TEST_STATUS: %03d" % self.status, self.logname)
            self.save_conf()  # save current progress of the test
            return

        except Exception as e:
            print("------------------------------------------------------------------")
            print("Test aborted due to a error (%s)! Saving..." % e)
            _log("ERROR %s" % e, self.logname)
            self.status = self.testlist[i]
            _log("TEST_STATUS: %03d" % self.status, self.logname)
            self.save_conf()  # save current progress of the test
            return

        self._complete()
        self.save_conf()  # save current progress of the test
        _clr_tmp()
        return self.status

    def _complete(self):
        _log("======================================================", self.logname)
        _log("TEST_STATUS: COMPLETED! CONGRATULATIONS", self.logname)
        _log("======================================================", self.logname)
        self.running, self.completed = self._check_completed()
        self.status = 0
        self.save_conf()  # save current progress of the test
        print_square("Test completed!\n\nSaving report as csv file")
        input('-->')
        self.print_report()
        return

    def print_report(self):
        """
        Print the results in a csv file suitable for the analysis with Excel.
        """
        report_file = "%s/report.csv" % self.wPath
        while True:
            try:
                print("\nSaving test results into %s...\n" % report_file)
                with open(report_file, "w", encoding="utf-16") as r:
                    r.write("LANGUAGE: %s\n" % self.lang)
                    r.write("WW RATIO:\t %0.2f\n" % (self.recognized_ww / self.issued_ww))
                    r.write("TEST N.\tRESULT\tCOMMENT\tTIMESTAMP\n")
                    for i in range(len(self.results)):
                        # write key
                        r.write("%s\t" % list(self.results.keys())[i])
                        for result in self.results[list(self.results.keys())[i]]:
                            r.write("%s\t" % result)
                        r.write("\n")

                _log("PRINTED REPORT", self.logname)
                break
            except PermissionError:
                input("Can't access to file! Make sure it's not open and press ENTER to continue\n-->")
        return


if __name__ == "__main__":
    # show splash screen
    splash()
    # declare a new test
    t = Test()
    # execute test
    t.execution()
