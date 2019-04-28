#
# foris-controller
# Copyright (C) 2017 CZ.NIC, z.s.p.o. (http://www.nic.cz/)
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software Foundation,
# Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301  USA
#

import logging

from foris_controller.handler_base import BaseMockHandler
from foris_controller.utils import logger_wrapper

from .. import Handler

logger = logging.getLogger(__name__)


class MockPasswordHandler(Handler, BaseMockHandler):
    system_password = None
    foris_password = None

    @logger_wrapper(logger)
    def check_foris_password(self, password):
        """ Mocks password checking

        :param password: in plain text password
        :type password: str
        :returns: "good" / "bad" / "unset"
        :rtype: str
        """
        if self.foris_password is None:
            return "unset"
        return "good" if self.foris_password == password else "bad"

    @logger_wrapper(logger)
    def set_foris_password(self, password):
        """ Mocks password setting for foris

        :param password: plain text password
        :type password: str
        :returns: True on success False otherwise
        :rtype: bool
        """
        self.foris_password = password
        return True

    @logger_wrapper(logger)
    def set_system_password(self, password):
        """ Mocks password setting for system

        :param password: plain text password
        :type password: str
        :returns: True on success False otherwise
        :rtype: bool
        """
        self.system_password = password
        return True
