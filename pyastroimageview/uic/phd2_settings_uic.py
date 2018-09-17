# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'phd2_settings.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_PHD2ControlUI(object):
    def setupUi(self, PHD2ControlUI):
        PHD2ControlUI.setObjectName("PHD2ControlUI")
        PHD2ControlUI.resize(211, 46)
        self.gridLayout = QtWidgets.QGridLayout(PHD2ControlUI)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.gridLayout.setHorizontalSpacing(4)
        self.gridLayout.setVerticalSpacing(2)
        self.gridLayout.setObjectName("gridLayout")
        self.phd2_settings = QtWidgets.QPushButton(PHD2ControlUI)
        self.phd2_settings.setMinimumSize(QtCore.QSize(24, 0))
        self.phd2_settings.setMaximumSize(QtCore.QSize(24, 16777215))
        self.phd2_settings.setObjectName("phd2_settings")
        self.gridLayout.addWidget(self.phd2_settings, 0, 4, 1, 1)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setSpacing(6)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.label_2 = QtWidgets.QLabel(PHD2ControlUI)
        self.label_2.setObjectName("label_2")
        self.horizontalLayout.addWidget(self.label_2)
        self.phd2_status = QtWidgets.QLabel(PHD2ControlUI)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(5)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.phd2_status.sizePolicy().hasHeightForWidth())
        self.phd2_status.setSizePolicy(sizePolicy)
        self.phd2_status.setObjectName("phd2_status")
        self.horizontalLayout.addWidget(self.phd2_status)
        self.gridLayout.addLayout(self.horizontalLayout, 1, 1, 1, 4)
        self.phd2_connect = QtWidgets.QToolButton(PHD2ControlUI)
        self.phd2_connect.setMinimumSize(QtCore.QSize(64, 23))
        self.phd2_connect.setMaximumSize(QtCore.QSize(64, 23))
        self.phd2_connect.setCheckable(True)
        self.phd2_connect.setObjectName("phd2_connect")
        self.gridLayout.addWidget(self.phd2_connect, 0, 2, 1, 1)
        self.phd2_pause = QtWidgets.QToolButton(PHD2ControlUI)
        self.phd2_pause.setMinimumSize(QtCore.QSize(48, 23))
        self.phd2_pause.setMaximumSize(QtCore.QSize(48, 23))
        self.phd2_pause.setCheckable(True)
        self.phd2_pause.setObjectName("phd2_pause")
        self.gridLayout.addWidget(self.phd2_pause, 0, 3, 1, 1)

        self.retranslateUi(PHD2ControlUI)
        QtCore.QMetaObject.connectSlotsByName(PHD2ControlUI)

    def retranslateUi(self, PHD2ControlUI):
        _translate = QtCore.QCoreApplication.translate
        PHD2ControlUI.setWindowTitle(_translate("PHD2ControlUI", "Form"))
        self.phd2_settings.setText(_translate("PHD2ControlUI", "..."))
        self.label_2.setText(_translate("PHD2ControlUI", "Status"))
        self.phd2_status.setText(_translate("PHD2ControlUI", "TextLabel"))
        self.phd2_connect.setText(_translate("PHD2ControlUI", "Connect"))
        self.phd2_pause.setText(_translate("PHD2ControlUI", "Pause"))

