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

from foris_client.buses.unix_socket import UnixSocketSender
from foris_client.buses.base import ControllerError

from .fixtures import unix_controller, unix_socket_client, SOCK_PATH, unix_listener, unix_notify


def test_about(unix_listener, unix_socket_client):
    response = unix_socket_client.send("about", "get", None)
    assert "errors" not in response


def test_long_messages(unix_listener, unix_socket_client):
    data = {
        "random_characters": "".join(
            random.choice(string.ascii_letters) for _ in range(1024 * 1024))
    }
    res = unix_socket_client.send("echo", "echo", {"request_msg": data})
    assert res == {"reply_msg": data}


def test_nonexisting_module(unix_listener, unix_socket_client):
    with pytest.raises(ControllerError):
        response = unix_socket_client.send("non-existing", "get", None)


def test_nonexisting_action(unix_listener, unix_socket_client):
    with pytest.raises(ControllerError):
        response = unix_socket_client.send("about", "non-existing", None)

def test_extra_data(unix_listener, unix_socket_client):
    with pytest.raises(ControllerError):
        response = unix_socket_client.send("about", "get", {})

def test_timeout(unix_listener, unix_socket_client):
    unix_socket_client.send("about", "get", None, timeout=1000)
    sender = UnixSocketSender(SOCK_PATH, default_timeout=1000)
    sender.send("about", "get", None)

def test_notifications_request(unix_listener, unix_socket_client):
    _, read_listener_output = unix_listener
    old_data = read_listener_output()
    unix_socket_client.send("web", "set_language", {"language": "cs"})
    last = read_listener_output(old_data)[-1]
    assert last == {
        u'action': u'set_language',
        u'data': {u'language': u'cs'},
        u'kind': u'notification',
        u'module': u'web'
     }


def test_notifications_cmd(unix_listener, unix_notify):
    _, read_listener_output = unix_listener
    old_data = read_listener_output()
    unix_notify.notify("test_module", "test_action", {"test_data": "test"})
    last = read_listener_output(old_data)[-1]
    assert last == {
        u'action': u'test_action',
        u'data': {u'test_data': u'test'},
        u'kind': u'notification',
        u'module': u'test_module',
    }
