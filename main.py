# /.venv/bin/python
import os
import shutil
import sys
import time
import webbrowser
from random import randint
from source import metadata
from source.testloop import Test
from source.testloop import langDict, show_dirs, log, now, nonsense
from source.testloop import TestExistsError, CorruptedTestError

# gui utilities
import tkinter as tk
from tkinter import messagebox
from PyQt5 import QtGui
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from source.gui.about import Ui_About
from source.gui.newtest import Ui_Dialog
from source.gui.note import Note_Dialog
from source.gui.result import ResultDialog
from source.gui.resume import Ui_Resume
from source.gui.settings import Ui_Settings
from source.gui.splash import Ui_Splash
from source.gui.window import Ui_MainWindow
from source.gui.record import Ui_Record


class GuiTest(Test):
    pass


class RecordDialog(QDialog):
    def __init__(self):
        super(RecordDialog, self).__init__()
        self.ui = Ui_Record()
        self.ui.setupUi(self)
        self.ui.pushButton.pressed.connect(lambda: self.measure_noise())
        self.setWindowIcon(QtGui.QIcon('source/gui/ico.ico'))
        self.setWindowTitle("VoRTEx")

    def measure_noise(self):
        self.ui.pushButton.setEnabled(False)
        self.ui.pushButton.setText("Recording...")
        app.processEvents()
        t.measure_noise()
        self.ui.label.setText("Done! Background noise: %0.2fdBA" % t.noise)
        self.ui.pushButton.setEnabled(True)
        self.ui.pushButton.setText("OK")
        self.ui.pushButton.pressed.disconnect()
        self.ui.pushButton.pressed.connect(lambda: self.close())

    def measure_noise_radio(self):
        self.ui.pushButton.setEnabled(False)
        self.ui.pushButton.setText("Recording...")
        app.processEvents()
        t.measure_noise_radio()
        self.ui.label.setText("Done! Background noise + radio: %0.2fdBA" % t.noise_radio)
        self.ui.pushButton.setEnabled(True)
        self.ui.pushButton.setText("OK")
        self.ui.pushButton.pressed.disconnect()
        self.ui.pushButton.pressed.connect(lambda: self.close())


