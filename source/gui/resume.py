# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'resume.ui'
#
# Created by: PyQt5 UI code generator 5.15.4
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Resume(object):
    def setupUi(self, Resume):
        Resume.setObjectName("Resume")
        Resume.resize(362, 212)
        self.resumeButton = QtWidgets.QPushButton(Resume)
        self.resumeButton.setGeometry(QtCore.QRect(250, 10, 101, 23))
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.resumeButton.setFont(font)
        self.resumeButton.setObjectName("resumeButton")
        self.cancelButton = QtWidgets.QPushButton(Resume)
        self.cancelButton.setGeometry(QtCore.QRect(250, 40, 101, 23))
        self.cancelButton.setObjectName("cancelButton")
        self.listWidget = QtWidgets.QListWidget(Resume)
        self.listWidget.setGeometry(QtCore.QRect(10, 10, 221, 192))
        self.listWidget.setObjectName("listWidget")
        self.textBrowser = QtWidgets.QTextBrowser(Resume)
        self.textBrowser.setGeometry(QtCore.QRect(250, 100, 101, 101))
        self.textBrowser.setObjectName("textBrowser")
        self.cancelButton_2 = QtWidgets.QPushButton(Resume)
        self.cancelButton_2.setGeometry(QtCore.QRect(250, 70, 101, 23))
        self.cancelButton_2.setObjectName("cancelButton_2")

        self.retranslateUi(Resume)
        QtCore.QMetaObject.connectSlotsByName(Resume)

    def retranslateUi(self, Resume):
        _translate = QtCore.QCoreApplication.translate
        Resume.setWindowTitle(_translate("Resume", "Dialog"))
        self.resumeButton.setText(_translate("Resume", "Resume"))
        self.cancelButton.setText(_translate("Resume", "Cancel"))
        self.textBrowser.setHtml(_translate("Resume", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'MS Shell Dlg 2\'; font-size:8.25pt; font-weight:400; font-style:normal;\">\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><br /></p></body></html>"))
        self.cancelButton_2.setText(_translate("Resume", "Delete"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Resume = QtWidgets.QDialog()
    ui = Ui_Resume()
    ui.setupUi(Resume)
    Resume.show()
    sys.exit(app.exec_())
