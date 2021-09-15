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

from foris_controller_testtools.fixtures import lock_backend, init_script_result
from foris_controller_testtools.utils import check_service_result, sh_was_called

from foris_controller.exceptions import ServiceCmdFailed


@pytest.fixture(scope="function")
def custom_cmdline_root(cmdline_script_root):
    os.environ["FORIS_CMDLINE_ROOT"] = cmdline_script_root
    yield cmdline_script_root
    del os.environ["FORIS_CMDLINE_ROOT"]


@pytest.fixture
def service_class(lock_backend):
    from foris_controller.app import app_info
    app_info["lock_backend"] = lock_backend
    from foris_controller_backends import services
    return services.OpenwrtServices


@pytest.mark.parametrize("action", ["start", "stop", "restart", "reload", "enable", "disable"])
def test_service(action, custom_cmdline_root, init_script_result, service_class):

    with service_class() as services:
        getattr(services, action)("pass")
        check_service_result("pass", True, action)
        with pytest.raises(ServiceCmdFailed):
            getattr(services, action)("fail")
        check_service_result("fail", False, action)
        getattr(services, action)("fail", fail_on_error=False)
        check_service_result("fail", False, action)
        with pytest.raises(ServiceCmdFailed):
            getattr(services, action)("non-existing")
        getattr(services, action)("non-existing", fail_on_error=False)


@pytest.mark.parametrize("action", ["start", "stop", "restart", "reload", "enable", "disable"])
def test_service_delayed(action, custom_cmdline_root, init_script_result, service_class):
    # can't check the result for delayed services thus fail_on_error doesn't make sense neither
    with service_class() as services:
        getattr(services, action)("pass", delay=2)
        assert sh_was_called("/etc/init.d/pass", [action])
