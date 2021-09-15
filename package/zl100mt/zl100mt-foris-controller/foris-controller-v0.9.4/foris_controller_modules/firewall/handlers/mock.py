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

class MockFirewallHandler(Handler, BaseMockHandler):
    ip_filter_enabled = False
    mac_filter_enabled = False
    dmz_enabled = False
    dmz_ip = None
    ip_filter_table = {}
    mac_filter_table = {}

    @logger_wrapper(logger)
    def get_settings(self):
        result = {
            "ip_filter_enabled": MockFirewallHandler.ip_filter_enabled,
            "mac_filter_enabled": MockFirewallHandler.mac_filter_enabled,
            "dmz_enabled": MockFirewallHandler.dmz_enabled,
            "dmz_ip": MockFirewallHandler.dmz_ip,
            "ip_filter_table": MockFirewallHandler.ip_filter_table,
            "mac_filter_table": MockFirewallHandler.mac_filter_table,
        }
        if MockFirewallHandler.dns_from_dhcp_domain:
            result["dns_from_dhcp_domain"] = MockFirewallHandler.dns_from_dhcp_domain
        return result

    @logger_wrapper(logger)
    def set_firewall(self, data):
        MockFirewallHandler.ip_filter_enabled = data.ip_filter_enabled
        MockFirewallHandler.mac_filter_enabled = data.mac_filter_enabled
        MockFirewallHandler.dmz_enabled = data.dmz_enabled
        MockFirewallHandler.dmz_ip = data.dmz_ip
        return True

    @logger_wrapper(logger)
    def set_ip_filter(self, data):
        MockFirewallHandler.ip_filter_table = data.ip_filter_table
        return True

    @logger_wrapper(logger)
    def set_mac_filter(self, data):
        MockFirewallHandler.mac_filter_table = data.mac_filter_table
        return True

