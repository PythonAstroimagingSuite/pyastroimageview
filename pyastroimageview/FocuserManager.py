#
# Focuser manager
#
# Copyright 2019 Michael Fulbright
#
#
#    pyastroimageview is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
import logging


class FocuserManager:
    def __init__(self, backend):
        super().__init__(backend)

    def connect(self, driver):
        if not super().is_connected():
            try:
                rc = super().connect(driver)

                if not rc:
                    return False

            except Exception:
                # FIXME need more specific exception
                logging.error('FocuserManager:connect() Exception ->', exc_info=True)
                return False

        return True
