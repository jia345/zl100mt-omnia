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


logger = logging.getLogger(__name__)


class BaseNotificationSender(object):

    def _validate(self, msg, validator):
        logger.debug("Starting to validate notification.")
        from jsonschema import ValidationError
        try:
            validator.validate(msg)
        except ValidationError:
            validator.validate_verbose(msg)
        logger.debug("Notification validation passed.")

    def _prepare_msg(self, module, action, data=None):
        msg = {
            "module": module,
            "kind": "notification",
            "action": action,
        }
        if data is not None:
            msg["data"] = data
        return msg

    def notify(self, module, action, data=None, validator=None):
        """ Send a notification on a message bus
        """
        msg = self._prepare_msg(module, action, data)
        if validator:
            self._validate(msg, validator)

        return self._send_message(msg, module, action, data)

    def _send_message(self, msg, module, action, data=None):
        raise NotImplementedError()

    def disconnect(self):
        raise NotImplementedError()

    def reset(self):
        raise NotImplementedError()