# main window
class MyMain(QMainWindow):
    def __init__(self):
        super(MyMain, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.raise_()
        self.setWindowIcon(QtGui.QIcon('source/gui/ico.ico'))
        self.setStyleSheet(stylesheet)
        # actions
        self.ui.actionNew.triggered.connect(self.on_newbutton_triggered)
        self.ui.actionSave.triggered.connect(lambda: self.save_pressed())
        self.ui.actionResume.triggered.connect(lambda: self.resume_pressed())
        self.ui.actionQuit.triggered.connect(lambda: self.close())
        self.ui.actionOnline_guide.triggered.connect(lambda: self.open_guide())
        self.ui.actionAudio_device.triggered.connect(lambda: self.open_settings())
        self.ui.actionAbout.triggered.connect(lambda: self.about())
        # buttons
        self.ui.pushButton.pressed.connect(lambda: self.lombard_pressed())
        self.ui.pushButton_2.pressed.connect(lambda: self.measure_noise())
        self.ui.pushButton_3.pressed.connect(lambda: self.measure_noise_radio())
        self.ui.playButton.pressed.connect(lambda: self.do_test())
        self.ui.playButton.pressed.connect(lambda: self.update())
        self.ui.playButton.pressed.connect(lambda: self.update_screens())
        self.ui.repeatButton.pressed.connect(lambda: self.repeat())
        self.ui.printButton.setText("Export csv")
        self.ui.printButton.clicked.connect(lambda: self.print_csv())
        self.ui.commandsBox.doubleClicked.connect(lambda: self.double_clicked_command())
        self.condition = -1
        self.update_screens()
        self.update()
        self.update()
        app.processEvents()
        print(t.logname)

    def print_csv(self):
        t.print_report()
        if messagebox.askyesno("VoRTEx", "CSV file saved. Do you want to open it?"):
            self.open_csv()

    @staticmethod
    def open_csv():
        os.system(t.report_file.replace("/", "\\"))

    @staticmethod
    def open_settings():
        sett = Settings()
        sett.exec_()

    def double_clicked_command(self):
        self.condition = self.ui.commandsBox.currentRow()
        self.do_test()

    def update_screens(self):
        self.ui.commandsBox.clear()
        if self.condition >= 0:
            for i in range(len(t.sequence[t.testlist[t.status]])):
                self.ui.commandsBox.addItem(t.sequence[t.status][i].replace("\t", "->").replace("\n", ""))
            self.ui.expectedBox.clear()
            for i in range(len(t.expected[t.testlist[t.status]])):
                self.ui.expectedBox.addItem(t.expected[t.status][i].replace("\t", "->").replace("\n", ""))
            self.ui.precBox.clear()
            try:
                self.ui.precBox.setText(t.preconditions[t.testlist[t.status]])
            except NameError:
                self.ui.precBox.setText("No preconditions available")
            except IndexError:
                self.ui.precBox.setText("No preconditions available")

    def repeat(self):
        self.condition -= 1
        cid = t.sequence[t.testlist[t.status]][self.condition].split("\t")[0]
        print("Repeating %s" % cid)
        if cid == "000":
            log("REPEATING WAKEWORD", t.logname)
        else:
            log("REPEATING COMMAND", t.logname)
        self.do_test()

    def measure_noise(self):
        if not t.recorder.calibrated[t.earChannel]:
            messagebox.showerror("VoRTEx", "You first have to calibrate the ear")
            return
        r = RecordDialog()
        r.ui.label.setText("Turn OFF the radio and press OK to measure the background noise")
        r.resize(r.sizeHint())
        r.ui.pushButton.pressed.disconnect()
        r.ui.pushButton.pressed.connect(lambda: r.measure_noise())
        r.exec_()
        self.update()

    def measure_noise_radio(self):
        if not t.recorder.calibrated[t.earChannel]:
            messagebox.showerror("VoRTEx", "You first have to calibrate the ear")
            return
        r = RecordDialog()
        r.ui.label.setText("Turn ON the radio and press OK to measure the background noise")
        r.resize(r.sizeHint())
        r.ui.pushButton.pressed.disconnect()
        r.ui.pushButton.pressed.connect(lambda: r.measure_noise_radio())
        r.exec_()
        self.update()

    def do_test(self):
        print(t.status)
        print(self.condition)
        if self.condition == -1:
            # First step
            if t.isLombardEnabled:
                self.measure_noise()
                self.measure_noise_radio()
            if not t.isRunning:
                # start test from 0
                print(t.logname)
                log("MAY THE FORCE BE WITH YOU", t.logname)  # the first line of the log file
                t.results = {}
                t.isRunning = True
            else:
                # resume the test
                log("WELCOME BACK", t.logname)

            # takes just the commands for the chosen language
            log("SELECTED LANGUAGE: %s - %s" % (t.lang, langDict[t.lang]), t.logname)
            self.condition += 1
            self.update()

        else:
            self.update_screens()
            self.ui.commandsBox.setCurrentRow(self.condition)
            self.ui.expectedBox.setCurrentRow(self.condition)
            try:
                previous_cid = t.sequence[t.testlist[t.status]][self.condition - 1].split("\t")[0]
                command = t.sequence[t.testlist[t.status]][self.condition].split("\t")[1].replace("\n", "")
                cid = t.sequence[t.testlist[t.status]][self.condition].split("\t")[0]
                if self.condition == 0:
                    log("=========================== TEST #%03d ==========================="
                        % (t.testlist[t.status] + 1), t.logname)
                if cid == "000":
                    log("HEY MASERATI", t.logname)
                    t.issued_ww += 1
                else:
                    if previous_cid == "000":
                        log("MIC ACTIVATED", t.logname)
                        t.recognized_ww += 1
                try:
                    next_command = t.sequence[t.testlist[t.status]][self.condition + 1].split("\t")[1].replace("\n", "")
                    next_cid = t.sequence[t.testlist[t.status]][self.condition + 1].split("\t")[0]
                except IndexError:
                    try:
                        next_command = t.sequence[t.testlist[t.status + 1]][0].split("\t")[1].replace("\n", "")
                        next_cid = t.sequence[t.testlist[t.status + 1]][0].split("\t")[0]
                    except IndexError:
                        next_cid = "000"
                        next_command = "End"
                #  Play wave file
                filename = t.phrasesPath + "/" + t.lang + "_" + str(next_cid) + ".wav"
                app.processEvents()
                self.ui.wavLabel.setText("Wave file: %s" % filename)
                log("OSCAR: <<%s>> (%s)" % (command, filename), t.logname)
                t.play_command(cid)
                # play button text
                if next_cid == "000":
                    self.ui.playButton.setText("PTT")
                else:
                    self.ui.playButton.setText("Play command: %s" % next_command)
                if self.condition + 1 == len(t.sequence[t.status]):
                    self.ui.playButton.setText("End test")
                    pass
                self.condition += 1

            except IndexError:
                t.cancel()
                r = self.results()
                r_time = now()
                if r != "r":
                    if r == "1":
                        print("PASS")
                        log("END_TEST #%03d: PASS" % (t.status + 1), t.logname)
                        t.passes += 1
                    elif r == "0":
                        print("FAIL")
                        log("END_TEST #%03d: FAILED" % (t.status + 1), t.logname)
                    note = self.note()
                    if len(note) > 0:
                        log("NOTE #%03d: %s" % ((t.status + 1), note), self.logname)
                    result = "%s\t%s\t%s\t" % (r, note, r_time.replace("_", " "))
                    try:
                        t.results[str(t.testlist[t.status] + 1)].append(result)
                    except KeyError:
                        t.results[str(t.testlist[t.status] + 1)] = []
                        t.results[str(t.testlist[t.status] + 1)].append(result)
                else:
                    print("REPEATING")
                    log("REPEATING TEST", t.logname)
                    t.status -= 1
                self.ui.playButton.setText("PTT")
                self.update()
                t.status += 1
                t.isSaved = False
                self.update_screens()
                self.condition = 0

        if self.condition > 0:
            self.ui.repeatButton.setEnabled(True)
        else:
            self.ui.repeatButton.setEnabled(False)

            # calibrate
        # elif self.condition == 1:

        #    print(t.sequence[t.testlist[t.status]])
        #    print("Condition = 1")

    def lombard_pressed(self):
        t.isLombardEnabled = not t.isLombardEnabled
        self.update()

    @staticmethod
    def results():
        result_box = TestResultDialog()
        result_box.exec()
        result = result_box.value
        print(result)
        return result

    @staticmethod
    def note():
        n = Note()
        n.exec_()
        return n.text

    def stop_test(self):
        self.condition = -1
        self.update()
        log("TEST INTERRUPTED", t.logname)
        pass

    @staticmethod
    def about():
        a = About()
        a.exec_()

    @staticmethod
    def open_guide():
        webbrowser.open(guidelink)

    @staticmethod
    def open_log():
        print(t.logname.replace("/", "\\"))
        os.system("notepad %s" % t.logname.replace("/", "\\"))

    def clear_screens(self):
        self.ui.commandsBox.clear()
        self.ui.precBox.clear()
        self.ui.expectedBox.clear()

    def resume_pressed(self):
        if len(tests) == 0:
            messagebox.showinfo("VoRTEx", "No tests found! Better to start a new one")
        else:
            resume = Resume()
            resume.exec_()
        self.update()

    def closeEvent(self, a0: QtGui.QCloseEvent) -> None:
        if not t.isSaved:
            if messagebox.askyesnocancel("VoRTEx", "Any progress will be lost. Do you want to save?"):
                self.save_pressed()
        quit()

    def save_pressed(self):
        t.save()
        t.save_settings()
        self.update()

    def on_newbutton_triggered(self):
        newdialog = NewDialog()
        newdialog.exec_()
        self.update()

    def update(self):
        print(t.noise)
        if self.condition == -1:  # test to be started
            if t.isRunning:
                self.ui.playButton.setText("Resume test")
            else:
                self.ui.playButton.setText("Start test")
        elif self.condition == 0:  # test started, PTT to be enabled
            self.ui.playButton.setEnabled(True)
            self.ui.repeatButton.setEnabled(False)
            self.ui.playButton.setText("PTT")
        if t.isSaved:
            self.setWindowTitle("VoRTEx - %s" % t.testName)
        else:
            self.setWindowTitle("VoRTEx - %s*" % t.testName)
        if t.isRunning:
            self.ui.statusLabel.setText("Status: RUNNING")
        else:
            self.ui.statusLabel.setText("Status: WAITING")
        self.ui.groupBox_2.setTitle("Test %s of %s" % (t.status + 1, len(t.testlist)))
        progress = round(100 * t.status / len(t.testlist))
        self.ui.progressBar.setProperty("value", progress)
        if t.isMultigenderEnabled:
            if t.gender == 0:
                self.ui.langLabel.setText("Language: %s (F)" % langDict[t.lang])
            elif t.gender == 1:
                self.ui.langLabel.setText("Language: %s (M)" % langDict[t.lang])
        else:
            self.ui.langLabel.setText("Language: %s" % langDict[t.lang])
        self.ui.completedLabel.setText("Completed: %d test(s)" % t.status)
        self.ui.lengthLabel.setText("Test length: %d" % len((t.database[t.lang])))
        try:
            self.ui.scoreLabel.setText("Score: {0:.0%}".format(t.passes / t.status))
        except ZeroDivisionError:
            self.ui.scoreLabel.setText("Score: (not started yet)")
        try:
            self.ui.wwLabel.setText("WW accuracy: {0:.0%}".format(t.recognized_ww / t.issued_ww))
        except ZeroDivisionError:
            self.ui.wwLabel.setText("WW accuracy: (not started yet)")
        self.ui.pushButton_2.setEnabled(t.isLombardEnabled)
        self.ui.pushButton_3.setEnabled(t.isLombardEnabled)
        self.ui.noiseLabel.setDisabled(not t.isLombardEnabled)
        self.ui.noiseLabel_2.setDisabled(not t.isLombardEnabled)
        if t.isLombardEnabled:
            self.ui.lombardLabel.setText("Lombard effect: enabled")
            self.ui.pushButton.setText("Disable")
        else:
            self.ui.lombardLabel.setText("Lombard effect: disabled")
            self.ui.pushButton.setText("Enable")
        self.ui.noiseLabel.setText("BG noise: %0.2fdBA" % t.noise)
        self.ui.noiseLabel_2.setText("BG noise + radio: %0.2fdBA" % t.noise_radio)
        app.processEvents()
        self.resize(self.sizeHint())
        app.processEvents()


# result dialog
class TestResultDialog(QDialog):
    def __init__(self):
        super(TestResultDialog, self).__init__()
        self.ui = ResultDialog()
        self.ui.setupUi(self)
        self.setWindowIcon(QtGui.QIcon('source/gui/ico.ico'))
        self.ui.label.setStyleSheet("color: black")
        self.ui.pushButton.pressed.connect(lambda: self.on_clicked("1"))
        self.ui.pushButton_2.pressed.connect(lambda: self.on_clicked("0"))
        self.ui.pushButton_3.pressed.connect(lambda: self.on_clicked("r"))
        self.value = 1

    def on_clicked(self, value):
        self.value = value
        self.close()
        return

    def closeEvent(self, a0: QtGui.QCloseEvent) -> None:
        self.close()
        MainWindow.update()
        return


# dialog to insert note regarding the result of the test
class Note(QDialog):
    def __init__(self):
        super(Note, self).__init__()
        self.setWindowIcon(QtGui.QIcon('source/gui/ico.ico'))
        self.ui = Note_Dialog()
        self.ui.setupUi(self)
        self.ui.label.setStyleSheet("color: black")
        self.text = ""
        self.ui.pushButton.pressed.connect(lambda: self.on_clicked())

    def on_clicked(self):
        self.text = self.ui.lineEdit.text()
        self.close()


# settings window
class Settings(QDialog):
    def __init__(self):
        super(Settings, self).__init__()
        self.ui = Ui_Settings()
        self.ui.setupUi(self)
        self.ui.comboBox.setCurrentIndex(t.recorder.deviceIn)
        self.ui.comboBox_2.setCurrentIndex(t.recorder.deviceOut - len(t.recorder.devicesIn))
        self.ui.pushButton.pressed.connect(lambda: self.submit())
        self.ui.pushButton_2.pressed.connect(lambda: self.apply())
        self.ui.pushButton_3.pressed.connect(lambda: self.cancel())
        self.ui.mouth_button.pressed.connect(lambda: self.calibrate_mouth())
        self.ui.ear_button.pressed.connect(lambda: self.calibrate_ear())
        self.ui.mic_button.pressed.connect(lambda: self.calibrate_mic())
        for i in range(len(t.recorder.devicesIn)):
            self.ui.comboBox.addItem(t.recorder.devicesIn[i].get('name'))
        for i in range(len(t.recorder.devicesOut)):
            self.ui.comboBox_2.addItem(t.recorder.devicesOut[i].get('name'))
        if t.isLombardEnabled:
            self.ui.checkBox.setChecked(True)
        else:
            self.ui.checkBox.setChecked(False)
        if t.mic_mode == 2:
            self.ui.radioButton.setChecked(True)
        elif t.mic_mode == 1:
            self.ui.radioButton_2.setChecked(True)
        self.update_calib()

    def calibrate_mic(self):
        messagebox.showinfo("VoRTEx", "Please place the measurement microphone into the calibrator and press OK")
        self.ui.mic_calibration.setText("calibrating...")
        t.calibrate_mic()
        messagebox.showinfo("VoRTEx", "Mic calibration completed: dBSPL/dBFS = %0.2f" % t.recorder.correction[0])
        self.update_calib()
        return

    def calibrate_ear(self):
        messagebox.showinfo("VoRTEx", "Please place the calibrator into the ear and press OK")
        self.ui.ear_calibration.setText("calibrating...")
        t.calibrate_ear()
        print(t.recorder.correction)
        messagebox.showinfo("VoRTEx", "Mic calibration completed: dBSPL/dBFS = %0.2f" % t.recorder.correction[1])
        self.update_calib()
        return

    def calibrate_mouth(self):
        if not t.recorder.calibrated[0]:
            messagebox.showerror("VoRTEx", "You need to calibrate the measurement microphone first")
            return
        messagebox.showinfo("VoRTEx", "Please place the measurement microphone at the MRP and press OK to continue")
        self.ui.mouth_gain.setText("calibrating...")
        t.calibrate_mouth()
        messagebox.showinfo("VoRTEx", "Mouth calibration completed")
        self.update_calib()
        return

    def update_calib(self):
        if t.isMouthCalibrated:
            self.ui.mouth_gain.setText("Gain = %0.2ddB" % t.gain)
        else:
            self.ui.mouth_gain.setText("calib. needed")
        print(t.recorder.correction[1])
        if t.recorder.calibrated[0]:
            self.ui.mic_calibration.setText("dBSPL/dBFS = %0.2f" % t.recorder.correction[0])
        else:
            self.ui.mic_calibration.setText("calib. needed")
        print(t.recorder.correction[1])
        if t.recorder.calibrated[1]:
            self.ui.ear_calibration.setText("dBSPL/dBFS = %0.2f" % t.recorder.correction[1])
        else:
            self.ui.ear_calibration.setText("calib. needed")
        print("DEBUG")

    def submit(self):
        self.apply()
        self.close()

    def apply(self):
        t.isLombardEnabled = self.ui.checkBox.isChecked()
        if self.ui.radioButton.isChecked():
            t.mic_mode = 2
        else:
            t.mic_mode = 1
        print("Microphone mode: %d" % t.mic_mode)
        t.recorder.deviceIn = self.ui.comboBox.currentIndex()
        t.recorder.deviceOut = self.ui.comboBox_2.currentIndex() + len(t.recorder.devicesIn)
        t.save_settings()
        MainWindow.update()

    def cancel(self):
        self.close()


# window containing the metadata
class About(QDialog):
    def __init__(self):
        super(About, self).__init__()
        self.setWindowIcon(QtGui.QIcon('source/gui/ico.ico'))
        self.ui = Ui_About()
        self.ui.setupUi(self)
        self.ui.label_2.setText("VoRTEx v%s - Voice Recognition Test Execution" % metadata["version"])
        self.ui.label_3.setText(metadata["description_short"])
        self.ui.label_3.setAlignment(Qt.AlignCenter)
        self.ui.label_4.setText("Os: %s" % metadata["os"])
        self.ui.label_5.setText(metadata["copyright"])
        self.ui.label_6.setText(metadata["email"])
        self.ui.label_7.setText(metadata["url"])

    def closeEvent(self, a0: QtGui.QCloseEvent) -> None:
        self.close()


# dialog to resume a test
class Resume(QDialog):
    def __init__(self):
        super(Resume, self).__init__()
        self.ui = Ui_Resume()
        self.ui.setupUi(self)
        self.setWindowIcon(QtGui.QIcon('source/gui/ico.ico'))
        self.ui.listWidget.doubleClicked.connect(lambda: self.on_resume_pressed())
        self.ui.resumeButton.pressed.connect(lambda: self.on_resume_pressed())
        self.ui.cancelButton.pressed.connect(lambda: self.close())
        self.ui.cancelButton_2.pressed.connect(lambda: self.delete_test())
        self.ui.newButton.pressed.connect(lambda: self.new_pressed())
        self.ui.listWidget.itemClicked.connect(lambda: self.update_info())
        self.test_list = []
        self.setWindowTitle("Resume test")
        self.update_list()

    def new_pressed(self):
        print(t.isFirstStart)
        n = NewDialog()
        n.exec_()
        self.close()

    def update_list(self):
        self.test_list = show_dirs(t.testDir)
        self.ui.listWidget.clear()
        for i in range(len(self.test_list)):
            self.ui.listWidget.addItem(self.test_list[i])

    def delete_test(self):
        tbd = t.testDir + self.test_list[self.ui.listWidget.currentRow()]
        if t.wPath == tbd:
            messagebox.showerror("VoRTEx", "You cannot delete the test in progress")
        else:
            if messagebox.askyesno("VoRTEx", "Do you really want to delete the selected test? (This can't be undone)"):
                try:
                    shutil.rmtree(tbd)
                    self.update_list()
                except PermissionError:
                    messagebox.showerror("VoRTEx", "Permission denied!")

    def update_info(self):
        path = t.testDir + tests[self.ui.listWidget.currentRow()]
        created = time.strftime('%Y/%m/%d at %H:%M:%S', time.gmtime(os.path.getctime(path)))
        modified = time.strftime('%Y/%m/%d at %H:%M:%S', time.gmtime(os.path.getmtime(path)))
        self.ui.textBrowser.setText("Created:\n%s\n\nLast modified:\n%s" % (created, modified))

    def on_resume_pressed(self):
        if not t.isSaved:
            if messagebox.askyesno("VoRTEx",
                                   "Do you want to save the current text (any unsaved progress will be lost)?"):
                t.save()
        t.resume(t.testDir + self.test_list[self.ui.listWidget.currentRow()])
        MainWindow.update()
        self.close()

    def closeEvent(self, a0: QtGui.QCloseEvent) -> None:
        if t.isFirstStart:
            quit()


# dialog to start a new test
class NewDialog(QDialog):
    def __init__(self):
        super(NewDialog, self).__init__()
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)
        self.setWindowIcon(QtGui.QIcon('source/gui/ico.ico'))
        self.setWindowTitle("Start new test")
        default_database = "/database/r1h.vrtl"
        self.ui.databaseLabel.setText(default_database)
        self.ui.nameEdit.textEdited.connect(lambda: self.update_ok())
        self.ui.pushButton.clicked.connect(lambda: self.browse_pressed())
        self.ui.submitButton.clicked.connect(lambda: self.submit_pressed())
        self.ui.langBox.setCurrentIndex(5)
        self.ui.langBox.currentIndexChanged.connect(lambda: self.update())
        self.ui.radioButton.setChecked(True)
        self.ui.submitButton.setEnabled(False)
        if t.mic_mode == 1:
            self.ui.radioButton_5.setChecked(True)
        else:
            self.ui.radioButton_6.setChecked(True)
        t.load_database(default_database)
        self.fill_lang_combo()
        self.ui.checkBox.setChecked(t.isLombardEnabled)

    def update_ok(self):
        print("Ciao")
        if self.ui.nameEdit.text().replace(" ", "") == "":
            self.ui.submitButton.setEnabled(False)
        else:
            self.ui.submitButton.setEnabled(True)
        return

    def browse_pressed(self):
        t.testlist = self.ui.databaseLabel.text()
        t.load_database()
        self.ui.databaseLabel.setText(t.listfile)
        self.fill_lang_combo()

    def submit_pressed(self):
        if not t.isSaved:
            if messagebox.askyesno("VoRTEx",
                                   "Do you want to save the current text (any unsaved progress will be lost)?"):
                t.save()
        try:
            # set multigender
            if t.isMultigenderEnabled:
                if self.ui.radioButton.isChecked():
                    t.gender = 0
                else:
                    t.gender = 1
            else:
                t.gender = None
            # set micmode
            if self.ui.radioButton_5.isChecked():
                t.mic_mode = 1
            else:
                t.mic_mode = 2
            # set lombard
            t.isLombardEnabled = self.ui.checkBox.isChecked()
            # setup a new test
            t.new(self.ui.nameEdit.text(), self.ui.langBox.currentIndex(), t.gender)
            t.save_settings()
            t.isFirstStart = False
            self.close()
        except TestExistsError:
            messagebox.showerror("Vortex", "The test %s already exists. Please choose another name"
                                 % self.ui.nameEdit.text())

    def update(self):
        t.lang = t.langs[self.ui.langBox.currentIndex()]
        self.ui.label_5.setText("Number of tests: %d" % len(t.database[t.lang]))
        g = 0
        for i in os.listdir(t.database["AUDIOPATH"]):
            if t.lang in i:
                g += 1
        if g == 2:
            t.isMultigenderEnabled = True
        else:
            t.isMultigenderEnabled = False

        self.ui.radioButton.setEnabled(t.isMultigenderEnabled)
        self.ui.radioButton_2.setEnabled(t.isMultigenderEnabled)

    def fill_lang_combo(self):
        self.ui.langBox.clear()
        print(t.langs)
        try:
            for i in range(len(t.langs)):
                self.ui.langBox.addItem(langDict[t.langs[i]])
        except AttributeError:
            pass


