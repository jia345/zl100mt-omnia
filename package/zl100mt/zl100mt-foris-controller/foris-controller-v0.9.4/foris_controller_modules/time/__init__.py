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

from datetime import datetime

from foris_controller.module_base import BaseModule
from foris_controller.handler_base import wrap_required_functions


class TimeModule(BaseModule):
    logger = logging.getLogger(__name__)

    def action_get_settings(self, data):
        """ Get current time settings
        :param data: supposed to be {}
        :type data: dict
        :returns: current time settings {'timezone': '..', 'zonename': '..'}
        :rtype: dict
        """
        backend_data = self.handler.get_settings()
        backend_data["time_settings"]["time"] = datetime.now().isoformat()
        return backend_data

    def action_update_settings(self, data):
        """ Updates time settings
        :param data: new time settings {'timezone': '..', 'zonename': '..'}
        :type data: dict
        :returns: result of the update {'result': '..'}
        :rtype: dict
        """
        if "time" in data["time_settings"]:
            time = datetime.strptime(data["time_settings"]["time"], "%Y-%m-%dT%H:%M:%S.%f")
        else:
            time = None
        res = self.handler.update_settings(
            data["region"], data["city"], data["timezone"],
            data["time_settings"]["how_to_set_time"], time
        )
        if res:
            self.notify("update_settings", data)
        return {"result": res}

    def action_get_router_time(self, data):
        """ Returns current router time

        :param data: supposed to be {}
        :type data: dict
        :returns: current time in isoformat (UTC)
        :rtype: dict
        """
        # I think that we can safely skip any backend interaction here...
        return {"time": datetime.now().isoformat()}

    def action_ntpdate_trigger(self, data):
        """ Tries to run ntpdate to update system time
        """

        def exit_notify(msg):
            if msg["result"]:
                # if passed fill in the time
                msg["time"] = datetime.now().isoformat()
            self.notify("ntpdate_finished", msg)

        async_id = self.handler.ntpdate_trigger(exit_notify, self.reset_notify)
        self.notify("ntpdate_started", {"id": async_id})
        return {"id": async_id}


@wrap_required_functions([
    'get_settings',
    'update_settings',
    'ntpdate_trigger',
])
class Handler(object):
    pass
