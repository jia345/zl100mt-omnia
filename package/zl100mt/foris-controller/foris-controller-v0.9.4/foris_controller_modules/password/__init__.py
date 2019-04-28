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
import base64

from foris_controller.module_base import BaseModule
from foris_controller.handler_base import wrap_required_functions


class PasswordModule(BaseModule):
    logger = logging.getLogger(__name__)

    def action_check(self, data):
        """ Checks whether provided password (base64 encoded) matches the current foris password

        :param data: {"password": "<base64 string>"}
        :type data: dict
        :returns: {"result": True / False}
        :rtype: dict
        """
        return {"status": self.handler.check_foris_password(base64.b64decode(data["password"]))}

    def action_set(self, data):
        """ Sets the password for foris web interface xor system

        :param data: {"password": "<base64 string>", "type": "foris" / "system"}
        :type data: dict
        :returns: {result: True/False}
        :rtype: dict
        """
        decoded = base64.b64decode(data["password"])
        if data["type"] == "system":
            res = self.handler.set_system_password(decoded)
        elif data["type"] == "foris":
            res = self.handler.set_foris_password(decoded)
        else:
            raise NotImplementedError()

        if res:
            self.notify("set", {"type": data["type"]})
        return {"result": res}


@wrap_required_functions([
    'check_foris_password',
    'set_foris_password',
    'set_system_password',
])
class Handler(object):
    pass
