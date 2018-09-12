# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'sequence_title_help.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_SequenceTitleHelpWindow(object):
    def setupUi(self, SequenceTitleHelpWindow):
        SequenceTitleHelpWindow.setObjectName("SequenceTitleHelpWindow")
        SequenceTitleHelpWindow.resize(256, 192)
        self.centralwidget = QtWidgets.QWidget(SequenceTitleHelpWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.formLayout = QtWidgets.QFormLayout(self.centralwidget)
        self.formLayout.setContentsMargins(0, 0, 0, 0)
        self.formLayout.setSpacing(0)
        self.formLayout.setObjectName("formLayout")
        self.plainTextEdit = QtWidgets.QPlainTextEdit(self.centralwidget)
        self.plainTextEdit.setTabChangesFocus(True)
        self.plainTextEdit.setReadOnly(True)
        self.plainTextEdit.setObjectName("plainTextEdit")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.plainTextEdit)
        SequenceTitleHelpWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(SequenceTitleHelpWindow)
        QtCore.QMetaObject.connectSlotsByName(SequenceTitleHelpWindow)

    def retranslateUi(self, SequenceTitleHelpWindow):
        _translate = QtCore.QCoreApplication.translate
        SequenceTitleHelpWindow.setWindowTitle(_translate("SequenceTitleHelpWindow", "MainWindow"))
        self.plainTextEdit.setPlainText(_translate("SequenceTitleHelpWindow", "Title Elements Help\n"
"\n"
"{name}      Name\n"
"{tempC}    Camera temperature\n"
"{bin}                 Camera Binning\n"
"{exp}    Length of exposure\n"
"{filter}    Name of filter\n"
"{ftype}    Type of frame\n"
"{idx}    Frame index\n"
""))

