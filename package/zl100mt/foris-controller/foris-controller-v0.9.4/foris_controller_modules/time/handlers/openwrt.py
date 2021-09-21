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
from foris_controller_backends.time import TimeUciCommands, TimeAsyncCmds

from .. import Handler

logger = logging.getLogger(__name__)


class OpenwrtTimeHandler(Handler, BaseOpenwrtHandler):
    uci = TimeUciCommands()
    async = TimeAsyncCmds()

    @logger_wrapper(logger)
    def get_settings(self):
        """ Get time settings

        :returns: current time settiongs
        :rtype: dict
        """
        return self.uci.get_settings()

    @logger_wrapper(logger)
    def update_settings(self, region, city, timezone, how_to_set_time, time=None):
        """ Updates current time settings

        :param region: set the region (Europe, America, Asia, ...)
        :type region: string
        :param city: set the city (Prague, London, ...)
        :type city: string
        :param timezone: set timezone ("UTC", "CET-1CEST,M3.5.0,M10.5.0/3", ...)
        :type timezone: string
        :param how_to_set_time: "ntp" or "manual"
        :type how_to_set_time: string
        :param time: time to be set
        :type time: datetime.datetime
        :returns: True if update passes
        :rtype: bool
        """

        return self.uci.update_settings(region, city, timezone, how_to_set_time, time)

    @logger_wrapper(logger)
    def ntpdate_trigger(self, exit_notify_function, reset_notify_function):
        """ Triggers the ntpdate command in async mode
        :param exit_notify_function: function for sending notification when the cmds finishes
        :type exit_notify_function: callable
        :param reset_notify_function: function to reconnect to the notification bus
        :type reset_notify_function: callable
        :returns: generated_ntpdate_id
        :rtype: str
        """
        return self.async.ntpdate_trigger(exit_notify_function, reset_notify_function)
