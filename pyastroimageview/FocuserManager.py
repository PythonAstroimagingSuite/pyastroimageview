# FIXME this needs to be 'configured' somewhere central as currently
# all source files for hw managers reference contrete backend class this way
from pyastrobackend import ASCOMBackend as Backend

class FocuserManager(Backend.Focuser):
    def __init__(self):
        super().__init__()
