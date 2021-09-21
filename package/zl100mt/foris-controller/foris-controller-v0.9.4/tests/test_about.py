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

from foris_controller_testtools.fixtures import infrastructure, ubusd_test, file_root_init

FILE_ROOT_PATH = os.path.join(os.path.dirname(os.path.realpath(__file__)), "test_about_files")


@pytest.mark.file_root_path(FILE_ROOT_PATH)
def test_get(infrastructure, ubusd_test):
    res = infrastructure.process_message({
        "module": "about",
        "action": "get",
        "kind": "request",
    })
    assert set(res.keys()) == {"action", "kind", "data", "module"}
    assert set(res["data"].keys()) == {
        u"model",
        u"board_name",
        u"serial",
        u"os_version",
        u"kernel",
        u"temperature",
        u"firewall_status",
        u"ucollect_status",
    }


@pytest.mark.file_root_path(FILE_ROOT_PATH)
def test_get_registration_number(infrastructure, ubusd_test):
    res = infrastructure.process_message({
        "module": "about",
        "action": "get_registration_number",
        "kind": "request",
    })
    assert set(res.keys()) == {"action", "kind", "data", "module"}
    assert set(res["data"].keys()) == {
            u"registration_number"
    }


@pytest.mark.file_root_path(FILE_ROOT_PATH)
def test_get_contract_status(infrastructure, ubusd_test):
    res = infrastructure.process_message({
        "module": "about",
        "action": "get_contract_status",
        "kind": "request",
    })
    assert set(res.keys()) == {"action", "kind", "data", "module"}
    assert set(res["data"].keys()) == {
            u"contract_status"
    }
    assert res["data"]["contract_status"] in ["valid", "not_valid", "unknown"]


@pytest.mark.file_root_path(FILE_ROOT_PATH)
def test_update_contract_status(infrastructure, ubusd_test):
    res = infrastructure.process_message({
        "module": "about",
        "action": "update_contract_status",
        "kind": "request",
    })
    assert res["data"] == {"result": True}
