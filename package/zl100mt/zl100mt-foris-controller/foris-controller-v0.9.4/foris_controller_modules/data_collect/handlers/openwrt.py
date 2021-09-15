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

from foris_controller_backends.data_collect import (
    RegisteredCmds, DataCollectUci
)

from .. import Handler

logger = logging.getLogger(__name__)


class OpenwrtDataCollectHandler(Handler, BaseOpenwrtHandler):

    registered_cmds = RegisteredCmds()
    uci = DataCollectUci()

    @logger_wrapper(logger)
    def get_registered(self, email, language):
        """ Tries to obtain info whether the user was registered

        :param email: email which will be used during the server query
        :type email: str
        :param language: language which will be used during the server query
        :type language: str
        :returns: result
        :rtype: dict
        """
        return OpenwrtDataCollectHandler.registered_cmds.get_registered(email, language)

    @logger_wrapper(logger)
    def get_agreed(self):
        """ Get information whether the user agreed with data collect
        :returns: True if user agreed, False otherwise
        :rtype: boolean
        """
        return self.uci.get_agreed()

    @logger_wrapper(logger)
    def set_agreed(self, agreed):
        """ Mock setting information whether the user agreed with data collect
        :param agreed: user agreed with data collect (True/False)
        :type agreed: boolean
        :returns: True
        :rtype: boolean
        """
        return self.uci.set_agreed(agreed)

    @logger_wrapper(logger)
    def get_honeypots(self):
        """ Get configuration of the honeypots
        :returns: {"minipots": {...}, "log_credentials": True/False}
        :rtype: dict
        """
        return self.uci.get_honeypots()

    @logger_wrapper(logger)
    def set_honeypots(self, honepot_settings):
        """ Set configuration of the honeypots
        :param honepot_settings: {"minipots": {...}, "log_credentials": True/False}
        :type honepot_settings: dict

        :returns: True
        :rtype: boolean
        """
        return self.uci.set_honeypots(honepot_settings)
