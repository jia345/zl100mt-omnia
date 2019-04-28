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
import os

from foris_controller_testtools.fixtures import (
    infrastructure, uci_configs_init, ubusd_test, only_backends, lock_backend,
    init_script_result
)
from foris_controller_testtools.utils import check_service_result, get_uci_module

NTPDATE_INDICATOR_PATH = "/tmp/foris-controller-ntp-fail"


def cmd_mock_gen(path):
    def inner_function():
        def try_unlink():
            try:
                os.unlink(path)
            except Exception:
                pass

        def read():
            res = None
            try:
                with open(path) as f:
                    res = f.read().strip()
            except Exception:
                pass
            try_unlink()

            return res

        try_unlink()
        yield read
        try_unlink()
    return inner_function


hwclock_mock = pytest.fixture(
    cmd_mock_gen('/tmp/foris-controller-tests-hwclock-called'), name="hwclock_mock",
)
date_mock = pytest.fixture(
    cmd_mock_gen('/tmp/foris-controller-tests-date-called'), name="date_mock",
)


@pytest.fixture
def fail_ntpdate():
    try:
        os.unlink(NTPDATE_INDICATOR_PATH)
    except Exception:
        pass

    with open(NTPDATE_INDICATOR_PATH, "w") as f:
        f.flush()

    yield NTPDATE_INDICATOR_PATH

    try:
        os.unlink(NTPDATE_INDICATOR_PATH)
    except Exception:
        pass


@pytest.fixture
def pass_ntpdate():
    try:
        os.unlink(NTPDATE_INDICATOR_PATH)
    except Exception:
        pass

    yield NTPDATE_INDICATOR_PATH


def test_get_settings(uci_configs_init, infrastructure, ubusd_test):
    res = infrastructure.process_message({
        "module": "time",
        "action": "get_settings",
        "kind": "request",
    })
    assert set(res.keys()) == {"action", "kind", "data", "module"}
    assert "region" in res["data"].keys()
    assert "city" in res["data"].keys()
    assert "timezone" in res["data"].keys()
    assert "time_settings" in res["data"].keys()
    assert "how_to_set_time" in res["data"]["time_settings"].keys()
    assert "time" in res["data"]["time_settings"].keys()


def test_update_settings(uci_configs_init, init_script_result, infrastructure, ubusd_test):
    filters = [("time", "update_settings")]
    notifications = infrastructure.get_notifications(filters=filters)
    res = infrastructure.process_message({
        "module": "time",
        "action": "update_settings",
        "kind": "request",
        "data": {
            "region": "Europe",
            "city": "Moscow",
            "timezone": "MSK-3",
            "time_settings": {
                "how_to_set_time": "ntp"
            }
        }
    })
    assert set(res.keys()) == {"action", "kind", "data", "module"}
    assert "result" in res["data"].keys()
    assert res["data"]["result"] is True
    notifications = infrastructure.get_notifications(notifications, filters=filters)
    assert notifications[-1] == {
        u"module": u"time",
        u"action": u"update_settings",
        u"kind": u"notification",
        u"data": {
            u"region": u"Europe",
            u"city": u"Moscow",
            u"timezone": u"MSK-3",
            u"time_settings": {
                u"how_to_set_time": u"ntp"
            }
        }
    }
    res = infrastructure.process_message({
        "module": "time",
        "action": "get_settings",
        "kind": "request",
    })
    assert res["data"]["region"] == u"Europe"
    assert res["data"]["city"] == u"Moscow"
    assert res["data"]["timezone"] == u"MSK-3"
    assert res["data"]["time_settings"]["how_to_set_time"] == u"ntp"

    res = infrastructure.process_message({
        "module": "time",
        "action": "update_settings",
        "kind": "request",
        "data": {
            "region": "Europe",
            "city": "Prague",
            "timezone": "CET-1CEST,M3.5.0,M10.5.0/3",
            "time_settings": {
                "how_to_set_time": "manual",
                "time": "2018-01-30T15:51:30.482515",
            }
        }
    })
    assert set(res.keys()) == {"action", "kind", "data", "module"}
    assert "result" in res["data"].keys()
    assert res["data"]["result"] is True
    notifications = infrastructure.get_notifications(notifications, filters=filters)
    assert notifications[-1] == {
        u"module": u"time",
        u"action": u"update_settings",
        u"kind": u"notification",
        u"data": {
            u"region": u"Europe",
            u"city": u"Prague",
            u"timezone": u"CET-1CEST,M3.5.0,M10.5.0/3",
            u"time_settings": {
                u"how_to_set_time": u"manual",
                u"time": u"2018-01-30T15:51:30.482515",
            }
        }
    }
    res = infrastructure.process_message({
        "module": "time",
        "action": "get_settings",
        "kind": "request",
    })
    assert res["data"]["region"] == u"Europe"
    assert res["data"]["city"] == u"Prague"
    assert res["data"]["timezone"] == u"CET-1CEST,M3.5.0,M10.5.0/3"
    assert res["data"]["time_settings"]["how_to_set_time"] == u"manual"


