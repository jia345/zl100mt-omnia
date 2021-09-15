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
import json

from foris_controller_backends.uci import (
    UciBackend, get_option_named, store_bool
)
from foris_controller.exceptions import (
    UciException, BackendCommandFailed, FailedToParseCommandOutput
)
from foris_controller_backends.cmdline import AsyncCommand, BaseCmdLine
from foris_controller_backends.services import OpenwrtServices
from foris_controller_backends.files import BaseFile


logger = logging.getLogger(__name__)


class WanUci(object):

    def get_settings(self):

        with UciBackend() as backend:
            network_data = backend.read("network")

        # WAN
        wan_settings = {}
        wan_settings["wan_type"] = get_option_named(network_data, "network", "wan", "proto")
        if wan_settings["wan_type"] == "dhcp":
            hostname = get_option_named(network_data, "network", "wan", "hostname", "")
            wan_settings["wan_dhcp"] = {"hostname": hostname} if hostname else {}
        elif wan_settings["wan_type"] == "static":
            wan_settings["wan_static"] = {
                "ip": get_option_named(network_data, "network", "wan", "ipaddr"),
                "netmask": get_option_named(network_data, "network", "wan", "netmask"),
                "gateway": get_option_named(network_data, "network", "wan", "gateway"),
            }
            dns = get_option_named(network_data, "network", "wan", "dns", [])
            dns = reversed(dns)  # dns with higher priority should be added last
            wan_settings["wan_static"].update(zip(("dns1", "dns2"), dns))
        elif wan_settings["wan_type"] == "pppoe":
            wan_settings["wan_pppoe"] = {
                "username": get_option_named(network_data, "network", "wan", "username"),
                "password": get_option_named(network_data, "network", "wan", "password"),
            }

        # WAN6
        wan6_settings = {}
        wan6_settings["wan6_type"] = get_option_named(
            network_data, "network", "wan6", "proto", "none")
        if wan6_settings["wan6_type"] == "static":
            wan6_settings["wan6_static"] = {
                "ip": get_option_named(network_data, "network", "wan6", "ip6addr"),
                "network": get_option_named(network_data, "network", "wan6", "ip6prefix"),
                "gateway": get_option_named(network_data, "network", "wan6", "ip6gw"),
            }
            dns = get_option_named(network_data, "network", "wan6", "dns", [])
            dns = reversed(dns)  # dns with higher priority should be last
            wan6_settings["wan6_static"].update(zip(("dns1", "dns2"), dns))
        elif wan6_settings["wan6_type"] == "dhcpv6":
            wan6_settings["wan6_dhcpv6"] = {
                "duid": get_option_named(network_data, "network", "wan6", "clientid", ""),
            }
        elif wan6_settings["wan6_type"] == "6to4":
            wan6_settings["wan6_6to4"] = {
                "ipv4_address": get_option_named(network_data, "network", "wan6", "ipaddr", ""),
            }
        elif wan6_settings["wan6_type"] == "6in4":
            wan6_settings["wan6_6in4"] = {
                "ipv6_prefix": get_option_named(network_data, "network", "wan6", "ip6prefix", ""),
                "mtu": int(get_option_named(network_data, "network", "wan6", "mtu", "1480")),
                "server_ipv4": get_option_named(network_data, "network", "wan6", "peeraddr", ""),
            }
            tunnel_id = get_option_named(network_data, "network", "wan6", "tunnelid", "")
            username = get_option_named(network_data, "network", "wan6", "username", "")
            password = get_option_named(network_data, "network", "wan6", "password", "")
            wan6_settings["wan6_6in4"]["dynamic_ipv4"] = {}
            if tunnel_id and username and password:
                wan6_settings["wan6_6in4"]["dynamic_ipv4"]["enabled"] = True
                wan6_settings["wan6_6in4"]["dynamic_ipv4"]["tunnel_id"] = tunnel_id
                wan6_settings["wan6_6in4"]["dynamic_ipv4"]["username"] = username
                wan6_settings["wan6_6in4"]["dynamic_ipv4"]["password_or_key"] = password
            else:
                wan6_settings["wan6_6in4"]["dynamic_ipv4"]["enabled"] = False

        # MAC
        custom_mac = get_option_named(network_data, "network", "wan", "macaddr", "")
        mac_settings = {"custom_mac_enabled": True, "custom_mac": custom_mac} if custom_mac \
            else {"custom_mac_enabled": False}

        return {
            "wan_settings": wan_settings,
            "wan6_settings": wan6_settings,
            "mac_settings": mac_settings,
        }

    def update_settings(self, wan_settings, wan6_settings, mac_settings):
        with UciBackend() as backend:
            # WAN
            wan_type = wan_settings["wan_type"]
            backend.add_section("network", "interface", "wan")
            backend.set_option("network", "wan", "proto", wan_type)
            if wan_type == "dhcp":
                if "hostname" in wan_settings["wan_dhcp"]:
                    backend.set_option(
                        "network", "wan", "hostname", wan_settings["wan_dhcp"]["hostname"])
                else:
                    try:
                        backend.del_option("network", "wan", "hostname")
                    except UciException:
                        pass

            elif wan_type == "static":
                backend.set_option("network", "wan", "ipaddr", wan_settings["wan_static"]["ip"])
                backend.set_option(
                    "network", "wan", "netmask", wan_settings["wan_static"]["netmask"])
                backend.set_option(
                    "network", "wan", "gateway", wan_settings["wan_static"]["gateway"])
                dns = [
                    wan_settings["wan_static"][name] for name in ("dns2", "dns1")
                    if name in wan_settings["wan_static"]
                ]  # dns with higher priority should be added last
                backend.replace_list("network", "wan", "dns", dns)

            elif wan_type == "pppoe":
                backend.set_option(
                    "network", "wan", "username", wan_settings["wan_pppoe"]["username"])
                backend.set_option(
                    "network", "wan", "password", wan_settings["wan_pppoe"]["password"])

            # WAN6
            wan6_type = wan6_settings["wan6_type"]
            backend.add_section("network", "interface", "wan6")
            backend.set_option("network", "wan6", "ifname", "@wan")
            backend.set_option("network", "wan6", "proto", wan6_type)

            # disable rule for 6in4 + cleanup
            if not wan6_type == "6in4":
                for item in ["tunnelid", "username", "password", "peeraddr", "mtu", "ip6prefix"]:
                    try:
                        backend.del_option("network", "wan6", item)
                    except UciException:
                        pass
                backend.add_section("firewall", "rule", "turris_wan_6in4_rule")
                backend.set_option("firewall", "turris_wan_6in4_rule", "enabled", store_bool(False))

            if wan6_type == "static":
                backend.set_option("network", "wan6", "ip6addr", wan6_settings["wan6_static"]["ip"])
                backend.set_option(
                    "network", "wan6", "ip6prefix", wan6_settings["wan6_static"]["network"])
                backend.set_option(
                    "network", "wan6", "ip6gw", wan6_settings["wan6_static"]["gateway"])
                dns = [
                    wan6_settings["wan6_static"][name] for name in ("dns2", "dns1")
                    if name in wan6_settings["wan6_static"]
                ]  # dns with higher priority should be added last
                backend.replace_list("network", "wan6", "dns", dns)
            elif wan6_type == "dhcpv6":
                new_duid = wan6_settings["wan6_dhcpv6"]["duid"]
                if new_duid:
                    backend.set_option("network", "wan6", "clientid", new_duid)
                else:
                    try:
                        backend.del_option("network", "wan6", "clientid")
                    except UciException:
                        pass
            elif wan6_type == "6to4":
                mapped_ipv4 = wan6_settings["wan6_6to4"]["ipv4_address"]
                backend.set_option("network", "lan", "ip6assign", "60")
                if mapped_ipv4:
                    backend.set_option("network", "wan6", "ipaddr", mapped_ipv4)
                else:
                    try:
                        backend.del_option("network", "wan6", "ipaddr")
                    except UciException:
                        pass
            elif wan6_type == "6in4":
                backend.set_option("network", "wan6", "mtu", wan6_settings["wan6_6in4"]["mtu"])
                backend.set_option(
                    "network", "wan6", "peeraddr", wan6_settings["wan6_6in4"]["server_ipv4"])
                backend.set_option(
                    "network", "wan6", "ip6prefix", wan6_settings["wan6_6in4"]["ipv6_prefix"])
                if wan6_settings["wan6_6in4"]["dynamic_ipv4"]["enabled"]:
                    backend.set_option(
                        "network", "wan6", "tunnelid",
                        wan6_settings["wan6_6in4"]["dynamic_ipv4"]["tunnel_id"]
                    )
                    backend.set_option(
                        "network", "wan6", "username",
                        wan6_settings["wan6_6in4"]["dynamic_ipv4"]["username"]
                    )
                    backend.set_option(
                        "network", "wan6", "password",
                        wan6_settings["wan6_6in4"]["dynamic_ipv4"]["password_or_key"]
                    )
                else:
                    for item in ["tunnelid", "username", "password"]:
                        try:
                            backend.del_option("network", "wan6", item)
                        except UciException:
                            pass

                backend.add_section("firewall", "rule", "turris_wan_6in4_rule")
                backend.set_option("firewall", "turris_wan_6in4_rule", "enabled", store_bool(True))
                backend.set_option("firewall", "turris_wan_6in4_rule", "family", "ipv4")
                backend.set_option("firewall", "turris_wan_6in4_rule", "proto", "41")
                backend.set_option("firewall", "turris_wan_6in4_rule", "target", "ACCEPT")
                backend.set_option("firewall", "turris_wan_6in4_rule", "src", "wan")
                backend.set_option(
                    "firewall", "turris_wan_6in4_rule", "src_ip",
                    wan6_settings["wan6_6in4"]["server_ipv4"]
                )
            else:
                # remove extra fields (otherwise it will mess with other settings)
                for field in ["ip6prefix", "ip6addr", "ip6gw"]:
                    try:
                        backend.del_option("network", "wan6", field)
                    except UciException:
                        pass

            # disable/enable ipv6 on wan interface
            if wan6_type == "none":
                backend.set_option("network", "wan", "ipv6", store_bool(False))
            else:
                backend.set_option("network", "wan", "ipv6", store_bool(True))

            # MAC
            if mac_settings["custom_mac_enabled"]:
                backend.set_option("network", "wan", "macaddr", mac_settings["custom_mac"])
            else:
                try:
                    backend.del_option("network", "wan", "macaddr")
                except UciException:
                    pass

        with OpenwrtServices() as services:
            services.restart("network", delay=2)

        return True


