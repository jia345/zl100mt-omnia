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

from foris_controller.handler_base import BaseOpenwrtHandler
from foris_controller.utils import logger_wrapper

from foris_controller_backends.password import ForisPasswordUci, SystemPasswordCmd
from foris_controller.exceptions import UciRecordNotFound

from .. import Handler

logger = logging.getLogger(__name__)


class OpenwrtPasswordHandler(Handler, BaseOpenwrtHandler):
    uci = ForisPasswordUci()
    cmd = SystemPasswordCmd()

    @logger_wrapper(logger)
    def check_foris_password(self, password):
        """ Checks foris password

        :param password: plain text password
        :type password: str
        :returns: "good" / "bad" / "unset"
        :rtype: str
        """
        try:
            return "good" if self.uci.check_password(password) else "bad"
        except UciRecordNotFound:
            return "unset"

    @logger_wrapper(logger)
    def set_foris_password(self, password):
        """ Sets password for foris

        :param password: plain text password
        :type password: str
        :returns: True on success False otherwise
        :rtype: bool
        """
        return self.uci.set_password(password)

    @logger_wrapper(logger)
    def set_system_password(self, password):
        """ Sets password for the system (root)

        :param password: plain text password
        :type password: str
        :returns: True on success False otherwise
        :rtype: bool
        """
        return self.cmd.set_password(password)
