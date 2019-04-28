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

from foris_controller_backends.uci import (
    UciBackend, get_option_named, parse_bool, store_bool
)
from foris_controller_backends.wifi import WifiUci

from foris_controller_backends.services import OpenwrtServices
from foris_controller.exceptions import UciRecordNotFound, UciException

logger = logging.getLogger(__name__)


class LanUci(object):
    DEFAULT_GUEST_ADDRESS = "10.111.222.1"
    DEFAULT_GUEST_NETMASK = "255.255.255.0"
    DEFAULT_DHCP_START = 100
    DEFAULT_DHCP_LIMIT = 150

    def get_guest_enabled(self, network_data, firewall_data, dhcp_data):
        def test(data, config, section, value, default=False):
            try:
                return parse_bool(get_option_named(data, config, section, value))
            except UciRecordNotFound:
                return default

        return \
            test(network_data, "network", "guest_turris", "enabled") \
            and not test(dhcp_data, "dhcp", "guest_turris", "ignore", True) \
            and test(firewall_data, "firewall", "guest_turris", "enabled") \
            and test(firewall_data, "firewall", "guest_turris_forward_wan", "enabled") \
            and test(firewall_data, "firewall", "guest_turris_dhcp_rule", "enabled") \
            and test(firewall_data, "firewall", "guest_turris_dns_rule", "enabled")

    def get_guest_network_settings(self, network_data, firewall_data, dhcp_data, sqm_data):
        guest = {}
        guest["enabled"] = self.get_guest_enabled(network_data, firewall_data, dhcp_data)

        guest["ip"] = get_option_named(
            network_data, "network", "guest_turris", "ipaddr", self.DEFAULT_GUEST_ADDRESS)
        guest["netmask"] = get_option_named(
            network_data, "network", "guest_turris", "netmask", self.DEFAULT_GUEST_NETMASK)

        guest["qos"] = {}
        guest["qos"]["enabled"] = parse_bool(
            get_option_named(sqm_data, "sqm", "guest_limit_turris", "enabled", "0"))
        # upload is actually download limit nad vice versa
        guest["qos"]["upload"] = int(get_option_named(
            sqm_data, "sqm", "guest_limit_turris", "download", 1024))
        guest["qos"]["download"] = int(get_option_named(
            sqm_data, "sqm", "guest_limit_turris", "upload", 1024))

        return guest

    def get_settings(self):

        with UciBackend() as backend:
            network_data = backend.read("network")
            dhcp_data = backend.read("dhcp")
            try:
                sqm_data = backend.read("sqm")
            except UciException:
                sqm_data = {"sqm": {}}
            firewall_data = backend.read("firewall")

        router_ip = get_option_named(network_data, "network", "lan", "ipaddr")
        netmask = get_option_named(network_data, "network", "lan", "netmask")
        dhcp = {}
        dhcp["enabled"] = not parse_bool(
            get_option_named(dhcp_data, "dhcp", "lan", "ignore", "0"))
        dhcp["start"] = int(get_option_named(
            dhcp_data, "dhcp", "lan", "start", self.DEFAULT_DHCP_START))
        dhcp["limit"] = int(get_option_named(
            dhcp_data, "dhcp", "lan", "limit", self.DEFAULT_DHCP_LIMIT))

        guest = self.get_guest_network_settings(network_data, firewall_data, dhcp_data, sqm_data)

        return {
            "ip": router_ip,
            "netmask": netmask,
            "dhcp": dhcp,
            "guest_network": guest,
        }

    @staticmethod
    def set_guest_network(backend, guest_network, interfaces=None):
        """
        :returns: None or "enable" or "disable" to set sqm service
        :rtype: NoneType or str
        """

        def set_if_exists(backend, config, section, option, data, key):
            if key in data:
                backend.set_option(config, section, option, data[key])

        enabled = store_bool(guest_network["enabled"])
        ignored = store_bool(not guest_network["enabled"])

        # update network interface list
        backend.add_section("network", "interface", "guest_turris")
        backend.set_option("network", "guest_turris", "enabled", enabled)
        backend.set_option("network", "guest_turris", "type", "bridge")
        interfaces = [
            "guest_turris_%d" % i for i, _ in enumerate(WifiUci.get_wifi_devices(backend))
        ] if not interfaces else interfaces
        if interfaces:
            backend.replace_list("network", "guest_turris", "ifname", interfaces)
        backend.set_option("network", "guest_turris", "proto", "static")
        set_if_exists(backend, "network", "guest_turris", "ipaddr", guest_network, "ip")
        set_if_exists(backend, "network", "guest_turris", "netmask", guest_network, "netmask")
        backend.set_option("network", "guest_turris", "bridge_empty", store_bool(True))

        # update firewall config
        backend.add_section("firewall", "zone", "guest_turris")
        backend.set_option("firewall", "guest_turris", "enabled", enabled)
        backend.set_option("firewall", "guest_turris", "name", "guest_turris")
        backend.replace_list("firewall", "guest_turris", "network", ["guest_turris"])
        backend.set_option("firewall", "guest_turris", "input", "REJECT")
        backend.set_option("firewall", "guest_turris", "forward", "REJECT")
        backend.set_option("firewall", "guest_turris", "output", "ACCEPT")

        backend.add_section("firewall", "forwarding", "guest_turris_forward_wan")
        backend.set_option("firewall", "guest_turris_forward_wan", "enabled", enabled)
        backend.set_option("firewall", "guest_turris_forward_wan", "name", "guest to wan forward")
        backend.set_option("firewall", "guest_turris_forward_wan", "src", "guest_turris")
        backend.set_option("firewall", "guest_turris_forward_wan", "dest", "wan")

        backend.add_section("firewall", "rule", "guest_turris_dns_rule")
        backend.set_option("firewall", "guest_turris_dns_rule", "enabled", enabled)
        backend.set_option("firewall", "guest_turris_dns_rule", "name", "guest dns rule")
        backend.set_option("firewall", "guest_turris_dns_rule", "src", "guest_turris")
        backend.set_option("firewall", "guest_turris_dns_rule", "proto", "tcpudp")
        backend.set_option("firewall", "guest_turris_dns_rule", "dest_port", "53")
        backend.set_option("firewall", "guest_turris_dns_rule", "target", "ACCEPT")

        backend.add_section("firewall", "rule", "guest_turris_dhcp_rule")
        backend.set_option("firewall", "guest_turris_dhcp_rule", "enabled", enabled)
        backend.set_option("firewall", "guest_turris_dhcp_rule", "name", "guest dhcp rule")
        backend.set_option("firewall", "guest_turris_dhcp_rule", "src", "guest_turris")
        backend.set_option("firewall", "guest_turris_dhcp_rule", "proto", "udp")
        backend.set_option("firewall", "guest_turris_dhcp_rule", "src_port", "67-68")
        backend.set_option("firewall", "guest_turris_dhcp_rule", "dest_port", "67-68")
        backend.set_option("firewall", "guest_turris_dhcp_rule", "target", "ACCEPT")

        # update dhcp config
        backend.add_section("dhcp", "dhcp", "guest_turris")
        backend.set_option("dhcp", "guest_turris", "ignore", ignored)
        backend.set_option("dhcp", "guest_turris", "interface", "guest_turris")
        # use fixed values for guest dhcp
        backend.set_option("dhcp", "guest_turris", "start", "200")
        backend.set_option("dhcp", "guest_turris", "limit", "50")
        backend.set_option("dhcp", "guest_turris", "leasetime", "1h")
        if guest_network.get("ip", False):
            backend.replace_list(
                "dhcp", "guest_turris", "dhcp_option", ["6,%s" % guest_network["ip"]])

        # qos part (replaces whole sqm section)
        try:
            # cleanup section
            backend.del_section("sqm", "guest_limit_turris")
        except UciException:
            pass  # section might not exist

        try:
            if guest_network["enabled"] and "qos" in guest_network and \
                    guest_network["qos"]["enabled"]:
                backend.add_section("sqm", "queue", "guest_limit_turris")
                backend.set_option("sqm", "guest_limit_turris", "enabled", enabled)
                backend.set_option("sqm", "guest_limit_turris", "interface", "br-guest_turris")
                backend.set_option("sqm", "guest_limit_turris", "qdisc", "fq_codel")
                backend.set_option("sqm", "guest_limit_turris", "script", "simple.qos")
                backend.set_option("sqm", "guest_limit_turris", "link_layer", "none")
                backend.set_option("sqm", "guest_limit_turris", "verbosity", "5")
                backend.set_option("sqm", "guest_limit_turris", "debug_logging", "1")
                # We need to swap dowload and upload
                # "upload" means upload to the guest network
                # "download" means dowload from the guest network
                set_if_exists(
                    backend, "sqm", "guest_limit_turris", "upload", guest_network["qos"],
                    "download"
                )
                set_if_exists(
                    backend, "sqm", "guest_limit_turris", "download", guest_network["qos"],
                    "upload"
                )
                return "enable"
            else:
                return "disable"
        except UciException:
            pass  # sqm might not be installed -> set at least the rest and don't fail

    def update_settings(self, ip, netmask, dhcp, guest_network):
        """  Updates the lan settings in uci

        :param ip: new router ip
        :type ip: str
        :param netmask: network mask of lan
        :type netmask: str
        :param dhcp: {"enabled": True/False, ["start": 10, "max": 40]}
        :type dhpc: dict
        :param guest: {"enabled": True/False, ["ip": "192.168.1.1", ...]}
        :type guest: dict
        """
        with UciBackend() as backend:
            backend.add_section("network", "interface", "lan")
            backend.set_option("network", "lan", "ipaddr", ip)
            backend.set_option("network", "lan", "netmask", netmask)

            backend.add_section("dhcp", "dhcp", "lan")
            backend.set_option("dhcp", "lan", "ignore", store_bool(not dhcp["enabled"]))

            # set dhcp part
            if dhcp["enabled"]:
                backend.set_option(
                    "dhcp", "lan", "start", dhcp.get("start", self.DEFAULT_DHCP_START))
                backend.set_option(
                    "dhcp", "lan", "limit", dhcp.get("limit", self.DEFAULT_DHCP_LIMIT))

                # this will override all user dhcp options
                # TODO we might want to preserve some options
                backend.replace_list("dhcp", "lan", "dhcp_option", ["6,%s" % ip])

            # disable guest wifi when guest network is not enabled
            if not guest_network["enabled"]:
                WifiUci.set_guest_wifi_disabled(backend)

            # set guest network part
            sqm_cmd = self.set_guest_network(backend, guest_network)

        with OpenwrtServices() as services:
            # try to restart sqm (best effort) in might not be installed yet
            # note that sqm will be restarted when the network is restarted
            if sqm_cmd == "enable":
                services.enable("sqm", fail_on_error=False)
            elif sqm_cmd == "disable":
                services.disable("sqm", fail_on_error=False)

            services.restart("network", delay=2)
