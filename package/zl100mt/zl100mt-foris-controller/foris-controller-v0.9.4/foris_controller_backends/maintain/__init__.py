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

import logging
import os
import svupdater
import svupdater.exceptions
import svupdater.hook

from foris_controller_backends.uci import (
    UciBackend, get_option_named
)
from foris_controller_backends.cmdline import BackendCommandFailed, BaseCmdLine

from foris_controller.exceptions import UciRecordNotFound

logger = logging.getLogger(__name__)


class MaintainUci(object):

    def get_lan_ips(self):

        res = []
        with UciBackend() as backend:
            network_data = backend.read("network")

        for option in ("ipaddr", "ip6addr"):
            try:
                res.append(get_option_named(network_data, "network", "lan", option))
            except UciRecordNotFound:
                pass

        return res


class MaintainCommands(BaseCmdLine):
    REBOOT_INDICATOR_PATH = '/tmp/device-reboot-required'

    def reboot(self):
        args = ("/bin/sh", "-c", "reboot -d 5 &")  # 5 seconds before reboot
        self._run_command_in_background(*args)
        retval, _, _ = self._run_command(*args)
        if not retval == 0:
            logger.error("Reboot cmd failed.")
            raise BackendCommandFailed(retval, args)

    def generate_backup(self):
        logger.debug("Starting to prepare the backup.")
        cmd = "/usr/bin/maintain-config-backup"
        retval, stdout, _ = self._run_command(cmd)
        if retval != 0:
            logger.error("Cmd which generates the backup '%s' failed." % str(cmd))
            raise BackendCommandFailed(retval, [cmd])
        return stdout.strip()  # output should be base64 encoded string

    def restore_backup(self, backup):
        logger.debug("Starting to restore the backup.")
        cmd = "/usr/bin/maintain-config-restore"
        retval, _, _ = self._run_command(cmd, input_data=backup)
        if retval != 0:
            logger.error("Cmd to restore the backup '%s' failed." % str(cmd))
            return False
        # start updater and prepare for reboot
        try:
            svupdater.run(hooklist=["/usr/bin/maintain-reboot-needed"])
        except svupdater.exceptions.ExceptionUpdaterDisabled:
            pass  # failed to start updater, but configuration was restored

        return True

    def reboot_required(self):
        return os.path.exists(MaintainCommands.REBOOT_INDICATOR_PATH)
