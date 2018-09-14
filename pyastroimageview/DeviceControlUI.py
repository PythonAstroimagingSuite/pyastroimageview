import logging

from PyQt5 import QtCore, QtWidgets

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
        self.sender().children()[1].setVisible(checked)

        # FIXME This seems to be needed so some callbacks occur to render/hide
        # widgets and so then adjustSize() reduces/increases size appropriately
        # Otherwise there is 'ghost' space left when you hide a control
        for i in range(0, 10):
            QtWidgets.QApplication.processEvents()

        self.adjustSize()
