# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'mount_settings.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_mount_settings_widget(object):
    def setupUi(self, mount_settings_widget):
        mount_settings_widget.setObjectName("mount_settings_widget")
        mount_settings_widget.resize(168, 119)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(mount_settings_widget.sizePolicy().hasHeightForWidth())
        mount_settings_widget.setSizePolicy(sizePolicy)
        mount_settings_widget.setMinimumSize(QtCore.QSize(0, 0))
        mount_settings_widget.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.formLayout = QtWidgets.QFormLayout(mount_settings_widget)
        self.formLayout.setContentsMargins(0, -1, 0, 0)
        self.formLayout.setSpacing(0)
        self.formLayout.setObjectName("formLayout")
        self.gridLayout = QtWidgets.QGridLayout()
        self.gridLayout.setHorizontalSpacing(3)
        self.gridLayout.setVerticalSpacing(4)
        self.gridLayout.setObjectName("gridLayout")
        self.label_8 = QtWidgets.QLabel(mount_settings_widget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_8.sizePolicy().hasHeightForWidth())
        self.label_8.setSizePolicy(sizePolicy)
        self.label_8.setObjectName("label_8")
        self.gridLayout.addWidget(self.label_8, 2, 0, 1, 1)
        self.label = QtWidgets.QLabel(mount_settings_widget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label.sizePolicy().hasHeightForWidth())
        self.label.setSizePolicy(sizePolicy)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)
        self.mount_setting_connect = QtWidgets.QPushButton(mount_settings_widget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.mount_setting_connect.sizePolicy().hasHeightForWidth())
        self.mount_setting_connect.setSizePolicy(sizePolicy)
        self.mount_setting_connect.setMinimumSize(QtCore.QSize(64, 0))
        self.mount_setting_connect.setMaximumSize(QtCore.QSize(64, 16777215))
        self.mount_setting_connect.setObjectName("mount_setting_connect")
        self.gridLayout.addWidget(self.mount_setting_connect, 1, 1, 1, 1)
        self.mount_setting_disconnect = QtWidgets.QPushButton(mount_settings_widget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.mount_setting_disconnect.sizePolicy().hasHeightForWidth())
        self.mount_setting_disconnect.setSizePolicy(sizePolicy)
        self.mount_setting_disconnect.setMinimumSize(QtCore.QSize(64, 0))
        self.mount_setting_disconnect.setMaximumSize(QtCore.QSize(64, 16777215))
        self.mount_setting_disconnect.setObjectName("mount_setting_disconnect")
        self.gridLayout.addWidget(self.mount_setting_disconnect, 1, 2, 1, 1)
        self.mount_setting_status = QtWidgets.QLabel(mount_settings_widget)
        self.mount_setting_status.setObjectName("mount_setting_status")
        self.gridLayout.addWidget(self.mount_setting_status, 2, 1, 1, 2)
        self.gridLayout_2 = QtWidgets.QGridLayout()
        self.gridLayout_2.setSpacing(0)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.mount_setting_position_ra = QtWidgets.QLabel(mount_settings_widget)
        self.mount_setting_position_ra.setObjectName("mount_setting_position_ra")
        self.gridLayout_2.addWidget(self.mount_setting_position_ra, 0, 1, 1, 1)
        self.mount_setting_position_az = QtWidgets.QLabel(mount_settings_widget)
        self.mount_setting_position_az.setObjectName("mount_setting_position_az")
        self.gridLayout_2.addWidget(self.mount_setting_position_az, 1, 4, 1, 1)
        self.label_9 = QtWidgets.QLabel(mount_settings_widget)
        self.label_9.setObjectName("label_9")
        self.gridLayout_2.addWidget(self.label_9, 1, 3, 1, 1)
        self.label_2 = QtWidgets.QLabel(mount_settings_widget)
        self.label_2.setObjectName("label_2")
        self.gridLayout_2.addWidget(self.label_2, 0, 0, 1, 1)
        spacerItem = QtWidgets.QSpacerItem(15, 20, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout_2.addItem(spacerItem, 0, 2, 1, 1)
        self.mount_setting_position_alt = QtWidgets.QLabel(mount_settings_widget)
        self.mount_setting_position_alt.setObjectName("mount_setting_position_alt")
        self.gridLayout_2.addWidget(self.mount_setting_position_alt, 0, 4, 1, 1)
        self.label_6 = QtWidgets.QLabel(mount_settings_widget)
        self.label_6.setObjectName("label_6")
        self.gridLayout_2.addWidget(self.label_6, 0, 3, 1, 1)
        self.label_4 = QtWidgets.QLabel(mount_settings_widget)
        self.label_4.setObjectName("label_4")
        self.gridLayout_2.addWidget(self.label_4, 1, 0, 1, 1)
        self.mount_setting_position_dec = QtWidgets.QLabel(mount_settings_widget)
        self.mount_setting_position_dec.setObjectName("mount_setting_position_dec")
        self.gridLayout_2.addWidget(self.mount_setting_position_dec, 1, 1, 1, 1)
        self.gridLayout.addLayout(self.gridLayout_2, 3, 0, 1, 3)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.mount_driver_label = QtWidgets.QLabel(mount_settings_widget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.mount_driver_label.sizePolicy().hasHeightForWidth())
        self.mount_driver_label.setSizePolicy(sizePolicy)
        self.mount_driver_label.setObjectName("mount_driver_label")
        self.horizontalLayout.addWidget(self.mount_driver_label)
        self.mount_setting_setup = QtWidgets.QPushButton(mount_settings_widget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.mount_setting_setup.sizePolicy().hasHeightForWidth())
        self.mount_setting_setup.setSizePolicy(sizePolicy)
        self.mount_setting_setup.setMinimumSize(QtCore.QSize(24, 0))
        self.mount_setting_setup.setMaximumSize(QtCore.QSize(24, 16777215))
        self.mount_setting_setup.setObjectName("mount_setting_setup")
        self.horizontalLayout.addWidget(self.mount_setting_setup)
        self.gridLayout.addLayout(self.horizontalLayout, 0, 1, 1, 2)
        self.formLayout.setLayout(0, QtWidgets.QFormLayout.LabelRole, self.gridLayout)

        self.retranslateUi(mount_settings_widget)
        QtCore.QMetaObject.connectSlotsByName(mount_settings_widget)

    def retranslateUi(self, mount_settings_widget):
        _translate = QtCore.QCoreApplication.translate
        mount_settings_widget.setWindowTitle(_translate("mount_settings_widget", "Form"))
        self.label_8.setText(_translate("mount_settings_widget", "Status"))
        self.label.setText(_translate("mount_settings_widget", " Driver"))
        self.mount_setting_connect.setText(_translate("mount_settings_widget", "Connect"))
        self.mount_setting_disconnect.setText(_translate("mount_settings_widget", "Disconnect"))
        self.mount_setting_status.setText(_translate("mount_settings_widget", "TextLabel"))
        self.mount_setting_position_ra.setText(_translate("mount_settings_widget", "TextLabel"))
        self.mount_setting_position_az.setText(_translate("mount_settings_widget", "TextLabel"))
        self.label_9.setText(_translate("mount_settings_widget", "AZ"))
        self.label_2.setText(_translate("mount_settings_widget", "RA"))
        self.mount_setting_position_alt.setText(_translate("mount_settings_widget", "TextLabel"))
        self.label_6.setText(_translate("mount_settings_widget", "ALT"))
        self.label_4.setText(_translate("mount_settings_widget", "DEC"))
        self.mount_setting_position_dec.setText(_translate("mount_settings_widget", "TextLabel"))
        self.mount_driver_label.setText(_translate("mount_settings_widget", "TextLabel"))
        self.mount_setting_setup.setText(_translate("mount_settings_widget", "..."))

