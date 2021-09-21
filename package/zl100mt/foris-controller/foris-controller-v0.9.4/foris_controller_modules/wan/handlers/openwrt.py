#
# foris-controller
# Copyright (C) 2018 CZ.NIC, z.s.p.o. (http://www.nic.cz/)
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
from foris_controller_backends.wan import WanUci, WanTestCommands, WanStatusCommands

from .. import Handler

logger = logging.getLogger(__name__)


class OpenwrtWanHandler(Handler, BaseOpenwrtHandler):
    uci = WanUci()
    test_cmds = WanTestCommands()
    status_cmds = WanStatusCommands()

    @logger_wrapper(logger)
    def get_settings(self):
        """ get wan settings

        :returns: current wan settings
        :rtype: dict
        """
        return self.uci.get_settings()

    @logger_wrapper(logger)
    def update_settings(self, new_settings):
        """ updates current wan settings

        :param new_settings: new settings dictionary
        :type new_settings: dict

        :return: True if update passes
        :rtype: boolean
        """
        self.uci.update_settings(**new_settings)
        return True

    @logger_wrapper(logger)
    def connection_test_trigger(
            self, test_kinds, notify_function, exit_notify_function, reset_notify_function):
        """ Triggering of the connection test
        :param test_kinds: which kinds of tests should be run (ipv4, ipv6, dns)
        :type test_kinds: array of str
        :param notify_function: function for sending notifications
        :type notify_function: callable
        :param exit_notify_function: function for sending notification when a test finishes
        :type exit_notify_function: callable
        :param reset_notify_function: function to reconnect to the notification bus
        :type reset_notify_function: callable
        :returns: generated_test_id
        :rtype: str
        """
        return OpenwrtWanHandler.test_cmds.connection_test_trigger(
            test_kinds, notify_function, exit_notify_function, reset_notify_function
        )

    @logger_wrapper(logger)
    def connection_test_status(self, test_id):
        """ Connection test status
        :param test_id: id of the test to display
        :type test_id: str
        :returns: connection test status + test data
        :rtype: dict
        """
        return OpenwrtWanHandler.test_cmds.connection_test_status(test_id)

    @logger_wrapper(logger)
    def get_wan_status(self):
        """ Obtians wan status
        :returns: {'up': True/False}
        :rtype: dict
        """
        status = self.status_cmds.get_status()
        return {
            'up': status["up"],
            'last_seen_duid': status["duid"],
            'proto': status["proto"],
        }
