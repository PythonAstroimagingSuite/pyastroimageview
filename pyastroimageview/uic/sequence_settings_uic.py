# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'sequence_settings.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_SequenceSettingsUI(object):
    def setupUi(self, SequenceSettingsUI):
        SequenceSettingsUI.setObjectName("SequenceSettingsUI")
        SequenceSettingsUI.resize(620, 351)
        self.gridLayout = QtWidgets.QGridLayout(SequenceSettingsUI)
        self.gridLayout.setObjectName("gridLayout")
        self.label_4 = QtWidgets.QLabel(SequenceSettingsUI)
        self.label_4.setObjectName("label_4")
        self.gridLayout.addWidget(self.label_4, 4, 5, 1, 1)
        self.label_7 = QtWidgets.QLabel(SequenceSettingsUI)
        self.label_7.setObjectName("label_7")
        self.gridLayout.addWidget(self.label_7, 3, 0, 1, 1)
        self.label_15 = QtWidgets.QLabel(SequenceSettingsUI)
        self.label_15.setObjectName("label_15")
        self.gridLayout.addWidget(self.label_15, 5, 0, 1, 1)
        self.sequence_binning = QtWidgets.QSpinBox(SequenceSettingsUI)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.sequence_binning.sizePolicy().hasHeightForWidth())
        self.sequence_binning.setSizePolicy(sizePolicy)
        self.sequence_binning.setMinimumSize(QtCore.QSize(48, 20))
        self.sequence_binning.setMaximumSize(QtCore.QSize(48, 20))
        self.sequence_binning.setMaximum(4)
        self.sequence_binning.setProperty("value", 1)
        self.sequence_binning.setObjectName("sequence_binning")
        self.gridLayout.addWidget(self.sequence_binning, 4, 3, 1, 1)
        self.label_16 = QtWidgets.QLabel(SequenceSettingsUI)
        self.label_16.setObjectName("label_16")
        self.gridLayout.addWidget(self.label_16, 14, 0, 1, 1)
        self.sequence_frametype = QtWidgets.QComboBox(SequenceSettingsUI)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.sequence_frametype.sizePolicy().hasHeightForWidth())
        self.sequence_frametype.setSizePolicy(sizePolicy)
        self.sequence_frametype.setMinimumSize(QtCore.QSize(0, 20))
        self.sequence_frametype.setMaximumSize(QtCore.QSize(16777215, 20))
        self.sequence_frametype.setObjectName("sequence_frametype")
        self.sequence_frametype.addItem("")
        self.sequence_frametype.addItem("")
        self.sequence_frametype.addItem("")
        self.sequence_frametype.addItem("")
        self.gridLayout.addWidget(self.sequence_frametype, 5, 6, 1, 1)
        self.sequence_targetdir = QtWidgets.QPlainTextEdit(SequenceSettingsUI)
        self.sequence_targetdir.setMinimumSize(QtCore.QSize(300, 20))
        self.sequence_targetdir.setMaximumSize(QtCore.QSize(16777215, 20))
        self.sequence_targetdir.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.sequence_targetdir.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.sequence_targetdir.setTabChangesFocus(True)
        self.sequence_targetdir.setLineWrapMode(QtWidgets.QPlainTextEdit.NoWrap)
        self.sequence_targetdir.setReadOnly(True)
        self.sequence_targetdir.setObjectName("sequence_targetdir")
        self.gridLayout.addWidget(self.sequence_targetdir, 13, 2, 1, 5)
        self.label_5 = QtWidgets.QLabel(SequenceSettingsUI)
        self.label_5.setObjectName("label_5")
        self.gridLayout.addWidget(self.label_5, 3, 5, 1, 1)
        self.sequence_select_targetdir = QtWidgets.QPushButton(SequenceSettingsUI)
        self.sequence_select_targetdir.setMinimumSize(QtCore.QSize(24, 0))
        self.sequence_select_targetdir.setMaximumSize(QtCore.QSize(24, 16777215))
        self.sequence_select_targetdir.setObjectName("sequence_select_targetdir")
        self.gridLayout.addWidget(self.sequence_select_targetdir, 13, 7, 1, 1)
        self.label_3 = QtWidgets.QLabel(SequenceSettingsUI)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_3.sizePolicy().hasHeightForWidth())
        self.label_3.setSizePolicy(sizePolicy)
        self.label_3.setObjectName("label_3")
        self.gridLayout.addWidget(self.label_3, 5, 5, 1, 1)
        self.label_9 = QtWidgets.QLabel(SequenceSettingsUI)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_9.sizePolicy().hasHeightForWidth())
        self.label_9.setSizePolicy(sizePolicy)
        self.label_9.setMinimumSize(QtCore.QSize(0, 40))
        self.label_9.setMaximumSize(QtCore.QSize(16777215, 40))
        self.label_9.setObjectName("label_9")
        self.gridLayout.addWidget(self.label_9, 11, 5, 1, 1)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem, 11, 4, 1, 1)
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.label_18 = QtWidgets.QLabel(SequenceSettingsUI)
        self.label_18.setMinimumSize(QtCore.QSize(0, 24))
        self.label_18.setMaximumSize(QtCore.QSize(16777215, 24))
        self.label_18.setObjectName("label_18")
        self.horizontalLayout_2.addWidget(self.label_18)
        self.sequence_dither = QtWidgets.QSpinBox(SequenceSettingsUI)
        self.sequence_dither.setMinimum(0)
        self.sequence_dither.setObjectName("sequence_dither")
        self.horizontalLayout_2.addWidget(self.sequence_dither)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        self.gridLayout.addLayout(self.verticalLayout, 11, 3, 1, 1)
        self.label_14 = QtWidgets.QLabel(SequenceSettingsUI)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_14.sizePolicy().hasHeightForWidth())
        self.label_14.setSizePolicy(sizePolicy)
        self.label_14.setObjectName("label_14")
        self.gridLayout.addWidget(self.label_14, 4, 0, 1, 1)
        self.label_2 = QtWidgets.QLabel(SequenceSettingsUI)
        self.label_2.setObjectName("label_2")
        self.gridLayout.addWidget(self.label_2, 1, 0, 1, 3)
        self.sequence_elements = QtWidgets.QPlainTextEdit(SequenceSettingsUI)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.sequence_elements.sizePolicy().hasHeightForWidth())
        self.sequence_elements.setSizePolicy(sizePolicy)
        self.sequence_elements.setMinimumSize(QtCore.QSize(0, 20))
        self.sequence_elements.setMaximumSize(QtCore.QSize(16777215, 20))
        self.sequence_elements.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.sequence_elements.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.sequence_elements.setTabChangesFocus(True)
        self.sequence_elements.setObjectName("sequence_elements")
        self.gridLayout.addWidget(self.sequence_elements, 1, 3, 1, 4)
        self.sequence_number = QtWidgets.QSpinBox(SequenceSettingsUI)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.sequence_number.sizePolicy().hasHeightForWidth())
        self.sequence_number.setSizePolicy(sizePolicy)
        self.sequence_number.setMinimum(1)
        self.sequence_number.setMaximum(999)
        self.sequence_number.setObjectName("sequence_number")
        self.gridLayout.addWidget(self.sequence_number, 4, 6, 1, 1)
        self.sequence_filter = QtWidgets.QComboBox(SequenceSettingsUI)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.sequence_filter.sizePolicy().hasHeightForWidth())
        self.sequence_filter.setSizePolicy(sizePolicy)
        self.sequence_filter.setObjectName("sequence_filter")
        self.gridLayout.addWidget(self.sequence_filter, 5, 3, 1, 1)
        self.label_8 = QtWidgets.QLabel(SequenceSettingsUI)
        self.label_8.setObjectName("label_8")
        self.gridLayout.addWidget(self.label_8, 13, 0, 1, 1)
        self.label_6 = QtWidgets.QLabel(SequenceSettingsUI)
        font = QtGui.QFont()
        font.setBold(False)
        font.setItalic(False)
        font.setWeight(50)
        self.label_6.setFont(font)
        self.label_6.setObjectName("label_6")
        self.gridLayout.addWidget(self.label_6, 2, 0, 1, 2)
        self.label = QtWidgets.QLabel(SequenceSettingsUI)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 0, 0, 1, 2)
        self.sequence_exposure = QtWidgets.QDoubleSpinBox(SequenceSettingsUI)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.sequence_exposure.sizePolicy().hasHeightForWidth())
        self.sequence_exposure.setSizePolicy(sizePolicy)
        self.sequence_exposure.setDecimals(3)
        self.sequence_exposure.setMaximum(3600.0)
        self.sequence_exposure.setObjectName("sequence_exposure")
        self.gridLayout.addWidget(self.sequence_exposure, 3, 3, 1, 1)
        self.gridLayout_2 = QtWidgets.QGridLayout()
        self.gridLayout_2.setContentsMargins(2, 0, 5, 0)
        self.gridLayout_2.setHorizontalSpacing(4)
        self.gridLayout_2.setVerticalSpacing(0)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.label_11 = QtWidgets.QLabel(SequenceSettingsUI)
        self.label_11.setObjectName("label_11")
        self.gridLayout_2.addWidget(self.label_11, 0, 2, 1, 1)
        self.sequence_roi_left = QtWidgets.QLabel(SequenceSettingsUI)
        self.sequence_roi_left.setObjectName("sequence_roi_left")
        self.gridLayout_2.addWidget(self.sequence_roi_left, 1, 0, 1, 1)
        self.sequence_roi_width = QtWidgets.QLabel(SequenceSettingsUI)
        self.sequence_roi_width.setObjectName("sequence_roi_width")
        self.gridLayout_2.addWidget(self.sequence_roi_width, 1, 2, 1, 1)
        self.label_10 = QtWidgets.QLabel(SequenceSettingsUI)
        self.label_10.setObjectName("label_10")
        self.gridLayout_2.addWidget(self.label_10, 0, 0, 1, 1)
        self.sequence_roi_top = QtWidgets.QLabel(SequenceSettingsUI)
        self.sequence_roi_top.setObjectName("sequence_roi_top")
        self.gridLayout_2.addWidget(self.sequence_roi_top, 1, 1, 1, 1)
        self.sequence_roi_height = QtWidgets.QLabel(SequenceSettingsUI)
        self.sequence_roi_height.setObjectName("sequence_roi_height")
        self.gridLayout_2.addWidget(self.sequence_roi_height, 1, 3, 1, 1)
        self.label_12 = QtWidgets.QLabel(SequenceSettingsUI)
        self.label_12.setObjectName("label_12")
        self.gridLayout_2.addWidget(self.label_12, 0, 1, 1, 1)
        self.label_13 = QtWidgets.QLabel(SequenceSettingsUI)
        self.label_13.setObjectName("label_13")
        self.gridLayout_2.addWidget(self.label_13, 0, 3, 1, 1)
        self.sequence_roi_set = QtWidgets.QPushButton(SequenceSettingsUI)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.sequence_roi_set.sizePolicy().hasHeightForWidth())
        self.sequence_roi_set.setSizePolicy(sizePolicy)
        self.sequence_roi_set.setMaximumSize(QtCore.QSize(24, 16777215))
        self.sequence_roi_set.setObjectName("sequence_roi_set")
        self.gridLayout_2.addWidget(self.sequence_roi_set, 0, 4, 1, 1)
        self.gridLayout.addLayout(self.gridLayout_2, 11, 6, 1, 1)
        self.sequence_elements_help = QtWidgets.QPushButton(SequenceSettingsUI)
        self.sequence_elements_help.setMinimumSize(QtCore.QSize(25, 0))
        self.sequence_elements_help.setMaximumSize(QtCore.QSize(25, 16777215))
        self.sequence_elements_help.setCheckable(True)
        self.sequence_elements_help.setObjectName("sequence_elements_help")
        self.gridLayout.addWidget(self.sequence_elements_help, 1, 7, 1, 1)
        self.sequence_name = QtWidgets.QPlainTextEdit(SequenceSettingsUI)
        self.sequence_name.setMaximumSize(QtCore.QSize(16777215, 20))
        self.sequence_name.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.sequence_name.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.sequence_name.setTabChangesFocus(True)
        self.sequence_name.setObjectName("sequence_name")
        self.gridLayout.addWidget(self.sequence_name, 0, 3, 1, 5)
        self.sequence_preview = QtWidgets.QLabel(SequenceSettingsUI)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.sequence_preview.sizePolicy().hasHeightForWidth())
        self.sequence_preview.setSizePolicy(sizePolicy)
        self.sequence_preview.setMinimumSize(QtCore.QSize(0, 20))
        self.sequence_preview.setMaximumSize(QtCore.QSize(16777215, 20))
        self.sequence_preview.setObjectName("sequence_preview")
        self.gridLayout.addWidget(self.sequence_preview, 2, 3, 1, 3)
        self.sequence_start = QtWidgets.QSpinBox(SequenceSettingsUI)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.sequence_start.sizePolicy().hasHeightForWidth())
        self.sequence_start.setSizePolicy(sizePolicy)
        self.sequence_start.setMinimum(1)
        self.sequence_start.setMaximum(999)
        self.sequence_start.setObjectName("sequence_start")
        self.gridLayout.addWidget(self.sequence_start, 3, 6, 1, 1)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem1)
        self.sequence_start_stop = QtWidgets.QPushButton(SequenceSettingsUI)
        self.sequence_start_stop.setMinimumSize(QtCore.QSize(0, 35))
        self.sequence_start_stop.setMaximumSize(QtCore.QSize(16777215, 35))
        self.sequence_start_stop.setObjectName("sequence_start_stop")
        self.horizontalLayout.addWidget(self.sequence_start_stop)
        self.gridLayout.addLayout(self.horizontalLayout, 15, 6, 1, 2)
        self.label_17 = QtWidgets.QLabel(SequenceSettingsUI)
        self.label_17.setObjectName("label_17")
        self.gridLayout.addWidget(self.label_17, 11, 0, 1, 1)
        self.sequence_status_label = QtWidgets.QLabel(SequenceSettingsUI)
        self.sequence_status_label.setObjectName("sequence_status_label")
        self.gridLayout.addWidget(self.sequence_status_label, 14, 3, 1, 5)
        self.label_19 = QtWidgets.QLabel(SequenceSettingsUI)
        self.label_19.setObjectName("label_19")
        self.gridLayout.addWidget(self.label_19, 12, 0, 1, 1)
        self.sequence_camera_gain = QtWidgets.QSpinBox(SequenceSettingsUI)
        self.sequence_camera_gain.setMaximum(300)
        self.sequence_camera_gain.setObjectName("sequence_camera_gain")
        self.gridLayout.addWidget(self.sequence_camera_gain, 12, 3, 1, 1)

        self.retranslateUi(SequenceSettingsUI)
        QtCore.QMetaObject.connectSlotsByName(SequenceSettingsUI)
        SequenceSettingsUI.setTabOrder(self.sequence_name, self.sequence_elements)
        SequenceSettingsUI.setTabOrder(self.sequence_elements, self.sequence_elements_help)
        SequenceSettingsUI.setTabOrder(self.sequence_elements_help, self.sequence_targetdir)
        SequenceSettingsUI.setTabOrder(self.sequence_targetdir, self.sequence_select_targetdir)
        SequenceSettingsUI.setTabOrder(self.sequence_select_targetdir, self.sequence_start_stop)

    def retranslateUi(self, SequenceSettingsUI):
        _translate = QtCore.QCoreApplication.translate
        SequenceSettingsUI.setWindowTitle(_translate("SequenceSettingsUI", "Form"))
        self.label_4.setText(_translate("SequenceSettingsUI", "Number"))
        self.label_7.setText(_translate("SequenceSettingsUI", "Exposure"))
        self.label_15.setText(_translate("SequenceSettingsUI", "Filter"))
        self.label_16.setText(_translate("SequenceSettingsUI", "Status"))
        self.sequence_frametype.setItemText(0, _translate("SequenceSettingsUI", "Light"))
        self.sequence_frametype.setItemText(1, _translate("SequenceSettingsUI", "Flat"))
        self.sequence_frametype.setItemText(2, _translate("SequenceSettingsUI", "Dark"))
        self.sequence_frametype.setItemText(3, _translate("SequenceSettingsUI", "Bias"))
        self.label_5.setText(_translate("SequenceSettingsUI", "Starting Index"))
        self.sequence_select_targetdir.setText(_translate("SequenceSettingsUI", "..."))
        self.label_3.setText(_translate("SequenceSettingsUI", "Frame Type"))
        self.label_9.setText(_translate("SequenceSettingsUI", "ROI"))
        self.label_18.setText(_translate("SequenceSettingsUI", "Every"))
        self.sequence_dither.setSuffix(_translate("SequenceSettingsUI", " frames"))
        self.label_14.setText(_translate("SequenceSettingsUI", "Binning"))
        self.label_2.setText(_translate("SequenceSettingsUI", "Name  Elements"))
        self.label_8.setText(_translate("SequenceSettingsUI", "Target Dir"))
        self.label_6.setText(_translate("SequenceSettingsUI", "Preview"))
        self.label.setText(_translate("SequenceSettingsUI", "Base Name"))
        self.sequence_exposure.setSuffix(_translate("SequenceSettingsUI", "s"))
        self.label_11.setText(_translate("SequenceSettingsUI", "Width"))
        self.sequence_roi_left.setText(_translate("SequenceSettingsUI", "0000"))
        self.sequence_roi_width.setText(_translate("SequenceSettingsUI", "9999"))
        self.label_10.setText(_translate("SequenceSettingsUI", "Left"))
        self.sequence_roi_top.setText(_translate("SequenceSettingsUI", "0000"))
        self.sequence_roi_height.setText(_translate("SequenceSettingsUI", "9999"))
        self.label_12.setText(_translate("SequenceSettingsUI", "Top"))
        self.label_13.setText(_translate("SequenceSettingsUI", "Height"))
        self.sequence_roi_set.setText(_translate("SequenceSettingsUI", "..."))
        self.sequence_elements_help.setText(_translate("SequenceSettingsUI", "?"))
        self.sequence_preview.setText(_translate("SequenceSettingsUI", "TextLabel"))
        self.sequence_start_stop.setText(_translate("SequenceSettingsUI", "Start"))
        self.label_17.setText(_translate("SequenceSettingsUI", "Dither"))
        self.sequence_status_label.setText(_translate("SequenceSettingsUI", "TextLabel"))
        self.label_19.setText(_translate("SequenceSettingsUI", "Camera Gain"))

