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

import itertools

from foris_controller.utils import IPv4

WRONG_IPS = [
    "1.1.1.1.1",
    "255.255.255",
    "1.1.1.256",
    "x1.1.1.1",
]

WRONG_NUMBERS = [
    -1,
    2**32,
]

WRONG_NETMASKS = [
    "255.255.254.255",
    "255.255.255.253",
    "255.255.253.0",
    "255.253.0.0",
    "253.0.0.0",
]


WRONG_PREFIXES= [
    -1,
    33,
]


def test_str_to_num():
    assert IPv4.str_to_num("0.0.0.0") == 0
    assert IPv4.str_to_num("255.255.255.255") == (2 ** 32) - 1

    for s in WRONG_IPS:
        with pytest.raises(ValueError):
            IPv4.str_to_num(s)


def test_num_to_str():
    assert "0.0.0.0" == IPv4.num_to_str(0)
    assert "255.255.255.255" == IPv4.num_to_str((2 ** 32) - 1)

    for s in WRONG_NUMBERS:
        with pytest.raises(ValueError):
            IPv4.num_to_str(s)


def test_normalize_subnet():
    assert "192.168.1.0" == IPv4.normalize_subnet("192.168.1.1", "255.255.255.0")
    assert "10.1.0.0" == IPv4.normalize_subnet("10.1.0.0", "255.255.0.0")
    assert "0.0.0.0" == IPv4.normalize_subnet("255.255.255.255", "0.0.0.0")
    assert "255.255.255.255" == IPv4.normalize_subnet("255.255.255.255", "255.255.255.255")

    for ip, subnet in itertools.product(WRONG_IPS, WRONG_NUMBERS):
        with pytest.raises(ValueError):
            IPv4.normalize_subnet(ip, subnet)


def test_mask_to_prefix():
    assert 32 == IPv4.mask_to_prefix("255.255.255.255")
    assert 0 == IPv4.mask_to_prefix("0.0.0.0")
    assert 24 == IPv4.mask_to_prefix("255.255.255.0")

    for netmask in WRONG_NETMASKS + WRONG_IPS:
        with pytest.raises(ValueError):
            IPv4.mask_to_prefix(netmask)

def test_prefix_to_mask():
    assert IPv4.prefix_to_mask(32) == "255.255.255.255"
    assert IPv4.prefix_to_mask(0) == "0.0.0.0"
    assert IPv4.prefix_to_mask(24) == "255.255.255.0"

    for prefix in WRONG_PREFIXES:
        with pytest.raises(ValueError):
            IPv4.prefix_to_mask(prefix)
