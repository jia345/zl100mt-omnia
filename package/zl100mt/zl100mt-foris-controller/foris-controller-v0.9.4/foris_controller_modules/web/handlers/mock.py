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

from foris_controller.handler_base import BaseMockHandler
from foris_controller.utils import logger_wrapper

from .. import Handler

logger = logging.getLogger(__name__)


class MockWebHandler(Handler, BaseMockHandler):
    language_list = ['en', 'de', 'cs']
    current_language = 'en'

    @logger_wrapper(logger)
    def get_language(self):
        """ Mocks get language

        :returns: current language
        :rtype: str
        """
        return self.current_language

    @logger_wrapper(logger)
    def set_language(self, language):
        """ Sets language

        :returns: True
        :rtype: bool
        """
        if language in MockWebHandler.language_list:
            MockWebHandler.current_language = language
            return True
        return False

    @logger_wrapper(logger)
    def list_languages(self):
        """ Lists languages

        :returns: available languages
        :rtype: list
        """
        return MockWebHandler.language_list[:]

    @logger_wrapper(logger)
    def reboot_required(self):
        return False

    @logger_wrapper(logger)
    def updater_running(self):
        from foris_controller_modules.updater.handlers.mock import MockUpdaterHandler
        return MockUpdaterHandler.updater_running

    @logger_wrapper(logger)
    def get_notification_count(self):
        from foris_controller_modules.router_notifications.handlers.mock import \
                MockRouterNotificationsHandler
        return len([e for e in MockRouterNotificationsHandler.notifications if not e["displayed"]])
