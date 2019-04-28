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

import os
import pytest

from foris_controller_testtools.fixtures import (
    only_backends, uci_configs_init, infrastructure, ubusd_test, lock_backend
)
from foris_controller_testtools.utils import sh_was_called, get_uci_module

FILE_ROOT_PATH = os.path.join(os.path.dirname(os.path.realpath(__file__)), "test_wan_files")


def test_get_settings(uci_configs_init, infrastructure, ubusd_test):
    res = infrastructure.process_message({
        "module": "wan",
        "action": "get_settings",
        "kind": "request",
    })
    assert set(res.keys()) == {"action", "kind", "data", "module"}
    assert "wan_settings" in res["data"].keys()
    assert "wan6_settings" in res["data"].keys()
    assert "mac_settings" in res["data"].keys()


@pytest.mark.file_root_path(FILE_ROOT_PATH)
def test_get_wan_status(uci_configs_init, infrastructure, ubusd_test):
    res = infrastructure.process_message({
        "module": "wan",
        "action": "get_wan_status",
        "kind": "request",
    })
    assert set(res.keys()) == {"action", "kind", "data", "module"}
    assert "up" in res["data"].keys()
    assert "last_seen_duid" in res["data"].keys()
    assert "proto" in res["data"].keys()


def test_update_settings(uci_configs_init, infrastructure, ubusd_test):
    filters = [("wan", "update_settings")]
    def update(input_data, output_data, notification_data):
        notifications = infrastructure.get_notifications(filters=filters)
        res = infrastructure.process_message({
            "module": "wan",
            "action": "update_settings",
            "kind": "request",
            "data": input_data
        })
        assert res == {
            u'action': u'update_settings',
            u'data': {u'result': True},
            u'kind': u'reply',
            u'module': u'wan'
        }
        notifications = infrastructure.get_notifications(notifications, filters=filters)
        assert notifications[-1]["module"] == "wan"
        assert notifications[-1]["action"] == "update_settings"
        assert notifications[-1]["kind"] == "notification"
        assert notification_data == notifications[-1]["data"]

        res = infrastructure.process_message({
            "module": "wan",
            "action": "get_settings",
            "kind": "request",
        })
        assert res["module"] == "wan"
        assert res["action"] == "get_settings"
        assert res["kind"] == "reply"
        assert output_data == res["data"]

    update(
        {
            'wan_settings': {'wan_type': 'dhcp', 'wan_dhcp': {}},
            'wan6_settings': {'wan6_type': 'none'},
            'mac_settings': {'custom_mac_enabled': False},
        },
        {
            'wan_settings': {'wan_type': 'dhcp', 'wan_dhcp': {}},
            'wan6_settings': {'wan6_type': 'none'},
            'mac_settings': {'custom_mac_enabled': False},
        },
        {
            'wan_type': 'dhcp',
            'wan6_type': 'none',
            'custom_mac_enabled': False,
        },
    )
    # WAN
    update(
        {
            'wan_settings': {'wan_type': 'dhcp', 'wan_dhcp': {"hostname": "my-nice-turris4"}},
            'wan6_settings': {'wan6_type': 'none'},
            'mac_settings': {'custom_mac_enabled': False},
        },
        {
            'wan_settings': {'wan_type': 'dhcp', 'wan_dhcp': {"hostname": "my-nice-turris4"}},
            'wan6_settings': {'wan6_type': 'none'},
            'mac_settings': {'custom_mac_enabled': False},
        },
        {
            'wan_type': 'dhcp',
            'wan6_type': 'none',
            'custom_mac_enabled': False,
        },
    )
    update(
        {
            'wan_settings': {
                'wan_type': 'pppoe',
                'wan_pppoe': {"username": "my_user", "password": "pass1"}
            },
            'wan6_settings': {'wan6_type': 'none'},
            'mac_settings': {'custom_mac_enabled': False},
        },
        {
            'wan_settings': {
                'wan_type': 'pppoe',
                'wan_pppoe': {"username": "my_user", "password": "pass1"}
            },
            'wan6_settings': {'wan6_type': 'none'},
            'mac_settings': {'custom_mac_enabled': False},
        },
        {
            'wan_type': 'pppoe',
            'wan6_type': 'none',
            'custom_mac_enabled': False,
        },
    )
    update(
        {
            'wan_settings': {
                'wan_type': 'static',
                'wan_static': {
                    "ip": "10.0.0.10",
                    "netmask": "255.255.0.0",
                    "gateway": "10.0.0.1",
                }
            },
            'wan6_settings': {'wan6_type': 'none'},
            'mac_settings': {'custom_mac_enabled': False},
        },
        {
            'wan_settings': {
                'wan_type': 'static',
                'wan_static': {
                    "ip": "10.0.0.10",
                    "netmask": "255.255.0.0",
                    "gateway": "10.0.0.1",
                }
            },
            'wan6_settings': {'wan6_type': 'none'},
            'mac_settings': {'custom_mac_enabled': False},
        },
        {
            'wan_type': 'static',
            'wan6_type': 'none',
            'custom_mac_enabled': False,
        },
    )
    update(
        {
            'wan_settings': {
                'wan_type': 'static',
                'wan_static': {
                    "ip": "10.0.0.10",
                    "netmask": "255.255.0.0",
                    "gateway": "10.0.0.1",
                    "dns1": "10.0.0.1",
                    "dns2": "8.8.8.8",
                }
            },
            'wan6_settings': {'wan6_type': 'none'},
            'mac_settings': {'custom_mac_enabled': False},
        },
        {
            'wan_settings': {
                'wan_type': 'static',
                'wan_static': {
                    "ip": "10.0.0.10",
                    "netmask": "255.255.0.0",
                    "gateway": "10.0.0.1",
                    "dns1": "10.0.0.1",
                    "dns2": "8.8.8.8",
                }
            },
            'wan6_settings': {'wan6_type': 'none'},
            'mac_settings': {'custom_mac_enabled': False},
        },
        {
            'wan_type': 'static',
            'wan6_type': 'none',
            'custom_mac_enabled': False,
        },
    )
    # WAN6
    update(
        {
            'wan_settings': {'wan_type': 'dhcp', 'wan_dhcp': {}},
            'wan6_settings': {'wan6_type': 'dhcpv6', 'wan6_dhcpv6': {"duid": ""}},
            'mac_settings': {'custom_mac_enabled': False},
        },
        {
            'wan_settings': {'wan_type': 'dhcp', 'wan_dhcp': {}},
            'wan6_settings': {'wan6_type': 'dhcpv6', 'wan6_dhcpv6': {"duid": ""}},
            'mac_settings': {'custom_mac_enabled': False},
        },
        {
            'wan_type': 'dhcp',
            'wan6_type': 'dhcpv6',
            'custom_mac_enabled': False,
        },
    )
    update(
        {
            'wan_settings': {'wan_type': 'dhcp', 'wan_dhcp': {}},
            'wan6_settings': {
                'wan6_type': 'dhcpv6', 'wan6_dhcpv6': {"duid": "00030001d858d7004555"}},
            'mac_settings': {'custom_mac_enabled': False},
        },
        {
            'wan_settings': {'wan_type': 'dhcp', 'wan_dhcp': {}},
            'wan6_settings': {
                'wan6_type': 'dhcpv6', 'wan6_dhcpv6': {"duid": "00030001d858d7004555"}},
            'mac_settings': {'custom_mac_enabled': False},
        },
        {
            'wan_type': 'dhcp',
            'wan6_type': 'dhcpv6',
            'custom_mac_enabled': False,
        },
    )
    update(
        {
            'wan_settings': {'wan_type': 'dhcp', 'wan_dhcp': {}},
            'wan6_settings': {
                'wan6_type': 'static',
                'wan6_static': {
                    "ip": "2001:1488:fffe:6:da9e:f3ff:fe73:59c/64",
                    "network": "2001:1488:fffe:6::/60",
                    "gateway": "2001:1488:fffe:6::1",
                },
            },
            'mac_settings': {'custom_mac_enabled': False},
        },
        {
            'wan_settings': {'wan_type': 'dhcp', 'wan_dhcp': {}},
            'wan6_settings': {
                'wan6_type': 'static',
                'wan6_static': {
                    "ip": "2001:1488:fffe:6:da9e:f3ff:fe73:59c/64",
                    "network": "2001:1488:fffe:6::/60",
                    "gateway": "2001:1488:fffe:6::1",
                },
            },
            'mac_settings': {'custom_mac_enabled': False},
        },
        {
            'wan_type': 'dhcp',
            'wan6_type': 'static',
            'custom_mac_enabled': False,
        },
    )
    update(
        {
            'wan_settings': {'wan_type': 'dhcp', 'wan_dhcp': {}},
            'wan6_settings': {
                'wan6_type': 'static',
                'wan6_static': {
                    "ip": "2001:1488:fffe:6:da9e:f3ff:fe73:59c/64",
                    "network": "2001:1488:fffe:6::/60",
                    "gateway": "2001:1488:fffe:6::1",
                    "dns1": "2001:1488:fffe:6::1",
                    "dns2": "2001:4860:4860::8888",
                },
            },
            'mac_settings': {'custom_mac_enabled': False},
        },
        {
            'wan_settings': {'wan_type': 'dhcp', 'wan_dhcp': {}},
            'wan6_settings': {
                'wan6_type': 'static',
                'wan6_static': {
                    "ip": "2001:1488:fffe:6:da9e:f3ff:fe73:59c/64",
                    "network": "2001:1488:fffe:6::/60",
                    "gateway": "2001:1488:fffe:6::1",
                    "dns1": "2001:1488:fffe:6::1",
                    "dns2": "2001:4860:4860::8888",
                },
            },
            'mac_settings': {'custom_mac_enabled': False},
        },
        {
            'wan_type': 'dhcp',
            'wan6_type': 'static',
            'custom_mac_enabled': False,
        },
    )
    update(
        {
            'wan_settings': {'wan_type': 'dhcp', 'wan_dhcp': {}},
            'wan6_settings': {'wan6_type': '6to4', 'wan6_6to4': {'ipv4_address': ""}},
            'mac_settings': {'custom_mac_enabled': True, "custom_mac": "11:22:33:44:55:66"},
        },
        {
            'wan_settings': {'wan_type': 'dhcp', 'wan_dhcp': {}},
            'wan6_settings': {'wan6_type': '6to4', 'wan6_6to4': {'ipv4_address': ""}},
            'mac_settings': {'custom_mac_enabled': True, "custom_mac": "11:22:33:44:55:66"},
        },
        {
            'wan_type': 'dhcp',
            'wan6_type': '6to4',
            'custom_mac_enabled': True,
        },
    )
    update(
        {
            'wan_settings': {'wan_type': 'dhcp', 'wan_dhcp': {}},
            'wan6_settings': {'wan6_type': '6to4', 'wan6_6to4': {'ipv4_address': "1.2.3.4"}},
            'mac_settings': {'custom_mac_enabled': True, "custom_mac": "11:22:33:44:55:66"},
        },
        {
            'wan_settings': {'wan_type': 'dhcp', 'wan_dhcp': {}},
            'wan6_settings': {'wan6_type': '6to4', 'wan6_6to4': {'ipv4_address': "1.2.3.4"}},
            'mac_settings': {'custom_mac_enabled': True, "custom_mac": "11:22:33:44:55:66"},
        },
        {
            'wan_type': 'dhcp',
            'wan6_type': '6to4',
            'custom_mac_enabled': True,
        },
    )
    update(
        {
            'wan_settings': {'wan_type': 'dhcp', 'wan_dhcp': {}},
            'wan6_settings': {
                'wan6_type': '6in4',
                'wan6_6in4': {
                    "mtu": 1480,
                    "server_ipv4": "111.22.33.44",
                    "ipv6_prefix": "2001:470:6e:39::/64",
                    "dynamic_ipv4": {
                        "enabled": False,
                    }
                },
            },
            'mac_settings': {'custom_mac_enabled': False},
        },
        {
            'wan_settings': {'wan_type': 'dhcp', 'wan_dhcp': {}},
            'wan6_settings': {
                'wan6_type': '6in4',
                'wan6_6in4': {
                    "mtu": 1480,
                    "server_ipv4": "111.22.33.44",
                    "ipv6_prefix": "2001:470:6e:39::/64",
                    "dynamic_ipv4": {
                        "enabled": False,
                    }
                },
            },
            'mac_settings': {'custom_mac_enabled': False},
        },
        {
            'wan_type': 'dhcp',
            'wan6_type': '6in4',
            'custom_mac_enabled': False,
        },
    )
    update(
        {
            'wan_settings': {'wan_type': 'dhcp', 'wan_dhcp': {}},
            'wan6_settings': {
                'wan6_type': '6in4',
                'wan6_6in4': {
                    "mtu": 1280,
                    "server_ipv4": "11.22.33.44",
                    "ipv6_prefix": "2001:470:6f:39::/64",
                    "dynamic_ipv4": {
                        "enabled": True,
                        "tunnel_id": "1122334455",
                        "username": "user1",
                        "password_or_key": "passphrase1"
                    }
                },
            },
            'mac_settings': {'custom_mac_enabled': False},
        },
        {
            'wan_settings': {'wan_type': 'dhcp', 'wan_dhcp': {}},
            'wan6_settings': {
                'wan6_type': '6in4',
                'wan6_6in4': {
                    "mtu": 1280,
                    "server_ipv4": "11.22.33.44",
                    "ipv6_prefix": "2001:470:6f:39::/64",
                    "dynamic_ipv4": {
                        "enabled": True,
                        "tunnel_id": "1122334455",
                        "username": "user1",
                        "password_or_key": "passphrase1"
                    }
                },
            },
            'mac_settings': {'custom_mac_enabled': False},
        },
        {
            'wan_type': 'dhcp',
            'wan6_type': '6in4',
            'custom_mac_enabled': False,
        },
    )
    update(
        {
            'wan_settings': {'wan_type': 'dhcp', 'wan_dhcp': {}},
            'wan6_settings': {'wan6_type': 'none'},
            'mac_settings': {'custom_mac_enabled': True, "custom_mac": "11:22:33:44:55:66"},
        },
        {
            'wan_settings': {'wan_type': 'dhcp', 'wan_dhcp': {}},
            'wan6_settings': {'wan6_type': 'none'},
            'mac_settings': {'custom_mac_enabled': True, "custom_mac": "11:22:33:44:55:66"},
        },
        {
            'wan_type': 'dhcp',
            'wan6_type': 'none',
            'custom_mac_enabled': True,
        },
    )


