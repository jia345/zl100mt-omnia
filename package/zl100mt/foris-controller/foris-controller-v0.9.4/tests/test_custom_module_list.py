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

from foris_controller_testtools.fixtures import (
    only_message_buses, uci_configs_init, infrastructure
)


@pytest.fixture(scope="module")
def controller_modules():
    """ Overriding controller. This is a basically a test for test in which we check,
        whether test module filtering works properly
    """
    # enable only dns module
    return ["dns"]


@pytest.mark.only_message_buses(['unix-socket'])
def test_call_existing_and_non_existing(uci_configs_init, infrastructure):
    res = infrastructure.process_message({
        "module": "dns",
        "action": "get_settings",
        "kind": "request",
    })
    assert "errors" not in res["data"]

    res = infrastructure.process_message({
        "module": "web",
        "action": "get_data",
        "kind": "request",
    })
    assert "errors" in res["data"]
