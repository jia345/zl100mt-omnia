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

import pytest

from foris_controller.exceptions import UciRecordNotFound

from foris_controller_testtools.fixtures import (
    only_backends, uci_configs_init, infrastructure, ubusd_test, lock_backend, init_script_result
)
from foris_controller_testtools.utils import (
    match_subdict, sh_was_called, get_uci_module, check_service_result
)


def test_get_settings(uci_configs_init, infrastructure, ubusd_test):
    res = infrastructure.process_message({
        "module": "lan",
        "action": "get_settings",
        "kind": "request",
    })
    assert set(res.keys()) == {"action", "kind", "data", "module"}
    assert "ip" in res["data"].keys()
    assert "netmask" in res["data"].keys()
    assert "dhcp" in res["data"].keys()
    assert "enabled" in res["data"]["dhcp"].keys()
    assert "start" in res["data"]["dhcp"].keys()
    assert "limit" in res["data"]["dhcp"].keys()
    assert "guest_network" in res["data"].keys()
    assert "enabled" in res["data"]["guest_network"].keys()
    assert "ip" in res["data"]["guest_network"].keys()
    assert "netmask" in res["data"]["guest_network"].keys()
    assert "qos" in res["data"]["guest_network"].keys()
    assert "enabled" in res["data"]["guest_network"]["qos"].keys()
    assert "upload" in res["data"]["guest_network"]["qos"].keys()
    assert "download" in res["data"]["guest_network"]["qos"].keys()


def test_update_settings(uci_configs_init, infrastructure, ubusd_test):
    filters = [("lan", "update_settings")]

    def update(data):
        notifications = infrastructure.get_notifications(filters=filters)
        res = infrastructure.process_message({
            "module": "lan",
            "action": "update_settings",
            "kind": "request",
            "data": data
        })
        assert res == {
            u'action': u'update_settings',
            u'data': {u'result': True},
            u'kind': u'reply',
            u'module': u'lan'
        }
        notifications = infrastructure.get_notifications(notifications, filters=filters)
        assert notifications[-1]["module"] == "lan"
        assert notifications[-1]["action"] == "update_settings"
        assert notifications[-1]["kind"] == "notification"
        assert match_subdict(data, notifications[-1]["data"])

        res = infrastructure.process_message({
            "module": "lan",
            "action": "get_settings",
            "kind": "request",
        })
        assert res["module"] == "lan"
        assert res["action"] == "get_settings"
        assert res["kind"] == "reply"
        assert match_subdict(data, res["data"])

    update({
        u"ip": u"192.168.5.8",
        u"netmask": u"255.255.255.0",
        u"dhcp": {u"enabled": False},
        u"guest_network": {u"enabled": False},
    })
    update({
        u"ip": u"10.0.0.3",
        u"netmask": u"255.255.0.0",
        u"dhcp": {u"enabled": False},
        u"guest_network": {u"enabled": False},
    })
    update({
        u"ip": u"10.1.0.3",
        u"netmask": u"255.255.0.0",
        u"dhcp": {
            u"enabled": True,
            u"start": 10,
            u"limit": 50,
        },
        u"guest_network": {u"enabled": False},
    })
    update({
        u"ip": u"10.2.0.3",
        u"netmask": u"255.255.0.0",
        u"dhcp": {u"enabled": False},
        u"guest_network": {
            u"enabled": True,
            u"ip": u"192.168.8.1",
            u"netmask": u"255.255.255.0",
            u"qos": {
                u"enabled": False,
            },
        },
    })
    update({
        u"ip": u"10.3.0.3",
        u"netmask": u"255.255.0.0",
        u"dhcp": {u"enabled": False},
        u"guest_network": {
            u"enabled": True,
            u"ip": u"192.168.9.1",
            u"netmask": u"255.255.255.0",
            u"qos": {
                u"enabled": True,
                u"download": 1200,
                u"upload": 1000,
            },
        },
    })


