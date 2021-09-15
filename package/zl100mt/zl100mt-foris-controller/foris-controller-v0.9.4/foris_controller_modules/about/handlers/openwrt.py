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

from foris_controller_backends.about import (
    AtshaCmds, SystemInfoCmds, TemperatureCmds, ServerUplinkCmds,
    SendingFiles, SystemInfoFiles, ServerUplinkFiles
)

from .. import Handler

logger = logging.getLogger(__name__)


class OpenwrtAboutHandler(Handler, BaseOpenwrtHandler):

    atsha_cmds = AtshaCmds()
    temperature_cmds = TemperatureCmds()
    sending_files = SendingFiles()
    system_info_cmds = SystemInfoCmds()
    system_info_files = SystemInfoFiles()
    server_uplink_files = ServerUplinkFiles()
    server_uplink_cmds = ServerUplinkCmds()

    @logger_wrapper(logger)
    def get_device_info(self):
        """ Obtains info about the device

        :returns: result
        :rtype: dict
        """
        return {
            "model": self.system_info_files.get_model(),
            "board_name": self.system_info_files.get_board_name(),
            "kernel": self.system_info_cmds.get_kernel_version(),
            "os_version": self.system_info_files.get_os_version(),
        }

    @logger_wrapper(logger)
    def get_serial(self):
        """ Obtains serial number

        :returns: result
        :rtype: dict
        """
        return {"serial": self.atsha_cmds.get_serial()}

    @logger_wrapper(logger)
    def get_temperature(self):
        """ Obtains temperature

        :returns: result
        :rtype: dict
        """
        return {
            "temperature": {"CPU": self.temperature_cmds.get_cpu_temperature()},
        }

    @logger_wrapper(logger)
    def get_sending_info(self):
        """ Obtains info whether the router is sending data to our servers

        :returns: result
        :rtype: dict
        """
        return self.sending_files.get_sending_info()

    @logger_wrapper(logger)
    def get_registration_number(self):
        """ Obtains registration number

        :returns: result
        :rtype: dict
        """
        return {"registration_number": self.server_uplink_files.get_registration_number()}

    @logger_wrapper(logger)
    def get_contract_status(self):
        """ Obtains the contract status

        :returns: result
        :rtype: dict
        """
        return {"contract_status": self.server_uplink_files.get_contract_status()}

    @logger_wrapper(logger)
    def update_contract_status(self):
        """ Calls a script which updates the contract status

        :returns: result
        :rtype: dict
        """
        self.server_uplink_cmds.update_contract_status()
        return {"result": True}
