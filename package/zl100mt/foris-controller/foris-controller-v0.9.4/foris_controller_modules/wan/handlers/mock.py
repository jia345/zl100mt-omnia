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
import copy

import random

from foris_controller.handler_base import BaseMockHandler
from foris_controller.utils import logger_wrapper

from .. import Handler

logger = logging.getLogger(__name__)


class MockWanHandler(Handler, BaseMockHandler):
    wan_type = "none"
    wan_dhcp = {
        "hostname": None,
    }
    wan_static = {
        "ip": None,
        "netmask": None,
        "gateway": None,
        "dns1": None,
        "dns2": None,
    }
    wan_pppoe = {
        "username": None,
        "password": None,
    }
    wan6_type = "none"
    wan6_static = {
        "ip": None,
        "network": None,
        "gateway": None,
        "dns1": None,
        "dns2": None,
    }
    wan6_6to4 = {
        "ipv4_address": "",
    }
    wan6_6in4 = {
        "mtu": 1480,
        "server_ipv4": "",
        "ipv6_prefix": "",
        "dynamic_ipv4": {
            "enabled": False
        }
    }
    custom_mac_enabled = False
    custom_mac = None
    test_id_set = set()

    def _cleanup(self):
        self.wan_type = "dhcp"
        self.wan_dhcp = {
            "hostname": None,
        }
        self.wan_static = {
            "ip": None,
            "netmask": None,
            "gateway": None,
            "dns1": None,
            "dns2": None,
        }
        self.wan_pppoe = {
            "username": None,
            "password": None,
        }
        self.wan6_type = "none"
        self.wan6_static = {
            "ip": None,
            "network": None,
            "gateway": None,
            "dns1": None,
            "dns2": None,
        }
        self.wan6_dhcpv6 = {
            "duid": "",
        }
        self.wan6_6to4 = {
            "ipv4_address": "",
        }
        self.wan6_6in4 = {
            "mtu": 1480,
            "server_ipv4": "",
            "ipv6_prefix": "",
            "dynamic_ipv4": {
                "enabled": False
            }
        }
        self.custom_mac_enabled = False
        self.custom_mac = None

    @logger_wrapper(logger)
    def get_settings(self):
        """ Mocks get wan settings

        :returns: current wan settiongs
        :rtype: str
        """
        res = {
            "wan_settings": {"wan_type": self.wan_type},
            "wan6_settings": {"wan6_type": self.wan6_type},
            "mac_settings": {"custom_mac_enabled": self.custom_mac_enabled},
        }
        if self.wan_type == "dhcp":
            if self.wan_dhcp["hostname"]:
                res["wan_settings"]["wan_dhcp"] = {"hostname": self.wan_dhcp["hostname"]}
            else:
                res["wan_settings"]["wan_dhcp"] = {}
        elif self.wan_type == "static":
            res["wan_settings"]["wan_static"] = {
                "ip": self.wan_static["ip"],
                "netmask": self.wan_static["netmask"],
                "gateway": self.wan_static["gateway"],
            }
            if self.wan_static["dns1"] is not None:
                res["wan_settings"]["wan_static"]["dns1"] = self.wan_static["dns1"]
            if self.wan_static["dns2"] is not None:
                res["wan_settings"]["wan_static"]["dns2"] = self.wan_static["dns2"]
        elif self.wan_type == "pppoe":
            res["wan_settings"]["wan_pppoe"] = {
                "username": self.wan_pppoe["username"],
                "password": self.wan_pppoe["password"],
            }

        if self.wan6_type == "static":
            res["wan6_settings"]["wan6_static"] = {
                "ip": self.wan6_static["ip"],
                "network": self.wan6_static["network"],
                "gateway": self.wan6_static["gateway"],
            }
            if self.wan6_static["dns1"] is not None:
                res["wan6_settings"]["wan6_static"]["dns1"] = self.wan6_static["dns1"]
            if self.wan6_static["dns2"] is not None:
                res["wan6_settings"]["wan6_static"]["dns2"] = self.wan6_static["dns2"]
        elif self.wan6_type == "dhcpv6":
            res["wan6_settings"]["wan6_dhcpv6"] = {
                "duid": self.wan6_dhcpv6["duid"]
            }
        elif self.wan6_type == "6to4":
            res["wan6_settings"]["wan6_6to4"] = {
                "ipv4_address": self.wan6_6to4["ipv4_address"]
            }
        elif self.wan6_type == "6in4":
            res["wan6_settings"]["wan6_6in4"] = copy.deepcopy(self.wan6_6in4)

        if self.custom_mac_enabled:
            res["mac_settings"]["custom_mac"] = self.custom_mac

        return copy.deepcopy(res)

    @logger_wrapper(logger)
    def update_settings(self, new_settings):
        """ Mocks updates current wan settings
        :returns: True if update passes
        :rtype: bool
        """
        self._cleanup()
        self.wan_type = new_settings["wan_settings"]["wan_type"]
        if self.wan_type == "dhcp":
            self.wan_dhcp["hostname"] = new_settings["wan_settings"]["wan_dhcp"].get(
                "hostname", None)
        if self.wan_type == "static":
            self.wan_static["ip"] = new_settings["wan_settings"]["wan_static"]["ip"]
            self.wan_static["netmask"] = new_settings["wan_settings"]["wan_static"]["netmask"]
            self.wan_static["gateway"] = new_settings["wan_settings"]["wan_static"]["gateway"]
            self.wan_static["dns1"] = new_settings["wan_settings"]["wan_static"].get("dns1", None)
            self.wan_static["dns2"] = new_settings["wan_settings"]["wan_static"].get("dns2", None)
        if self.wan_type == "pppoe":
            self.wan_pppoe["username"] = new_settings["wan_settings"]["wan_pppoe"]["username"]
            self.wan_pppoe["password"] = new_settings["wan_settings"]["wan_pppoe"]["password"]

        self.wan6_type = new_settings["wan6_settings"]["wan6_type"]
        if self.wan6_type == "static":
            self.wan6_static["ip"] = new_settings["wan6_settings"]["wan6_static"]["ip"]
            self.wan6_static["network"] = new_settings["wan6_settings"]["wan6_static"]["network"]
            self.wan6_static["gateway"] = new_settings["wan6_settings"]["wan6_static"]["gateway"]
            self.wan6_static["dns1"] = new_settings["wan6_settings"]["wan6_static"].get(
                "dns1", None)
            self.wan6_static["dns2"] = new_settings["wan6_settings"]["wan6_static"].get(
                "dns2", None)
        elif self.wan6_type == "dhcpv6":
            self.wan6_dhcpv6["duid"] = new_settings["wan6_settings"]["wan6_dhcpv6"]["duid"]
        elif self.wan6_type == "6to4":
            self.wan6_6to4["ipv4_address"] = \
                new_settings["wan6_settings"]["wan6_6to4"]["ipv4_address"]
        elif self.wan6_type == "6in4":
            self.wan6_6in4 = copy.deepcopy(new_settings["wan6_settings"]["wan6_6in4"])

        self.custom_mac_enabled = new_settings["mac_settings"]["custom_mac_enabled"]
        self.custom_mac = new_settings["mac_settings"].get("custom_mac", None)

        return True

    @logger_wrapper(logger)
    def connection_test_trigger(
            self, test_kinds, notify_function, exit_notify_function, reset_notify_function):
        """ Mocks triggering of the connection test
        :param test_kinds: which kinds of tests should be run (ipv4, ipv6, dns)
        :type test_kinds: array of str
        :param notify_function: function to publish notifications
        :type notify_function: callable
        :param exit_notify_function: function for sending notification when a test finishes
        :type exit_notify_function: callable
        :param reset_notify_function: function to reconnect to the notification bus
        :type reset_notify_function: callable
        :returns: generated_test_id
        :rtype: str
        """
        new_test_id = "%032X" % random.randrange(2**32)
        MockWanHandler.test_id_set.add(new_test_id)
        return new_test_id

    @logger_wrapper(logger)
    def connection_test_status(self, test_id):
        """ Mocks connection test status
        :param test_id: id of the test to display
        :type test_id: str
        :returns: connection test status + test data
        :rtype: dict
        """
        if test_id in MockWanHandler.test_id_set:
            return {'status': 'running', 'data': {'ipv4': True, 'ipv6': False}}
        else:
            return {'status': 'not_found'}

    @logger_wrapper(logger)
    def get_wan_status(self):
        """ Mocks wan status
        :returns: {'up': True/False}
        :rtype: dict
        """
        return {
            'up': random.choice([True, False]),
            'last_seen_duid': random.choice(["", "00030001d858d7004555"]),
            'proto': random.choice(["pppoe", "dhcp", "static", "none"]),
        }