# splash screen
class SplashScreen(QDialog):
    def __init__(self):
        super(SplashScreen, self).__init__()
        self.ui = Ui_Splash()
        self.setWindowFlag(Qt.WindowStaysOnTopHint)
        self.ui.setupUi(self)
        self.ui.label_2.setText("Loading...")
        self.ui.label_2.setStyleSheet("color: grey")
        self.ui.label_2.setAlignment(Qt.AlignHCenter)
        self.ui.label_3.setStyleSheet("color: grey")
        self.ui.label_3.setText(metadata["version"])
        self.ui.label_4.setStyleSheet("color: grey")
        self.ui.label_4.setText(metadata["description_short"])
        self.ui.label_4.setAlignment(Qt.AlignHCenter)
        self.ui.label_6.setStyleSheet("color: grey")
        self.ui.label_6.setText(metadata["copyright"])
        self.ui.label_7.setStyleSheet("color: grey")
        self.ui.label_7.setText(metadata["email"])
        self.ui.label_8.setStyleSheet("color: grey")
        self.ui.label_8.setText(metadata["url"])
        self.setWindowFlag(Qt.FramelessWindowHint)
        self.ui.label.setPixmap(QtGui.QPixmap("source/gui/vortex_splash.png"))
        self.ui.progressBar.setValue(0)
        self.progress = 0

    @staticmethod
    def load(value):
        splash.ui.label_2.setText(nonsense[randint(0, len(nonsense)) - 1])
        splash.ui.progressBar.setValue(value)
        time.sleep(0.2)


