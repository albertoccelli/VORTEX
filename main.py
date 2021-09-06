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
from source.gui.note import Ui_Note_Dialog
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
        self.autosave = True
        # actions
        self.ui.actionNew_2.triggered.connect(self.on_newbutton_triggered)
        self.ui.actionSave.triggered.connect(lambda: self.save_pressed())
        self.ui.actionResume.triggered.connect(lambda: self.resume_pressed())
        self.ui.actionQuit.triggered.connect(lambda: self.close())
        self.ui.actionOnline_guide.triggered.connect(lambda: self.open_guide())
        self.ui.actionAudio_device.triggered.connect(lambda: self.open_settings())
        self.ui.actionAbout.triggered.connect(lambda: self.about())
        # buttons
        self.ui.cancel_button.pressed.connect(lambda: self.cancel_pressed())
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
        self.ww_waiting = False
        print("Current test: %s" % t.current_test)
        app.processEvents()

    def cancel_pressed(self):
        self.condition = len(t.sequence[t.testlist[t.current_test]])
        self.do_test()

    @staticmethod
    def recap_test():
        messagebox.showinfo("%s" % t.testName, "Test progress: \n"
                                               "language: %s\n"
                                               "status: %d/%d\n"
                                               "results: %d/%d passed" %
                            (langDict[t.lang], t.current_test, len(t.testlist), t.passes, len(t.testlist)))

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

    def repeat(self):
        self.condition -= 1
        cid = t.sequence[t.testlist[t.current_test]][self.condition].split("\t")[0]
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
        r.ui.pushButton.pressed.disconnect()
        r.ui.pushButton.pressed.connect(lambda: r.measure_noise_radio())
        r.exec_()
        self.update()

    def do_review(self):
        if messagebox.askyesno("VoRTEx", "Do you really want to start a new test with just the errors of this one?"):
            newname = Note()
            newname.ui.label.setText("Choose a name for the test")
            newname.exec_()
            print("REDOING :")
            print(t.redo)
            t.new(testname=newname.text, l_index=None, testlist=t.redo)
            print("REDOING :")
            print(t.testlist)
            self.update()

    def do_test(self):
        print(self.condition)
        if self.condition == -1:
            # Recap test progress
            self.recap_test()
            # First step
            if t.isLombardEnabled:
                if (not t.recorder.calibrated[t.micChannel]) or (not t.recorder.calibrated[t.earChannel]) or (
                        not t.isMouthCalibrated):
                    want_to_calibrate = messagebox.askyesno("VoRTEx", "You first have to calibrate the microphones and "
                                                                      "the mouth in order to apply the Lombard effect. "
                                                                      "Do you want to do it now?")
                    if not want_to_calibrate:
                        t.isLombardEnabled = False
                        self.update()
                    else:
                        if not t.recorder.calibrated[t.micChannel]:
                            messagebox.showinfo("VoRTEx",
                                                "Please place the measurement mirophone into the calibrator and "
                                                "press OK")
                            t.calibrate_mic()
                            messagebox.showinfo("VoRTEx", "Mic calibration completed: dBSPL/dBFS = %0.2f"
                                                % t.recorder.correction[t.mouthChannel])
                        if not t.recorder.calibrated[t.earChannel]:
                            messagebox.showinfo("VoRTEx", "Please place the calibrator into the ear and press OK")
                            t.calibrate_ear()
                            messagebox.showinfo("VoRTEx", "Mic calibration completed: dBSPL/dBFS = %0.2f"
                                                % t.recorder.correction[t.earChannel])
                        if not t.isMouthCalibrated:
                            messagebox.showinfo("VoRTEx",
                                                "Please place the measurement microphone at the MRP and press OK")
                            t.calibrate_mouth()
                            messagebox.showinfo("VoRTEx", "Mouth calibration completed: gain = %0.2f"
                                                % t.gain)
                        self.measure_noise()
                        self.measure_noise_radio()
                else:
                    self.measure_noise()
                    self.measure_noise_radio()
            if t.status == 0:
                # start test from 0
                log("MAY THE FORCE BE WITH YOU", t.logname)  # the first line of the log file
                t.results = {}
                t.status = 1
            else:
                # resume the test
                log("WELCOME BACK", t.logname)

            # takes just the commands for the chosen language
            log("SELECTED LANGUAGE: %s - %s" % (t.lang, langDict[t.lang]), t.logname)
            self.condition += 1
            self.update()

        else:
            if self.condition == 0:
                t.issued_ww += 1
                self.ww_waiting = True
                print("WW issued")
            if self.condition == 1:
                if self.ww_waiting:
                    print("WW recognized")
                    t.recognized_ww += 1
                    self.ww_waiting = False
            self.update_screens()
            self.ui.commandsBox.setCurrentRow(self.condition)
            self.ui.expectedBox.setCurrentRow(self.condition)
            try:
                previous_cid = t.sequence[t.testlist[t.current_test]][self.condition - 1].split("\t")[0]
                command = t.sequence[t.testlist[t.current_test]][self.condition].split("\t")[1].replace("\n", "")
                cid = t.sequence[t.testlist[t.current_test]][self.condition].split("\t")[0]
                if self.condition == 0:
                    log("=========================== TEST #%03d ==========================="
                        % (t.testlist[t.current_test] + 1), t.logname)
                if cid == "000":
                    log("HEY MASERATI", t.logname)
                else:
                    if previous_cid == "000":
                        log("MIC ACTIVATED", t.logname)
                try:
                    next_command = t.sequence[t.testlist[t.current_test]][self.condition + 1].split("\t")[1].replace(
                        "\n", "")
                    next_cid = t.sequence[t.testlist[t.current_test]][self.condition + 1].split("\t")[0]
                except IndexError:
                    try:
                        next_command = t.sequence[t.testlist[t.current_test + 1]][0].split("\t")[1].replace("\n", "")
                        next_cid = t.sequence[t.testlist[t.current_test + 1]][0].split("\t")[0]
                    except IndexError:
                        next_cid = "000"
                        next_command = "End"
                #  Play wave file
                filename = t.phrasesPath + "/" + t.lang + "_" + str(next_cid) + ".wav"
                app.processEvents()
                self.ui.wavLabel.setText("Wave file: %s" % filename)
                self.ui.gainLabel.setText("Gain adjust: %0.2fdB" % t.gain)
                log("OSCAR: <<%s>> (%s)" % (command, filename), t.logname)
                t.play_command(cid)
                # play button text
                if next_cid == "000":
                    self.ui.playButton.setText("PTT")
                else:
                    self.ui.playButton.setText("Play command: %s" % next_command)
                if self.condition + 1 == len(t.sequence[t.testlist[t.current_test]]):
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
                        log("END_TEST #%03d: PASS" % (t.current_test + 1), t.logname)
                        t.passes += 1
                    elif r == "0":
                        print("FAIL")
                        log("END_TEST #%03d: FAILED" % (t.current_test + 1), t.logname)
                    n = Note()
                    if r == '0':
                        n.ui.checkBox.setChecked(True)
                    n.exec_()
                    note = n.text
                    if len(note) > 0:
                        log("NOTE #%03d: %s" % ((t.current_test + 1), note), t.logname)
                    result = "%s\t%s\t%s\t" % (r, note, r_time)
                    if n.is_checked:
                        print("To be reviewed!")
                        t.redo.append(t.current_test)
                        print("REDO's list: ")
                        print(t.redo)
                    try:
                        t.results[str(t.testlist[t.current_test] + 1)] = result
                    except KeyError:
                        t.results[str(t.testlist[t.current_test] + 1)] = []
                        t.results[str(t.testlist[t.current_test] + 1)] = result
                    self.update()
                else:
                    print("REPEATING")
                    log("REPEATING TEST", t.logname)
                    t.current_test -= 1
                self.ui.playButton.setText("PTT")
                t.current_test += 1
                print("Current test: %s" % t.current_test)
                if t.current_test == len(t.testlist):
                    messagebox.showinfo("VoRTEx", "Congratulations! You just completed another test!\n"
                                                  "It wasn't easy, you deserve a cup of coffee ;)")
                    t.status = 2
                    t.current_test = 0
                    self.completed()
                t.isSaved = False
                self.update_table()
                self.update_screens()
                self.condition = 0

        if self.condition > 0:
            self.ui.cancel_button.setEnabled(True)
            self.ui.repeatButton.setEnabled(True)
        else:
            self.ui.repeatButton.setEnabled(False)
            self.ui.cancel_button.setEnabled(False)

            # calibrate
        # elif self.condition == 1:

        #    print(t.sequence[t.testlist[t.status]])
        #    print("Condition = 1")

    def lombard_pressed(self):
        t.isLombardEnabled = not t.isLombardEnabled
        if t.isLombardEnabled:
            if (not t.recorder.calibrated[t.micChannel]) or (not t.recorder.calibrated[t.earChannel]) or (
                    not t.isMouthCalibrated):
                want_to_calibrate = messagebox.askyesno("VoRTEx", "You first have to calibrate the microphones and "
                                                                  "the mouth in order to apply the Lombard effect. "
                                                                  "Do you want to do it now?")
                if not want_to_calibrate:
                    t.isLombardEnabled = False
                    self.update()
                else:
                    if not t.recorder.calibrated[t.micChannel]:
                        messagebox.showinfo("VoRTEx", "Please place the measurement mirophone into the calibrator and "
                                                      "press OK")
                        t.calibrate_mic()
                        messagebox.showinfo("VoRTEx", "Mic calibration completed: dBSPL/dBFS = %0.2f"
                                            % t.recorder.correction[t.mouthChannel])
                    if not t.recorder.calibrated[t.earChannel]:
                        messagebox.showinfo("VoRTEx", "Please place the calibrator into the ear and press OK")
                        t.calibrate_ear()
                        messagebox.showinfo("VoRTEx", "Mic calibration completed: dBSPL/dBFS = %0.2f"
                                            % t.recorder.correction[t.earChannel])
                    if not t.isMouthCalibrated:
                        messagebox.showinfo("VoRTEx", "Please place the measurement microphone at the MRP and press OK")
                        t.calibrate_mouth()
                        messagebox.showinfo("VoRTEx", "Mouth calibration completed: gain = %0.2f"
                                            % t.gain)
                    self.measure_noise()
                    self.measure_noise_radio()
            else:
                self.measure_noise()
                self.measure_noise_radio()
        self.update()

    @staticmethod
    def results():
        result_box = TestResultDialog()
        result_box.exec()
        result = result_box.value
        return result

    @staticmethod
    def note():
        n = Note()
        n.exec_()
        return n.text, n.is_checked

    @staticmethod
    def open_log():
        os.system("notepad %s" % t.logname.replace("/", "\\"))

    def completed(self):
        self.ui.playButton.disconnect()
        self.ui.playButton.setText("Review errors")
        self.ui.playButton.pressed.connect(lambda: self.do_review())

    @staticmethod
    def about():
        a = About()
        a.exec_()

    @staticmethod
    def open_guide():
        webbrowser.open(guidelink)

    def resume_pressed(self):
        if len(tests) == 0:
            messagebox.showinfo("VoRTEx", "No tests found! Better to start a new one")
        else:
            resume = Resume()
            resume.exec_()
        self.update()

    def save_pressed(self):
        t.save()
        t.save_settings()
        self.update()

    def on_newbutton_triggered(self):
        newdialog = NewDialog()
        newdialog.exec_()
        self.update()

    def clear_screens(self):
        self.ui.commandsBox.clear()
        self.ui.precBox.clear()
        self.ui.expectedBox.clear()

    def update_screens(self):
        self.clear_screens()
        if t.status == 1:
            if self.condition >= 0:
                for i in range(len(t.sequence[t.testlist[t.current_test]])):
                    self.ui.commandsBox.addItem(t.sequence[t.testlist[t.current_test]][i].replace("\t", "->").
                                                replace("\n", ""))
                self.ui.expectedBox.clear()
                try:
                    for i in range(len(t.expected[t.testlist[t.current_test]])):
                        self.ui.expectedBox.addItem(t.sequence[t.testlist[t.current_test]][i].replace("\t", "->").
                                                    replace("\n", ""))
                except IndexError:
                    pass
                self.ui.precBox.clear()
                try:
                    self.ui.precBox.setText(t.preconditions[t.testlist[t.current_test]])
                except NameError:
                    self.ui.precBox.setText("No preconditions available")
                except IndexError:
                    self.ui.precBox.setText("No preconditions available")

    def review_test(self, n_test):
        print("Reviewing test %s" % (n_test + 1))
        t.current_test = n_test
        self.update()

    def update_table(self):
        horizontal_labels = ["ID", "Result", "Timestamp", "Review", "Note"]
        self.ui.tableWidget.setRowCount(len(t.testlist))
        self.ui.tableWidget.setColumnCount(len(horizontal_labels))
        self.ui.tableWidget.setHorizontalHeaderLabels(horizontal_labels)
        btns = []
        for i in range(len(t.testlist)):
            result = 'TO BE DONE'
            note = ""
            timestamp = ""
            btns.append(QPushButton(self.ui.tableWidget))
            btns[i].clicked.connect(lambda: self.review_test(self.ui.tableWidget.currentRow()))
            btns[i].setText("Go to...")
            self.ui.tableWidget.setCellWidget(i, 3, btns[i])
            self.ui.tableWidget.setItem(i, 0, QTableWidgetItem(str(t.testlist[i] + 1)))
            self.ui.tableWidget.setItem(i, 1, QTableWidgetItem(result))
            self.ui.tableWidget.setItem(i, 2, QTableWidgetItem(timestamp))
            self.ui.tableWidget.setItem(i, 4, QTableWidgetItem(note))
        for i in range(len(t.results)):
            split_res = t.results[list(t.results.keys())[i]].split("\t")
            if split_res[0] == '1':
                result = 'PASS'
            else:
                result = 'FAIL'
            note = split_res[1]
            timestamp = split_res[2]
            self.ui.tableWidget.setItem(t.testlist.index(int(list(t.results.keys())[i]) - 1), 1,
                                        QTableWidgetItem(result))
            self.ui.tableWidget.setItem(t.testlist.index(int(list(t.results.keys())[i]) - 1), 2,
                                        QTableWidgetItem(timestamp))
            self.ui.tableWidget.setItem(t.testlist.index(int(list(t.results.keys())[i]) - 1), 4, QTableWidgetItem(note))
            for j in range(self.ui.tableWidget.columnCount()):
                if j != 3:
                    if result == 'PASS':
                        self.ui.tableWidget.item(t.testlist.index(int(list(t.results.keys())[i]) - 1), j) \
                            .setBackground(QtGui.QColor(0, 255, 0))
                    elif result == 'FAIL':
                        self.ui.tableWidget.item(t.testlist.index(int(list(t.results.keys())[i]) - 1), j) \
                            .setBackground(QtGui.QColor(255, 0, 0))
        self.ui.tableWidget.setItem(t.current_test, 1, QTableWidgetItem("CURRENT"))
        for j in range(self.ui.tableWidget.columnCount()):
            if j != 3:
                self.ui.tableWidget.item(t.current_test, j).setBackground(QtGui.QColor(255, 255, 0))

        self.ui.tableWidget.resizeColumnsToContents()
        self.ui.tableWidget.resizeRowsToContents()

    def update_playbutton(self):
        pass

    def update(self):
        self.update_table()
        self.update_screens()
        if self.condition == -1:  # test to be started
            self.ui.repeatButton.setEnabled(False)
            self.ui.cancel_button.setEnabled(False)
            if t.status != 2:
                self.ui.playButton.disconnect()
                self.ui.playButton.pressed.connect(lambda: self.do_test())
                if t.status == 1:
                    self.ui.playButton.setText("Resume test")
                    self.ui.statusLabel.setText("Status: RUNNING")
                elif t.status == 0:
                    self.ui.playButton.setText("Start test")
                    self.ui.statusLabel.setText("Status: WAITING")
            else:
                self.completed()
                self.ui.statusLabel.setText("Status: COMPLETED!")
        elif self.condition == 0:  # test started, PTT to be enabled
            self.ui.playButton.setEnabled(True)
            self.ui.repeatButton.setEnabled(False)
            self.ui.playButton.setText("PTT")
        if t.isSaved:
            self.setWindowTitle("VoRTEx - %s" % t.testName)
        else:
            self.setWindowTitle("VoRTEx - %s*" % t.testName)
        self.ui.groupBox_2.setTitle("Test %s of %s" % (t.current_test % len(t.testlist) + 1, len(t.testlist)))
        try:
            progress = round(100 * len(t.results) / len(t.testlist))
        except ZeroDivisionError:
            progress = 0
        self.ui.progressBar.setProperty("value", progress)
        if t.isMultigenderEnabled:
            if t.gender == 0:
                self.ui.langLabel.setText("Language: %s (F)" % langDict[t.lang])
            elif t.gender == 1:
                self.ui.langLabel.setText("Language: %s (M)" % langDict[t.lang])
        else:
            self.ui.langLabel.setText("Language: %s" % langDict[t.lang])
        self.ui.completedLabel.setText("Completed: %d test(s)" % t.current_test)
        self.ui.lengthLabel.setText("Test length: %d" % len(t.testlist))
        try:
            self.ui.scoreLabel.setText("Score: {0:d}/{1:d}({2:.1%})"
                                       .format(t.passes, len(t.results), t.passes / len(t.results)))
        except ZeroDivisionError:
            self.ui.scoreLabel.setText("Score: (not started yet)")
        try:
            self.ui.wwLabel.setText("WW accuracy: {0:d}/{1:d}({2:.1%})"
                                    .format(int(t.recognized_ww), int(t.issued_ww), t.recognized_ww / t.issued_ww))
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
        t.save()
        app.processEvents()

    def closeEvent(self, a0: QtGui.QCloseEvent) -> None:
        if not t.isSaved:
            if messagebox.askyesnocancel("VoRTEx", "Any progress will be lost. Do you want to save?"):
                self.save_pressed()
        quit()


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
        self.ui = Ui_Note_Dialog()
        self.ui.setupUi(self)
        self.ui.label.setStyleSheet("color: black")
        self.ui.checkBox.setChecked(False)
        self.is_checked = self.ui.checkBox.isChecked()
        self.text = ""
        self.ui.pushButton.pressed.connect(lambda: self.on_clicked())

    def on_clicked(self):
        self.text = self.ui.lineEdit.text()
        self.is_checked = self.ui.checkBox.isChecked()
        self.close()


