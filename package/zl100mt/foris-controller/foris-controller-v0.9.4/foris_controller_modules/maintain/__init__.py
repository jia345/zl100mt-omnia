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

from foris_controller.module_base import BaseModule
from foris_controller.handler_base import wrap_required_functions


class MaintainModule(BaseModule):
    logger = logging.getLogger(__name__)

    def action_reboot(self, data):
        """ Calls action to perform the reboot

        :param data: input data (supposed to be {})
        :type data: dict
        :returns: list of probable router's IPs of the router after reboot
        :rtype: dict
        """
        msg = {"new_ips": self.handler.reboot()}
        self.notify("reboot", msg)
        return msg

    def action_generate_backup(self, data):
        """ Which calls a command which returns a backup of curret system

        :param data: input data (supposed to be {})
        :type data: dict
        :returns: dict contianing the backup in base64 encoding
        :rtype: dict
        """
        return {"backup": self.handler.generate_backup()}

    def action_restore_backup(self, data):
        """ Restores backup (overrides current configuration with the backup)

        :param data: should contain the backup in base64 encoding ({"backup": "..."})
        :type data: dict
        :returns: {result: True/False}
        :rtype: dict
        """
        res = self.handler.restore_backup(data["backup"])
        return {"result": res}


@wrap_required_functions([
    'reboot',
    'generate_backup',
    'restore_backup',
])
class Handler(object):
    pass
