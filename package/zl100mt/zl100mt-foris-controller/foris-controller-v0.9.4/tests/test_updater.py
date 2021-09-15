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
import uuid
import time

from datetime import datetime

from foris_controller.exceptions import UciRecordNotFound

from foris_controller_testtools.fixtures import (
    only_backends, uci_configs_init, infrastructure, ubusd_test, lock_backend,
    clean_reboot_indicator, updater_languages, updater_userlists
)
from foris_controller_testtools.utils import set_approval, get_uci_module


def wait_for_updater_run_finished(notifications, infrastructure):
    filters = [("updater", "run")]
    # filter notifications
    notifications = [
        e for e in notifications if e["module"] == "updater" and e["action"] == "run"
    ]

    def notification_status_count(notifications, name):
        return len([
            e for e in notifications
            if e["module"] == "updater" and e["action"] == "run" and e["data"]["status"] == name
        ])
    # the count of updater run has to be increased
    before_count = notification_status_count(notifications, "initialize")

    # and instances should finish
    notifications = infrastructure.get_notifications(notifications, filters=filters)
    initialize_count = notification_status_count(notifications, "initialize")
    exit_count = notification_status_count(notifications, "exit")
    while before_count == initialize_count or initialize_count > exit_count:
        notifications = infrastructure.get_notifications(notifications, filters=filters)
        initialize_count = notification_status_count(notifications, "initialize")
        exit_count = notification_status_count(notifications, "exit")


def test_get_settings(
    updater_languages, updater_userlists, uci_configs_init, infrastructure, ubusd_test
):
    def get(lang):
        res = infrastructure.process_message({
            "module": "updater",
            "action": "get_settings",
            "kind": "request",
            "data": {"lang": lang},
        })
        assert set(res.keys()) == {"action", "kind", "data", "module"}
        assert "enabled" in res["data"].keys()
        assert "languages" in res["data"].keys()
        assert {"enabled", "code"} == set(res["data"]["languages"][0].keys())
        assert "user_lists" in res["data"].keys()
        assert {"enabled", "name", "title", "msg", "hidden"} == \
            set(res["data"]["user_lists"][0].keys())
        assert "approval_settings" in res["data"].keys()
        assert "status" in res["data"]["approval_settings"].keys()
        assert "branch" in res["data"].keys()
        assert "approval" in res["data"].keys()

    get("en")
    get("cs")
    get("de")
    get("xx")


def test_update_settings(
    updater_languages, updater_userlists,
    uci_configs_init, infrastructure, ubusd_test
):

    def update_settings(new_settings, expected=None):
        res = infrastructure.process_message({
            "module": "updater",
            "action": "update_settings",
            "kind": "request",
            "data": new_settings,
        })
        assert "result" in res["data"] and res["data"]["result"] is True
        res = infrastructure.process_message({
            "module": "updater",
            "action": "get_settings",
            "kind": "request",
            "data": {"lang": "en"}
        })

        new_settings = expected if expected else new_settings
        del res["data"]["approval"]
        list_data = res["data"].pop("user_lists")
        assert set(new_settings["user_lists"]) == {e["name"] for e in list_data if e["enabled"]}
        lang_data = res["data"].pop("languages")
        assert set(new_settings["languages"]) == {e["code"] for e in lang_data if e["enabled"]}

        del new_settings["user_lists"]
        del new_settings["languages"]
        assert res["data"] == new_settings

    update_settings({
        "enabled": True,
        "branch": "",
        "approval_settings": {"status": "off"},
        "user_lists": [],
        "languages": [],
    })

    update_settings({
        "enabled": True,
        "branch": "nightly",
        "approval_settings": {"status": "on"},
        "user_lists": ['api-token'],
        "languages": ['cs'],
    })

    update_settings({
        "enabled": True,
        "branch": "",
        "approval_settings": {"status": "delayed", "delay": 24},
        "user_lists": ['dvb'],
        "languages": ['cs', 'de'],
    })

    update_settings({
        "enabled": True,
        "branch": "",
        "approval_settings": {"status": "off"},
        "user_lists": [],
        "languages": [],
    })

    update_settings({
        "enabled": False,
    }, {
        "enabled": False,
        "branch": "",
        "approval_settings": {"status": "off"},
        "user_lists": [],
        "languages": [],
    })


