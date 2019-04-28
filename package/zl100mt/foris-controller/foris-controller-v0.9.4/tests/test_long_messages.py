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
import random
import string
import uuid

from foris_controller_testtools.fixtures import only_message_buses, infrastructure, ubusd_test


@pytest.fixture(scope="module")
def extra_module_paths():
    """ Override of extra module paths fixture
    """
    return [
        os.path.join(os.path.dirname(os.path.realpath(__file__)), "test_modules", "echo")
    ]


@pytest.mark.parametrize("chars_len", (1024, 1024 * 1024, 10 * 1024 * 1024))
def test_long_messsages(infrastructure, ubusd_test, chars_len):
    data = {
        "random_characters": "".join(random.choice(string.ascii_letters) for _ in range(chars_len))
    }
    res = infrastructure.process_message({
        "module": "echo",
        "action": "echo",
        "kind": "request",
        "data": {"request_msg": data}
    })
    assert res["data"]["reply_msg"] == data


@pytest.mark.only_message_buses(['ubus'])
def test_ubus_malformed_multipart_resend(infrastructure, ubusd_test):
    # First lets test whether the multipart is working
    request_id = str(uuid.uuid4())
    res = infrastructure.process_message_ubus_raw(
        data={"action": "echo", "kind": "request", "module": "echo", "data": {}},
        request_id=request_id,
        multipart=True,
        multipart_data='{',
        final=False,
    )
    assert res is None
    res = infrastructure.process_message_ubus_raw(
        data={"action": "echo", "kind": "request", "module": "echo", "data": {}},
        request_id=request_id,
        multipart=True,
        multipart_data='"request_msg": {"xx": "yy"}}',
        final=True,
    )
    assert res == {
        "module": "echo",
        "action": "echo",
        "kind": "reply",
        "data": {"reply_msg": {"xx": "yy"}}
    }

    # resend last message
    res = infrastructure.process_message_ubus_raw(
        data={"action": "echo", "kind": "request", "module": "echo", "data": {}},
        request_id=request_id,
        multipart=True,
        multipart_data='"request_msg": {"xx": "yy"}}',
        final=True,
    )
    assert res == {
        u'action': u'echo',
        u'data': {
            u'errors': [{u'description': u'failed to parse multipart', u'stacktrace': u''}]
        },
        u'kind': u'reply',
        u'module': u'echo'
    }


@pytest.mark.only_message_buses(['ubus'])
def test_ubus_malformed_multipart_one(infrastructure, ubusd_test):
    # resend wrong json in one multipart
    request_id = str(uuid.uuid4())
    res = infrastructure.process_message_ubus_raw(
        data={"action": "echo", "kind": "request", "module": "echo", "data": {}},
        request_id=request_id,
        multipart=True,
        multipart_data='"request_msg": {"xx": "yy"',
        final=True,
    )
    assert res == {
        u'action': u'echo',
        u'data': {
            u'errors': [{u'description': u'failed to parse multipart', u'stacktrace': u''}]
        },
        u'kind': u'reply',
        u'module': u'echo'
    }


@pytest.mark.only_message_buses(['ubus'])
def test_ubus_malformed_multipart_two(infrastructure, ubusd_test):
    # resend wrong json in two multiparts
    request_id = str(uuid.uuid4())
    res = infrastructure.process_message_ubus_raw(
        data={"action": "echo", "kind": "request", "module": "echo", "data": {}},
        request_id=request_id,
        multipart=True,
        multipart_data='{',
        final=False,
    )
    assert res is None
    res = infrastructure.process_message_ubus_raw(
        data={"action": "echo", "kind": "request", "module": "echo", "data": {}},
        request_id=request_id,
        multipart=True,
        multipart_data='"request_msg": {"xx": "yy"}}_wrong',
        final=True,
    )

    assert res == {
        u'action': u'echo',
        u'data': {
            u'errors': [{u'description': u'failed to parse multipart', u'stacktrace': u''}]
        },
        u'kind': u'reply',
        u'module': u'echo'
    }
