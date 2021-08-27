# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'settings.ui'
#
# Created by: PyQt5 UI code generator 5.15.4
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Settings(object):
    def setupUi(self, Settings):
        Settings.setObjectName("Settings")
        Settings.resize(378, 322)
        self.tabWidget = QtWidgets.QTabWidget(Settings)
        self.tabWidget.setGeometry(QtCore.QRect(10, 10, 361, 251))
        self.tabWidget.setObjectName("tabWidget")
        self.tab = QtWidgets.QWidget()
        self.tab.setObjectName("tab")
        self.groupBox = QtWidgets.QGroupBox(self.tab)
        self.groupBox.setGeometry(QtCore.QRect(10, 10, 331, 91))
        self.groupBox.setObjectName("groupBox")
        self.label = QtWidgets.QLabel(self.groupBox)
        self.label.setGeometry(QtCore.QRect(16, 22, 61, 21))
        self.label.setObjectName("label")
        self.label_2 = QtWidgets.QLabel(self.groupBox)
        self.label_2.setGeometry(QtCore.QRect(16, 60, 61, 21))
        self.label_2.setObjectName("label_2")
        self.comboBox = QtWidgets.QComboBox(self.groupBox)
        self.comboBox.setGeometry(QtCore.QRect(70, 20, 251, 22))
        self.comboBox.setObjectName("comboBox")
        self.comboBox_2 = QtWidgets.QComboBox(self.groupBox)
        self.comboBox_2.setGeometry(QtCore.QRect(70, 60, 251, 21))
        self.comboBox_2.setObjectName("comboBox_2")
        self.groupBox_2 = QtWidgets.QGroupBox(self.tab)
        self.groupBox_2.setGeometry(QtCore.QRect(10, 110, 331, 111))
        self.groupBox_2.setObjectName("groupBox_2")
        self.widget = QtWidgets.QWidget(self.groupBox_2)
        self.widget.setGeometry(QtCore.QRect(20, 20, 291, 83))
        self.widget.setObjectName("widget")
        self.gridLayout = QtWidgets.QGridLayout(self.widget)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.gridLayout.setObjectName("gridLayout")
        self.label_3 = QtWidgets.QLabel(self.widget)
        self.label_3.setObjectName("label_3")
        self.gridLayout.addWidget(self.label_3, 0, 0, 1, 1)
        self.mic_calibration = QtWidgets.QLabel(self.widget)
        self.mic_calibration.setObjectName("mic_calibration")
        self.gridLayout.addWidget(self.mic_calibration, 0, 1, 1, 1)
        self.mic_button = QtWidgets.QPushButton(self.widget)
        self.mic_button.setObjectName("mic_button")
        self.gridLayout.addWidget(self.mic_button, 0, 2, 1, 1)
        self.label_4 = QtWidgets.QLabel(self.widget)
        self.label_4.setObjectName("label_4")
        self.gridLayout.addWidget(self.label_4, 1, 0, 1, 1)
        self.ear_calibration = QtWidgets.QLabel(self.widget)
        self.ear_calibration.setObjectName("ear_calibration")
        self.gridLayout.addWidget(self.ear_calibration, 1, 1, 1, 1)
        self.ear_button = QtWidgets.QPushButton(self.widget)
        self.ear_button.setObjectName("ear_button")
        self.gridLayout.addWidget(self.ear_button, 1, 2, 1, 1)
        self.label_5 = QtWidgets.QLabel(self.widget)
        self.label_5.setObjectName("label_5")
        self.gridLayout.addWidget(self.label_5, 2, 0, 1, 1)
        self.mouth_gain = QtWidgets.QLabel(self.widget)
        self.mouth_gain.setObjectName("mouth_gain")
        self.gridLayout.addWidget(self.mouth_gain, 2, 1, 1, 1)
        self.mouth_button = QtWidgets.QPushButton(self.widget)
        self.mouth_button.setObjectName("mouth_button")
        self.gridLayout.addWidget(self.mouth_button, 2, 2, 1, 1)
        self.tabWidget.addTab(self.tab, "")
        self.tab_2 = QtWidgets.QWidget()
        self.tab_2.setObjectName("tab_2")
        self.groupBox_3 = QtWidgets.QGroupBox(self.tab_2)
        self.groupBox_3.setGeometry(QtCore.QRect(10, 10, 151, 71))
        self.groupBox_3.setObjectName("groupBox_3")
        self.groupBox_4 = QtWidgets.QGroupBox(self.groupBox_3)
        self.groupBox_4.setGeometry(QtCore.QRect(0, 0, 151, 71))
        self.groupBox_4.setObjectName("groupBox_4")
        self.layoutWidget = QtWidgets.QWidget(self.groupBox_4)
        self.layoutWidget.setGeometry(QtCore.QRect(20, 20, 101, 42))
        self.layoutWidget.setObjectName("layoutWidget")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.layoutWidget)
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.radioButton_3 = QtWidgets.QRadioButton(self.layoutWidget)
        self.radioButton_3.setChecked(True)
        self.radioButton_3.setObjectName("radioButton_3")
        self.verticalLayout_2.addWidget(self.radioButton_3)
        self.radioButton_4 = QtWidgets.QRadioButton(self.layoutWidget)
        self.radioButton_4.setObjectName("radioButton_4")
        self.verticalLayout_2.addWidget(self.radioButton_4)
        self.groupBox_5 = QtWidgets.QGroupBox(self.groupBox_4)
        self.groupBox_5.setGeometry(QtCore.QRect(140, 70, 151, 71))
        self.groupBox_5.setObjectName("groupBox_5")
        self.layoutWidget_2 = QtWidgets.QWidget(self.groupBox_5)
        self.layoutWidget_2.setGeometry(QtCore.QRect(20, 20, 101, 42))
        self.layoutWidget_2.setObjectName("layoutWidget_2")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.layoutWidget_2)
        self.verticalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.radioButton_5 = QtWidgets.QRadioButton(self.layoutWidget_2)
        self.radioButton_5.setChecked(True)
        self.radioButton_5.setObjectName("radioButton_5")
        self.verticalLayout_3.addWidget(self.radioButton_5)
        self.radioButton_6 = QtWidgets.QRadioButton(self.layoutWidget_2)
        self.radioButton_6.setObjectName("radioButton_6")
        self.verticalLayout_3.addWidget(self.radioButton_6)
        self.widget1 = QtWidgets.QWidget(self.groupBox_3)
        self.widget1.setGeometry(QtCore.QRect(20, 20, 101, 42))
        self.widget1.setObjectName("widget1")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.widget1)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.radioButton = QtWidgets.QRadioButton(self.widget1)
        self.radioButton.setChecked(True)
        self.radioButton.setObjectName("radioButton")
        self.verticalLayout.addWidget(self.radioButton)
        self.radioButton_2 = QtWidgets.QRadioButton(self.widget1)
        self.radioButton_2.setObjectName("radioButton_2")
        self.verticalLayout.addWidget(self.radioButton_2)
        self.groupBox_6 = QtWidgets.QGroupBox(self.tab_2)
        self.groupBox_6.setGeometry(QtCore.QRect(190, 10, 151, 71))
        self.groupBox_6.setObjectName("groupBox_6")
        self.groupBox_7 = QtWidgets.QGroupBox(self.groupBox_6)
        self.groupBox_7.setGeometry(QtCore.QRect(140, 70, 151, 71))
        self.groupBox_7.setObjectName("groupBox_7")
        self.layoutWidget_4 = QtWidgets.QWidget(self.groupBox_7)
        self.layoutWidget_4.setGeometry(QtCore.QRect(20, 20, 101, 42))
        self.layoutWidget_4.setObjectName("layoutWidget_4")
        self.verticalLayout_5 = QtWidgets.QVBoxLayout(self.layoutWidget_4)
        self.verticalLayout_5.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_5.setObjectName("verticalLayout_5")
        self.radioButton_9 = QtWidgets.QRadioButton(self.layoutWidget_4)
        self.radioButton_9.setChecked(True)
        self.radioButton_9.setObjectName("radioButton_9")
        self.verticalLayout_5.addWidget(self.radioButton_9)
        self.radioButton_10 = QtWidgets.QRadioButton(self.layoutWidget_4)
        self.radioButton_10.setObjectName("radioButton_10")
        self.verticalLayout_5.addWidget(self.radioButton_10)
        self.checkBox = QtWidgets.QCheckBox(self.groupBox_6)
        self.checkBox.setGeometry(QtCore.QRect(20, 30, 70, 17))
        self.checkBox.setObjectName("checkBox")
        self.tabWidget.addTab(self.tab_2, "")
        self.widget2 = QtWidgets.QWidget(Settings)
        self.widget2.setGeometry(QtCore.QRect(50, 290, 281, 25))
        self.widget2.setObjectName("widget2")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.widget2)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.pushButton = QtWidgets.QPushButton(self.widget2)
        self.pushButton.setObjectName("pushButton")
        self.horizontalLayout.addWidget(self.pushButton)
        self.pushButton_2 = QtWidgets.QPushButton(self.widget2)
        self.pushButton_2.setObjectName("pushButton_2")
        self.horizontalLayout.addWidget(self.pushButton_2)
        self.pushButton_3 = QtWidgets.QPushButton(self.widget2)
        self.pushButton_3.setObjectName("pushButton_3")
        self.horizontalLayout.addWidget(self.pushButton_3)

        self.retranslateUi(Settings)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(Settings)

    def retranslateUi(self, Settings):
        _translate = QtCore.QCoreApplication.translate
        Settings.setWindowTitle(_translate("Settings", "Dialog"))
        self.groupBox.setTitle(_translate("Settings", "Audio devices"))
        self.label.setText(_translate("Settings", "Input"))
        self.label_2.setText(_translate("Settings", "Output"))
        self.groupBox_2.setTitle(_translate("Settings", "Calibration"))
        self.label_3.setText(_translate("Settings", "Microphone: "))
        self.mic_calibration.setText(_translate("Settings", "CALIB. NEEDED"))
        self.mic_button.setText(_translate("Settings", "Calibrate"))
        self.label_4.setText(_translate("Settings", "Ear: "))
        self.ear_calibration.setText(_translate("Settings", "CALIB. NEEDED"))
        self.ear_button.setText(_translate("Settings", "Calibrate"))
        self.label_5.setText(_translate("Settings", "Mouth"))
        self.mouth_gain.setText(_translate("Settings", "CALIB. NEEDED"))
        self.mouth_button.setText(_translate("Settings", "Calibrate"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), _translate("Settings", "Audio"))
        self.groupBox_3.setTitle(_translate("Settings", "Microphone activation"))
        self.groupBox_4.setTitle(_translate("Settings", "Microphone activation"))
        self.radioButton_3.setText(_translate("Settings", "Wake word"))
        self.radioButton_4.setText(_translate("Settings", "Manual"))
        self.groupBox_5.setTitle(_translate("Settings", "Microphone activation"))
        self.radioButton_5.setText(_translate("Settings", "Wake word"))
        self.radioButton_6.setText(_translate("Settings", "Manual"))
        self.radioButton.setText(_translate("Settings", "Wake word"))
        self.radioButton_2.setText(_translate("Settings", "Manual"))
        self.groupBox_6.setTitle(_translate("Settings", "Lombard effect"))
        self.groupBox_7.setTitle(_translate("Settings", "Microphone activation"))
        self.radioButton_9.setText(_translate("Settings", "Wake word"))
        self.radioButton_10.setText(_translate("Settings", "Manual"))
        self.checkBox.setText(_translate("Settings", "Enable"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_2), _translate("Settings", "Test execution"))
        self.pushButton.setText(_translate("Settings", "OK"))
        self.pushButton_2.setText(_translate("Settings", "Apply"))
        self.pushButton_3.setText(_translate("Settings", "Cancel"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Settings = QtWidgets.QDialog()
    ui = Ui_Settings()
    ui.setupUi(Settings)
    Settings.show()
    sys.exit(app.exec_())
