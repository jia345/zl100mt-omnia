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
from foris_controller.utils import logger_wrapper

class FirewallModule(BaseModule):
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)

    @logger_wrapper(logger)
    def action_get_settings(self, data):
        return self.handler.get_settings()

    @logger_wrapper(logger)
    def action_set_firewall(self, data):
        res = self.handler.set_firewall(data)
        if res:
            self.notify("set_firewall", data)
        return {"result": res}

    @logger_wrapper(logger)
    def action_set_ip_filter(self, data):
        res = self.handler.set_ip_filter(data)
        if res:
            self.notify("set_ip_filter", data)
        return {"result": res}

    @logger_wrapper(logger)
    def action_set_mac_filter(self, data):
        res = self.handler.set_mac_filter(data)
        if res:
            self.notify("set_mac_filter", data)
        return {"result": res}

@wrap_required_functions([
    'get_settings',
    'set_firewall',
    'set_ip_filter',
    'set_mac_filter',
])

class Handler(object):
    pass