# settings window
class Settings(QDialog):
    def __init__(self):
        super(Settings, self).__init__()
        self.ui = Ui_Settings()
        self.ui.setupUi(self)
        self.setWindowTitle("VoRTEx settings")
        self.setWindowIcon(QtGui.QIcon('source/gui/ico.ico'))
        self.ui.pushButton.pressed.connect(lambda: self.submit())
        self.ui.pushButton_2.pressed.connect(lambda: self.apply())
        self.ui.pushButton_3.pressed.connect(lambda: self.cancel())
        self.ui.mouth_button.pressed.connect(lambda: self.calibrate_mouth())
        self.ui.ear_button.pressed.connect(lambda: self.calibrate_ear())
        self.ui.mic_button.pressed.connect(lambda: self.calibrate_mic())
        for i in range(len(t.recorder.devicesIn)):
            self.ui.comboBox.addItem(t.recorder.devicesIn[i].get('name'))
        self.ui.comboBox.setCurrentIndex(t.recorder.deviceIn)
        for i in range(len(t.recorder.devicesOut)):
            self.ui.comboBox_2.addItem(t.recorder.devicesOut[i].get('name'))
        self.ui.comboBox.setCurrentIndex(t.recorder.deviceOut - len(t.recorder.devicesIn))
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
            self.ui.mouth_gain.setText("Gain = %0.2fdB" % t.gain)
        else:
            self.ui.mouth_gain.setText("calib. needed")
        if t.recorder.calibrated[0]:
            self.ui.mic_calibration.setText("dBSPL/dBFS = %0.2f" % t.recorder.correction[0])
        else:
            self.ui.mic_calibration.setText("calib. needed")
        if t.recorder.calibrated[1]:
            self.ui.ear_calibration.setText("dBSPL/dBFS = %0.2f" % t.recorder.correction[1])
        else:
            self.ui.ear_calibration.setText("calib. needed")

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
        self.temp = False

    @staticmethod
    def new_pressed():
        n = NewDialog()
        n.exec_()

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
        self.temp = False
        if not t.isSaved:
            if messagebox.askyesno("VoRTEx",
                                   "Do you want to save the current text (any unsaved progress will be lost)?"):
                t.save()
        t.resume(t.testDir + self.test_list[self.ui.listWidget.currentRow()])
        t.isFirstStart = False
        MainWindow.condition = -1
        self.close()

    def closeEvent(self, a0: QtGui.QCloseEvent) -> None:
        if self.temp:
            quit()


