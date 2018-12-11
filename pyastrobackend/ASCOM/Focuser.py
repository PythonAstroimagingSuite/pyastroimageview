""" Pure ASCOM solution """
from pyastrobackend.BaseBackend import BaseFocuser

import logging

import pythoncom
import win32com.client

class Focuser(BaseFocuser):
    def __init__(self):
        self.focus = None

    def has_chooser(self):
        return True

    def show_chooser(self, last_choice):
        pythoncom.CoInitialize()
        chooser = win32com.client.Dispatch("ASCOM.Utilities.Chooser")
        chooser.DeviceType="Focuser"
        focuser = chooser.Choose(last_choice)
        logging.info(f'choice = {focuser}')
        return focuser

    def connect(self, name):
        pythoncom.CoInitialize()
        self.focus = win32com.client.Dispatch(name)

        if self.focus.Connected:
            logging.info("	-> Focuser was already connected")
        else:
            try:
                self.focus.Connected = True
            except Exception as e:
                logging.error('ASCOMBackend:focuser:connect() Exception ->', exc_info=True)
                return False

        if self.focus.Connected:
            logging.info(f"	Connected to focuser {name} now")
        else:
            logging.info("	Unable to connect to focuser, expect exception")

        # check focuser works in absolute position
        if not self.focus.Absolute:
            logging.info("ERROR - focuser does not use absolute position!")

        return True

    def disconnect(self):
        if self.focuser:
            if self.focuser.Connected:
                self.focuser.Connected = False
                self.focuser = None

    def is_connected(self):
        if self.focus:
            return self.focus.Connected
        else:
            return False

    def get_absolute_position(self):
        return self.focus.Position

    def move_absolute_position(self, abspos):
        self.focus.Move(abspos)
        return True

    def get_max_absolute_position(self):
        return self.focus.MaxStep

    def get_current_temperature(self):
        return self.focus.Temperature

    def stop(self):
        self.focus.Halt()

    def is_moving(self):
        return self.focus.isMoving