@pytest.mark.only_backends(['openwrt'])
def test_update_settings_openwrt(
    updater_languages, updater_userlists, uci_configs_init, infrastructure, ubusd_test
):
    filters = [("updater", "run")]
    notifications = infrastructure.get_notifications(filters=filters)
    res = infrastructure.process_message({
        "module": "updater",
        "action": "update_settings",
        "kind": "request",
        "data": {
            "enabled": True,
            "branch": "",
            "approval_settings": {"status": "off"},
            "user_lists": [],
            "languages": [],
        },
    })
    assert res["data"]["result"]
    wait_for_updater_run_finished(notifications, infrastructure)


@pytest.mark.only_backends(['openwrt'])
def test_uci(
    updater_languages, updater_userlists, uci_configs_init, lock_backend, infrastructure, ubusd_test
):

    uci = get_uci_module(lock_backend)

    def update_settings(new_settings):
        res = infrastructure.process_message({
            "module": "updater",
            "action": "update_settings",
            "kind": "request",
            "data": new_settings,
        })
        assert "result" in res["data"] and res["data"]["result"] is True

    update_settings({
        "enabled": True,
        "branch": "",
        "approval_settings": {"status": "off"},
        "user_lists": [],
        "languages": [],
    })
    with uci.UciBackend() as backend:
        data = backend.read("updater")
    assert not uci.parse_bool(uci.get_option_named(data, "updater", "override", "disable"))
    with pytest.raises(UciRecordNotFound):
        uci.get_option_named(data, "updater", "override", "branch")
    with pytest.raises(UciRecordNotFound):
        uci.get_option_named(data, "updater", "approvals", "auto_grant_seconds")
    assert not uci.parse_bool(uci.get_option_named(data, "updater", "approvals", "need"))

    update_settings({
        "enabled": True,
        "branch": "nightly",
        "approval_settings": {"status": "on"},
        "user_lists": ['list1'],
        "languages": ['cs'],
    })
    with uci.UciBackend() as backend:
        data = backend.read("updater")
    assert not uci.parse_bool(uci.get_option_named(data, "updater", "override", "disable"))
    assert uci.get_option_named(data, "updater", "override", "branch") == "nightly"
    with pytest.raises(UciRecordNotFound):
        uci.get_option_named(data, "updater", "approvals", "auto_grant_seconds")
    assert uci.parse_bool(uci.get_option_named(data, "updater", "approvals", "need"))

    update_settings({
        "enabled": True,
        "branch": "",
        "approval_settings": {"status": "delayed", "delay": 24},
        "user_lists": ['list2'],
        "languages": ['cs', 'de'],
    })
    with uci.UciBackend() as backend:
        data = backend.read("updater")
    assert not uci.parse_bool(uci.get_option_named(data, "updater", "override", "disable"))
    with pytest.raises(UciRecordNotFound):
        uci.get_option_named(data, "updater", "override", "branch")
    assert int(uci.get_option_named(data, "updater", "approvals", "auto_grant_seconds")) \
        == 24 * 60 * 60
    assert uci.parse_bool(uci.get_option_named(data, "updater", "approvals", "need"))

    update_settings({
        "enabled": True,
        "branch": "",
        "approval_settings": {"status": "off"},
        "user_lists": [],
        "languages": [],
    })
    with uci.UciBackend() as backend:
        data = backend.read("updater")
    assert not uci.parse_bool(uci.get_option_named(data, "updater", "override", "disable"))
    with pytest.raises(UciRecordNotFound):
        uci.get_option_named(data, "updater", "override", "branch")
    with pytest.raises(UciRecordNotFound):
        uci.get_option_named(data, "updater", "approvals", "auto_grant_seconds")
    assert not uci.parse_bool(uci.get_option_named(data, "updater", "approvals", "need"))

    update_settings({
        "enabled": False,
    })
    with uci.UciBackend() as backend:
        data = backend.read("updater")
    assert uci.parse_bool(uci.get_option_named(data, "updater", "override", "disable"))