# dialog to start a new testz
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
        self.ui.pushButton_3.clicked.connect(lambda: self.close())
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
        self.temp = False
        self.testlist = None
        self.testlist = [5, 10, 38, 53, 54, 62, 64, 86, 88, 94, 97, 102, 106, 109, 110, 111, 121, 122, 133, 134, 137,
                         139, 140, 142, 148]
        for i in range(len(self.testlist)):
            self.testlist[i] = self.testlist[i] - 1

    def update_ok(self):
        if self.ui.nameEdit.text().replace(" ", "") == "":
            self.ui.submitButton.setEnabled(False)
        else:
            self.ui.submitButton.setEnabled(True)
        return

    def browse_pressed(self):
        t.listfile = self.ui.databaseLabel.text()
        t.load_database()
        self.ui.databaseLabel.setText(t.listfile)
        self.fill_lang_combo()

    def submit_pressed(self):
        try:
            res.temp = False
            res.close()
        except NameError:
            pass
        t.temp = False
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
            t.new(self.ui.nameEdit.text(), self.ui.langBox.currentIndex(), t.gender, self.testlist)
            t.save()
            t.isFirstStart = False
            self.close()
        except TestExistsError:
            messagebox.showerror("Vortex", "The test %s already exists. Please choose another name"
                                 % self.ui.nameEdit.text())

    def update(self):
        self.ui.label_5.setText("Number of tests: %d" % len(t.database[t.langs[self.ui.langBox.currentIndex()]]))
        g = 0
        for i in os.listdir(t.database["AUDIOPATH"]):
            if t.langs[self.ui.langBox.currentIndex()] in i:
                g += 1
        if g == 2:
            t.isMultigenderEnabled = True
        else:
            t.isMultigenderEnabled = False

        self.ui.radioButton.setEnabled(t.isMultigenderEnabled)
        self.ui.radioButton_2.setEnabled(t.isMultigenderEnabled)

    def fill_lang_combo(self):
        self.ui.langBox.clear()
        try:
            for i in range(len(t.langs)):
                self.ui.langBox.addItem(langDict[t.langs[i]])
        except AttributeError:
            pass

    def closeEvent(self, QCloseEvent):
        if self.temp:
            quit()


