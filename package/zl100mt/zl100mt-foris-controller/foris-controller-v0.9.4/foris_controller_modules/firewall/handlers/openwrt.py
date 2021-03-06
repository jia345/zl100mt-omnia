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
from foris_controller_backends.firewall import FirewallUciCommands

from .. import Handler

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

class OpenwrtFirewallHandler(Handler, BaseOpenwrtHandler):
    uci_firewall_cmds = FirewallUciCommands()

    @logger_wrapper(logger)
    def get_settings(self):
        return OpenwrtFirewallHandler.uci_firewall_cmds.get_settings()

    @logger_wrapper(logger)
    def set_firewall(self, data):
        return OpenwrtFirewallHandler.uci_firewall_cmds.set_firewall(data)

    @logger_wrapper(logger)
    def set_ip_filter(self, data):
        return OpenwrtFirewallHandler.uci_firewall_cmds.set_ip_filter(data)

    @logger_wrapper(logger)
    def set_mac_filter(self, data):
        return OpenwrtFirewallHandler.uci_firewall_cmds.set_mac_filter(data)

