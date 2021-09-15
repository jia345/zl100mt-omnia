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

import copy
import logging

from foris_controller.handler_base import BaseMockHandler
from foris_controller.utils import logger_wrapper

from .. import Handler

logger = logging.getLogger(__name__)


class MockLanHandler(Handler, BaseMockHandler):
    router_ip = "192.168.1.1"
    netmask = "255.255.255.0"
    dhcp = {
        "enabled": False,
        "start": 100,
        "limit": 150,
    }
    guest = {
        "enabled": True,
        "ip": "10.0.0.1",
        "netmask": "255.255.255.0",
        "qos": {
            "enabled": False,
            "download": 1000,
            "upload": 1000,
        }
    }

    @logger_wrapper(logger)
    def get_settings(self):
        """ Mocks get lan settings

        :returns: current lan settiongs
        :rtype: str
        """
        result = {
            "ip": self.router_ip,
            "netmask": self.netmask,
            "dhcp": self.dhcp,
            "guest_network": self.guest,
        }
        return result

    @logger_wrapper(logger)
    def update_settings(self, new_settings):
        """ Mocks updates current lan settings
        :returns: True if update passes
        :rtype: bool
        """
        self.router_ip = new_settings["ip"]
        self.netmask = new_settings["netmask"]
        self.dhcp["enabled"] = new_settings["dhcp"]["enabled"]
        self.dhcp["start"] = new_settings["dhcp"].get("start", self.dhcp["start"])
        self.dhcp["limit"] = new_settings["dhcp"].get("limit", self.dhcp["limit"])
        self.guest["enabled"] = new_settings["guest_network"]["enabled"]
        self.guest["ip"] = new_settings["guest_network"].get("ip", self.guest["ip"])
        self.guest["netmask"] = new_settings["guest_network"].get("netmask", self.guest["netmask"])
        if "qos" in new_settings["guest_network"]:
            self.guest["qos"]["enabled"] = new_settings["guest_network"]["qos"]["enabled"]
            if new_settings["guest_network"]["qos"]["enabled"]:
                self.guest["qos"]["download"] = new_settings["guest_network"]["qos"].get(
                    "download", self.guest["qos"]["download"])
                self.guest["qos"]["upload"] = new_settings["guest_network"]["qos"].get(
                    "upload", self.guest["qos"]["upload"])

        return True
