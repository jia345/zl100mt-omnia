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

from foris_controller_testtools.fixtures import only_message_buses, infrastructure, ubusd_test


def test_wrong_input_data(infrastructure, ubusd_test):
    res = infrastructure.process_message({
        "module": "about",
        "action": "get",
        "kind": "request",
        "data": {"extra": "data"},
    })
    assert res["action"] == u"get"
    assert res["kind"] == u"reply"
    assert res["module"] == u"about"
    assert "errors" in res["data"]
    assert "Incorrect input." in res["data"]["errors"][0]["description"]


@pytest.mark.only_message_buses(['unix-socket'])
def test_wrong_input_kind(infrastructure, ubusd_test):
    res = infrastructure.process_message({
        "module": "about",
        "action": "get",
        "kind": "reply",
        "data": {
            "model": "Turris Omnia",
            "board_name": "rtrom01",
            "kernel": "4.4.77-967673b9d511e4292e3bcb76c9e064bc-0",
            "os_version": "3.7",
            "serial": "0000000B00009CD6",
            "temperature": {"CPU": 73},
            "firewall_status": {"state": "online", "last_check": 1501857960},
            "ucollect_status": {"state": "offline", "last_check": 1501857970},
        },
    })
    assert res == {
            u'action': u'get',
            u'data': {
                u'errors': [{
                    u'description': u'Wrong message kind (only request are allowed).'
                }]
            },
            u'kind': u'reply',
            u'module': u'about'
    }

@pytest.mark.only_message_buses(['unix-socket'])
def test_wrong_input_action(infrastructure, ubusd_test):
    res = infrastructure.process_message({
        "module": "about",
        "action": "non-exiting",
        "kind": "request",
    })
    assert res["action"] == u"non-exiting"
    assert res["kind"] == u"reply"
    assert res["module"] == u"about"
    assert "errors" in res["data"]
    assert "Incorrect input." in res["data"]["errors"][0]["description"]


@pytest.mark.only_message_buses(['unix-socket'])
def test_wrong_input_module(infrastructure, ubusd_test):
    res = infrastructure.process_message({
        "module": "non-exiting",
        "action": "get",
        "kind": "request",
    })
    assert res["action"] == u"get"
    assert res["kind"] == u"reply"
    assert res["module"] == u"non-exiting"
    assert "errors" in res["data"]
    assert "Incorrect input." in res["data"]["errors"][0]["description"]
