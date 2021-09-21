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
import re

from foris_controller.app import app_info
from foris_controller.utils import writelock, readlock, RWLock
from foris_controller_backends.cmdline import BaseCmdLine, i2c_lock
from foris_controller_backends.files import server_uplink_lock, BaseFile

logger = logging.getLogger(__name__)


class AtshaCmds(BaseCmdLine):
    @writelock(i2c_lock, logger)
    def get_serial(self):
        """ Obrains serial number

        :returns: serial number
        :rtype: str
        """
        return self._trigger_and_parse(
            ("/usr/bin/atsha204cmd", "serial-number"), r'^([0-9a-fA-F]{16})$', (1, ))


class TemperatureCmds(BaseCmdLine):
    @writelock(i2c_lock, logger)
    def get_cpu_temperature(self):
        """ Obtains temperature from the cpu

        :returns: temperature of cpu
        :rtype: int
        """
        return int(self._trigger_and_parse(
            ("/usr/bin/thermometer", ), r'^CPU:\s+([0-9]+)$', (1, )))


class SystemInfoCmds(BaseCmdLine):
    def get_kernel_version(self):
        """ Obtains kernel version

        :returns: kernel version
        :rtype: str
        """
        return self._trigger_and_parse(("/bin/uname", "-r"), r'^([^\s]+)$', (1, ))


class ServerUplinkCmds(BaseCmdLine):
    @writelock(server_uplink_lock, logger)
    def update_contract_status(self):
        """ Updates contract status
        """
        self._run_command_in_background("/usr/share/server-uplink/contract_valid.sh")


class SendingFiles(BaseFile):
    FW_PATH = "/tmp/firewall-turris-status.txt"
    UC_PATH = "/tmp/ucollect-status"
    file_lock = RWLock(app_info["lock_backend"])
    STATE_ONLINE = "online"
    STATE_OFFLINE = "offline"
    STATE_UNKNOWN = "unknown"

    @readlock(file_lock, logger)
    def get_sending_info(self):
        """ Returns sending info

        :returns: sending info
        :rtype: dict
        """
        result = {
            'firewall_status': {"state": SendingFiles.STATE_UNKNOWN, "last_check": 0},
            'ucollect_status': {"state": SendingFiles.STATE_UNKNOWN, "last_check": 0},
        }
        try:
            content = self._file_content(SendingFiles.FW_PATH)
            if re.search(r"turris firewall working: yes", content):
                result['firewall_status']["state"] = SendingFiles.STATE_ONLINE
            else:
                result['firewall_status']["state"] = SendingFiles.STATE_OFFLINE
            match = re.search(r"last working timestamp: ([0-9]+)", content)
            if match:
                result['firewall_status']["last_check"] = int(match.group(1))
        except IOError:
            # file doesn't probably exists yet
            logger.warning("Failed to read file '%s'." % SendingFiles.FW_PATH)

        try:
            content = self._file_content(SendingFiles.UC_PATH)
            match = re.search(r"^(\w+)\s+([0-9]+)$", content)
            if not match:
                logger.error("Wrong format of file '%s'." % SendingFiles.UC_PATH)
            else:
                if match.group(1) == "online":
                    result['ucollect_status']["state"] = SendingFiles.STATE_ONLINE
                else:
                    result['ucollect_status']["state"] = SendingFiles.STATE_OFFLINE
                result['ucollect_status']["last_check"] = int(match.group(2))

        except IOError:
            # file doesn't probably exists yet
            logger.warning("Failed to read file '%s'." % SendingFiles.UC_PATH)

        return result


class SystemInfoFiles(BaseFile):
    OS_RELEASE_PATH = "/etc/turris-version"
    MODEL_PATH = "/tmp/sysinfo/model"
    BOARD_NAME_PATH = "/tmp/sysinfo/board_name"
    file_lock = RWLock(app_info["lock_backend"])

    @readlock(file_lock, logger)
    def get_os_version(self):
        """ Returns turris os version

        :returns: os version
        :rtype: str
        """
        return self._read_and_parse(
            SystemInfoFiles.OS_RELEASE_PATH, r'^([0-9]+(\.[0-9]+)*)$', (1, ))

    @readlock(file_lock, logger)
    def get_model(self):
        """ Returns model of the device

        :returns: model
        :rtype: str
        """
        return self._read_and_parse(SystemInfoFiles.MODEL_PATH, r'^(\w+.*)$', (1, ))

    @readlock(file_lock, logger)
    def get_board_name(self):
        """ Returns board name

        :returns: board name
        :rtype: str
        """
        return self._read_and_parse(SystemInfoFiles.BOARD_NAME_PATH, r'^(\w+).*$', (1, ))


class ServerUplinkFiles(BaseFile):
    REGNUM_PATH = "/usr/share/server-uplink/registration_code"
    CONTRACT_PATH = "/usr/share/server-uplink/contract_valid"

    @readlock(server_uplink_lock, logger)
    def get_registration_number(self):
        """ Returns registration number

        :returns: registration number
        :rtype: str
        """
        try:
            res = self._read_and_parse(ServerUplinkFiles.REGNUM_PATH, r'^([a-zA-Z0-9]{16})$', (1, ))
        except:
            # failed to read file -> return False
            res = False

        return res

    @readlock(server_uplink_lock, logger)
    def get_contract_status(self):
        """ Returns contract status

        :returns: contract status
        :rtype: str
        """
        try:
            res = self._read_and_parse(ServerUplinkFiles.CONTRACT_PATH, r'^(\w+)$', (1, ))
            res = "not_valid" if res != "valid" else "valid"
        except:
            # failed to read file -> return None
            res = "unknown"
        return res
