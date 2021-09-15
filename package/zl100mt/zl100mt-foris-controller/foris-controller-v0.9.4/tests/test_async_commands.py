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
import time

from foris_controller_testtools.fixtures import lock_backend

NOTIFICATION_PATH = "/tmp/async-notification.txt"
RESET_PATH = "/tmp/async-reset.txt"
SCRIPT_PATH = "/tmp/async-script.sh"  # test root dir will be injected


def get_data(old_data=None):
    while True:
        with open(NOTIFICATION_PATH) as f:
            data = f.readlines()
            last_data = [e.strip() for e in data]
            if not old_data == last_data:
                break
            else:
                time.sleep(0.1)
    return last_data


@pytest.fixture(scope="function")
def async_infrastructure(lock_backend):
    from foris_controller.app import app_info
    app_info["lock_backend"] = lock_backend
    from foris_controller_backends.cmdline import AsyncCommand

    for path in [NOTIFICATION_PATH, RESET_PATH]:
        try:
            os.unlink(path)
        except OSError:
            if os.path.exists(path):
                raise

    with open(NOTIFICATION_PATH, "w") as f:
        f.flush()

        def notify(text):
            f.write(text + "\n")
            f.flush()

        yield notify, AsyncCommand

    for path in [NOTIFICATION_PATH, RESET_PATH]:
        try:
            os.unlink(path)
        except OSError:
            pass


def test_async_complex(async_infrastructure):
    notify, AsyncCommand = async_infrastructure

    class TestCommand(AsyncCommand):
        def read_data(self, process_id):
            if process_id not in self.processes:
                return "not_found", None, None
            process_data = self.processes[process_id]

            if process_data.get_exitted():
                return "finished", process_data.get_retval(), process_data.read_all_data()
            else:
                return "running", None, process_data.read_all_data()

        def start(self):
            def handler(matched, process_data):
                data = matched.group(1)
                process_data.append_data(data)
                notify("%s: %s" % (process_data.id, data))

            handlers = [
                (r'FIRST (\w+)', handler),
                (r'SECOND (\w+)', handler),
                (r'THIRD (\w+)', handler),
            ]

            def exit_handler(process_data):
                notify("%s: exitted %d" % (process_data.id, process_data.get_retval()))

            def reset_notify_function():
                with open(RESET_PATH, "w") as f:
                    f.flush()

            return self.start_process(
                [SCRIPT_PATH, "10", "11", "22", "33"],
                handlers,
                exit_handler,
                reset_notify_function,
            )

    command = TestCommand()

    data = get_data()

    assert command.read_data("unknown") == ("not_found", None, None)
    cmd_id = command.start()
    data = get_data(data)

    assert command.read_data(cmd_id)[0] == "running"

    assert data[0] == "%s: 11" % cmd_id
    data = get_data(data)
    assert data[1] == "%s: 22" % cmd_id
    data = get_data(data)
    assert data[2] == "%s: 33" % cmd_id

    if len(data) == 3:
        data = get_data(data)

    assert data[3] == "%s: exitted 10" % cmd_id

    assert command.read_data(cmd_id) == (
        "finished", 10, ["11", "22", "33"]
    )

    assert os.path.exists(RESET_PATH)
