import logging

from PyQt5 import QtWidgets

from pyastrobackend.BackendConfig import get_backend_for_os, get_backend, get_backend_choices

def backend_setup_ui(current_backend):
    new_backend = None
    possible_backends = get_backend_choices()

    if len(possible_backends) < 1:
        QtWidgets.QMessageBox.critical(None, 'Error', 'No backends available!',
                                       QtWidgets.QMessageBox.Ok)
        return

    if current_backend in possible_backends:
        selection = possible_backends.index(current_backend)
    else:
        selection = 0

    choice, ok = QtWidgets.QInputDialog.getItem(None, 'Choose Backend',
                                                       'Backend', possible_backends, selection)
    if ok:
        new_backend = choice

    return new_backend

def device_setup_ui(backend, manager, driver, device_class):
    logging.debug(f'device_setup_ui: backend={backend} manager={manager} ' + \
                  f'driver={driver} device_class={device_class}')
    if driver:
        last_choice = driver
    else:
        last_choice = ''

    new_driver = None
    if manager.has_chooser():
        choice = manager.show_chooser(last_choice)
        if len(choice) > 0:
            new_driver = choice
    else:
        choices = backend.getDevicesByClass(device_class)

        if len(choices) < 1:
            QtWidgets.QMessageBox.critical(None, 'Error', 'No devices available!',
                                           QtWidgets.QMessageBox.Ok)
            return

        if last_choice in choices:
            selection = choices.index(last_choice)
        else:
            selection = 0

        choice, ok = QtWidgets.QInputDialog.getItem(None, 'Choose Driver',
                                                           'Driver', choices, selection)
        if ok:
            new_driver = choice

    return new_driver