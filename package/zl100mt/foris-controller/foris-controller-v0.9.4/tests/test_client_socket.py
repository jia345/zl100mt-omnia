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

import os
import pytest


from foris_controller_testtools.fixtures import infrastructure, ubusd_test


@pytest.fixture(scope="module")
def extra_module_paths():
    """ Override of extra module paths fixture
    """
    return [
        os.path.join(os.path.dirname(os.path.realpath(__file__)), "test_modules", "echo")
    ]


def test_request(infrastructure, ubusd_test):
    def request(req, reply):
        res = infrastructure.client_socket.request(req)
        assert res == reply

    request({
        "module": "echo",
        "action": "echo",
        "kind": "request",
        "data": {"request_msg": {"text": "testmsg1"}}
    }, {
        "module": "echo",
        "action": "echo",
        "kind": "reply",
        "data": {"reply_msg": {"text": "testmsg1"}}
    })

    request({
        "module": "echo",
        "action": "echo",
        "kind": "request",
        "data": {"request_msg": {"text": "testmsg2"}}
    }, {
        "module": "echo",
        "action": "echo",
        "kind": "reply",
        "data": {"reply_msg": {"text": "testmsg2"}}
    })


def test_request_error(infrastructure, ubusd_test):
    def request_error(req):
        with pytest.raises(Exception):
            # raises exception due to the connection is closed (socket.read(4) returns "")
            infrastructure.client_socket.request(req)

        # reconnect after
        infrastructure.client_socket.close()
        infrastructure.client_socket.connect()

    request_error({
        "module": "echox",
        "action": "echo",
        "kind": "request",
        "data": {"request_msg": {"text": "testmsg1"}}
    })
    request_error({
        "module": "echo",
        "action": "echox",
        "kind": "request",
        "data": {"request_msg": {"text": "testmsg1"}}
    })
    request_error({
        "module": "echo",
        "action": "echo",
        "kind": "requestx",
        "data": {"request_msg": {"text": "testmsg1"}}
    })
    request_error({
        "module": "echo",
        "action": "echo",
        "kind": "request",
        "data": {"request_msgx": {"text": "testmsg1"}}
    })
    request_error({
        "module": "echo",
        "action": "echo",
        "kind": "request",
    })


def test_notification(infrastructure, ubusd_test):
    def notify(msg):
        filters = [("echo", "echo"), ("echo", "echo2")]
        notifications = infrastructure.get_notifications(filters=filters)
        infrastructure.client_socket.notification(msg)
        notifications = infrastructure.get_notifications(notifications, filters=filters)
        assert notifications[-1] == msg

    notify({
        "module": "echo",
        "action": "echo",
        "kind": "notification",
    })

    notify({
        "module": "echo",
        "action": "echo2",
        "kind": "notification",
        "data": {"msg": "notification text"}
    })


def test_notification_error(infrastructure, ubusd_test):
    def notify_error(msg):
        # send msg and one correct notification and make sure that only the correct
        # notification is recievd
        filters = [("echo", "echo"), ("echo", "echo2")]
        notifications = infrastructure.get_notifications(filters=filters)
        old_len = len(notifications)
        infrastructure.client_socket.notification(msg)
        infrastructure.client_socket.close()
        infrastructure.client_socket.connect()
        infrastructure.client_socket.notification({
            "module": "echo",
            "action": "echo",
            "kind": "notification",
        })
        notifications = infrastructure.get_notifications(notifications, filters=filters)
        assert old_len + 1 == len(notifications)
        assert notifications[-1] == {
            "module": "echo",
            "action": "echo",
            "kind": "notification",
        }

    notify_error({
        "module": "echo",
        "action": "echox",
        "kind": "notification",
    })
    notify_error({
        "module": "echox",
        "action": "echo",
        "kind": "notification",
    })
    notify_error({
        "module": "echo",
        "action": "echo",
        "kind": "notification",
        "data": {},
    })
    notify_error({
        "module": "echo",
        "action": "echo2",
        "kind": "notification",
        "data": {"msgx": "dafdafda"},
    })
