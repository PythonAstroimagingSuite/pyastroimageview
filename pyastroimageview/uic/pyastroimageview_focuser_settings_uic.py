# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'pyastroimageview_focuser_settings.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_focuser_settings_widget(object):
    def setupUi(self, focuser_settings_widget):
        focuser_settings_widget.setObjectName("focuser_settings_widget")
        focuser_settings_widget.resize(206, 175)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(focuser_settings_widget.sizePolicy().hasHeightForWidth())
        focuser_settings_widget.setSizePolicy(sizePolicy)
        focuser_settings_widget.setMinimumSize(QtCore.QSize(0, 0))
        focuser_settings_widget.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.formLayout = QtWidgets.QFormLayout(focuser_settings_widget)
        self.formLayout.setContentsMargins(0, 0, 0, 0)
        self.formLayout.setSpacing(0)
        self.formLayout.setObjectName("formLayout")
        self.gridLayout = QtWidgets.QGridLayout()
        self.gridLayout.setHorizontalSpacing(3)
        self.gridLayout.setVerticalSpacing(4)
        self.gridLayout.setObjectName("gridLayout")
        self.label = QtWidgets.QLabel(focuser_settings_widget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label.sizePolicy().hasHeightForWidth())
        self.label.setSizePolicy(sizePolicy)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)
        self.focuser_setting_status = QtWidgets.QLabel(focuser_settings_widget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.focuser_setting_status.sizePolicy().hasHeightForWidth())
        self.focuser_setting_status.setSizePolicy(sizePolicy)
        self.focuser_setting_status.setObjectName("focuser_setting_status")
        self.gridLayout.addWidget(self.focuser_setting_status, 2, 1, 1, 2)
        self.label_3 = QtWidgets.QLabel(focuser_settings_widget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_3.sizePolicy().hasHeightForWidth())
        self.label_3.setSizePolicy(sizePolicy)
        self.label_3.setObjectName("label_3")
        self.gridLayout.addWidget(self.label_3, 5, 0, 1, 1)
        self.label_6 = QtWidgets.QLabel(focuser_settings_widget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_6.sizePolicy().hasHeightForWidth())
        self.label_6.setSizePolicy(sizePolicy)
        self.label_6.setObjectName("label_6")
        self.gridLayout.addWidget(self.label_6, 6, 0, 1, 1)
        self.label_2 = QtWidgets.QLabel(focuser_settings_widget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_2.sizePolicy().hasHeightForWidth())
        self.label_2.setSizePolicy(sizePolicy)
        self.label_2.setObjectName("label_2")
        self.gridLayout.addWidget(self.label_2, 4, 0, 1, 1)
        self.focuser_setting_position = QtWidgets.QLabel(focuser_settings_widget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.focuser_setting_position.sizePolicy().hasHeightForWidth())
        self.focuser_setting_position.setSizePolicy(sizePolicy)
        self.focuser_setting_position.setObjectName("focuser_setting_position")
        self.gridLayout.addWidget(self.focuser_setting_position, 3, 1, 1, 2)
        self.label_7 = QtWidgets.QLabel(focuser_settings_widget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_7.sizePolicy().hasHeightForWidth())
        self.label_7.setSizePolicy(sizePolicy)
        self.label_7.setObjectName("label_7")
        self.gridLayout.addWidget(self.label_7, 3, 0, 1, 1)
        self.focuser_setting_disconnect = QtWidgets.QPushButton(focuser_settings_widget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.focuser_setting_disconnect.sizePolicy().hasHeightForWidth())
        self.focuser_setting_disconnect.setSizePolicy(sizePolicy)
        self.focuser_setting_disconnect.setMinimumSize(QtCore.QSize(64, 0))
        self.focuser_setting_disconnect.setMaximumSize(QtCore.QSize(64, 16777215))
        self.focuser_setting_disconnect.setObjectName("focuser_setting_disconnect")
        self.gridLayout.addWidget(self.focuser_setting_disconnect, 1, 2, 1, 1)
        self.focuser_setting_connect = QtWidgets.QPushButton(focuser_settings_widget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.focuser_setting_connect.sizePolicy().hasHeightForWidth())
        self.focuser_setting_connect.setSizePolicy(sizePolicy)
        self.focuser_setting_connect.setMinimumSize(QtCore.QSize(64, 0))
        self.focuser_setting_connect.setMaximumSize(QtCore.QSize(64, 16777215))
        self.focuser_setting_connect.setObjectName("focuser_setting_connect")
        self.gridLayout.addWidget(self.focuser_setting_connect, 1, 1, 1, 1)
        self.focuser_setting_small_spinbox = QtWidgets.QSpinBox(focuser_settings_widget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.focuser_setting_small_spinbox.sizePolicy().hasHeightForWidth())
        self.focuser_setting_small_spinbox.setSizePolicy(sizePolicy)
        self.focuser_setting_small_spinbox.setMinimumSize(QtCore.QSize(40, 0))
        self.focuser_setting_small_spinbox.setMaximumSize(QtCore.QSize(64, 16777215))
        self.focuser_setting_small_spinbox.setMaximum(1000)
        self.focuser_setting_small_spinbox.setObjectName("focuser_setting_small_spinbox")
        self.gridLayout.addWidget(self.focuser_setting_small_spinbox, 4, 1, 1, 1)
        self.label_8 = QtWidgets.QLabel(focuser_settings_widget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_8.sizePolicy().hasHeightForWidth())
        self.label_8.setSizePolicy(sizePolicy)
        self.label_8.setObjectName("label_8")
        self.gridLayout.addWidget(self.label_8, 2, 0, 1, 1)
        self.focuser_setting_large_spinbox = QtWidgets.QSpinBox(focuser_settings_widget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.focuser_setting_large_spinbox.sizePolicy().hasHeightForWidth())
        self.focuser_setting_large_spinbox.setSizePolicy(sizePolicy)
        self.focuser_setting_large_spinbox.setMinimumSize(QtCore.QSize(40, 0))
        self.focuser_setting_large_spinbox.setMaximumSize(QtCore.QSize(64, 16777215))
        self.focuser_setting_large_spinbox.setMaximum(1000)
        self.focuser_setting_large_spinbox.setSingleStep(10)
        self.focuser_setting_large_spinbox.setObjectName("focuser_setting_large_spinbox")
        self.gridLayout.addWidget(self.focuser_setting_large_spinbox, 5, 1, 1, 1)
        self.focuser_setting_moveabs_spinbox = QtWidgets.QSpinBox(focuser_settings_widget)
        self.focuser_setting_moveabs_spinbox.setMinimumSize(QtCore.QSize(40, 0))
        self.focuser_setting_moveabs_spinbox.setMaximumSize(QtCore.QSize(64, 16777215))
        self.focuser_setting_moveabs_spinbox.setMaximum(64000)
        self.focuser_setting_moveabs_spinbox.setObjectName("focuser_setting_moveabs_spinbox")
        self.gridLayout.addWidget(self.focuser_setting_moveabs_spinbox, 6, 1, 1, 1)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setSpacing(0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.focuser_setting_movein_small = QtWidgets.QPushButton(focuser_settings_widget)
        self.focuser_setting_movein_small.setMinimumSize(QtCore.QSize(40, 0))
        self.focuser_setting_movein_small.setMaximumSize(QtCore.QSize(40, 16777215))
        self.focuser_setting_movein_small.setObjectName("focuser_setting_movein_small")
        self.horizontalLayout.addWidget(self.focuser_setting_movein_small)
        self.focuser_setting_moveout_small = QtWidgets.QPushButton(focuser_settings_widget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.focuser_setting_moveout_small.sizePolicy().hasHeightForWidth())
        self.focuser_setting_moveout_small.setSizePolicy(sizePolicy)
        self.focuser_setting_moveout_small.setMinimumSize(QtCore.QSize(40, 0))
        self.focuser_setting_moveout_small.setMaximumSize(QtCore.QSize(40, 16777215))
        self.focuser_setting_moveout_small.setObjectName("focuser_setting_moveout_small")
        self.horizontalLayout.addWidget(self.focuser_setting_moveout_small)
        self.gridLayout.addLayout(self.horizontalLayout, 4, 2, 1, 1)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setSpacing(0)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.focuser_setting_movein_large = QtWidgets.QPushButton(focuser_settings_widget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.focuser_setting_movein_large.sizePolicy().hasHeightForWidth())
        self.focuser_setting_movein_large.setSizePolicy(sizePolicy)
        self.focuser_setting_movein_large.setMinimumSize(QtCore.QSize(40, 0))
        self.focuser_setting_movein_large.setMaximumSize(QtCore.QSize(40, 16777215))
        self.focuser_setting_movein_large.setObjectName("focuser_setting_movein_large")
        self.horizontalLayout_2.addWidget(self.focuser_setting_movein_large)
        self.focuser_setting_moveout_large = QtWidgets.QPushButton(focuser_settings_widget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.focuser_setting_moveout_large.sizePolicy().hasHeightForWidth())
        self.focuser_setting_moveout_large.setSizePolicy(sizePolicy)
        self.focuser_setting_moveout_large.setMinimumSize(QtCore.QSize(40, 0))
        self.focuser_setting_moveout_large.setMaximumSize(QtCore.QSize(40, 16777215))
        self.focuser_setting_moveout_large.setObjectName("focuser_setting_moveout_large")
        self.horizontalLayout_2.addWidget(self.focuser_setting_moveout_large)
        self.gridLayout.addLayout(self.horizontalLayout_2, 5, 2, 1, 1)
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setSpacing(0)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.focuser_setting_moveabs_move = QtWidgets.QPushButton(focuser_settings_widget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.focuser_setting_moveabs_move.sizePolicy().hasHeightForWidth())
        self.focuser_setting_moveabs_move.setSizePolicy(sizePolicy)
        self.focuser_setting_moveabs_move.setMinimumSize(QtCore.QSize(40, 0))
        self.focuser_setting_moveabs_move.setMaximumSize(QtCore.QSize(40, 16777215))
        self.focuser_setting_moveabs_move.setObjectName("focuser_setting_moveabs_move")
        self.horizontalLayout_3.addWidget(self.focuser_setting_moveabs_move)
        self.focuser_setting_moveabs_stop = QtWidgets.QPushButton(focuser_settings_widget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.focuser_setting_moveabs_stop.sizePolicy().hasHeightForWidth())
        self.focuser_setting_moveabs_stop.setSizePolicy(sizePolicy)
        self.focuser_setting_moveabs_stop.setMinimumSize(QtCore.QSize(40, 0))
        self.focuser_setting_moveabs_stop.setMaximumSize(QtCore.QSize(40, 16777215))
        self.focuser_setting_moveabs_stop.setObjectName("focuser_setting_moveabs_stop")
        self.horizontalLayout_3.addWidget(self.focuser_setting_moveabs_stop)
        self.gridLayout.addLayout(self.horizontalLayout_3, 6, 2, 1, 1)
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.focuser_driver_label = QtWidgets.QLabel(focuser_settings_widget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.focuser_driver_label.sizePolicy().hasHeightForWidth())
        self.focuser_driver_label.setSizePolicy(sizePolicy)
        self.focuser_driver_label.setObjectName("focuser_driver_label")
        self.horizontalLayout_4.addWidget(self.focuser_driver_label)
        self.focuser_setting_setup = QtWidgets.QPushButton(focuser_settings_widget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.focuser_setting_setup.sizePolicy().hasHeightForWidth())
        self.focuser_setting_setup.setSizePolicy(sizePolicy)
        self.focuser_setting_setup.setMinimumSize(QtCore.QSize(24, 0))
        self.focuser_setting_setup.setMaximumSize(QtCore.QSize(24, 16777215))
        self.focuser_setting_setup.setObjectName("focuser_setting_setup")
        self.horizontalLayout_4.addWidget(self.focuser_setting_setup)
        self.gridLayout.addLayout(self.horizontalLayout_4, 0, 1, 1, 2)
        self.formLayout.setLayout(0, QtWidgets.QFormLayout.LabelRole, self.gridLayout)

        self.retranslateUi(focuser_settings_widget)
        QtCore.QMetaObject.connectSlotsByName(focuser_settings_widget)

    def retranslateUi(self, focuser_settings_widget):
        _translate = QtCore.QCoreApplication.translate
        focuser_settings_widget.setWindowTitle(_translate("focuser_settings_widget", "Form"))
        self.label.setText(_translate("focuser_settings_widget", " Driver"))
        self.focuser_setting_status.setText(_translate("focuser_settings_widget", "TextLabel"))
        self.label_3.setText(_translate("focuser_settings_widget", "Large Step"))
        self.label_6.setText(_translate("focuser_settings_widget", "Position"))
        self.label_2.setText(_translate("focuser_settings_widget", "Small Step"))
        self.focuser_setting_position.setText(_translate("focuser_settings_widget", "TextLabel"))
        self.label_7.setText(_translate("focuser_settings_widget", "Position"))
        self.focuser_setting_disconnect.setText(_translate("focuser_settings_widget", "Disconnect"))
        self.focuser_setting_connect.setText(_translate("focuser_settings_widget", "Connect"))
        self.label_8.setText(_translate("focuser_settings_widget", "Status"))
        self.focuser_setting_movein_small.setText(_translate("focuser_settings_widget", "In"))
        self.focuser_setting_moveout_small.setText(_translate("focuser_settings_widget", "Out"))
        self.focuser_setting_movein_large.setText(_translate("focuser_settings_widget", "In"))
        self.focuser_setting_moveout_large.setText(_translate("focuser_settings_widget", "Out"))
        self.focuser_setting_moveabs_move.setText(_translate("focuser_settings_widget", "Move"))
        self.focuser_setting_moveabs_stop.setText(_translate("focuser_settings_widget", "Stop"))
        self.focuser_driver_label.setText(_translate("focuser_settings_widget", "TextLabel"))
        self.focuser_setting_setup.setText(_translate("focuser_settings_widget", "..."))
