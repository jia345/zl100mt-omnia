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


class UpdaterModule(BaseModule):
    logger = logging.getLogger(__name__)

    def action_get_settings(self, data):
        """ Get current updater settings
        :param data: supposed to be {'lang': }
        :type data: dict
        :returns: current updater settings
        :rtype: dict
        """
        res = self.handler.get_settings()
        res["approval"] = self.handler.get_approval()
        res["user_lists"] = self.handler.get_user_lists(data["lang"])
        res["languages"] = self.handler.get_languages()
        return res

    def action_update_settings(self, data):
        """ Updates updater settings

        :param data: data containing new updater settings
        :type data: dict
        :returns: {"result": True/False}
        :rtype: dict
        """
        return {
            "result": self.handler.update_settings(
                data.get("user_lists", None), data.get("languages", None),
                data.get("approval_settings", None), data["enabled"], data.get("branch", None)
            )
        }

    def action_resolve_approval(self, data):
        """ Resolvs approval
        :param data: {"id": "...", "solution": "grant/deny"}
        :type data: dict

        :returns: {"result": True/False}
        :rtype: dict
        """
        res = self.handler.resolve_approval(**data)
        if res:
            self.notify("resolve_approval", data)
        return {"result": res}

    def action_run(self, data):
        """ Starts the updater

        :param data: {"set_reboot_indicator": True/False}
        :type data: dict
        :returns: {"result": True/False}
        :rtype: dict
        """
        return {"result": self.handler.run(**data)}

    def action_get_enabled(self, data):
        """ Get information whether updater is enabled
        :param data: supposed to be {}
        :type data: dict
        :returns: {"enabled": True/False}
        :rtype: dict
        """
        return {"enabled": self.handler.get_enabled()}


@wrap_required_functions([
    'get_settings',
    'update_settings',
    'get_approval',
    'get_user_lists',
    'get_languages',
    'resolve_approval',
    'run',
    'get_enabled',
])
class Handler(object):
    pass
