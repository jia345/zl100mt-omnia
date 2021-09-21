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

from foris_controller.handler_base import BaseOpenwrtHandler
from foris_controller.utils import logger_wrapper

from foris_controller_backends.updater import Updater
from foris_controller_backends.web import WebUciCommands, Languages
from foris_controller_backends.maintain import MaintainCommands
from foris_controller_backends.router_notifications import RouterNotificationsCmds

from .. import Handler

logger = logging.getLogger(__name__)


class OpenwrtWebHandler(Handler, BaseOpenwrtHandler):
    web_uci_cmds = WebUciCommands()
    langs = Languages()
    maintain_cmds = MaintainCommands()
    notifications_cmds = RouterNotificationsCmds()
    updater = Updater()

    @logger_wrapper(logger)
    def get_language(self):
        """ Mocks get language

        :returns: current language
        :rtype: str
        """
        return self.web_uci_cmds.get_language()

    @logger_wrapper(logger)
    def set_language(self, language):
        """ Sets language

        :returns: True
        :rtype: bool
        """
        return self.web_uci_cmds.set_language(language)

    @logger_wrapper(logger)
    def list_languages(self):
        """ Lists languages

        :returns: available languages
        :rtype: list
        """
        return self.langs.list_languages()

    @logger_wrapper(logger)
    def reboot_required(self):
        """ Is reboot required indicator
        :returns: True if reboot is required False otherwise
        :rtype: bool
        """
        return self.maintain_cmds.reboot_required()

    @logger_wrapper(logger)
    def get_notification_count(self):
        """ Get notifications count

        :returns: current notifcations count
        :rtype: int
         """
        return self.notifications_cmds.active_count()

    @logger_wrapper(logger)
    def updater_running(self):
        """ Returns indicator whether the updater is running
        :returns: True if updater is running False otherwise
        :rtype: bool
        """
        return self.updater.updater_running()
