import logging

from PyQt5 import QtWidgets, QtGui

from pyastroimageview.uic.sequence_settings_uic import Ui_SequenceSettingsUI
from pyastroimageview.uic.sequence_title_help_uic import Ui_SequenceTitleHelpWindow

from pyastroimageview.ImageSequence import ImageSequence

class ImageSequnceControlUI(QtWidgets.QWidget):

    class HelpWindow(QtWidgets.QMainWindow):
        def __init__(self):
            super().__init__()

            self.ui = Ui_SequenceTitleHelpWindow()
            self.ui.setupUi(self)

            self.setWindowTitle('Title Formatting Help')

        def hide_help(self):
            self.hide()

        def show_help(self):
            self.show()

    def __init__(self, device_manager):
        super().__init__()

        self.ui = Ui_SequenceSettingsUI()
        self.ui.setupUi(self)

        self.ui.sequence_elements_help.toggled.connect(self.help_toggle)
        self.ui.sequence_select_targetdir.pressed.connect(self.select_targetdir)

        self.device_manager = device_manager

        self.sequence = ImageSequence(self.device_manager)

        self.update_ui()

        self.ui.sequence_name.textChanged.connect(self.values_changed)
        self.ui.sequence_elements.textChanged.connect(self.values_changed)
        self.ui.sequence_exposure.valueChanged.connect(self.values_changed)
        self.ui.sequence_frametype.currentIndexChanged.connect(self.values_changed)
        self.ui.sequence_exposure.valueChanged.connect(self.values_changed)
        self.ui.sequence_start.valueChanged.connect(self.values_changed)

        self.title_help = self.HelpWindow()

        self.setWindowTitle('Sequence')

        self.show()

    def values_changed(self, *obj):
        self.update_sequence()
        self.ui.sequence_preview.setText(self.sequence.get_filename())

    def update_sequence(self):
        if self.sender() == self.ui.sequence_name:
            self.sequence.name = self.ui.sequence_name.toPlainText()
        elif self.sender() == self.ui.sequence_elements:
            self.sequence.name_elements = self.ui.sequence_elements.toPlainText()
        elif self.sender() == self.ui.sequence_exposure:
            self.sequence.exposure = self.ui.sequence_exposure.value()
        elif self.sender() == self.ui.sequence_start:
            self.sequence.start_index = self.ui.sequence_start.value()
        elif self.sender == self.ui.sequence_number:
            self.sequence.number_frames = self.ui.sequence_number.value()
        elif self.sender() == self.ui.sequence_frametype:
            self.sequence.frame_type = self.ui.sequence_frametype.itemText(self.ui.sequence_frametype.currentIndex())
        elif self.sender() == self.ui.sequence_targetdir:
            self.sequence.target_dir = self.ui.sequence_targetdir.toPlainText()
        else:
            logging.error('Unknown sender is update_sequence!')

    def update_ui(self):
        logging.info(f'settings target dir plaintext to {self.sequence.target_dir}')
        self.ui.sequence_name.setPlainText(self.sequence.name)
        self.ui.sequence_elements.setPlainText(self.sequence.name_elements)
        self.ui.sequence_preview.setText(self.sequence.get_filename())
        self.ui.sequence_exposure.setValue(self.sequence.exposure)
        self.ui.sequence_frametype.setCurrentText(self.sequence.frame_type)
        self.ui.sequence_number.setValue(self.sequence.number_frames)
        self.ui.sequence_start.setValue(self.sequence.start_index)
        logging.info(f'settings target dir plaintext to {self.sequence.target_dir}')
        self.ui.sequence_targetdir.setPlainText(self.sequence.target_dir)

        # move cursor to end of target_dir
        cursor = self.ui.sequence_targetdir.textCursor()
        logging.info(f'{cursor.position()}')
        cursor.movePosition(QtGui.QTextCursor.EndOfLine)
        logging.info(f'{cursor.position()}')
        self.ui.sequence_targetdir.setTextCursor(cursor)

    def help_toggle(self):
        if self.ui.sequence_elements_help.isChecked():
            self.title_help.show()
        else:
            self.title_help.hide()

    def select_targetdir(self):
        target_dir = QtWidgets.QFileDialog.getExistingDirectory(None,
                                                                'Target Directory',
                                                                self.sequence.target_dir,
                                                                QtWidgets.QFileDialog.ShowDirsOnly)

        logging.info(f'select target_dir: {target_dir}')

        if len(target_dir) < 1:
            return

        self.sequence.target_dir = target_dir
        logging.info(f'set target dir {self.sequence.target_dir}')
        self.update_ui()
