# FIXME this needs to be 'configured' somewhere central as currently
# all source files for hw managers reference contrete backend class this way
from pyastrobackend.BackendConfig import get_backend_for_os

import logging

class MountManager:
    def __init__(self, backend):
        super().__init__(backend)

    def connect(self, driver):
        if not super().is_connected():
            try:
                rc = super().connect(driver)

                if not rc:
                    return False

            except Exception:
                logging.error('MountManager:connect() Exception ->', exc_info=True)
                return False

        return True
