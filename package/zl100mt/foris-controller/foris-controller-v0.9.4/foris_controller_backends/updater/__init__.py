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
import svupdater
import svupdater.approvals
import svupdater.exceptions
import svupdater.hook
import svupdater.l10n
import svupdater.lists

from datetime import datetime

from svupdater.exceptions import ExceptionUpdaterApproveInvalid

from foris_controller_backends.uci import (
    UciBackend, get_option_named, parse_bool, store_bool
)
from foris_controller.exceptions import UciRecordNotFound, UciException

logger = logging.getLogger(__name__)


class UpdaterUci(object):

    def get_settings(self):

        with UciBackend() as backend:
            updater_data = backend.read("updater")

        res = {
            "enabled": not parse_bool(
                get_option_named(updater_data, "updater", "override", "disable", "0")
            ),
            "branch": get_option_named(updater_data, "updater", "override", "branch", ""),
            "user_lists": get_option_named(updater_data, "updater", "pkglists", "lists", []),
            "languages": get_option_named(updater_data, "updater", "l10n", "langs", []),
            "approval_settings": {
                "status": "on" if parse_bool(
                    get_option_named(updater_data, "updater", "approvals", "need", "0"),
                ) else "off"
            }
        }

        try:
            delay_seconds = int(get_option_named(
                updater_data, "updater", "approvals", "auto_grant_seconds"))
            delay_hours = delay_seconds / (60 * 60)
            res["approval_settings"]["delay"] = delay_hours
            if res["approval_settings"]["status"] == "on":
                res["approval_settings"]["status"] = "delayed"
        except UciRecordNotFound:
            pass

        return res

    def get_enabled(self):
        with UciBackend() as backend:
            updater_data = backend.read("updater")
        return not parse_bool(
            get_option_named(updater_data, "updater", "override", "disable", "0")
        )

    def update_settings(
        self, user_lists, languages, approvals_status, approvals_delay, enabled, branch
    ):
        with UciBackend() as backend:
            if approvals_status is not None:
                backend.add_section("updater", "approvals", "approvals")
                if approvals_status == "off":
                    try:
                        backend.del_option("updater", "approvals", "auto_grant_seconds")
                    except UciException:
                        pass
                    backend.set_option("updater", "approvals", "need", store_bool(False))
                elif approvals_status == "on":
                    try:
                        backend.del_option("updater", "approvals", "auto_grant_seconds")
                    except UciException:
                        pass
                    backend.set_option("updater", "approvals", "need", store_bool(True))
                elif approvals_status == "delayed":
                    backend.set_option(
                        "updater", "approvals", "auto_grant_seconds",
                        str(approvals_delay * 60 * 60)
                    )
                    backend.set_option("updater", "approvals", "need", store_bool(True))
                else:
                    raise NotImplementedError()
            if branch is not None:
                backend.add_section("updater", "override", "override")
                if branch:
                    backend.set_option("updater", "override", "branch", branch)
                else:
                    try:
                        backend.del_option("updater", "override", "branch")
                    except UciException:
                        pass

            backend.set_option("updater", "override", "disable", store_bool(not enabled))

            if user_lists is not None:
                svupdater.lists.update_userlists(user_lists)

            if languages is not None:
                svupdater.l10n.update_languages(languages)

        if enabled:
            try:
                svupdater.run()
            except svupdater.exceptions.ExceptionUpdaterDisabled:
                pass  # failed to run updater, but settings were updated

        return True


class Updater(object):
    def updater_running(self):
        """ Returns indicator whether the updater is running
        :returns: True if updater is running False otherwise
        :rtype: bool
        """
        logger.debug("Calling opkg_lock() check whether the updater is running")
        res = svupdater.opkg_lock()
        logger.debug("opkg_lock() -> %s", res)
        return res

    def get_approval(self):
        """ Returns current approval
        :returns: approval
        :rtype: dict
        """
        logger.debug("Try to get current approval.")
        approval = svupdater.approvals.current()
        logger.debug("Approval obtained: %s", approval)
        if approval:
            approval["present"] = True
            approval["time"] = datetime.fromtimestamp(approval["time"]).isoformat()

            # remove cur_ver: None and new_ver: None
            for record in approval["plan"]:
                if record["new_ver"] is None:
                    del record["new_ver"]
                if record["cur_ver"] is None:
                    del record["cur_ver"]

            return approval
        else:
            return {"present": False}

    def get_user_lists(self, lang):
        logger.debug("Getting user lists for '%s'", lang)
        user_lists = svupdater.lists.userlists(lang)
        logger.debug("Userlists obtained: %s", user_lists)
        return [
            {
                "name": k, "enabled": v["enabled"], "hidden": v["hidden"],
                "title": v["title"], "msg": v["message"],
            }
            for k, v in user_lists.items()
        ]

    def get_languages(self):
        logger.debug("Getting languages")
        languages = svupdater.l10n.languages()
        logger.debug("Languages obtained: %s", languages)
        return [{"code": k, "enabled": v} for k, v in languages.items()]

    def resolve_approval(self, approval_id, solution):
        """ Resolves approval
        """
        try:
            logger.debug("Resolving approval %s (->%s)", approval_id, solution)
            svupdater.approvals.approve(approval_id) if solution == "grant" \
                else svupdater.approvals.deny(approval_id)
            logger.debug("Approval resolved %s (->%s)", approval_id, solution)

            # Run updater after approval was granted
            if solution == "grant":
                try:
                    self.run(False)
                except svupdater.exceptions.ExceptionUpdaterDisabled:
                    pass  # updater failed to run, but approval was resolved

        except ExceptionUpdaterApproveInvalid:
            logger.warning("Failed to resolve approval %s (->%s)", approval_id, solution)

            return False

        return True

    def run(self, set_reboot_indicator):
        """ Starts updater run
        """

        try:
            logger.debug(
                "Staring to trigger updater (set_reboot_indicator=%s)", set_reboot_indicator)
            hooks = ["/usr/bin/maintain-reboot-needed"] if set_reboot_indicator else []
            svupdater.run(hooklist=hooks)
            logger.debug("Updater triggered")
        except svupdater.exceptions.ExceptionUpdaterDisabled:
            return False

        return True