stylesheet = """
    MyMain {
        border-image: url("source/gui/vortex_bg.jpg"); 
    }
    QLabel {
        color: white;
    }
    QGroupBox {
        color: white;
    }
    QProgressBar {
        color: white;
    }
"""

if __name__ == "__main__":
    print(metadata["version"])
    # creating application
    app = QApplication(sys.argv)
    splash = SplashScreen()  # defining the splashscreen
    splash.show()
    app.processEvents()
    splash.load(20)
    guidelink = "https://github.com/albertoccelli/VoRTEx/blob/main/README.md"
    iconfile = "source/gui/ico.ico"
    splash.load(40)
    root = tk.Tk()
    root.iconbitmap(r'source/gui/ico.ico')
    root.title('VoRTEx')
    root.withdraw()
    splash.load(60)
    t = GuiTest()  # create new istance of the test
    tests = show_dirs(t.testDir)
    splash.load(80)
    try:
        t.resume_last()
        t.isFirstStart = False
    except CorruptedTestError:
        t.isFirstStart = True
        print(messagebox.showerror("VoRTEx", "Test corrupted!! Please resume another one"))
        res = Resume()
        res.exec_()
    except FileNotFoundError:
        t.isFirstStart = True
        res = Resume()
        res.exec_()
    splash.load(99)
    time.sleep(0.5)
    # open main window
    MainWindow = MyMain()
    MainWindow.show()
    splash.close()  # close splashscreen
    sys.exit(app.exec_())
