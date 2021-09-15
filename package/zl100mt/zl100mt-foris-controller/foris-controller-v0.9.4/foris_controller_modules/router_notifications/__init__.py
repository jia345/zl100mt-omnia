#
# foris-controller
# Copyright (C) 2018 CZ.NIC, z.s.p.o. (http://www.nic.cz/)
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


class RouterNotificationsModule(BaseModule):
    logger = logging.getLogger(__name__)

    def action_list(self, data):
        """ Displays current notifications

        :param data: input data (supposed to be {"lang": "en/cs/.."})
        :type data: dict
        :returns: response to request
        :rtype: dict
        """
        return {"notifications": self.handler.list(data["lang"])}

    def action_mark_as_displayed(self, data):
        """ Marks notifications as displayed

        displayed notifications will be removed by cleanup script later

        :param data: input data (supposed to be {"ids": ["12345678-1234"]})
        :type data: dict
        :returns: {"result": True/False}
        :rtype: dict
        """
        # Note that notifications to message bus should be created in the backend command
        return {"result": self.handler.mark_as_displayed(data["ids"])}

    def action_get_settings(self, data):
        """ Get current notification settings
        :param data: supposed to be {}
        :type data: dict
        :returns: current notification settings
        :rtype: dict
        """
        return self.handler.get_settings()

    def action_update_settings(self, data):
        """ Updates notification settings
        :param data: new notification settings
        :type data: dict
        :returns: result of the update {'result': True/False}
        :rtype: dict
        """
        res = self.handler.update_settings(
            emails_settings=data["emails"], reboots_settings=data["reboots"])
        if res:
            self.notify("update_settings", {
                "reboots": data["reboots"],
                "emails": {
                    "enabled": True, "smtp_type": data["emails"]["smtp_type"]
                } if data["emails"]["enabled"] else {"enabled": False}
            })
        return {"result": res}

    def action_create(self, data):
        """ Creates notification

        :param data: {'severity': 'news/update/...', 'message': "TEXT", 'immediate': True/False}
        :type data: dict
        :returns: result of the update {'result': True/False}
        :rtype: dict
        """
        # Note that notifications to message bus should be created in the backend command
        return {"result": self.handler.create(**data)}


@wrap_required_functions([
    'list',
    'mark_as_displayed',
    'get_settings',
    'update_settings',
    'create',
])
class Handler(object):
    pass
