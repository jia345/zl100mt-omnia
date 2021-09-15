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

from foris_controller.module_base import BaseModule
from foris_controller.handler_base import wrap_required_functions


class DataCollectModule(BaseModule):
    logger = logging.getLogger(__name__)

    def action_get_registered(self, data):
        """ Obtains information whether a user(email) appears to have this device registered.
        :param data: {email:..., language:...}
        :type data: dict
        :returns: status and sometimes url to register the device
        :rtype: dict
        """
        return self.handler.get_registered(data["email"], data["language"])

    def action_get(self, data):
        """ Get information whether user allowd to collect data
        :param data: {}
        :type data: dict
        :returns: info about data collecting
        :rtype: dict
        """
        return {"agreed": self.handler.get_agreed()}

    def action_set(self, data):
        """ Update configuration of data collect
        :param data: {"agreed": True/False}
        :type data: dict
        :returns: {"result": True / False}
        :rtype: dict
        """
        res = self.handler.set_agreed(data["agreed"])
        if res:
            self.notify("set", data)
        return {"result": res}

    def action_get_honeypots(self, data):
        """ Get configuration of honeypots
        :param data: {}
        :type data: dict
        :returns: {"minipots": {...}, "log_credentials": True/False}
        :rtype: dict
        """
        return self.handler.get_honeypots()

    def action_set_honeypots(self, data):
        """ Update configuration of honeypots
        :param data: {"minipots": {...}, "log_credentials": True/False}
        :type data: dict
        :returns: {"result": True / False}
        :rtype: dict
        """
        res = self.handler.set_honeypots(data)
        if res:
            self.notify("set_honeypots", data)
        return {"result": res}


@wrap_required_functions([
    'get_registered',
    'get_agreed',
    'set_agreed',
    'get_honeypots',
    'set_honeypots',
])
class Handler(object):
    pass