@pytest.mark.only_backends(['openwrt'])
def test_approval(
    updater_languages, updater_userlists, uci_configs_init, infrastructure, ubusd_test
):
    def approval(data):
        set_approval(data)
        res = infrastructure.process_message({
            "module": "updater",
            "action": "get_settings",
            "kind": "request",
            "data": {"lang": "en"},
        })
        approval = res["data"]["approval"]
        if data:
            data["present"] = True
            data["time"] = datetime.fromtimestamp(data["time"]).isoformat()
            for record in data["plan"]:
                if record["new_ver"] is None:
                    del record["new_ver"]
                if record["cur_ver"] is None:
                    del record["cur_ver"]
            assert data == approval
        else:
            assert approval == {"present": False}

    approval(None)
    approval({
        "hash": str(uuid.uuid4()),
        "status": "asked",
        "time": int(time.time()),
        "plan": [],
        "reboot": False,
    })
    approval({
        "hash": str(uuid.uuid4()),
        "status": "granted",
        "time": int(time.time()),
        "plan": [
            {"name": "package1", "op": "install", "cur_ver": None, "new_ver": "1.0"},
            {"name": "package2", "op": "remove", "cur_ver": "2.0", "new_ver": None},
        ],
        "reboot": True,
    })
    approval({
        "hash": str(uuid.uuid4()),
        "status": "denied",
        "time": int(time.time()),
        "plan": [
            {"name": "package3", "op": "upgrade", "cur_ver": "1.0", "new_ver": "1.1"},
            {"name": "package4", "op": "downgrade", "cur_ver": "2.1", "new_ver": "2.0"},
            {"name": "package5", "op": "remove", "cur_ver": None, "new_ver": None},
            {"name": "package6", "op": "upgrade", "cur_ver": None, "new_ver": "1.1"},
            {"name": "package7", "op": "downgrade", "cur_ver": None, "new_ver": "2.0"},
        ],
        "reboot": True,
    })


def test_approval_resolve(
    updater_languages, updater_userlists, uci_configs_init, infrastructure, ubusd_test
):
    res = infrastructure.process_message({
        "module": "updater",
        "action": "resolve_approval",
        "kind": "request",
        "data": {
            "hash": str(uuid.uuid4()),
            "solution": "grant",
        }
    })
    assert set(res.keys()) == {"action", "kind", "data", "module"}
    assert "result" in res["data"].keys()

    res = infrastructure.process_message({
        "module": "updater",
        "action": "resolve_approval",
        "kind": "request",
        "data": {
            "hash": str(uuid.uuid4()),
            "solution": "deny",
        }
    })
    assert set(res.keys()) == {"action", "kind", "data", "module"}
    assert "result" in res["data"].keys()


