#
# foris-controller-storage-module
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

from foris_controller.handler_base import BaseMockHandler
from foris_controller.utils import logger_wrapper

from .. import Handler

logger = logging.getLogger(__name__)


class MockStorageHandler(Handler, BaseMockHandler):
    old_device = "/dev/mmcblk0p1"
    old_uuid = "rootfs"
    uuid = ""
    formatting = False

    drives = [
        {
            "fs": "btrfs",
            "description": "srv - Generic Flash Disk (7 GiB)",
            "dev": "sda",
            "uuid": "fb002a7a-7504-4f08-882b-09eebb2b26e6"
        }
    ]

    @logger_wrapper(logger)
    def get_settings(self):
        return {
            "old_device": MockStorageHandler.old_device,
            "old_uuid": MockStorageHandler.old_uuid,
            "uuid": MockStorageHandler.uuid,
            "formating": MockStorageHandler.formatting,
        }

    @logger_wrapper(logger)
    def get_drives(self):
        return {"drives": MockStorageHandler.drives}

    @logger_wrapper(logger)
    def prepare_srv_drive(self, srv):
        return {}

    @logger_wrapper(logger)
    def update_settings(self, srv):
        raise NotImplementedError()
