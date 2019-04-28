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

import json
import logging
import glob

from foris_controller_backends.cmdline import BaseCmdLine
from foris_controller_backends.uci import (
    UciBackend, get_option_named, parse_bool, store_bool
)
from foris_controller.exceptions import FailedToParseCommandOutput

logger = logging.getLogger(__name__)


class RouterNotificationsCmds(BaseCmdLine):
    def list(self):
        """ Lists notifications

        :returns: list of notifications in following format
            {
                "notifications": [
                    {
                        "id": "1234567-1234",
                        "displayed": True/False,
                        "severity": "restart/news/error/update",
                        "messages": {
                            "cs": "msg in cs",
                            "en": "msg in en",
                        }
                    },
                    ...
                ]
            }
        :rtype: list
        """
        args = ("/usr/bin/list_notifications", "-n")
        stdout, _ = self._run_command_and_check_retval(args, 0)
        try:
            parsed = json.loads(stdout.strip())
        except ValueError:
            raise FailedToParseCommandOutput(args, stdout)
        return parsed

    def active_count(self):
        """ get active notifications
        :returns: number of active notifiations
        :rtype: int
        """
        return len(glob.glob("/tmp/user_notify/*-*")) \
            - len(glob.glob("/tmp/user_notify/*-*/displayed"))

    def mark_as_displayed(self, ids):
        """ Marks notifications as displayed

        displayed notifications will be removed by cleanup script later

        :param ids: list of notifications to be marked
        :type data: list
        """
        args = ["/usr/bin/user-notify-display"] + ids
        _, _ = self._run_command_and_check_retval(args, 0)

    def create_notification(self, msg, severity, immediate):
        """ Call cmd to create notification

        :param msg: message to be stored
        :type msg: str
        :param severity: message severity (news, update, restart, error)
        :type severity: str
        :param immediate:
        :type immediate: bool
        """
        args = ["/usr/bin/create_notification"] + (["-t"] if immediate else []) + \
            ["-s", severity, msg]
        retval, _, _ = self._run_command(*args)
        return retval == 0


class RouterNotificationsUci(object):

    def get_settings(self):
        with UciBackend() as backend:
            data = backend.read("user_notify")

        res = {
            "emails": {
                "enabled": parse_bool(
                    get_option_named(data, "user_notify", "smtp", "enable", "0")),
                "common": {
                    "to": get_option_named(data, "user_notify", "smtp", "to", []),
                    "severity_filter": int(
                        get_option_named(data, "user_notify", "notifications", "severity", "1")),
                    "send_news": parse_bool(
                        get_option_named(data, "user_notify", "notifications", "news", "1")),
                },
                "smtp_turris": {
                    "sender_name": get_option_named(
                        data, "user_notify", "smtp", "sender_name", "turris"),
                },
                "smtp_custom": {
                    "from": get_option_named(
                        data, "user_notify", "smtp", "from", "router@example.com"),
                    "host": get_option_named(
                        data, "user_notify", "smtp", "server", "example.com"),
                    "port": int(get_option_named(
                        data, "user_notify", "smtp", "port", "587")),
                    "username": get_option_named(
                        data, "user_notify", "smtp", "username", ""),
                    "password": get_option_named(
                        data, "user_notify", "smtp", "password", ""),
                    "security": get_option_named(
                        data, "user_notify", "smtp", "security", "starttls"),
                },
            },
            "reboots": {
                "time": get_option_named(data, "user_notify", "reboot", "time"),
                "delay": int(get_option_named(data, "user_notify", "reboot", "delay")),
            }
        }
        smtp_type = "turris" if parse_bool(get_option_named(
            data, "user_notify", "smtp", "use_turris_smtp", "1")) else "custom"
        res["emails"]["smtp_type"] = smtp_type

        return res

    def update_settings(self, emails_settings, reboots_settings):
        with UciBackend() as backend:
            if emails_settings["enabled"]:
                backend.add_section("user_notify", "smtp", "smtp")
                backend.set_option("user_notify", "smtp", "enable", store_bool(True))
                if emails_settings["smtp_type"] == "turris":
                    backend.set_option("user_notify", "smtp", "use_turris_smtp", store_bool(True))
                    backend.set_option(
                        "user_notify", "smtp", "sender_name",
                        emails_settings["smtp_turris"]["sender_name"]
                    )
                if emails_settings["smtp_type"] == "custom":
                    backend.set_option("user_notify", "smtp", "use_turris_smtp", store_bool(False))
                    backend.set_option(
                        "user_notify", "smtp", "from", emails_settings["smtp_custom"]["from"])
                    backend.set_option(
                        "user_notify", "smtp", "server", emails_settings["smtp_custom"]["host"])
                    backend.set_option(
                        "user_notify", "smtp", "port", int(emails_settings["smtp_custom"]["port"]))
                    backend.set_option(
                        "user_notify", "smtp", "security",
                        emails_settings["smtp_custom"]["security"]
                    )
                    if emails_settings["smtp_custom"]["username"].strip():
                        backend.set_option(
                            "user_notify", "smtp", "username",
                            emails_settings["smtp_custom"]["username"].strip()
                        )
                    if emails_settings["smtp_custom"]["password"]:
                        backend.set_option(
                            "user_notify", "smtp", "password",
                            emails_settings["smtp_custom"]["password"]
                        )
                backend.replace_list("user_notify", "smtp", "to", emails_settings["common"]["to"])
                backend.add_section("user_notify", "notifications", "notifications")
                backend.set_option(
                    "user_notify", "notifications", "severity",
                    emails_settings["common"]["severity_filter"]
                )
                backend.set_option(
                    "user_notify", "notifications", "news",
                    store_bool(emails_settings["common"]["send_news"])
                )
            else:
                backend.set_option("user_notify", "smtp", "enable", store_bool(False))

            # Set reboots
            backend.add_section("user_notify", "reboot", "reboot")
            backend.set_option("user_notify", "reboot", "time", reboots_settings["time"])
            backend.set_option("user_notify", "reboot", "delay", str(reboots_settings["delay"]))

        return True
