#
# foris-controller-openvpn-module
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
import random

from foris_controller.handler_base import BaseMockHandler
from foris_controller.utils import logger_wrapper

from .. import Handler

logger = logging.getLogger(__name__)


class MockOpenvpnHandler(Handler, BaseMockHandler):
    ca_generated = False
    clients = []
    current_id = 2
    settings = {
        "enabled": False,
        "ipv6": False,
        "protocol": "udp",
        "network": "10.111.111.0",
        "network_netmask": "255.255.255.0",
        "routes": [
            {"network": "192.168.1.0", "netmask": "255.255.255.0"}
        ],
        "device": "tun_turris",
        "server_hostname": "",
        "port": 1194,
        "route_all": False,
        "use_dns": False,
    }

    @logger_wrapper(logger)
    def generate_ca(self, notify, exit_notify, reset_notify):
        MockOpenvpnHandler.ca_generated = True
        return "%08X" % random.randrange(2**32)

    @logger_wrapper(logger)
    def get_status(self):
        return {
            "status": "ready" if MockOpenvpnHandler.ca_generated else "missing",
            "clients": MockOpenvpnHandler.clients,
        }

    @logger_wrapper(logger)
    def generate_client(self, name, notify, exit_notify, reset_notify):
        MockOpenvpnHandler.clients.append({
            "id": "%02X" % MockOpenvpnHandler.current_id,
            "name": name,
            "status": "valid",
        })
        MockOpenvpnHandler.current_id += 1

        return "%08X" % random.randrange(2**32)

    @logger_wrapper(logger)
    def revoke(self, cert_id):
        for client in MockOpenvpnHandler.clients:
            if client["id"] == cert_id:
                client["status"] = "revoked"
                return True
        return False

    @logger_wrapper(logger)
    def delete_ca(self):
        MockOpenvpnHandler.ca_generated = False
        MockOpenvpnHandler.clients = []
        MockOpenvpnHandler.current_id = 2
        return True

    @logger_wrapper(logger)
    def get_settings(self):
        return MockOpenvpnHandler.settings

    @logger_wrapper(logger)
    def update_settings(
        self, enabled, network=None, network_netmask=None, route_all=None, use_dns=None,
        ipv6=None, protocol=None
    ):
        MockOpenvpnHandler.settings["enabled"] = enabled
        if enabled:
            MockOpenvpnHandler.settings["network"] = network
            MockOpenvpnHandler.settings["network_netmask"] = network_netmask
            MockOpenvpnHandler.settings["route_all"] = route_all
            MockOpenvpnHandler.settings["use_dns"] = use_dns
            MockOpenvpnHandler.settings["protocol"] = protocol
            MockOpenvpnHandler.settings["ipv6"] = ipv6

        return True

    @logger_wrapper(logger)
    def get_client_config(self, id, hostname=None):
        filtered = [e for e in MockOpenvpnHandler.clients if e["id"] == id]
        MockOpenvpnHandler.settings["server_hostname"] = hostname if hostname else ""
        if not filtered:
            return {"status": "not_found"}
        if filtered[0]["status"] == "revoked":
            return {"status": "revoked"}
        return {"status": "valid", "config": "%s" % hostname if hostname else "<guessed_hostname>"}