@pytest.mark.only_backends(['openwrt'])
def test_guest_openwrt_backend(
    uci_configs_init, lock_backend, init_script_result, infrastructure, ubusd_test
):

    uci = get_uci_module(lock_backend)

    def update(data):
        res = infrastructure.process_message({
            "module": "lan",
            "action": "update_settings",
            "kind": "request",
            "data": data
        })
        assert res == {
            u'action': u'update_settings',
            u'data': {u'result': True},
            u'kind': u'reply',
            u'module': u'lan'
        }
        assert sh_was_called("/etc/init.d/network", ["restart"])
        if data["guest_network"]["enabled"]:
            if data["guest_network"]["qos"]["enabled"]:
                check_service_result("sqm", True, "enable")
            else:
                check_service_result("sqm", True, "disable")

    # test guest network
    update({
        u"ip": u"10.2.0.3",
        u"netmask": u"255.255.0.0",
        u"dhcp": {u"enabled": False},
        u"guest_network": {
            u"enabled": True,
            u"ip": u"192.168.8.1",
            u"netmask": u"255.255.255.0",
            u"qos": {
                u"enabled": False,
            },
        },
    })
    with uci.UciBackend() as backend:
        data = backend.read()

    assert uci.parse_bool(uci.get_option_named(data, "network", "guest_turris", "enabled"))
    assert uci.get_option_named(data, "network", "guest_turris", "type") == "bridge"
    # this depends on default uci wireless config if it changes this line needs to be updated
    required_set = {"guest_turris_0", "guest_turris_1"}
    assert set(uci.get_option_named(data, "network", "guest_turris", "ifname")) == \
        required_set
    assert uci.get_option_named(data, "network", "guest_turris", "proto") == "static"
    assert uci.get_option_named(data, "network", "guest_turris", "ipaddr") == "192.168.8.1"
    assert uci.get_option_named(data, "network", "guest_turris", "netmask") == "255.255.255.0"
    assert uci.get_option_named(data, "network", "guest_turris", "bridge_empty") == "1"

    assert not uci.parse_bool(uci.get_option_named(data, "dhcp", "guest_turris", "ignore"))
    assert uci.get_option_named(data, "dhcp", "guest_turris", "interface") == "guest_turris"
    assert uci.get_option_named(data, "dhcp", "guest_turris", "start") == "200"
    assert uci.get_option_named(data, "dhcp", "guest_turris", "limit") == "50"
    assert uci.get_option_named(data, "dhcp", "guest_turris", "leasetime") == "1h"
    assert uci.get_option_named(data, "dhcp", "guest_turris", "dhcp_option") == ["6,192.168.8.1"]

    assert uci.parse_bool(uci.get_option_named(data, "firewall", "guest_turris", "enabled"))
    assert uci.get_option_named(data, "firewall", "guest_turris", "name") == "guest_turris"
    assert uci.get_option_named(data, "firewall", "guest_turris", "input") == "REJECT"
    assert uci.get_option_named(data, "firewall", "guest_turris", "forward") == "REJECT"
    assert uci.get_option_named(data, "firewall", "guest_turris", "output") == "ACCEPT"
    assert uci.parse_bool(uci.get_option_named(
        data, "firewall", "guest_turris_forward_wan", "enabled"))
    assert uci.get_option_named(
        data, "firewall", "guest_turris_forward_wan", "src") == "guest_turris"
    assert uci.get_option_named(
        data, "firewall", "guest_turris_forward_wan", "dest") == "wan"
    assert uci.parse_bool(uci.get_option_named(
        data, "firewall", "guest_turris_dns_rule", "enabled"))
    assert uci.get_option_named(
        data, "firewall", "guest_turris_dns_rule", "src") == "guest_turris"
    assert uci.get_option_named(
        data, "firewall", "guest_turris_dns_rule", "proto") == "tcpudp"
    assert uci.get_option_named(
        data, "firewall", "guest_turris_dns_rule", "dest_port") == "53"
    assert uci.get_option_named(
        data, "firewall", "guest_turris_dns_rule", "target") == "ACCEPT"
    assert uci.parse_bool(uci.get_option_named(
        data, "firewall", "guest_turris_dhcp_rule", "enabled"))
    assert uci.get_option_named(
        data, "firewall", "guest_turris_dhcp_rule", "src") == "guest_turris"
    assert uci.get_option_named(
        data, "firewall", "guest_turris_dhcp_rule", "proto") == "udp"
    assert uci.get_option_named(
        data, "firewall", "guest_turris_dhcp_rule", "src_port") == "67-68"
    assert uci.get_option_named(
        data, "firewall", "guest_turris_dhcp_rule", "dest_port") == "67-68"
    assert uci.get_option_named(
        data, "firewall", "guest_turris_dhcp_rule", "target") == "ACCEPT"

    with pytest.raises(UciRecordNotFound):
        assert uci.get_option_named(data, "sqm", "guest_limit_turris", "enabled")

    # test guest network + qos
    update({
        u"ip": u"10.3.0.3",
        u"netmask": u"255.255.0.0",
        u"dhcp": {u"enabled": False},
        u"guest_network": {
            u"enabled": True,
            u"ip": u"192.168.9.1",
            u"netmask": u"255.255.255.0",
            u"qos": {
                u"enabled": True,
                u"download": 1200,
                u"upload": 1000,
            },
        },
    })
    with uci.UciBackend() as backend:
        data = backend.read()
    assert uci.parse_bool(uci.get_option_named(data, "sqm", "guest_limit_turris", "enabled"))
    assert uci.get_option_named(data, "sqm", "guest_limit_turris", "interface") \
        == "br-guest_turris"
    assert uci.get_option_named(data, "sqm", "guest_limit_turris", "qdisc") == "fq_codel"
    assert uci.get_option_named(data, "sqm", "guest_limit_turris", "script") == "simple.qos"
    assert uci.get_option_named(data, "sqm", "guest_limit_turris", "link_layer") == "none"
    assert uci.get_option_named(data, "sqm", "guest_limit_turris", "verbosity") == "5"
    assert uci.get_option_named(data, "sqm", "guest_limit_turris", "debug_logging") == "1"
    assert uci.get_option_named(data, "sqm", "guest_limit_turris", "download") == "1000"
    assert uci.get_option_named(data, "sqm", "guest_limit_turris", "upload") == "1200"

    # test guest wi-fi disabled and other disabled
    update({
        u"ip": u"10.3.0.3",
        u"netmask": u"255.255.0.0",
        u"dhcp": {u"enabled": False},
        u"guest_network": {
            u"enabled": False,
        },
    })
    with uci.UciBackend() as backend:
        data = backend.read()
    assert not uci.parse_bool(uci.get_option_named(data, "network", "guest_turris", "enabled"))
    assert uci.parse_bool(uci.get_option_named(data, "dhcp", "guest_turris", "ignore"))
    assert not uci.parse_bool(uci.get_option_named(data, "firewall", "guest_turris", "enabled"))
    assert not uci.parse_bool(uci.get_option_named(
        data, "firewall", "guest_turris_forward_wan", "enabled"))
    assert not uci.parse_bool(uci.get_option_named(
        data, "firewall", "guest_turris_dns_rule", "enabled"))
    assert not uci.parse_bool(uci.get_option_named(
        data, "firewall", "guest_turris_dhcp_rule", "enabled"))
    assert uci.parse_bool(uci.get_option_named(data, "wireless", "guest_iface_0", "disabled"))
    assert uci.parse_bool(uci.get_option_named(data, "wireless", "guest_iface_1", "disabled"))

    with pytest.raises(UciRecordNotFound):
        assert uci.get_option_named(data, "sqm", "guest_limit_turris", "enabled")


