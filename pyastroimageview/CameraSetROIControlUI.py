#
# Camera ROI dialog
#
# Copyright 2019 Michael Fulbright
#
#
#    pyastroimageview is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
import logging

from PyQt5 import QtWidgets
from pyastroimageview.uic.camera_roidialog_uic import Ui_camera_set_roi_dialog

class CameraSetROIDialog(QtWidgets.QDialog):
    def __init__(self):
        super().__init__()

        self.ui = Ui_camera_set_roi_dialog()
        self.ui.setupUi(self)

    def reset_roi_fields(self):
        self.ui.left_spinbox.setValue(self.roi[0])
        self.ui.top_spinbox.setValue(self.roi[1])
        self.ui.width_spinbox.setValue(self.roi[2])
        self.ui.height_spinbox.setValue(self.roi[3])

    def update_roi(self, left=None, top=None, width=None, height=None):
        """Validate roi values.

        Width and height have precedence over left and top.

        Should only pass one value in at a time but it should work in theory.
        """
        if left:
            width = self.ui.width_spinbox.value()
            left = min(left, self.maxx - width)
            self.ui.left_spinbox.setValue(left)

        if top:
            height = self.ui.height_spinbox.value()
            top = min(top, self.maxy - height)
            self.ui.top_spinbox.setValue(top)

        if width:
            left = self.ui.left_spinbox.value()
            left = min(left, self.maxx - width)
            self.ui.left_spinbox.setValue(left)

        if height:
            top = self.ui.top_spinbox.value()
            top = min(top, self.maxy - height)
            self.ui.top_spinbox.setValue(top)

    def left_changed(self, new_left):
        self.update_roi(left=new_left)

    def top_changed(self, new_top):
        self.update_roi(top=new_top)

    def width_changed(self, new_width):
        self.update_roi(width=new_width)

    def height_changed(self, new_height):
        self.update_roi(height=new_height)

    def center_roi(self):
        width = self.ui.width_spinbox.value()
        height = self.ui.height_spinbox.value()

        top = int((self.maxy - height) / 2)
        left = int((self.maxx - width) / 2)

        self.ui.top_spinbox.setValue(top)
        self.ui.left_spinbox.setValue(left)

    def run(self, roi, settings):

        self.roi = roi

        self.maxx = int(settings.frame_width / settings.binning)
        self.maxy = int(settings.frame_height / settings.binning)

        self.ui.left_spinbox.setValue(roi[0])
        self.ui.top_spinbox.setValue(roi[1])
        self.ui.width_spinbox.setValue(roi[2])
        self.ui.height_spinbox.setValue(roi[3])

        self.ui.width_spinbox.setMaximum(self.maxx)
        self.ui.height_spinbox.setMaximum(self.maxy)
        self.ui.left_spinbox.setMaximum(self.maxx)
        self.ui.top_spinbox.setMaximum(self.maxy)

        self.ui.left_spinbox.valueChanged.connect(self.left_changed)
        self.ui.top_spinbox.valueChanged.connect(self.top_changed)
        self.ui.width_spinbox.valueChanged.connect(self.width_changed)
        self.ui.height_spinbox.valueChanged.connect(self.height_changed)

        self.ui.reset.pressed.connect(self.reset_roi_fields)
        self.ui.center.pressed.connect(self.center_roi)

        result = self.exec()

        logging.info(f'diag result = {result}')

        if result == QtWidgets.QDialog.Accepted:
            return (self.ui.left_spinbox.value(), self.ui.top_spinbox.value(),
                    self.ui.width_spinbox.value(), self.ui.height_spinbox.value())
        else:
            return None