@pytest.mark.only_backends(['openwrt'])
def test_wan_openwrt_backend(uci_configs_init, lock_backend, infrastructure, ubusd_test):

    uci = get_uci_module(lock_backend)

    def update(data):
        res = infrastructure.process_message({
            "module": "wan",
            "action": "update_settings",
            "kind": "request",
            "data": data
        })
        assert res == {
            u'action': u'update_settings',
            u'data': {u'result': True},
            u'kind': u'reply',
            u'module': u'wan'
        }
        assert sh_was_called("/etc/init.d/network", ["restart"])
        with uci.UciBackend() as backend:
            data = backend.read()
        return data

    # WAN
    data = update({
        'wan_settings': {'wan_type': 'dhcp', 'wan_dhcp': {}},
        'wan6_settings': {'wan6_type': 'none'},
        'mac_settings': {'custom_mac_enabled': False},
    })

    assert uci.get_option_named(data, "network", "wan", "proto") == "dhcp"
    assert uci.get_option_named(data, "network", "wan", "hostname", "") == ""
    assert uci.get_option_named(data, "network", "wan6", "proto") == "none"
    assert uci.get_option_named(data, "network", "wan6", "ip6addr", "") == ""
    assert uci.get_option_named(data, "network", "wan6", "ip6prefix", "") == ""
    assert uci.get_option_named(data, "network", "wan6", "ip6gw", "") == ""
    assert uci.get_option_named(data, "network", "wan", "macaddr", "") == ""
    assert uci.parse_bool(uci.get_option_named(data, "network", "wan", "ipv6", "0")) is False

    data = update({
        'wan_settings': {'wan_type': 'dhcp', 'wan_dhcp': {"hostname": "my-nice-turris"}},
        'wan6_settings': {'wan6_type': 'none'},
        'mac_settings': {'custom_mac_enabled': False},
    })

    assert uci.get_option_named(data, "network", "wan", "proto") == "dhcp"
    assert uci.get_option_named(data, "network", "wan", "hostname", "") == "my-nice-turris"
    assert uci.get_option_named(data, "network", "wan6", "proto") == "none"
    assert uci.get_option_named(data, "network", "wan6", "ip6addr", "") == ""
    assert uci.get_option_named(data, "network", "wan6", "ip6prefix", "") == ""
    assert uci.get_option_named(data, "network", "wan6", "ip6gw", "") == ""
    assert uci.get_option_named(data, "network", "wan", "macaddr", "") == ""
    assert uci.parse_bool(uci.get_option_named(data, "network", "wan", "ipv6", "0")) is False

    data = update({
        'wan_settings': {
            'wan_type': 'pppoe',
            'wan_pppoe': {"username": "my_user", "password": "pass1"}
        },
        'wan6_settings': {'wan6_type': 'none'},
        'mac_settings': {'custom_mac_enabled': False},
    })

    assert uci.get_option_named(data, "network", "wan", "proto") == "pppoe"
    assert uci.get_option_named(data, "network", "wan", "username") == "my_user"
    assert uci.get_option_named(data, "network", "wan", "password") == "pass1"
    assert uci.get_option_named(data, "network", "wan6", "proto") == "none"
    assert uci.get_option_named(data, "network", "wan6", "ip6addr", "") == ""
    assert uci.get_option_named(data, "network", "wan6", "ip6prefix", "") == ""
    assert uci.get_option_named(data, "network", "wan6", "ip6gw", "") == ""
    assert uci.get_option_named(data, "network", "wan", "macaddr", "") == ""
    assert uci.parse_bool(uci.get_option_named(data, "network", "wan", "ipv6", "0")) is False

    data = update({
        'wan_settings': {
            'wan_type': 'static',
            'wan_static': {
                "ip": "10.0.0.10",
                "netmask": "255.255.0.0",
                "gateway": "10.0.0.1",
            }
        },
        'wan6_settings': {'wan6_type': 'none'},
        'mac_settings': {'custom_mac_enabled': False},
    })

    assert uci.get_option_named(data, "network", "wan", "proto") == "static"
    assert uci.get_option_named(data, "network", "wan", "ipaddr") == "10.0.0.10"
    assert uci.get_option_named(data, "network", "wan", "netmask") == "255.255.0.0"
    assert uci.get_option_named(data, "network", "wan", "gateway") == "10.0.0.1"
    assert uci.get_option_named(data, "network", "wan6", "proto") == "none"
    assert uci.get_option_named(data, "network", "wan6", "ip6addr", "") == ""
    assert uci.get_option_named(data, "network", "wan6", "ip6prefix", "") == ""
    assert uci.get_option_named(data, "network", "wan6", "ip6gw", "") == ""
    assert uci.get_option_named(data, "network", "wan", "macaddr", "") == ""
    assert uci.parse_bool(uci.get_option_named(data, "network", "wan", "ipv6", "0")) is False

    data = update({
        'wan_settings': {
            'wan_type': 'static',
            'wan_static': {
                "ip": "10.0.0.10",
                "netmask": "255.255.0.0",
                "gateway": "10.0.0.1",
                "dns1": "10.0.0.1",
                "dns2": "8.8.8.8",
            }
        },
        'wan6_settings': {'wan6_type': 'none'},
        'mac_settings': {'custom_mac_enabled': False},
    })

    assert uci.get_option_named(data, "network", "wan", "proto") == "static"
    assert uci.get_option_named(data, "network", "wan", "ipaddr") == "10.0.0.10"
    assert uci.get_option_named(data, "network", "wan", "netmask") == "255.255.0.0"
    assert uci.get_option_named(data, "network", "wan", "gateway") == "10.0.0.1"
    assert uci.get_option_named(data, "network", "wan6", "proto") == "none"
    assert uci.get_option_named(data, "network", "wan6", "ip6addr", "") == ""
    assert uci.get_option_named(data, "network", "wan6", "ip6prefix", "") == ""
    assert uci.get_option_named(data, "network", "wan6", "ip6gw", "") == ""
    assert uci.get_option_named(data, "network", "wan", "macaddr", "") == ""
    assert uci.get_option_named(data, "network", "wan", "dns", []) == ["8.8.8.8", "10.0.0.1"]
    assert uci.parse_bool(uci.get_option_named(data, "network", "wan", "ipv6", "0")) is False

    # WAN6
    data = update({
        'wan_settings': {'wan_type': 'dhcp', 'wan_dhcp': {}},
        'wan6_settings': {'wan6_type': 'dhcpv6', 'wan6_dhcpv6': {"duid": "00030001d858d7004566"}},
        'mac_settings': {'custom_mac_enabled': False},
    })

    assert uci.get_option_named(data, "network", "wan", "proto") == "dhcp"
    assert uci.get_option_named(data, "network", "wan", "hostname", "") == ""
    assert uci.get_option_named(data, "network", "wan6", "proto") == "dhcpv6"
    assert uci.get_option_named(data, "network", "wan6", "clientid") == "00030001d858d7004566"
    assert uci.get_option_named(data, "network", "wan6", "ip6addr", "") == ""
    assert uci.get_option_named(data, "network", "wan6", "ip6prefix", "") == ""
    assert uci.get_option_named(data, "network", "wan6", "ip6gw", "") == ""
    assert uci.get_option_named(data, "network", "wan", "macaddr", "") == ""
    assert uci.parse_bool(uci.get_option_named(data, "network", "wan", "ipv6", "0")) is True

    data = update({
        'wan_settings': {'wan_type': 'dhcp', 'wan_dhcp': {}},
        'wan6_settings': {
            'wan6_type': 'static',
            'wan6_static': {
                "ip": "2001:1488:fffe:6:da9e:f3ff:fe73:59c/64",
                "network": "2001:1488:fffe:6::/60",
                "gateway": "2001:1488:fffe:6::1",
            },
        },
        'mac_settings': {'custom_mac_enabled': False},
    })

    assert uci.get_option_named(data, "network", "wan", "proto") == "dhcp"
    assert uci.get_option_named(data, "network", "wan", "hostname", "") == ""
    assert uci.get_option_named(data, "network", "wan6", "proto") == "static"
    assert uci.get_option_named(data, "network", "wan6", "ip6addr") == \
        "2001:1488:fffe:6:da9e:f3ff:fe73:59c/64"
    assert uci.get_option_named(data, "network", "wan6", "ip6prefix") == "2001:1488:fffe:6::/60"
    assert uci.get_option_named(data, "network", "wan6", "ip6gw") == "2001:1488:fffe:6::1"
    assert uci.get_option_named(data, "network", "wan", "macaddr", "") == ""
    assert uci.parse_bool(uci.get_option_named(data, "network", "wan", "ipv6", "0")) is True

    data = update({
        'wan_settings': {'wan_type': 'dhcp', 'wan_dhcp': {}},
        'wan6_settings': {
            'wan6_type': 'static',
            'wan6_static': {
                "ip": "2001:1488:fffe:6:da9e:f3ff:fe73:59c/64",
                "network": "2001:1488:fffe:6::/60",
                "gateway": "2001:1488:fffe:6::1",
                "dns1": "2001:1488:fffe:6::1",
                "dns2": "2001:4860:4860::8888",
            },
        },
        'mac_settings': {'custom_mac_enabled': False},
    })

    assert uci.get_option_named(data, "network", "wan", "proto") == "dhcp"
    assert uci.get_option_named(data, "network", "wan", "hostname", "") == ""
    assert uci.get_option_named(data, "network", "wan6", "proto") == "static"
    assert uci.get_option_named(data, "network", "wan6", "ip6addr") == \
        "2001:1488:fffe:6:da9e:f3ff:fe73:59c/64"
    assert uci.get_option_named(data, "network", "wan6", "ip6prefix") == "2001:1488:fffe:6::/60"
    assert uci.get_option_named(data, "network", "wan6", "ip6gw") == "2001:1488:fffe:6::1"
    assert uci.get_option_named(data, "network", "wan", "macaddr", "") == ""
    assert uci.get_option_named(data, "network", "wan6", "dns", []) == [
        "2001:4860:4860::8888",
        "2001:1488:fffe:6::1",
    ]
    assert uci.parse_bool(uci.get_option_named(data, "network", "wan", "ipv6", "0")) is True

    data = update({
        'wan_settings': {'wan_type': 'dhcp', 'wan_dhcp': {}},
        'wan6_settings': {'wan6_type': 'none'},
        'mac_settings': {'custom_mac_enabled': True, "custom_mac": "11:22:33:44:55:66"},
    })

    assert uci.get_option_named(data, "network", "wan", "proto") == "dhcp"
    assert uci.get_option_named(data, "network", "wan", "hostname", "") == ""
    assert uci.get_option_named(data, "network", "wan6", "proto") == "none"
    assert uci.get_option_named(data, "network", "wan6", "ip6addr", "") == ""
    assert uci.get_option_named(data, "network", "wan6", "ip6prefix", "") == ""
    assert uci.get_option_named(data, "network", "wan6", "ip6gw", "") == ""
    assert uci.get_option_named(data, "network", "wan", "macaddr", "") == "11:22:33:44:55:66"

    with uci.UciBackend() as backend:
        backend.del_option("network", "lan", "ip6assign")
    data = update({
        'wan_settings': {'wan_type': 'dhcp', 'wan_dhcp': {}},
        'wan6_settings': {'wan6_type': '6to4', 'wan6_6to4': {'ipv4_address': ""}},
        'mac_settings': {'custom_mac_enabled': False},
    })

    assert uci.get_option_named(data, "network", "wan", "proto") == "dhcp"
    assert uci.get_option_named(data, "network", "wan", "hostname", "") == ""
    assert uci.get_option_named(data, "network", "wan6", "proto") == "6to4"
    assert uci.get_option_named(data, "network", "wan6", "ip6addr", "") == ""
    assert uci.get_option_named(data, "network", "wan6", "ip6prefix", "") == ""
    assert uci.get_option_named(data, "network", "wan6", "ip6gw", "") == ""
    assert uci.get_option_named(data, "network", "wan6", "ipaddr", "") == ""
    assert uci.get_option_named(data, "network", "wan", "macaddr", "") == ""
    assert uci.get_option_named(data, "network", "lan", "ip6assign", "") == "60"
    assert uci.parse_bool(uci.get_option_named(data, "network", "wan", "ipv6", "0")) is True

    with uci.UciBackend() as backend:
        backend.del_option("network", "lan", "ip6assign")
    data = update({
        'wan_settings': {'wan_type': 'dhcp', 'wan_dhcp': {}},
        'wan6_settings': {'wan6_type': '6to4', 'wan6_6to4': {'ipv4_address': "1.5.7.9"}},
        'mac_settings': {'custom_mac_enabled': False},
    })

    assert uci.get_option_named(data, "network", "wan", "proto") == "dhcp"
    assert uci.get_option_named(data, "network", "wan", "hostname", "") == ""
    assert uci.get_option_named(data, "network", "wan6", "proto") == "6to4"
    assert uci.get_option_named(data, "network", "wan6", "ip6addr", "") == ""
    assert uci.get_option_named(data, "network", "wan6", "ip6prefix", "") == ""
    assert uci.get_option_named(data, "network", "wan6", "ip6gw", "") == ""
    assert uci.get_option_named(data, "network", "wan6", "ipaddr", "") == "1.5.7.9"
    assert uci.get_option_named(data, "network", "wan", "macaddr", "") == ""
    assert uci.get_option_named(data, "network", "lan", "ip6assign", "") == "60"
    assert uci.parse_bool(uci.get_option_named(data, "network", "wan", "ipv6", "0")) is True

    data = update({
        'wan_settings': {'wan_type': 'dhcp', 'wan_dhcp': {}},
        'wan6_settings': {
            'wan6_type': '6in4',
            'wan6_6in4': {
                "mtu": 1470,
                "server_ipv4": "1.22.33.44",
                "ipv6_prefix": "2001:470:6a:39::/64",
                "dynamic_ipv4": {
                    "enabled": False,
                }
            },
        },
        'mac_settings': {'custom_mac_enabled': False},
    })
    assert uci.get_option_named(data, "network", "wan", "proto") == "dhcp"
    assert uci.get_option_named(data, "network", "wan", "hostname", "") == ""
    assert uci.get_option_named(data, "network", "wan6", "proto") == "6in4"
    assert uci.get_option_named(data, "network", "wan6", "ip6addr", "") == ""
    assert uci.get_option_named(data, "network", "wan6", "ip6prefix", "") == "2001:470:6a:39::/64"
    assert uci.get_option_named(data, "network", "wan6", "ip6gw", "") == ""
    assert uci.get_option_named(data, "network", "wan6", "peeraddr", "") == "1.22.33.44"
    assert uci.get_option_named(data, "network", "wan6", "mtu", "") == "1470"
    assert uci.get_option_named(data, "network", "wan6", "tunnelid", "") == ""
    assert uci.get_option_named(data, "network", "wan6", "username", "") == ""
    assert uci.get_option_named(data, "network", "wan6", "password", "") == ""
    assert uci.get_option_named(data, "network", "wan", "macaddr", "") == ""
    assert uci.parse_bool(uci.get_option_named(
        data, "firewall", "turris_wan_6in4_rule", "enabled", "0")) is True
    assert uci.get_option_named(data, "firewall", "turris_wan_6in4_rule", "family", "") == "ipv4"
    assert uci.get_option_named(data, "firewall", "turris_wan_6in4_rule", "src", "") == "wan"
    assert uci.get_option_named(
        data, "firewall", "turris_wan_6in4_rule", "src_ip", "") == "1.22.33.44"
    assert uci.get_option_named(data, "firewall", "turris_wan_6in4_rule", "proto", "") == "41"
    assert uci.get_option_named(data, "firewall", "turris_wan_6in4_rule", "target", "") == "ACCEPT"
    assert uci.parse_bool(uci.get_option_named(data, "network", "wan", "ipv6", "0")) is True

    data = update({
        'wan_settings': {'wan_type': 'dhcp', 'wan_dhcp': {}},
        'wan6_settings': {
            'wan6_type': '6in4',
            'wan6_6in4': {
                "mtu": 1290,
                "server_ipv4": "1.222.33.44",
                "ipv6_prefix": "2001:470:6c:39::/64",
                "dynamic_ipv4": {
                    "enabled": True,
                    "tunnel_id": "123456",
                    "username": "user11",
                    "password_or_key": "passphrase11"
                }
            },
        },
        'mac_settings': {'custom_mac_enabled': False},
    })
    assert uci.get_option_named(data, "network", "wan", "proto") == "dhcp"
    assert uci.get_option_named(data, "network", "wan", "hostname", "") == ""
    assert uci.get_option_named(data, "network", "wan6", "proto") == "6in4"
    assert uci.get_option_named(data, "network", "wan6", "ip6addr", "") == ""
    assert uci.get_option_named(data, "network", "wan6", "ip6prefix", "") == "2001:470:6c:39::/64"
    assert uci.get_option_named(data, "network", "wan6", "ip6gw", "") == ""
    assert uci.get_option_named(data, "network", "wan6", "peeraddr", "") == "1.222.33.44"
    assert uci.get_option_named(data, "network", "wan6", "mtu", "") == "1290"
    assert uci.get_option_named(data, "network", "wan6", "tunnelid", "") == "123456"
    assert uci.get_option_named(data, "network", "wan6", "username", "") == "user11"
    assert uci.get_option_named(data, "network", "wan6", "password", "") == "passphrase11"
    assert uci.get_option_named(data, "network", "wan", "macaddr", "") == ""
    assert uci.parse_bool(uci.get_option_named(
        data, "firewall", "turris_wan_6in4_rule", "enabled", "")) is True
    assert uci.get_option_named(data, "firewall", "turris_wan_6in4_rule", "family", "") == "ipv4"
    assert uci.get_option_named(data, "firewall", "turris_wan_6in4_rule", "src", "") == "wan"
    assert uci.get_option_named(
        data, "firewall", "turris_wan_6in4_rule", "src_ip", "") == "1.222.33.44"
    assert uci.get_option_named(data, "firewall", "turris_wan_6in4_rule", "proto", "") == "41"
    assert uci.get_option_named(data, "firewall", "turris_wan_6in4_rule", "target", "") == "ACCEPT"
    assert uci.parse_bool(uci.get_option_named(data, "network", "wan", "ipv6", "0")) is True

    data = update({
        'wan_settings': {'wan_type': 'dhcp', 'wan_dhcp': {}},
        'wan6_settings': {'wan6_type': 'none'},
        'mac_settings': {'custom_mac_enabled': False},
    })
    assert uci.get_option_named(data, "network", "wan", "proto") == "dhcp"
    assert uci.get_option_named(data, "network", "wan", "hostname", "") == ""
    assert uci.get_option_named(data, "network", "wan6", "proto") == "none"
    assert uci.get_option_named(data, "network", "wan6", "ip6addr", "") == ""
    assert uci.get_option_named(data, "network", "wan6", "ip6prefix", "") == ""
    assert uci.get_option_named(data, "network", "wan6", "ip6gw", "") == ""
    assert uci.get_option_named(data, "network", "wan6", "peeraddr", "") == ""
    assert uci.get_option_named(data, "network", "wan6", "mtu", "") == ""
    assert uci.get_option_named(data, "network", "wan6", "tunnelid", "") == ""
    assert uci.get_option_named(data, "network", "wan6", "username", "") == ""
    assert uci.get_option_named(data, "network", "wan6", "password", "") == ""
    assert uci.get_option_named(data, "network", "wan", "macaddr", "") == ""
    assert uci.parse_bool(uci.get_option_named(
        data, "firewall", "turris_wan_6in4_rule", "enabled", "0")) is False
    assert uci.parse_bool(uci.get_option_named(data, "network", "wan", "ipv6", "0")) is False