# splash screen
class SplashScreen(QDialog):
    def __init__(self):
        super(SplashScreen, self).__init__()
        self.ui = Ui_Splash()
        self.ui.setupUi(self)
        self.raise_()
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
    root.iconbitmap('source/gui/ico.ico')
    root.title('VoRTEx')
    root.withdraw()
    splash.load(60)
    t = GuiTest()  # create new istance of the test
    tests = show_dirs(t.testDir)
    splash.load(80)
    # load settings
    try:
        t.load_settings()
        t.resume()  # resume the test file contained in the "LAST" line of the settings file
    except CorruptedTestError:  # if the file in the "LAST" line is not available, choose another one
        messagebox.showerror("VoRTEx", "Corrupted test! Please start a new one!")
        res = Resume()
        res.temp = True
        res.ui.cancelButton.clicked.connect(lambda: quit())
        res.exec_()
        t.save_settings()
    except FileNotFoundError:  # If the settings file is not available, assume this is the first time the app is started
        if len(tests) == 0:
            messagebox.showinfo("VoRTEx", "Welcome! Let's start a new test!")
            new = NewDialog()
            new.temp = True
            new.ui.pushButton_3.clicked.connect(lambda: new.close())
            new.exec_()
        elif len(tests) == 1:
            t.resume(t.testDir + "/" + tests[0])
        else:
            messagebox.showinfo("VoRTEx", "Welcome! Let's resume a test or start a new one!")
            res = Resume()
            res.temp = True
            res.exec_()
    splash.load(99)
    time.sleep(0.5)
    # open main window
    MainWindow = MyMain()
    MainWindow.show()
    splash.close()  # close splashscreen
    sys.exit(app.exec_())
