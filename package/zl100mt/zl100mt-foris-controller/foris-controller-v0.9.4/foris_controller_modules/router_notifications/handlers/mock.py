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
import collections
import time

from datetime import datetime

from foris_controller.handler_base import BaseMockHandler
from foris_controller.utils import logger_wrapper

from .. import Handler

logger = logging.getLogger(__name__)


class MockRouterNotificationsHandler(Handler, BaseMockHandler):
    notification_counter = 0
    notifications = [
        {
            "displayed": False,
            "id": "1518776436-2593",
            "severity": "restart",
            "messages": {
                "cs": "REBOOT1 CS",
                "en": "REBOOT1 EN"
            }
        },
        {
            "displayed": False,
            "id": "1518776436-2598",
            "severity": "restart",
            "messages": {
                "cs": "REBOOT2 CS",
                "en": "REBOOT2 EN"
            }
        },
        {
            "displayed": False,
            "id": "1518776436-2603",
            "severity": "news",
            "messages": {
                "cs": "NEWS1 CS",
                "en": "NEWS1 EN"
            }
        },
        {
            "displayed": False,
            "id": "1518776436-2608",
            "severity": "news",
            "messages": {
                "cs": "NEWS2 CS",
                "en": "NEWS2 EN"
            }
        },
        {
            "displayed": False,
            "id": "1518776436-2613",
            "severity": "error",
            "messages": {
                "cs": "ERROR1 CS",
                "en": "ERROR1 EN"
            }
        },
        {
            "displayed": False,
            "id": "1518776436-2618",
            "severity": "error",
            "messages": {
                "cs": "ERROR2 CS",
                "en": "ERROR2 EN"
            }
        },
        {
            "displayed": False,
            "id": "1518776436-2623",
            "severity": "update",
            "messages": {
                "cs": "UPDATE1 CS",
                "en": "UPDATE1 EN"
            }
        },
        {
            "displayed": False,
            "id": "1518776436-2628",
            "severity": "update",
            "messages": {
                "cs": "UPDATE2 CS",
                "en": "UPDATE2 EN"
            }
        }
    ]

    reboots_settings = {
        "time": "03:00",
        "delay": 3,
    }

    emails_settings = {
        "enabled": False,
        "common": {
            "to": [],
            "severity_filter": 1,
            "send_news": True
        },
        "smtp_type": "turris",
        "smtp_turris": {
            "sender_name": "turris"
        },
        "smtp_custom": {
            "from": "turris@example.com",
            "host": "example.com",
            "port": 25,
            "security": "none",
            "username": "",
            "password": "",
        },
    }

    @logger_wrapper(logger)
    def list(self, lang):
        res = []
        for notification in MockRouterNotificationsHandler.notifications:
            new = {
                "id": notification["id"],
                "displayed": notification["displayed"],
                "severity": notification["severity"],
                "created_at": datetime.fromtimestamp(
                    int(notification['id'].split("-")[0])).isoformat()
            }
            msg = notification["messages"].get(lang, None)
            if msg:
                new["msg"] = msg
                new["lang"] = lang
            else:
                # english fallback
                msg = notification["messages"].get("en", None)
                if msg:
                    new["msg"] = msg
                    new["lang"] = "en"
                else:
                    raise KeyError(lang)  # this should not happen
            res.append(new)
        return res

    @logger_wrapper(logger)
    def mark_as_displayed(self, ids):
        for notification in MockRouterNotificationsHandler.notifications:
            if notification["id"] in ids:
                notification["displayed"] = True
        return True

    @logger_wrapper(logger)
    def get_settings(self):
        return {
            "emails": self.emails_settings,
            "reboots": self.reboots_settings,
        }

    @logger_wrapper(logger)
    def update_settings(self, emails_settings, reboots_settings):

        # update values
        def update_dict(d, u):
            for k, v in u.items():
                if isinstance(v, collections.Mapping):
                    update_dict(d.get(k, {}), v)
                else:
                    d[k] = v

        update_dict(self.emails_settings, emails_settings)
        self.reboots_settings = reboots_settings

        return True

    @logger_wrapper(logger)
    def create(self, msg, severity, immediate):
        self.notification_counter += 1
        MockRouterNotificationsHandler.notifications.append({
            "displayed": False,
            "id": "%d-%d" % (time.mktime(datetime.utcnow().timetuple()), self.notification_counter),
            "severity": severity,
            "messages": {
                "en": msg,
                "cs": msg,
            }
        })
        return True
