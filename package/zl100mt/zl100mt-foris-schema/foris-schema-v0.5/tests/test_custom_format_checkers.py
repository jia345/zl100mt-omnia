# foris-schema
# Copyright (C) 2017 CZ.NIC, z.s.p.o. <http://www.nic.cz>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

import pytest

from jsonschema import ValidationError

from foris_schema import ForisValidator


@pytest.fixture(scope="module")
def validator():
    return ForisValidator(["tests/schemas/modules/custom_format_checkers/"])


def test_schema_load(validator):
    pass


def test_ipv4netmask(validator):
    passing = [
        "0.0.0.0",
        "255.0.0.0",
        "255.255.0.0",
        "255.255.255.0",
        "255.255.255.255",
    ]
    for item in passing:
        validator.validate({
            "module": "custom_format_checkers", "kind": "request", "action": "ipv4netmask",
            "data": {"item": item}
        })
    failing = [
        "192.168.1.1",
        "10.0.0.0",
        "0.0.0.255",
        None,
        0,
        1,
    ]
    for item in failing:
        with pytest.raises(ValidationError):
            validator.validate({
                "module": "custom_format_checkers", "kind": "request", "action": "ipv4netmask",
                "data": {"item": item}
            })


def test_ipv4prefix(validator):
    passing = [
        "192.168.1.1/32",
        "192.168.1.1/0",
    ]
    failing = [
        "192.168.1.1",
        "::/128",
        "192.168.1.1/33",
        None,
        0,
        1,
    ]
    for item in passing:
        validator.validate({
            "module": "custom_format_checkers", "kind": "request", "action": "ipv4prefix",
            "data": {"item": item}
        })

    for item in failing:
        with pytest.raises(ValidationError):
            validator.validate({
                "module": "custom_format_checkers", "kind": "request", "action": "ipv4prefix",
                "data": {"item": item}
            })


def test_ipv6prefix(validator):
    passing = [
        "::/128",
        "::/0",
        "::1/64",
    ]
    failing = [
        "192.168.1.1/32",
        "192.168.1.1/0",
        "192.168.1.1",
        "192.168.1.1/33",
        "x::/64",
        "::/-1",
        "::1",
        None,
        0,
        1,
    ]

    for item in passing:
        validator.validate({
            "module": "custom_format_checkers", "kind": "request", "action": "ipv6prefix",
            "data": {"item": item}
        })

    for item in failing:
        with pytest.raises(ValidationError):
            validator.validate({
                "module": "custom_format_checkers", "kind": "request", "action": "ipv6prefix",
                "data": {"item": item}
            })


def test_macaddress(validator):
    passing = [
        "d8:9e:f3:73:05:9c",
    ]
    failing = [
        "d8:9e:f3:g3:05:9c",
        "d8:9e:f3:73:05",
        "d8-9e-f3-73-05-9c",
        "d8:9e:f3:73:05:9c:11",
        None,
        0,
        1,
    ]

    for item in passing:
        validator.validate({
            "module": "custom_format_checkers", "kind": "request", "action": "macaddress",
            "data": {"item": item}
        })

    for item in failing:
        with pytest.raises(ValidationError):
            validator.validate({
                "module": "custom_format_checkers", "kind": "request", "action": "macaddress",
                "data": {"item": item}
            })
