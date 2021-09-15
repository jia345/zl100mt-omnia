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

import pytest

from .test_updater import wait_for_updater_run_finished
from foris_controller_testtools.fixtures import (
    infrastructure, uci_configs_init, ubusd_test, init_script_result, lock_backend,
    only_backends, updater_userlists
)
from foris_controller_testtools.utils import check_service_result, get_uci_module


def test_get_registered(uci_configs_init, infrastructure, ubusd_test):
    res = infrastructure.process_message({
        "module": "data_collect",
        "action": "get_registered",
        "kind": "request"
    })

    assert "errors" in res["data"].keys()
    assert "Incorrect input." in res["data"]["errors"][0]["description"]

    res = infrastructure.process_message({
        "module": "data_collect",
        "action": "get_registered",
        "kind": "request",
        "data": {
        }
    })
    assert "errors" in res["data"].keys()
    assert "Incorrect input." in res["data"]["errors"][0]["description"]

    res = infrastructure.process_message({
        "module": "data_collect",
        "action": "get_registered",
        "kind": "request",
        "data": {
            "email": "test@test.test",
            "language": "en"
        }
    })
    assert "status" in res["data"].keys()


def test_get(uci_configs_init, infrastructure, ubusd_test):
    res = infrastructure.process_message({
        "module": "data_collect",
        "action": "get",
        "kind": "request"
    })
    assert "agreed" in res["data"].keys()


def test_set(updater_userlists, infrastructure, ubusd_test):
    def set_agreed(agreed):
        filters = [("data_collect", "set")]
        old_notifications = infrastructure.get_notifications(filters=filters)
        res = infrastructure.process_message({
            "module": "data_collect",
            "action": "set",
            "kind": "request",
            "data": {
                "agreed": agreed
            }
        })
        assert res == {
            u'action': u'set',
            u'data': {u'result': True},
            u'kind': u'reply',
            u'module': u'data_collect'
        }
        notifications = infrastructure.get_notifications(old_notifications, filters=filters)
        assert notifications[-1] == {
            u"module": u"data_collect",
            u"action": u"set",
            u"kind": u"notification",
            u"data": {
                u"agreed": agreed,
            }
        }
        res = infrastructure.process_message({
            "module": "data_collect",
            "action": "get",
            "kind": "request"
        })
        assert res == {
            u"module": u"data_collect",
            u"action": u"get",
            u"kind": u"reply",
            u"data": {
                u"agreed": agreed,
            }
        }

    set_agreed(True)
    set_agreed(False)
    set_agreed(True)
    set_agreed(False)


@pytest.mark.only_backends(['openwrt'])
def test_set_openwrt(
    updater_userlists, uci_configs_init, init_script_result, infrastructure, ubusd_test
):
    filters = [("data_collect", "set"), ("updater", "run")]
    notifications = infrastructure.get_notifications(filters=filters)
    res = infrastructure.process_message({
        "module": "data_collect",
        "action": "set",
        "kind": "request",
        "data": {
            "agreed": True
        }
    })
    assert res == {
        u'action': u'set',
        u'data': {u'result': True},
        u'kind': u'reply',
        u'module': u'data_collect'
    }
    check_service_result("ucollect", True, "restart")
    wait_for_updater_run_finished(notifications, infrastructure)


def test_get_honeypots(infrastructure, ubusd_test):
    res = infrastructure.process_message({
        "module": "data_collect",
        "action": "get_honeypots",
        "kind": "request"
    })
    assert {"minipots", "log_credentials"} == set(res["data"].keys())


def test_set_honeypots(infrastructure, ubusd_test):
    filters = [("data_collect", "set_honeypots")]

    def set_honeypots(result):
        notifications = infrastructure.get_notifications(filters=filters)
        res = infrastructure.process_message({
            "module": "data_collect",
            "action": "set_honeypots",
            "kind": "request",
            "data": {
                "minipots": {
                    "23tcp": result,
                    "2323tcp": result,
                    "80tcp": result,
                    "3128tcp": result,
                    "8123tcp": result,
                    "8080tcp": result,
                },
                "log_credentials": result,
            }
        })
        assert res == {
            u'action': u'set_honeypots',
            u'data': {u'result': True},
            u'kind': u'reply',
            u'module': u'data_collect'
        }
        notifications = infrastructure.get_notifications(notifications, filters=filters)
        assert notifications[-1] == {
            u"module": u"data_collect",
            u"action": u"set_honeypots",
            u"kind": u"notification",
            u"data": {
                "minipots": {
                    "23tcp": result,
                    "2323tcp": result,
                    "80tcp": result,
                    "3128tcp": result,
                    "8123tcp": result,
                    "8080tcp": result,
                },
                "log_credentials": result,
            }
        }
        res = infrastructure.process_message({
            "module": "data_collect",
            "action": "get_honeypots",
            "kind": "request"
        })
        assert res == {
            u"module": u"data_collect",
            u"action": u"get_honeypots",
            u"kind": u"reply",
            u"data": {
                "minipots": {
                    "23tcp": result,
                    "2323tcp": result,
                    "80tcp": result,
                    "3128tcp": result,
                    "8123tcp": result,
                    "8080tcp": result,
                },
                "log_credentials": result,
            }
        }

    set_honeypots(True)
    set_honeypots(False)
    set_honeypots(True)
    set_honeypots(False)


@pytest.mark.only_backends(['openwrt'])
def test_set_honeypots_service_restart(
    uci_configs_init, init_script_result, infrastructure, ubusd_test
):
    res = infrastructure.process_message({
        "module": "data_collect",
        "action": "set_honeypots",
        "kind": "request",
        "data": {
            "minipots": {
                "23tcp": True,
                "2323tcp": False,
                "80tcp": True,
                "3128tcp": False,
                "8123tcp": True,
                "8080tcp": False,
            },
            "log_credentials": False,
        }
    })
    assert res == {
        u'action': u'set_honeypots',
        u'data': {u'result': True},
        u'kind': u'reply',
        u'module': u'data_collect'
    }
    check_service_result("ucollect", True, "restart")


@pytest.mark.only_backends(['openwrt'])
def test_set_agreed_uci(
    updater_userlists, uci_configs_init, lock_backend, init_script_result, infrastructure,
    ubusd_test
):
    uci = get_uci_module(lock_backend)

    res = infrastructure.process_message({
        "module": "data_collect",
        "action": "set",
        "kind": "request",
        "data": {
            "agreed": True
        }
    })
    assert res == {
        u'action': u'set',
        u'data': {u'result': True},
        u'kind': u'reply',
        u'module': u'data_collect'
    }
    with uci.UciBackend() as backend:
        data = backend.read()

    assert uci.parse_bool(uci.get_option_named(data, "foris", "eula", "agreed_collect", "0"))

    res = infrastructure.process_message({
        "module": "data_collect",
        "action": "set",
        "kind": "request",
        "data": {
            "agreed": False
        }
    })
    assert res == {
        u'action': u'set',
        u'data': {u'result': True},
        u'kind': u'reply',
        u'module': u'data_collect'
    }

    with uci.UciBackend() as backend:
        data = backend.read()

    assert not uci.parse_bool(uci.get_option_named(data, "foris", "eula", "agreed_collect", "0"))
