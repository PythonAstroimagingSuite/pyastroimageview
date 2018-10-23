# FIXME not best way to control the backend!

#backend = 'ASCOM'
#BACKEND = 'INDI'

def get_backend_for_os():
    import os
    # chose an implementation, depending on os
    if os.name == 'nt': #sys.platform == 'win32':
        return 'ASCOM'
    elif os.name == 'posix':
        return 'INDI'
    else:
        raise Exception("Sorry: no implementation for your platform ('%s') available" % os.name)