@pytest.mark.only_backends(['openwrt'])
def test_approval_resolve_openwrt(
    updater_languages, updater_userlists, uci_configs_init, infrastructure, ubusd_test
):
    filters = [("updater", "run")]

    def resolve(approval_data, query_data, result):
        set_approval(approval_data)
        notifications = infrastructure.get_notifications(filters=filters)
        res = infrastructure.process_message({
            "module": "updater",
            "action": "resolve_approval",
            "kind": "request",
            "data": query_data,
        })
        assert res["data"]["result"] == result
        if res["data"]["result"]:
            res = infrastructure.process_message({
                "module": "updater",
                "action": "get_settings",
                "kind": "request",
                "data": {"lang": "en"},
            })
            approval = res["data"]["approval"]
            if query_data["solution"] == "deny":
                assert approval["status"] == "denied"
            elif query_data["solution"] == "grant":
                assert approval["status"] == "granted"
                wait_for_updater_run_finished(notifications, infrastructure)

    # No approval
    set_approval(None)
    resolve(None, {"hash": str(uuid.uuid4()), "solution": "grant"}, False)
    resolve(None, {"hash": str(uuid.uuid4()), "solution": "deny"}, False)

    # Other approval
    resolve(
        {
            "hash": str(uuid.uuid4()),
            "status": "asked",
            "time": int(time.time()),
            "plan": [],
            "reboot": False,
        },
        {"hash": str(uuid.uuid4()), "solution": "grant"},
        False
    )
    resolve(
        {
            "hash": str(uuid.uuid4()),
            "status": "asked",
            "time": int(time.time()),
            "plan": [],
            "reboot": False,
        },
        {"hash": str(uuid.uuid4()), "solution": "deny"},
        False
    )

    # Incorrect status
    approval_id = str(uuid.uuid4())
    resolve(
        {
            "hash": approval_id,
            "status": "granted",
            "time": int(time.time()),
            "plan": [],
            "reboot": False,
        },
        {"hash": approval_id, "solution": "grant"},
        False
    )
    resolve(
        {
            "hash": approval_id,
            "status": "denied",
            "time": int(time.time()),
            "plan": [],
            "reboot": False,
        },
        {"hash": approval_id, "solution": "deny"},
        False
    )

    # Passed
    approval_id = str(uuid.uuid4())
    resolve(
        {
            "hash": approval_id,
            "status": "asked",
            "time": int(time.time()),
            "plan": [],
            "reboot": False,
        },
        {"hash": approval_id, "solution": "grant"},
        True
    )
    resolve(
        {
            "hash": approval_id,
            "status": "asked",
            "time": int(time.time()),
            "plan": [],
            "reboot": False,
        },
        {"hash": approval_id, "solution": "deny"},
        True
    )
    resolve(
        {
            "hash": approval_id,
            "status": "denied",
            "time": int(time.time()),
            "plan": [],
            "reboot": False,
        },
        {"hash": approval_id, "solution": "grant"},
        True
    )


def test_run(uci_configs_init, infrastructure, ubusd_test):
    res = infrastructure.process_message({
        "module": "updater",
        "action": "run",
        "kind": "request",
        "data": {"set_reboot_indicator": True},
    })
    assert res == {
        "module": "updater",
        "action": "run",
        "kind": "reply",
        "data": {"result": True},
    }
    res = infrastructure.process_message({
        "module": "updater",
        "action": "run",
        "kind": "request",
        "data": {"set_reboot_indicator": False},
    })
    assert res == {
        "module": "updater",
        "action": "run",
        "kind": "reply",
        "data": {"result": True},
    }


@pytest.mark.only_backends(['openwrt'])
def test_run_notifications(uci_configs_init, infrastructure, ubusd_test):
    filters = [("updater", "run")]
    try:
        os.unlink(clean_reboot_indicator)
    except Exception:
        pass

    notifications = infrastructure.get_notifications(filters=filters)
    res = infrastructure.process_message({
        "module": "updater",
        "action": "run",
        "kind": "request",
        "data": {"set_reboot_indicator": False},
    })
    assert res["data"]["result"]
    wait_for_updater_run_finished(notifications, infrastructure)

    notifications = infrastructure.get_notifications(notifications, filters=filters)
    res = infrastructure.process_message({
        "module": "updater",
        "action": "run",
        "kind": "request",
        "data": {"set_reboot_indicator": True},
    })
    assert res["data"]["result"]
    wait_for_updater_run_finished(notifications, infrastructure)


def test_get_enabled(
    updater_languages, updater_userlists,
    uci_configs_init, infrastructure, ubusd_test
):

    res = infrastructure.process_message({
        "module": "updater",
        "action": "update_settings",
        "kind": "request",
        "data": {
            "enabled": True,
            "branch": "",
            "approval_settings": {"status": "off"},
            "user_lists": [],
            "languages": [],
        },
    })
    assert res["data"]["result"]

    res = infrastructure.process_message({
        "module": "updater",
        "action": "get_enabled",
        "kind": "request",
    })
    assert res["data"]["enabled"] is True

    res = infrastructure.process_message({
        "module": "updater",
        "action": "update_settings",
        "kind": "request",
        "data": {
            "enabled": False,
        },
    })
    assert res["data"]["result"]

    res = infrastructure.process_message({
        "module": "updater",
        "action": "get_enabled",
        "kind": "request",
    })
    assert res["data"]["enabled"] is False
