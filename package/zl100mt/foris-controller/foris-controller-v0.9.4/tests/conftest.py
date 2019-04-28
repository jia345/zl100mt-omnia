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
import os

# load common fixtures
from foris_controller_testtools.fixtures import (
    ubusd_acl_path, uci_config_default_path, file_root,
    controller_modules, extra_module_paths, message_bus, backend
)


@pytest.fixture(scope="session")
def ubusd_acl_path():
    return os.path.join(os.path.dirname(os.path.realpath(__file__)), "ubus-acl")


@pytest.fixture(scope="session")
def uci_config_default_path():
    return os.path.join(
        os.path.dirname(os.path.realpath(__file__)), "uci_configs", "defaults"
    )


@pytest.fixture(scope="session")
def cmdline_script_root():
    return os.path.join(
        os.path.dirname(os.path.realpath(__file__)), "test_root"
    )


@pytest.fixture(scope="session")
def file_root():
    # default src dirctory will be the same as for the scripts  (could be override later)
    return os.path.join(
        os.path.dirname(os.path.realpath(__file__)), "test_root"
    )


@pytest.fixture(scope="module")
def controller_modules():
    return [
        "about", "data_collect", "web", "dns", "maintain", "password", "updater", "lan", "time",
        "wan", "router_notifications", "wifi"
    ]


def pytest_addoption(parser):
    parser.addoption(
        "--backend", action="append",
        default=[],
        help=("Set test backend here. available values = (mock, openwrt)")
    )
    parser.addoption(
        "--debug-output", action="store_true",
        default=False,
        help=("Whether show output of foris-controller cmd")
    )


def pytest_generate_tests(metafunc):
    if 'backend' in metafunc.fixturenames:
        backend = set(metafunc.config.option.backend)
        if not backend:
            backend = ['mock']
        metafunc.parametrize("backend_param", backend, scope='module')
