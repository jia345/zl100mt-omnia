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


class WanModule(BaseModule):
    logger = logging.getLogger(__name__)

    def action_get_settings(self, data):
        """ Get current wan settings
        :param data: supposed to be {}
        :type data: dict
        :returns: current wan settings
        :rtype: dict
        """
        return self.handler.get_settings()

    def action_update_settings(self, data):
        """ Updates wan settings
        :param data: new wan settings
        :type data: dict
        :returns: result of the update {'result': True/False}
        :rtype: dict
        """
        res = self.handler.update_settings(data)
        if res:
            notify_data = {
                "wan_type": data["wan_settings"]["wan_type"],
                "wan6_type": data["wan6_settings"]["wan6_type"],
                "custom_mac_enabled": data["mac_settings"]["custom_mac_enabled"],
            }
            self.notify("update_settings", notify_data)
        return {"result": res}

    def action_connection_test_trigger(self, data):
        """ Triggers connectio test
        :param data: supposed to be {}
        :type data: dict
        :returns: dict containing test id {'test_id': 'xxxx'}
        :rtype: dict
        """

        # wrap action into notify function
        def notify(msg):
            self.notify("connection_test", msg)

        def exit_notify(msg):
            self.notify("connection_test_finished", msg)

        return {
            "test_id": self.handler.connection_test_trigger(
                data["test_kinds"], notify, exit_notify, self.reset_notify)
        }

    def action_connection_test_status(self, data):
        """ Reads connection test data
        :param data: supposed to be {'test_id': 'xxxx'}
        :type data: dict
        :returns: data about connection test {'status': 'xxxx', 'data': {...}}
        :rtype: dict
        """
        return self.handler.connection_test_status(data['test_id'])

    def action_get_wan_status(self, data):
        """ Obtains info regarding wan interface status
        :param data: supposed to be {}
        :type data: dict
        :returns: data regarding wan interface status {'up': True/False}
        :rtype: dict
        """
        return self.handler.get_wan_status()


@wrap_required_functions([
    'get_settings',
    'update_settings',
    'connection_test_trigger',
    'connection_test_status',
    'get_wan_status',
])
class Handler(object):
    pass
