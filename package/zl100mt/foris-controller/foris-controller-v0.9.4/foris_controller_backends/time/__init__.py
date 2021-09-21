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

from foris_controller.app import app_info
from foris_controller_backends.uci import (
    UciBackend, get_option_anonymous, get_option_named, parse_bool, store_bool
)
from foris_controller_backends.services import OpenwrtServices
from foris_controller_backends.cmdline import BaseCmdLine, AsyncCommand
from foris_controller.utils import writelock, RWLock


logger = logging.getLogger(__name__)


class SetTimeCommand(BaseCmdLine):
    time_lock = RWLock(app_info["lock_backend"])

    @writelock(time_lock, logger)
    def set_hwclock(self):
        self._set_hwclock()

    def _set_hwclock(self):
        # sometimes hwclock fails without an error so let's try to call it twice to be sure
        self._run_command("/sbin/hwclock", "-u", "-w")
        self._run_command("/sbin/hwclock", "-u", "-w")

    @writelock(time_lock, logger)
    def set_time(self, time):
        """ Sets current time using date command
        :param time: time to be set
        :type time: datetime.datetime
        """
        # don't care about retvals of next command (it should raise an exception on error)
        self._run_command("/bin/date", "-s", time.strftime("%Y-%m-%d %H:%M:%S"))
        self._set_hwclock()


class TimeUciCommands(object):

    def get_settings(self):

        with UciBackend() as backend:
            system_data = backend.read("system")

        timezone = get_option_anonymous(system_data, "system", "system", 0, "timezone")
        zonename = get_option_anonymous(system_data, "system", "system", 0, "zonename")
        try:
            region, city = zonename.split("/")
        except ValueError:
            region, city = "", ""
        ntp = parse_bool(get_option_named(system_data, "system", "ntp", "enabled", "1"))

        return {
            "region": region,
            "city": city,
            "timezone": timezone,
            "time_settings":  {"how_to_set_time": "ntp" if ntp else "manual"},
        }

    def update_settings(self, region, city, timezone, how_to_set_time, time=None):
        """
        :param time: Time to be set
        """

        with UciBackend() as backend:
            backend.set_option("system", "@system[0]", "timezone", timezone)
            backend.set_option("system", "@system[0]", "zonename", "%s/%s" % (region, city))
            backend.set_option("system", "ntp", "enabled", store_bool(how_to_set_time == "ntp"))

        with OpenwrtServices() as services:
            if how_to_set_time == "ntp":
                # enable might fail, when sysntpd is already enabled
                services.enable("sysntpd", fail_on_error=False)
                services.restart("sysntpd", fail_on_error=False)
            else:
                # disable might fail, when sysntpd is already disabled
                services.disable("sysntpd", fail_on_error=False)
                services.stop("sysntpd", fail_on_error=False)

            # restart system (update timezones etc)
            services.restart("system")

        if how_to_set_time == "manual":
            SetTimeCommand().set_time(time)  # time should be set (thanks to validation)

        return True


class TimeAsyncCmds(AsyncCommand):

    def ntpdate_trigger(self, exit_notify_function, reset_notify_function):
        """ Executes ntpdate in async modude

        This means that we don't wait for result, but a async_id will be returned immediatelly.
        Then we cat watch ntpdate notifications with the same async_id

        :param exit_notify_function: function which is used to send notifications back to client
                                     when cmd exits
        :type exit_notify_function: callable
        :param reset_notify_function: function which resets notification connection
        :type reset_notify_function: callable
        :returns: async id
        :rtype: str
        """
        logger.debug("Starting ntpdate.")

        # handler which will be called when the program
        def handler_exit(process_data):
            result = process_data.get_retval() == 0

            if result:
                # try to write data directly into hw
                # before sending a successful notification
                SetTimeCommand().set_hwclock()

            exit_notify_function({"id": process_data.id, "result": result})
            logger.debug("ntpdate finished: (retval=%d)" % process_data.get_retval())

        # get all ntpserver
        with UciBackend() as backend:
            system_data = backend.read("system")

        servers = get_option_named(system_data, "system", "ntp", "server", [])

        async_id = self.start_process(
            ["/usr/sbin/ntpdate"] + servers,
            [],
            handler_exit,
            reset_notify_function,
        )
        logger.debug("ntpdate started in async mode '%s'." % async_id)

        return async_id
