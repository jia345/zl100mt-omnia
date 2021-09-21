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

import json
import os
import pytest
import subprocess

from foris_schema import ForisValidator

from foris_controller.utils import get_validator_dirs

from foris_controller_testtools.fixtures import uci_configs_init, infrastructure, ubusd_test


@pytest.fixture(scope="module")
def extra_module_paths():
    """ Override of extra module paths fixture
    """
    return [
        os.path.join(os.path.dirname(os.path.realpath(__file__)), "test_modules", "echo")
    ]

def notify_cmd(infras, module, action, data, validate=True):
    args = [
        "bin/foris-notify", "-m", module, "-a", action,
        infras.name, "--path", infras.notification_sock_path, json.dumps(data)
    ]
    if not validate:
        args.insert(1, "-n")
    process = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()
    return process.returncode, stdout, stderr


@pytest.fixture(scope="module")
def notify_api(extra_module_paths, infrastructure):
    if infrastructure.name == "ubus":
        from foris_controller.buses.ubus import UbusNotificationSender
        sender = UbusNotificationSender(infrastructure.notification_sock_path)

    elif infrastructure.name == "unix-socket":
        from foris_controller.buses.unix_socket import UnixSocketNotificationSender
        sender = UnixSocketNotificationSender(infrastructure.notification_sock_path)

    def notify(module, action, notification=None, validate=True):
        if validate:
            validator = ForisValidator(*get_validator_dirs([module], extra_module_paths))
        else:
            validator = None
        sender.notify(module, action, notification, validator)

    yield notify
    sender.disconnect()


def test_notify_cmd(uci_configs_init, infrastructure, ubusd_test):
    filters = [("web", "set_language")]
    notifications = infrastructure.get_notifications(filters=filters)
    retval, stdout, stderr = notify_cmd(
        infrastructure, "web", "set_language", {"language": "en"}, True)
    assert retval == 0

    notifications = infrastructure.get_notifications(notifications, filters=filters)
    assert notifications[-1] == {
        u"module": u"web",
        u"action": u"set_language",
        u"kind": u"notification",
        u"data": {u"language": u"en"},
    }

    retval, stdout, stderr = notify_cmd(
        infrastructure, "web", "set_language", {"language": "en", "invalid": True}, True)
    assert retval == 1
    assert u"ValidationError" in stderr
    assert notifications == infrastructure.get_notifications(filters=filters)

    retval, stdout, stderr = notify_cmd(
        infrastructure, "web", "set_language", {"language": "en", "invalid": True}, False)
    assert retval == 0

    notifications = infrastructure.get_notifications(notifications, filters=filters)
    assert notifications[-1] == {
        u"module": u"web",
        u"action": u"set_language",
        u"kind": u"notification",
        u"data": {u"language": u"en", u"invalid": True},
    }


def test_notify_api(uci_configs_init, infrastructure, ubusd_test, notify_api):
    filters = [("web", "set_language"), ("echo", "echo")]
    notify = notify_api
    notifications = infrastructure.get_notifications(filters=filters)
    notify("web", "set_language", {"language": "en"}, True)
    notifications = infrastructure.get_notifications(notifications, filters=filters)
    assert notifications[-1] == {
        u"module": u"web",
        u"action": u"set_language",
        u"kind": u"notification",
        u"data": {u"language": u"en"},
    }

    from jsonschema import ValidationError
    with pytest.raises(ValidationError):
        notify("web", "set_language", {"language": "en", "invalid": True}, True)
    assert notifications == infrastructure.get_notifications(filters=filters)

    notify("web", "set_language", {"language": "en", "invalid": True}, False)
    notifications = infrastructure.get_notifications(notifications, filters=filters)
    assert notifications[-1] == {
        u"module": u"web",
        u"action": u"set_language",
        u"kind": u"notification",
        u"data": {u"language": u"en", u"invalid": True},
    }

    notify("echo", "echo")
    notifications = infrastructure.get_notifications(notifications, filters=filters)
    assert notifications[-1] == {
        u"module": u"echo",
        u"action": u"echo",
        u"kind": u"notification",
    }
