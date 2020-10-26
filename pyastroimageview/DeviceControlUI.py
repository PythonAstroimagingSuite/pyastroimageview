#
# Device control UI
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

class DeviceControlUI(QtWidgets.QMainWindow):

    def add_ui_element(self, ui, name):
        vbox = QtWidgets.QVBoxLayout()
        vbox.addWidget(ui)
        vbox.setSpacing(0)
        gbox = QtWidgets.QGroupBox(name)
        gbox.setLayout(vbox)
        gbox.setCheckable(True)
        gbox.clicked.connect(self.handle_groupbox_show_hide)
        self.form.addWidget(gbox)

    def __init__(self):
        super().__init__()

        self.form = QtWidgets.QFormLayout()
        self.form.setHorizontalSpacing(0)
        self.form.setVerticalSpacing(4)
        self.form.setContentsMargins(3, 3, 3, 3)

        window = QtWidgets.QWidget()
        window.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        self.form.setSizeConstraint(QtWidgets.QLayout.SetFixedSize)
        window.setLayout(self.form)

        self.setCentralWidget(window)

        self.setWindowTitle('Device Control')

        self.activateWindow()
#       window_flags = self.windowFlags()
#        self.setWindowFlags(window_flags | QtCore.Qt.WindowStaysOnTopHint)
        self.showNormal()

    # FIXME would be nice if this was inside the function that created all this
    # probably should be a separate object!
    def handle_groupbox_show_hide(self, checked):
        logging.info(f'groupbox {checked} {self.sender()} {self.sender().children()}')

        # FIXME THIS IS VERY DEPENDENT ON HOW WIDGETS ADDED ABOVE!
        # FIXME Consider using QSignalMapper or individual handlers
        self.sender().children()[1].setVisible(checked)

        # FIXME This seems to be needed so some callbacks occur to render/hide
        # widgets and so then adjustSize() reduces/increases size appropriately
        # Otherwise there is 'ghost' space left when you hide a control
        for i in range(0, 10):
            QtWidgets.QApplication.processEvents()

        self.adjustSize()