def test_wrong_update(uci_configs_init, infrastructure, ubusd_test):

    def update(data):
        res = infrastructure.process_message({
            "module": "wan",
            "action": "update_settings",
            "kind": "request",
            "data": data
        })
        assert "errors" in res["data"]

    update(
        {
            'wan_settings': {'wan_type': 'dhcp', 'wan_dhcp': {}},
            'wan6_settings': {
                'wan6_type': 'static',
                'wan6_static': {
                    "ip": "2001:1488:fffe:6:da9e:f3ff:fe73:59c",
                    "network": "2001:1488:fffe:6::/60",
                    "gateway": "2001:1488:fffe:6::1",
                    "dns1": "2001:1488:fffe:6::1",
                    "dns2": "2001:4860:4860::8888",
                },
            },
            'mac_settings': {'custom_mac_enabled': False},
        }
    )
    update(
        {
            'wan_settings': {'wan_type': 'dhcp', 'wan_dhcp': {}},
            'wan6_settings': {
                'wan6_type': 'static',
                'wan6_static': {
                    "ip": "2001:1488:fffe:6:da9e:f3ff:fe73:59c/64",
                    "network": "2001:1488:fffe:6::",
                    "gateway": "2001:1488:fffe:6::1/128",
                    "dns1": "2001:1488:fffe:6::1",
                    "dns2": "2001:4860:4860::8888",
                },
            },
            'mac_settings': {'custom_mac_enabled': False},
        }
    )
    update(
        {
            'wan_settings': {'wan_type': 'dhcp', 'wan_dhcp': {}},
            'wan6_settings': {
                'wan6_type': 'static',
                'wan6_static': {
                    "ip": "2001:1488:fffe:6:da9e:f3ff:fe73:59c/64",
                    "network": "2001:1488:fffe:6::/60",
                    "gateway": "2001:1488:fffe:6::1",
                    "dns1": "2001:1488:fffe:6::1/128",
                    "dns2": "2001:4860:4860::8888",
                },
            },
            'mac_settings': {'custom_mac_enabled': False},
        }
    )
    update(
        {
            'wan_settings': {'wan_type': 'dhcp', 'wan_dhcp': {}},
            'wan6_settings': {
                'wan6_type': 'static',
                'wan6_static': {
                    "ip": None,
                    "network": "2001:1488:fffe:6::/60",
                    "gateway": "2001:1488:fffe:6::1",
                    "dns1": "2001:1488:fffe:6::1",
                    "dns2": "2001:4860:4860::8888",
                },
            },
            'mac_settings': {'custom_mac_enabled': False},
        }
    )
    update(
        {
            'wan_settings': {'wan_type': 'dhcp', 'wan_dhcp': {}},
            'wan6_settings': {
                'wan6_type': 'static',
                'wan6_static': {
                    "ip": "2001:1488:fffe:6:da9e:f3ff:fe73:59c/64",
                    "network": None,
                    "gateway": "2001:1488:fffe:6::1/128",
                    "dns1": "2001:1488:fffe:6::1",
                    "dns2": "2001:4860:4860::8888",
                },
            },
            'mac_settings': {'custom_mac_enabled': False},
        }
    )
    update(
        {
            'wan_settings': {'wan_type': 'dhcp', 'wan_dhcp': {}},
            'wan6_settings': {
                'wan6_type': 'static',
                'wan6_static': {
                    "ip": "2001:1488:fffe:6:da9e:f3ff:fe73:59c/64",
                    "network": "2001:1488:fffe:6::/60",
                    "gateway": "2001:1488:fffe:6::1",
                    "dns1": None,
                    "dns2": "2001:4860:4860::8888",
                },
            },
            'mac_settings': {'custom_mac_enabled': False},
        }
    )
    update(
        {
            'wan_settings': {'wan_type': 'dhcp', 'wan_dhcp': {}},
            'wan6_settings': {
                'wan6_type': '6to4',
                'wan6_6to4': {
                    "ipv4_address": "256.0.0.0",
                },
            },
            'mac_settings': {'custom_mac_enabled': False},
        }
    )
    update(
        {
            'wan_settings': {'wan_type': 'dhcp', 'wan_dhcp': {}},
            'wan6_settings': {
                'wan6_type': '6in4',
                'wan6_6in4': {
                    "mtu": 1480,
                    "server_ipv4": "11.22.333.44",
                    "ipv6_prefix": "2001:470:6f:39::/64",
                    "dynamic_ipv4": {
                        "enabled": True,
                        "tunnel_id": "1122334455",
                        "username": "user1",
                        "password_or_key": "passphrase1"
                    }
                },
            },
            'mac_settings': {'custom_mac_enabled': False},
        }
    )
    update(
        {
            'wan_settings': {'wan_type': 'dhcp', 'wan_dhcp': {}},
            'wan6_settings': {
                'wan6_type': '6in4',
                'wan6_6in4': {
                    "mtu": 1480,
                    "server_ipv4": "11.22.33.44",
                    "ipv6_prefix": "2001:470::6f:39::/64",
                    "dynamic_ipv4": {
                        "enabled": True,
                        "tunnel_id": "1122334455",
                        "username": "user1",
                        "password_or_key": "passphrase1"
                    }
                },
            },
            'mac_settings': {'custom_mac_enabled': False},
        }
    )
    update(
        {
            'wan_settings': {'wan_type': 'dhcp', 'wan_dhcp': {}},
            'wan6_settings': {
                'wan6_type': '6in4',
                'wan6_6in4': {
                    "mtu": 1480,
                    "server_ipv4": "11.22.33.44",
                    "ipv6_prefix": "2001:470:6f:39::/129",
                    "dynamic_ipv4": {
                        "enabled": True,
                        "tunnel_id": "1122334455",
                        "username": "user1",
                        "password_or_key": "passphrase1"
                    }
                },
            },
            'mac_settings': {'custom_mac_enabled': False},
        }
    )
    update(
        {
            'wan_settings': {'wan_type': 'dhcp', 'wan_dhcp': {}},
            'wan6_settings': {
                'wan6_type': '6in4',
                'wan6_6in4': {
                    "mtu": 1480,
                    "server_ipv4": "11.22.33.44",
                    "ipv6_prefix": "2001:470:6f:39::/64",
                    "dynamic_ipv4": {
                        "enabled": False,
                        "tunnel_id": "1122334455",
                        "username": "user1",
                        "password_or_key": "passphrase1"
                    }
                },
            },
            'mac_settings': {'custom_mac_enabled': False},
        }
    )