def test_get_router_time(uci_configs_init, infrastructure, ubusd_test):
    res = infrastructure.process_message({
        "module": "time",
        "action": "get_router_time",
        "kind": "request",
    })
    assert set(res.keys()) == {"action", "kind", "data", "module"}
    assert "time" in res["data"].keys()


@pytest.mark.only_backends(['openwrt'])
def test_openwrt_complex(
    uci_configs_init, init_script_result, date_mock, hwclock_mock,
    cmdline_script_root, infrastructure, ubusd_test, lock_backend
):
    res = infrastructure.process_message({
        "module": "time",
        "action": "update_settings",
        "kind": "request",
        "data": {
            "region": "Europe",
            "city": "Moscow",
            "timezone": "MSK-3",
            "time_settings": {
                "how_to_set_time": "ntp"
            }
        }
    })
    assert res["data"]["result"] is True
    check_service_result("sysntpd", True, "restart")

    uci = get_uci_module(lock_backend)
    with uci.UciBackend() as backend:
        data = backend.read()

    assert uci.get_option_anonymous(data, "system", "system", 0, "timezone") == "MSK-3"
    assert uci.get_option_anonymous(data, "system", "system", 0, "zonename") == "Europe/Moscow"
    assert uci.parse_bool(uci.get_option_named(data, "system", "ntp", "enabled"))

    assert not date_mock()
    assert not hwclock_mock()

    res = infrastructure.process_message({
        "module": "time",
        "action": "update_settings",
        "kind": "request",
        "data": {
            u"region": u"Europe",
            u"city": u"Prague",
            u"timezone": u"CET-1CEST,M3.5.0,M10.5.0/3",
            u"time_settings": {
                u"how_to_set_time": u"manual",
                u"time": u"2018-01-30T15:51:30.482515",
            }
        }
    })
    assert res["data"]["result"] is True
    check_service_result("sysntpd", True, "stop")

    uci = get_uci_module(lock_backend)
    with uci.UciBackend() as backend:
        data = backend.read()

    assert uci.get_option_anonymous(data, "system", "system", 0, "timezone") == \
        "CET-1CEST,M3.5.0,M10.5.0/3"
    assert uci.get_option_anonymous(data, "system", "system", 0, "zonename") == "Europe/Prague"
    assert not uci.parse_bool(uci.get_option_named(data, "system", "ntp", "enabled"))

    assert "2018-01-30" in date_mock()
    assert hwclock_mock()


@pytest.mark.only_backends(['mock'])
def test_ntpdate_trigger_mock(uci_configs_init, infrastructure, ubusd_test):
    res = infrastructure.process_message({
        "module": "time",
        "action": "ntpdate_trigger",
        "kind": "request",
    })
    assert set(res.keys()) == {"action", "kind", "data", "module"}
    assert "id" in res["data"].keys()


@pytest.mark.only_backends(['openwrt'])
def test_ntpdate_trigger_pass_openwrt(
    uci_configs_init, init_script_result, date_mock, hwclock_mock,
    cmdline_script_root, infrastructure, ubusd_test, lock_backend,
    pass_ntpdate
):
    filters = [("time", "ntpdate_started"), ("time", "ntpdate_finished")]
    notifications = infrastructure.get_notifications(filters=filters)
    res = infrastructure.process_message({
        "module": "time",
        "action": "ntpdate_trigger",
        "kind": "request",
    })
    async_id = res["data"]["id"]

    # get started notification
    notifications = infrastructure.get_notifications(notifications, filters=filters)
    assert notifications[-1] == {
        u"module": u"time",
        u"action": u"ntpdate_started",
        u"kind": u"notification",
        u"data": {
            u"id": async_id,
        }
    }

    # get finished notification
    notifications = infrastructure.get_notifications(notifications, filters=filters)
    assert notifications[-1]["action"] == "ntpdate_finished"
    assert notifications[-1]["data"]["id"] == async_id
    assert notifications[-1]["data"]["result"]
    assert "time" in notifications[-1]["data"].keys()
    assert not date_mock()
    assert hwclock_mock()


@pytest.mark.only_backends(['openwrt'])
def test_ntpdate_trigger_fail_openwrt(
    uci_configs_init, init_script_result, date_mock, hwclock_mock,
    cmdline_script_root, infrastructure, ubusd_test, lock_backend,
    fail_ntpdate
):
    filters = [("time", "ntpdate_started"), ("time", "ntpdate_finished")]
    notifications = infrastructure.get_notifications(filters=filters)
    res = infrastructure.process_message({
        "module": "time",
        "action": "ntpdate_trigger",
        "kind": "request",
    })
    async_id = res["data"]["id"]

    # get started notification
    notifications = infrastructure.get_notifications(notifications, filters=filters)
    assert notifications[-1] == {
        u"module": u"time",
        u"action": u"ntpdate_started",
        u"kind": u"notification",
        u"data": {
            u"id": async_id,
        }
    }

    notifications = infrastructure.get_notifications(notifications, filters=filters)
    assert notifications[-1] == {
        u"module": u"time",
        u"action": u"ntpdate_finished",
        u"kind": u"notification",
        u"data": {
            u"id": async_id,
            u"result": False,
        }
    }
    assert not date_mock()
    assert not hwclock_mock()
