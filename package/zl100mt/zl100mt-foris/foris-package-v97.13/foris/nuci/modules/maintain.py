# Foris - web administration interface for OpenWrt based on NETCONF
# Copyright (C) 2013 CZ.NIC, z.s.p.o. <http://www.nic.cz>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from xml.etree import cElementTree as ET

from .base import YinElement


class Maintain(YinElement):
    tag = "maintain"
    NS_URI = "http://www.nic.cz/ns/router/maintain"

    def __init__(self, data):
        """

        :param data: base64 encoded .tar.bz2 backup file
        :return:
        """
        super(Maintain, self).__init__()
        self.data = data

    @staticmethod
    def from_element(element):
        data = element.find(Maintain.qual_tag("data")).text
        return Maintain(data)

    @property
    def key(self):
        return "maintain"

    @staticmethod
    def rpc_reboot():
        """
        Request a system reboot.
        """
        backup_tag = Maintain.qual_tag("reboot")
        element = ET.Element(backup_tag)
        return element

    @staticmethod
    def rpc_config_backup():
        """
        Request for a configuration backup from Nuci.
        """
        backup_tag = Maintain.qual_tag("config-backup")
        element = ET.Element(backup_tag)
        return element

    @staticmethod
    def rpc_config_restore(data):
        """
        Request for a configuration restore from a base64 encoded .tar.bz2
        file returned by config-backup RPC.

        :param data: string with base64 encoded backup file
        :return: element with config-restore RPC
        """
        restore_tag = Maintain.qual_tag("config-restore")
        element = ET.Element(restore_tag)
        data_tag = Maintain.qual_tag("data")
        data_elem = ET.SubElement(element, data_tag)
        data_elem.text = data
        return element

    @staticmethod
    def get_new_ip(reply_element):
        new_ip_el = reply_element.find(Maintain.qual_tag("new-ip"))
        if new_ip_el is not None:
            return new_ip_el.text
        return None

####################################################################################################
ET.register_namespace("maintain", Maintain.NS_URI)
