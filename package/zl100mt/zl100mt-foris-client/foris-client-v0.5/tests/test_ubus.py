#
# foris-client
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
import random
import string
import ubus

from foris_client.buses.ubus import UbusSender
from foris_client.buses.base import ControllerError

from .fixtures import (
    ubusd_test, ubusd_test2, ubus_controller, ubus_client, UBUS_PATH, UBUS_PATH2, ubus_listener,
    ubus_notify
)


def test_about(ubusd_test, ubus_client):
    response = ubus_client.send("about", "get", None)
    assert isinstance(response, dict)
    assert "errors" not in response


def test_long_messages(ubusd_test, ubus_client):
    data = {
        "random_characters": "".join(
            random.choice(string.ascii_letters) for _ in range(1024 * 1024))
    }
    res = ubus_client.send("echo", "echo", {"request_msg": data})
    assert res == {"reply_msg": data}


def test_nonexisting_module(ubusd_test, ubus_client):
    with pytest.raises(RuntimeError):
        ubus_client.send("non-existing", "get", None)


def test_nonexisting_action(ubusd_test, ubus_client):
    with pytest.raises(RuntimeError):
        ubus_client.send("about", "non-existing", None)


def test_extra_data(ubusd_test, ubus_client):
    with pytest.raises(ControllerError):
        response = ubus_client.send("about", "get", {"extra": "data"})


def test_reconnect(ubusd_test, ubusd_test2):
    import logging
    logging.basicConfig()
    logging.disable(logging.ERROR)
    sender1 = UbusSender(UBUS_PATH)
    assert ubus.get_socket_path() == UBUS_PATH
    assert ubus.get_connected()
    UbusSender(UBUS_PATH2)
    assert ubus.get_socket_path() == UBUS_PATH2
    assert ubus.get_connected()
    sender1.disconnect()
    assert ubus.get_connected() is False


def test_timeout(ubusd_test, ubus_client):
    ubus_client.send("about", "get", None, timeout=1000)
    sender = UbusSender(UBUS_PATH, default_timeout=1000)
    sender.send("about", "get", None)


def test_notifications_request(ubusd_test, ubus_controller, ubus_listener, ubus_client):
    _, read_listener_output = ubus_listener

    old_data = read_listener_output()
    ubus_client.send("web", "set_language", {"language": "cs"})
    last = read_listener_output(old_data)[-1]
    assert last == {
        u'action': u'set_language',
        u'data': {u'language': u'cs'},
        u'kind': u'notification',
        u'module': u'web'
    }


def test_notifications_cmd(ubusd_test, ubus_listener, ubus_notify):
    _, read_listener_output = ubus_listener
    old_data = read_listener_output()
    ubus_notify.notify("test_module", "test_action", {"test_data": "test"})
    last = read_listener_output(old_data)[-1]
    assert last == {
        u'action': u'test_action',
        u'data': {u'test_data': u'test'},
        u'kind': u'notification',
        u'module': u'test_module',
    }
