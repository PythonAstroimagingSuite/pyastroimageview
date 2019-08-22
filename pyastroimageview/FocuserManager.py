# FIXME this needs to be 'configured' somewhere central as currently
# all source files for hw managers reference contrete backend class this way
from pyastrobackend.BackendConfig import get_backend_for_os

import logging

BACKEND = get_backend_for_os()
if BACKEND == 'ASCOM':
    from pyastrobackend.ASCOM.Focuser import Focuser
elif BACKEND == 'ALPACA':
    from pyastrobackend.Alpaca.Focuser import Focuser
elif BACKEND == 'INDI':
    from pyastrobackend.INDIBackend import Focuser
else:
    raise Exception(f'Unknown backend {BACKEND} - choose ASCOM or INDI in BackendConfig.py')

class FocuserManager(Focuser):
    def __init__(self, backend):
        super().__init__(backend)

    def connect(self, driver):
        if not super().is_connected():
            try:
                logging.info('calling connect')
                if BACKEND == 'ALPACA':
                    device_number = driver.split(':')[1]
                    logging.debug(f'Connecting to ALPACA:focuser:{device_number}')
                    rc = super().connect(f'ALPACA:focuser:{device_number}')
                else:
                    rc = super().connect(driver)
                if not rc:
                    return False

            except Exception:
                logging.error('FocuserManager:connect() Exception ->', exc_info=True)
                return False

        return True
