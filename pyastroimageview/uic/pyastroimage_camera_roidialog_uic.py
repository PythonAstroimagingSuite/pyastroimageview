# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'pyastroimage_camera_roidialog.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_camera_set_roi_dialog(object):
    def setupUi(self, camera_set_roi_dialog):
        camera_set_roi_dialog.setObjectName("camera_set_roi_dialog")
        camera_set_roi_dialog.setWindowModality(QtCore.Qt.ApplicationModal)
        camera_set_roi_dialog.resize(291, 191)
        self.formLayout = QtWidgets.QFormLayout(camera_set_roi_dialog)
        self.formLayout.setObjectName("formLayout")
        self.gridLayout_2 = QtWidgets.QGridLayout()
        self.gridLayout_2.setContentsMargins(5, 5, 5, 5)
        self.gridLayout_2.setSpacing(15)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.reset = QtWidgets.QPushButton(camera_set_roi_dialog)
        self.reset.setMinimumSize(QtCore.QSize(64, 0))
        self.reset.setMaximumSize(QtCore.QSize(64, 16777215))
        self.reset.setObjectName("reset")
        self.gridLayout_2.addWidget(self.reset, 2, 3, 1, 1)
        self.height_spinbox = QtWidgets.QSpinBox(camera_set_roi_dialog)
        self.height_spinbox.setMinimumSize(QtCore.QSize(64, 0))
        self.height_spinbox.setMaximum(9999)
        self.height_spinbox.setObjectName("height_spinbox")
        self.gridLayout_2.addWidget(self.height_spinbox, 1, 3, 1, 1)
        self.label_4 = QtWidgets.QLabel(camera_set_roi_dialog)
        self.label_4.setObjectName("label_4")
        self.gridLayout_2.addWidget(self.label_4, 1, 2, 1, 1)
        self.label_3 = QtWidgets.QLabel(camera_set_roi_dialog)
        self.label_3.setObjectName("label_3")
        self.gridLayout_2.addWidget(self.label_3, 0, 2, 1, 1)
        self.label = QtWidgets.QLabel(camera_set_roi_dialog)
        self.label.setObjectName("label")
        self.gridLayout_2.addWidget(self.label, 0, 0, 1, 1)
        self.label_2 = QtWidgets.QLabel(camera_set_roi_dialog)
        self.label_2.setObjectName("label_2")
        self.gridLayout_2.addWidget(self.label_2, 1, 0, 1, 1)
        self.top_spinbox = QtWidgets.QSpinBox(camera_set_roi_dialog)
        self.top_spinbox.setMinimumSize(QtCore.QSize(64, 0))
        self.top_spinbox.setMaximum(9999)
        self.top_spinbox.setObjectName("top_spinbox")
        self.gridLayout_2.addWidget(self.top_spinbox, 1, 1, 1, 1)
        self.width_spinbox = QtWidgets.QSpinBox(camera_set_roi_dialog)
        self.width_spinbox.setMinimumSize(QtCore.QSize(64, 0))
        self.width_spinbox.setMaximum(9999)
        self.width_spinbox.setObjectName("width_spinbox")
        self.gridLayout_2.addWidget(self.width_spinbox, 0, 3, 1, 1)
        self.left_spinbox = QtWidgets.QSpinBox(camera_set_roi_dialog)
        self.left_spinbox.setMinimumSize(QtCore.QSize(64, 0))
        self.left_spinbox.setMaximum(999)
        self.left_spinbox.setObjectName("left_spinbox")
        self.gridLayout_2.addWidget(self.left_spinbox, 0, 1, 1, 1)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        spacerItem = QtWidgets.QSpacerItem(0, 0, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.buttonBox = QtWidgets.QDialogButtonBox(camera_set_roi_dialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.horizontalLayout.addWidget(self.buttonBox)
        self.horizontalLayout.setStretch(0, 2)
        self.gridLayout_2.addLayout(self.horizontalLayout, 4, 0, 1, 4)
        spacerItem1 = QtWidgets.QSpacerItem(20, 15, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        self.gridLayout_2.addItem(spacerItem1, 3, 0, 1, 1)
        self.center = QtWidgets.QPushButton(camera_set_roi_dialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.center.sizePolicy().hasHeightForWidth())
        self.center.setSizePolicy(sizePolicy)
        self.center.setMinimumSize(QtCore.QSize(64, 0))
        self.center.setMaximumSize(QtCore.QSize(64, 16777215))
        self.center.setObjectName("center")
        self.gridLayout_2.addWidget(self.center, 2, 2, 1, 1)
        self.formLayout.setLayout(0, QtWidgets.QFormLayout.LabelRole, self.gridLayout_2)

        self.retranslateUi(camera_set_roi_dialog)
        self.buttonBox.accepted.connect(camera_set_roi_dialog.accept)
        self.buttonBox.rejected.connect(camera_set_roi_dialog.reject)
        QtCore.QMetaObject.connectSlotsByName(camera_set_roi_dialog)
        camera_set_roi_dialog.setTabOrder(self.left_spinbox, self.width_spinbox)
        camera_set_roi_dialog.setTabOrder(self.width_spinbox, self.top_spinbox)
        camera_set_roi_dialog.setTabOrder(self.top_spinbox, self.height_spinbox)
        camera_set_roi_dialog.setTabOrder(self.height_spinbox, self.reset)

    def retranslateUi(self, camera_set_roi_dialog):
        _translate = QtCore.QCoreApplication.translate
        camera_set_roi_dialog.setWindowTitle(_translate("camera_set_roi_dialog", "Dialog"))
        self.reset.setText(_translate("camera_set_roi_dialog", "Reset"))
        self.label_4.setText(_translate("camera_set_roi_dialog", "Height"))
        self.label_3.setText(_translate("camera_set_roi_dialog", "Width"))
        self.label.setText(_translate("camera_set_roi_dialog", "Left"))
        self.label_2.setText(_translate("camera_set_roi_dialog", "Top"))
        self.center.setText(_translate("camera_set_roi_dialog", "Center"))

