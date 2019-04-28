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


import base64
import os
import pytest
import random
import string

from foris_controller_testtools.fixtures import (
    uci_configs_init, infrastructure, ubusd_test, only_backends
)

PASS_PATH = "/tmp/passwd_input"

@pytest.fixture
def pass_file():
    try:
        os.unlink(PASS_PATH)
    except:
        pass

    yield PASS_PATH

    try:
        os.unlink(PASS_PATH)
    except:
        pass


def test_set_and_check_system(uci_configs_init, pass_file, infrastructure, ubusd_test):
    filters = [("password", "set")]
    new_pass = "".join(random.choice(string.ascii_letters) for _ in range(20))
    old_notifications = infrastructure.get_notifications(filters=filters)
    res = infrastructure.process_message({
        "module": "password",
        "action": "set",
        "kind": "request",
        "data": {"password": base64.b64encode(new_pass), "type": "system"},
    })
    assert res == {
        u'action': u'set',
        u'data': {u'result': True},
        u'kind': u'reply',
        u'module': u'password'
    }
    assert infrastructure.get_notifications(old_notifications, filters=filters)[-1] == {
        u"module": u"password",
        u"action": u"set",
        u"kind": u"notification",
        u"data": {
            u"type": u"system"
        }
    }
    res = infrastructure.process_message({
        "module": "password",
        "action": "check",
        "kind": "request",
        "data": {"password": base64.b64encode(new_pass)},
    })
    assert res["data"]["status"] != u"good"


def test_set_and_check_foris(uci_configs_init, pass_file, infrastructure, ubusd_test):
    filters = [("password", "set")]
    new_pass = "".join(random.choice(string.ascii_letters) for _ in range(20))
    old_notifications = infrastructure.get_notifications(filters=filters)
    res = infrastructure.process_message({
        "module": "password",
        "action": "set",
        "kind": "request",
        "data": {"password": base64.b64encode(new_pass), "type": "foris"},
    })
    assert res == {
        u'action': u'set',
        u'data': {u'result': True},
        u'kind': u'reply',
        u'module': u'password'
    }
    assert infrastructure.get_notifications(old_notifications, filters=filters)[-1] == {
        u"module": u"password",
        u"action": u"set",
        u"kind": u"notification",
        u"data": {
            u"type": u"foris"
        }
    }
    res = infrastructure.process_message({
        "module": "password",
        "action": "check",
        "kind": "request",
        "data": {"password": base64.b64encode(new_pass)},
    })
    assert res == {
        u'action': u'check',
        u'data': {u'status': u"good"},
        u'kind': u'reply',
        u'module': u'password'
    }



@pytest.mark.only_backends(['openwrt'])
def test_passowrd_openwrt(uci_configs_init, pass_file, infrastructure, ubusd_test):
    new_pass = "".join(random.choice(string.ascii_letters) for _ in range(20))
    res = infrastructure.process_message({
        "module": "password",
        "action": "set",
        "kind": "request",
        "data": {"password": base64.b64encode(new_pass), "type": "system"},
    })
    assert res == {
        u'action': u'set',
        u'data': {u'result': True},
        u'kind': u'reply',
        u'module': u'password'
    }
    with open(pass_file) as f:
        assert f.read() == ("%(password)s\n%(password)s\n" % dict(password=new_pass))