class WanTestCommands(AsyncCommand):

    FIELDS = ("ipv6", "ipv6_gateway", "ipv4", "ipv4_gateway", "dns", "dnssec")
    TEST_KIND_MAP = {
        "ipv4": ["IP4GATE", "IP4"],
        "ipv6": ["IP6GATE", "IP6"],
        "dns": ["IP4GATE", "IP4", "IP6GATE", "IP6", "DNS", "DNSSEC"],  # IP has to be working
    }

    def connection_test_status(self, process_id):
        """ Get the status of some connection test
        :param process_id: test process identifier
        :type process_id: str
        :returns: data about test process
        :rtype: dict
        """

        with self.lock.readlock:
            if process_id not in self.processes:
                return {'status': 'not_found'}
            process_data = self.processes[process_id]

        exitted = process_data.get_exitted()

        data = {e: False for e in WanTestCommands.FIELDS} if exitted else {}
        for record in process_data.read_all_data():
            for option, res in record["data"].items():
                data[option] = res or data.get(option, False)

        return {'status': "finished" if process_data.get_exitted() else "running", "data": data}

    def connection_test_trigger(
            self, test_kinds, notify_function, exit_notify_function, reset_notify_function):
        """ Executes connection test in asyncronous mode

        This means that we don't wait for the test results. Only a test id is returned.
        This id can be used in other queries.

        :param test_kinds: which kinds of tests should be run (ipv4, ipv6, dns)
        :type test_kinds: array of str
        :param notify_function: function which is used to send notifications back to client
        :type notify_function: callable
        :param exit_notify_function: function which is used to send notifications back to client
                                     when test exits
        :type exit_notify_function: callable
        :param reset_notify_function: function which resets notification connection
        :type reset_notify_function: callable
        :returns: test id
        :rtype: str

        """
        logger.debug("Starting connection test.")

        # generate a notification handler
        def handler_gen(regex, option):
            def handler(matched, process_data):
                passed = matched.group(1) == "OK"
                res = {"test_id": process_data.id, "data": {option: passed}}
                process_data.append_data(res)
                notify_function(res)

            return regex, handler

        # handler which will be called when the test exits
        def handler_exit(process_data):
            data = {e: False for e in WanTestCommands.FIELDS}
            for record in process_data.read_all_data():
                for option, res in record["data"].items():
                    data[option] = res or data.get(option, False)
            exit_notify_function({
                "test_id": process_data.id, "data": data,
                "passed": process_data.get_retval() == 0}
            )
            logger.debug("Connection test finished: (retval=%d)" % process_data.get_retval())

        # prepare test kinds
        cmd_line_kinds = []
        for kind in test_kinds:
            cmd_line_kinds.extend(self.TEST_KIND_MAP[kind])

        process_id = self.start_process(
            ["/sbin/check_connection"] + list(set(cmd_line_kinds)),
            [
                handler_gen(r"^IPv6: (\w+)", "ipv6"),
                handler_gen(r"^IPv6 Gateway: (\w+)", "ipv6_gateway"),
                handler_gen(r"^IPv4: (\w+)", "ipv4"),
                handler_gen(r"^IPv4 Gateway: (\w+)", "ipv4_gateway"),
                handler_gen(r"DNS: (\w+)", "dns"),
                handler_gen(r"DNSSEC: (\w+)", "dnssec"),
            ],
            handler_exit,
            reset_notify_function
        )

        logger.debug("Connection test started '%s'." % process_id)
        return process_id


class WanStatusCommands(BaseCmdLine, BaseFile):
    DUID_STATUS_FILE = '/var/run/odhcp6c-duid'

    def get_status(self):
        args = ("/bin/ubus", "-S", "call", "network.interface.wan", "status")
        retval, stdout, _ = self._run_command(*args)
        if not retval == 0:
            logger.error("Command %s failed." % str(args))
            raise BackendCommandFailed(retval, args)

        try:
            parsed = json.loads(stdout.strip())
        except ValueError:
            raise FailedToParseCommandOutput(args, stdout)

        # try to figure out duid (best effort)
        device = parsed.get("device", None)
        parsed["duid"] = ""
        if device:
            duid_path = "%s.%s" % (WanStatusCommands.DUID_STATUS_FILE, device)
            try:
                parsed["duid"] = self._file_content(duid_path).strip()
            except (OSError, IOError):
                pass

        return parsed