def test_wrong_update(uci_configs_init, infrastructure, ubusd_test):

    def update(data):
        res = infrastructure.process_message({
            "module": "lan",
            "action": "update_settings",
            "kind": "request",
            "data": data
        })
        assert "errors" in res["data"]

    update({
        u"ip": u"10.1.0.3",
        u"netmask": u"255.255.0.0",
        u"dhcp": {
            u"enabled": False,
            u"start": 10,
            u"limit": 50,
        },
        u"guest_network": {u"enabled": False},
    })
    update({
        u"ip": u"10.2.0.3",
        u"netmask": u"255.255.0.0",
        u"dhcp": {u"enabled": False},
        u"guest_network": {
            u"enabled": True,
            u"ip": u"192.168.8.1",
            u"netmask": u"255.255.255.0",
        },
    }),
    update({
        u"ip": u"10.2.0.3",
        u"netmask": u"255.255.0.0",
        u"dhcp": {u"enabled": False},
        u"guest_network": {
            u"enabled": False,
            u"ip": u"192.168.8.1",
            u"netmask": u"255.255.255.0",
            u"qos": {
                u"enabled": False,
            },
        },
    })
    update({
        u"ip": u"10.3.0.3",
        u"netmask": u"255.255.0.0",
        u"dhcp": {u"enabled": False},
        u"guest_network": {
            u"enabled": True,
            u"ip": u"192.168.9.1",
            u"netmask": u"255.255.255.0",
            u"qos": {
                u"enabled": False,
                u"download": 1200,
                u"upload": 1000,
            },
        },
    })
