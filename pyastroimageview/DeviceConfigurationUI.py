import logging

from PyQt5 import QtWidgets

from pyastrobackend.BackendConfig import get_backend_for_os, get_backend, get_backend_choices
from pyastroimageview.ApplicationContainer import AppContainer

# FIXME nasty looks into objects with getattr but
#       just a placeholder till I can figure out something
#       better
def device_setup_ui(device, device_class):
    backend_attr = f'{device_class}_backend'
    driver_attr = f'{device_class}_driver'
    manager_attr = f'{device_class}_manager'
    old_backend = device.settings.get_key(backend_attr)
    logging.info(f'device_setup_ui: old backend = {old_backend}')
    new_backend = backend_setup_ui(old_backend)
    logging.info(f'device_setup_ui: new backend = {new_backend}')
    if new_backend != old_backend:
        backend_changed = True
        device.settings.set_key(backend_attr, new_backend)
        device_manager = AppContainer.find('/dev')
        manager_fn = f'set_{device_class}_backend'
        fn = getattr(device_manager, manager_fn)
        logging.debug(f'manager_fn = {manager_fn} fn={fn}')
        if fn is not None:
            logging.debug(f'calling {fn}')
            fn(new_backend)
        else:
            logging.error(f'unabled to find {manager_fn}')
            return None
        device.settings.set_key(f'{device_class}_driver', '')
        device.settings.write()
    else:
        backend_changed = False

    # if backend changed call to set_<device_class>_backend() above
    # will change /dev/<device_class>_backend
    backend = AppContainer.find(f'/dev/{device_class}_backend')
    logging.debug(f'device_setup_ui: backend = {backend}')

    # update internal data structures to reflect changes
    # at device manager level
    #device.settings.set_key(f'{device_class}_driver', '')
    #logging.debug('calling update_manager()')
    #device.update_manager()

    new_choice = driver_setup_ui(backend,
                                 getattr(device, manager_attr),
                                 device.settings.get_key(driver_attr),
                                 device_class)

    if new_choice is not None:
        device.settings.set_key(driver_attr, new_choice)
        device.settings.write()
        device.set_device_label()

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

def driver_setup_ui(backend, manager, driver, device_class):
    logging.debug(f'driver_setup_ui: backend={backend} manager={manager} ' + \
                  f'driver={driver} device_class={device_class}')
    if driver:
        last_choice = driver
    else:
        last_choice = ''

    new_driver = None
    logging.debug(f'manager = {dir(manager)}')
    logging.debug(f'manager module = {manager.__module__}')
    logging.debug(f'manager.has_chooser = {manager.has_chooser} {manager.has_chooser()}')
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