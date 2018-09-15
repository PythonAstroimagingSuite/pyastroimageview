# this is a simple dependency injector/IOC idea
# I can't use dbus in windows (easily) and pyro seems like overkill
# and I don't want to involve networking
#
# I just want a way to register objects with a 'name' and have anywhere in
# the code reference this object by its 'name'.  The advantage, as I understand
# from DI articles I've read, is that I can change the implementation anytime
# and via this container the rest of the code shouldn't have to change
#
# The downside is this is essentially a signleton/big global state block
# which seems to be discouraged as it can make testing difficult
#
# But honestly I don't understand how a big application can avoid this other
# than passing variables up and down code paths which doesn't seem any better.
#
# So we'll give this a try...
import sys
import logging
import traceback

class ApplicationContainer(object):
    __debug = True

    def __init__(self):
        super().__setattr__('_values', {})

    def register(self, key, value):
        self._values[key] = value

        if self.__debug:
            stack = sys._getframe(1)
            f = traceback.extract_stack(stack)[-1]
            logging.info(f'AppContainer: key \'{key}\' registered to {value} from {f}')

    def find(self, key):
        if key not in self._values:
            raise AttributeError(f'\'{key}\' is not registered.')

        if self.__debug:
            stack = sys._getframe(1)
            f = traceback.extract_stack(stack)[-1]
            logging.info(f'AppContainer: key \'{key}\' referenced from {f}')

        attribute = self._values[key]

        return attribute(self) if callable(attribute) else attribute

    def __setattr__(self, key, value):
        print(key, value)
        self.register(key, value)

#    def __getattr__(self, key):
#        if key != '_values':
#            if key not in self._values:
#                raise AttributeError(f"'{key}' is not registered.")
#
#            attribute = self._values[key]
#
#            return attribute(self) if callable(attribute) else attribute

# this is what we use
AppContainer = ApplicationContainer()
