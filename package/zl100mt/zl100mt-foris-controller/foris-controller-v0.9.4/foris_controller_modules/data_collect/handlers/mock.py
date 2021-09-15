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
import random

from foris_controller.handler_base import BaseMockHandler
from foris_controller.utils import logger_wrapper

from .. import Handler

logger = logging.getLogger(__name__)


class MockDataCollectHandler(Handler, BaseMockHandler):
    agreed = False
    log_credentials = False
    minipots = {
        "23tcp": False,
        "2323tcp": False,
        "80tcp": False,
        "3128tcp": False,
        "8123tcp": False,
        "8080tcp": False,
    }

    @logger_wrapper(logger)
    def get_registered(self, email, language):
        """ Mocks registration info

        :param email: email which was used during the registration
        :type email: str
        :param language: language which will be used in the server query (iso2)
        :type language: str

        :returns: Mocked result
        :rtype: dict
        """
        registration_code = "%016X" % random.randrange(0x10000000000000000)
        return random.choice([
            {
                "status": "free",
                "url": "https://some.page/%s/data?email=%s&registration_code=%s" %
                (language, email, registration_code),
                "registration_number": registration_code,
            },
            {
                "status": "foreign",
                "url": "https://some.page/%s/data?email=%s&registration_code=%s" %
                (language, email, registration_code),
                "registration_number": registration_code,
            },
            {
                "status": "unknown",
            },
            {
                "status": "not_found",
            },
            {
                "status": "owned",
            },
        ])

    @logger_wrapper(logger)
    def get_agreed(self):
        """ Mock getting information whether the user agreed with data collect
        :returns: True if user agreed, False otherwise
        :rtype: boolean
        """
        return self.agreed

    @logger_wrapper(logger)
    def set_agreed(self, agreed):
        """ Mock setting information whether the user agreed with data collect
        :returns: True
        :rtype: boolean
        """
        self.agreed = agreed
        return True

    @logger_wrapper(logger)
    def get_honeypots(self):
        """ Mock getting configuration of the honeypots
        :returns: {"minipots": {...}, "log_credentials": True/False}
        :rtype: dict
        """
        return {
            "minipots": self.minipots,
            "log_credentials": self.log_credentials,
        }

    @logger_wrapper(logger)
    def set_honeypots(self, honepot_settings):
        """ Mock setting configuration of the honeypots
        :param honepot_settings: {"minipots": {...}, "log_credentials": True/False}
        :type honepot_settings: dict

        :returns: True
        :rtype: boolean
        """
        self.log_credentials = honepot_settings["log_credentials"]
        self.minipots = honepot_settings["minipots"]
        return True
