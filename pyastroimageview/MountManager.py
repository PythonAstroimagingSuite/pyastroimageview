# FIXME this needs to be 'configured' somewhere central as currently
# all source files for hw managers reference contrete backend class this way
from pyastroimageview.BackendConfig import get_backend_for_os

BACKEND = get_backend_for_os()

if BACKEND == 'ASCOM':
    from pyastrobackend.ASCOM.Mount import Mount
elif BACKEND == 'INDI':
    from pyastrobackend import INDIBackend as Backend
else:
    raise Exception(f'Unknown backend {BACKEND} - choose ASCOM or INDI in BackendConfig.py')

class MountManager(Mount):
    def __init__(self, backend):
        super().__init__(backend)