def test_connection_test(uci_configs_init, infrastructure, ubusd_test):
    res = infrastructure.process_message({
        "module": "wan",
        "action": "connection_test_status",
        "kind": "request",
        "data": {
            "test_id": "non-existing",
        }
    })
    assert set(res.keys()) == {"action", "kind", "data", "module"}
    assert res['data'] == {u'status': u'not_found'}

    res = infrastructure.process_message({
        "module": "wan",
        "action": "connection_test_trigger",
        "kind": "request",
        "data": {"test_kinds": ["ipv4", "ipv6", "dns"]},
    })
    assert set(res.keys()) == {"action", "kind", "data", "module"}
    assert "test_id" in res["data"].keys()

    test_id = res["data"]["test_id"]
    res = infrastructure.process_message({
        "module": "wan",
        "action": "connection_test_status",
        "kind": "request",
        "data": {
            "test_id": test_id,
        }
    })
    assert set(res.keys()) == {"action", "kind", "data", "module"}
    assert res['data']['status'] in ["running", "finished"]
    assert "data" in res['data']


@pytest.mark.only_backends(['openwrt'])
def test_missing_wan6_openwrt(uci_configs_init, lock_backend, infrastructure, ubusd_test):
    uci = get_uci_module(lock_backend)
    with uci.UciBackend() as backend:
        backend.del_section("network", "wan6")

    res = infrastructure.process_message({
        "module": "wan",
        "action": "get_settings",
        "kind": "request",
    })
    assert "wan6_settings" in res["data"].keys()
    assert res["data"]["wan6_settings"]["wan6_type"] == "none"

    res = infrastructure.process_message({
        "module": "wan",
        "action": "update_settings",
        "kind": "request",
        "data": {
            'wan_settings': {'wan_type': 'dhcp', 'wan_dhcp': {}},
            'wan6_settings': {'wan6_type': 'dhcpv6', 'wan6_dhcpv6': {"duid": ""}},
            'mac_settings': {'custom_mac_enabled': False},
        },
    })
    assert "result" in res["data"]
    assert res["data"]["result"]

    res = infrastructure.process_message({
        "module": "wan",
        "action": "get_settings",
        "kind": "request",
    })
    assert "wan6_settings" in res["data"].keys()
    assert res["data"]["wan6_settings"]["wan6_type"] == "dhcpv6"

    with uci.UciBackend() as backend:
        data = backend.read()

    assert uci.get_option_named(data, "network", "wan6", "proto") == "dhcpv6"
    assert uci.get_option_named(data, "network", "wan6", "ifname") == "@wan"
