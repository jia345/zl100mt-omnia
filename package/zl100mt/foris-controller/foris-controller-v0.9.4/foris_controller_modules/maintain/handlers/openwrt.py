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

from foris_controller.handler_base import BaseOpenwrtHandler
from foris_controller.utils import logger_wrapper

from foris_controller_backends.maintain import MaintainUci, MaintainCommands

from .. import Handler

logger = logging.getLogger(__name__)


class OpenwrtMaintainHandler(Handler, BaseOpenwrtHandler):
    uci_cmds = MaintainUci()
    cmds = MaintainCommands()

    @logger_wrapper(logger)
    def reboot(self):
        """ Starts a reboot process of the router

        :returns: probable new ips of the router
        :rtype: dict
        """
        ips = self.uci_cmds.get_lan_ips()

        self.cmds.reboot()

        return ips

    @logger_wrapper(logger)
    def generate_backup(self):
        return self.cmds.generate_backup()

    @logger_wrapper(logger)
    def restore_backup(self, backup):
        return self.cmds.restore_backup(backup)
