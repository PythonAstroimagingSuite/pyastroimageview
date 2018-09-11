# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'pyastroimage_camera_settings.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_camera_settings_widget(object):
    def setupUi(self, camera_settings_widget):
        camera_settings_widget.setObjectName("camera_settings_widget")
        camera_settings_widget.resize(201, 178)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(camera_settings_widget.sizePolicy().hasHeightForWidth())
        camera_settings_widget.setSizePolicy(sizePolicy)
        self.formLayout = QtWidgets.QFormLayout(camera_settings_widget)
        self.formLayout.setContentsMargins(0, 0, 0, 0)
        self.formLayout.setSpacing(0)
        self.formLayout.setObjectName("formLayout")
        self.gridLayout = QtWidgets.QGridLayout()
        self.gridLayout.setHorizontalSpacing(0)
        self.gridLayout.setVerticalSpacing(2)
        self.gridLayout.setObjectName("gridLayout")
        self.label = QtWidgets.QLabel(camera_settings_widget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label.sizePolicy().hasHeightForWidth())
        self.label.setSizePolicy(sizePolicy)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)
        self.camera_setting_disconnect = QtWidgets.QPushButton(camera_settings_widget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.camera_setting_disconnect.sizePolicy().hasHeightForWidth())
        self.camera_setting_disconnect.setSizePolicy(sizePolicy)
        self.camera_setting_disconnect.setMinimumSize(QtCore.QSize(48, 0))
        self.camera_setting_disconnect.setMaximumSize(QtCore.QSize(80, 16777215))
        self.camera_setting_disconnect.setObjectName("camera_setting_disconnect")
        self.gridLayout.addWidget(self.camera_setting_disconnect, 1, 2, 1, 1)
        self.label_7 = QtWidgets.QLabel(camera_settings_widget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_7.sizePolicy().hasHeightForWidth())
        self.label_7.setSizePolicy(sizePolicy)
        self.label_7.setObjectName("label_7")
        self.gridLayout.addWidget(self.label_7, 2, 0, 1, 1)
        self.camera_setting_connect = QtWidgets.QPushButton(camera_settings_widget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.camera_setting_connect.sizePolicy().hasHeightForWidth())
        self.camera_setting_connect.setSizePolicy(sizePolicy)
        self.camera_setting_connect.setMinimumSize(QtCore.QSize(48, 0))
        self.camera_setting_connect.setMaximumSize(QtCore.QSize(80, 16777215))
        self.camera_setting_connect.setObjectName("camera_setting_connect")
        self.gridLayout.addWidget(self.camera_setting_connect, 1, 1, 1, 1)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setContentsMargins(2, 1, 5, 1)
        self.horizontalLayout.setSpacing(0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.camera_driver_label = QtWidgets.QLabel(camera_settings_widget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.camera_driver_label.sizePolicy().hasHeightForWidth())
        self.camera_driver_label.setSizePolicy(sizePolicy)
        self.camera_driver_label.setMinimumSize(QtCore.QSize(0, 0))
        self.camera_driver_label.setObjectName("camera_driver_label")
        self.horizontalLayout.addWidget(self.camera_driver_label)
        self.camera_setting_setup = QtWidgets.QPushButton(camera_settings_widget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.camera_setting_setup.sizePolicy().hasHeightForWidth())
        self.camera_setting_setup.setSizePolicy(sizePolicy)
        self.camera_setting_setup.setMaximumSize(QtCore.QSize(24, 16777215))
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/gear/gear.png"), QtGui.QIcon.Normal, QtGui.QIcon.On)
        self.camera_setting_setup.setIcon(icon)
        self.camera_setting_setup.setObjectName("camera_setting_setup")
        self.horizontalLayout.addWidget(self.camera_setting_setup)
        self.gridLayout.addLayout(self.horizontalLayout, 0, 1, 1, 2)
        self.label_8 = QtWidgets.QLabel(camera_settings_widget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_8.sizePolicy().hasHeightForWidth())
        self.label_8.setSizePolicy(sizePolicy)
        self.label_8.setObjectName("label_8")
        self.gridLayout.addWidget(self.label_8, 3, 0, 1, 1)
        self.camera_setting_progress = QtWidgets.QLabel(camera_settings_widget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.camera_setting_progress.sizePolicy().hasHeightForWidth())
        self.camera_setting_progress.setSizePolicy(sizePolicy)
        self.camera_setting_progress.setWordWrap(False)
        self.camera_setting_progress.setObjectName("camera_setting_progress")
        self.gridLayout.addWidget(self.camera_setting_progress, 3, 1, 1, 2)
        self.camera_setting_status = QtWidgets.QLabel(camera_settings_widget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.camera_setting_status.sizePolicy().hasHeightForWidth())
        self.camera_setting_status.setSizePolicy(sizePolicy)
        self.camera_setting_status.setObjectName("camera_setting_status")
        self.gridLayout.addWidget(self.camera_setting_status, 2, 1, 1, 2)
        self.label_2 = QtWidgets.QLabel(camera_settings_widget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_2.sizePolicy().hasHeightForWidth())
        self.label_2.setSizePolicy(sizePolicy)
        self.label_2.setObjectName("label_2")
        self.gridLayout.addWidget(self.label_2, 4, 0, 1, 1)
        self.camera_setting_exposure_spinbox = QtWidgets.QDoubleSpinBox(camera_settings_widget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.camera_setting_exposure_spinbox.sizePolicy().hasHeightForWidth())
        self.camera_setting_exposure_spinbox.setSizePolicy(sizePolicy)
        self.camera_setting_exposure_spinbox.setMinimumSize(QtCore.QSize(64, 0))
        self.camera_setting_exposure_spinbox.setMaximumSize(QtCore.QSize(64, 16777215))
        self.camera_setting_exposure_spinbox.setMinimum(0.0)
        self.camera_setting_exposure_spinbox.setMaximum(3600.0)
        self.camera_setting_exposure_spinbox.setProperty("value", 1.0)
        self.camera_setting_exposure_spinbox.setObjectName("camera_setting_exposure_spinbox")
        self.gridLayout.addWidget(self.camera_setting_exposure_spinbox, 4, 1, 1, 1)
        self.label_3 = QtWidgets.QLabel(camera_settings_widget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_3.sizePolicy().hasHeightForWidth())
        self.label_3.setSizePolicy(sizePolicy)
        self.label_3.setObjectName("label_3")
        self.gridLayout.addWidget(self.label_3, 5, 0, 1, 1)
        self.camera_setting_expose = QtWidgets.QPushButton(camera_settings_widget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.camera_setting_expose.sizePolicy().hasHeightForWidth())
        self.camera_setting_expose.setSizePolicy(sizePolicy)
        self.camera_setting_expose.setMinimumSize(QtCore.QSize(64, 0))
        self.camera_setting_expose.setMaximumSize(QtCore.QSize(80, 16777215))
        self.camera_setting_expose.setObjectName("camera_setting_expose")
        self.gridLayout.addWidget(self.camera_setting_expose, 4, 2, 1, 1)
        self.label_4 = QtWidgets.QLabel(camera_settings_widget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_4.sizePolicy().hasHeightForWidth())
        self.label_4.setSizePolicy(sizePolicy)
        self.label_4.setObjectName("label_4")
        self.gridLayout.addWidget(self.label_4, 6, 0, 1, 1)
        self.gridLayout_2 = QtWidgets.QGridLayout()
        self.gridLayout_2.setContentsMargins(2, 0, 5, 0)
        self.gridLayout_2.setHorizontalSpacing(4)
        self.gridLayout_2.setVerticalSpacing(0)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.label_11 = QtWidgets.QLabel(camera_settings_widget)
        self.label_11.setObjectName("label_11")
        self.gridLayout_2.addWidget(self.label_11, 0, 2, 1, 1)
        self.camera_setting_roi_left = QtWidgets.QLabel(camera_settings_widget)
        self.camera_setting_roi_left.setObjectName("camera_setting_roi_left")
        self.gridLayout_2.addWidget(self.camera_setting_roi_left, 1, 0, 1, 1)
        self.camera_setting_roi_width = QtWidgets.QLabel(camera_settings_widget)
        self.camera_setting_roi_width.setObjectName("camera_setting_roi_width")
        self.gridLayout_2.addWidget(self.camera_setting_roi_width, 1, 2, 1, 1)
        self.label_9 = QtWidgets.QLabel(camera_settings_widget)
        self.label_9.setObjectName("label_9")
        self.gridLayout_2.addWidget(self.label_9, 0, 0, 1, 1)
        self.camera_setting_roi_top = QtWidgets.QLabel(camera_settings_widget)
        self.camera_setting_roi_top.setObjectName("camera_setting_roi_top")
        self.gridLayout_2.addWidget(self.camera_setting_roi_top, 1, 1, 1, 1)
        self.camera_setting_roi_height = QtWidgets.QLabel(camera_settings_widget)
        self.camera_setting_roi_height.setObjectName("camera_setting_roi_height")
        self.gridLayout_2.addWidget(self.camera_setting_roi_height, 1, 3, 1, 1)
        self.label_10 = QtWidgets.QLabel(camera_settings_widget)
        self.label_10.setObjectName("label_10")
        self.gridLayout_2.addWidget(self.label_10, 0, 1, 1, 1)
        self.label_12 = QtWidgets.QLabel(camera_settings_widget)
        self.label_12.setObjectName("label_12")
        self.gridLayout_2.addWidget(self.label_12, 0, 3, 1, 1)
        self.camera_setting_roi_set = QtWidgets.QPushButton(camera_settings_widget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.camera_setting_roi_set.sizePolicy().hasHeightForWidth())
        self.camera_setting_roi_set.setSizePolicy(sizePolicy)
        self.camera_setting_roi_set.setMaximumSize(QtCore.QSize(24, 16777215))
        self.camera_setting_roi_set.setObjectName("camera_setting_roi_set")
        self.gridLayout_2.addWidget(self.camera_setting_roi_set, 0, 4, 1, 1)
        self.gridLayout.addLayout(self.gridLayout_2, 6, 1, 1, 2)
        self.camera_setting_binning_spinbox = QtWidgets.QSpinBox(camera_settings_widget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.camera_setting_binning_spinbox.sizePolicy().hasHeightForWidth())
        self.camera_setting_binning_spinbox.setSizePolicy(sizePolicy)
        self.camera_setting_binning_spinbox.setMinimumSize(QtCore.QSize(48, 0))
        self.camera_setting_binning_spinbox.setMaximumSize(QtCore.QSize(48, 16777215))
        self.camera_setting_binning_spinbox.setMaximum(4)
        self.camera_setting_binning_spinbox.setProperty("value", 1)
        self.camera_setting_binning_spinbox.setObjectName("camera_setting_binning_spinbox")
        self.gridLayout.addWidget(self.camera_setting_binning_spinbox, 5, 1, 1, 1)
        self.formLayout.setLayout(0, QtWidgets.QFormLayout.LabelRole, self.gridLayout)

        self.retranslateUi(camera_settings_widget)
        QtCore.QMetaObject.connectSlotsByName(camera_settings_widget)
        camera_settings_widget.setTabOrder(self.camera_setting_exposure_spinbox, self.camera_setting_binning_spinbox)

    def retranslateUi(self, camera_settings_widget):
        _translate = QtCore.QCoreApplication.translate
        camera_settings_widget.setWindowTitle(_translate("camera_settings_widget", "Form"))
        self.label.setText(_translate("camera_settings_widget", "Driver"))
        self.camera_setting_disconnect.setText(_translate("camera_settings_widget", "Disconnect"))
        self.label_7.setText(_translate("camera_settings_widget", "Status"))
        self.camera_setting_connect.setText(_translate("camera_settings_widget", "Connect"))
        self.camera_driver_label.setText(_translate("camera_settings_widget", "TextLabel"))
        self.camera_setting_setup.setText(_translate("camera_settings_widget", "..."))
        self.label_8.setText(_translate("camera_settings_widget", "Progress"))
        self.camera_setting_progress.setText(_translate("camera_settings_widget", "TextLabel"))
        self.camera_setting_status.setText(_translate("camera_settings_widget", "TextLabel"))
        self.label_2.setText(_translate("camera_settings_widget", "Exposure"))
        self.label_3.setText(_translate("camera_settings_widget", "Binning"))
        self.camera_setting_expose.setText(_translate("camera_settings_widget", "Expose"))
        self.label_4.setText(_translate("camera_settings_widget", "ROI"))
        self.label_11.setText(_translate("camera_settings_widget", "Width"))
        self.camera_setting_roi_left.setText(_translate("camera_settings_widget", "0000"))
        self.camera_setting_roi_width.setText(_translate("camera_settings_widget", "9999"))
        self.label_9.setText(_translate("camera_settings_widget", "Left"))
        self.camera_setting_roi_top.setText(_translate("camera_settings_widget", "0000"))
        self.camera_setting_roi_height.setText(_translate("camera_settings_widget", "9999"))
        self.label_10.setText(_translate("camera_settings_widget", "Top"))
        self.label_12.setText(_translate("camera_settings_widget", "Height"))
        self.camera_setting_roi_set.setText(_translate("camera_settings_widget", "..."))

