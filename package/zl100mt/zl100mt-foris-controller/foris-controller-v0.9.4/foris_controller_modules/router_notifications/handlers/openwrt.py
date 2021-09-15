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

from datetime import datetime

from foris_controller.handler_base import BaseOpenwrtHandler
from foris_controller.utils import logger_wrapper

from foris_controller_backends.router_notifications import (
    RouterNotificationsCmds, RouterNotificationsUci
)

from .. import Handler

logger = logging.getLogger(__name__)


class OpenwrtRouterNotificationsHandler(Handler, BaseOpenwrtHandler):
    cmds = RouterNotificationsCmds()
    uci = RouterNotificationsUci()

    @logger_wrapper(logger)
    def list(self, lang):
        res = []
        for notification in self.cmds.list()["notifications"]:
            new = {
                "id": notification["id"],
                "displayed": notification["displayed"],
                "severity": notification["severity"],
                "created_at": datetime.fromtimestamp(
                    int(notification['id'].split("-")[0])).isoformat()
            }
            msg = notification["messages"].get(lang, None)
            if msg is not None:
                new["msg"] = msg
                new["lang"] = lang
            else:
                # english fallback
                msg = notification["messages"].get("en", None)
                if msg is not None:
                    new["msg"] = msg
                    new["lang"] = "en"
                else:
                    raise KeyError(lang)  # this should not happen
            res.append(new)
        return res

    @logger_wrapper(logger)
    def mark_as_displayed(self, ids):
        self.cmds.mark_as_displayed(ids)
        return True

    @logger_wrapper(logger)
    def get_settings(self):
        return self.uci.get_settings()

    @logger_wrapper(logger)
    def update_settings(self, emails_settings, reboots_settings):
        return self.uci.update_settings(emails_settings, reboots_settings)

    @logger_wrapper(logger)
    def create(self, msg, severity, immediate):
        return self.cmds.create_notification(msg, severity, immediate)
