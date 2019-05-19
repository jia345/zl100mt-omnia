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

from foris_controller_backends.uci import (
    UciBackend, get_option_anonymous, get_option_named, parse_bool, store_bool, get_sections_by_type
)
from foris_controller_backends.services import OpenwrtServices
from foris_controller.exceptions import UciRecordNotFound

logger = logging.getLogger(__name__)


class IpmacbindUciCommands(object):

    def get_settings(self):

        with UciBackend() as backend:
            dhcp_data = backend.read("dhcp")
            hosts = get_sections_by_type(dhcp_data, "dhcp", "host")
        print 'xijia %s' % hosts
        ipmacbinds = []
        for host in hosts:
            if 'mac' in host and 'ip' in host:
                ipmacbinds.append(host['data'])

        res = {
            "ipmac_binds": ipmacbinds
        }

        return res

    def update_settings(self, data):
        print 'IPMAC bind update_settings :'
        with UciBackend() as backend:
            dhcp_data = backend.read("dhcp")
            hosts = get_sections_by_type(dhcp_data, "dhcp", "host")
            for i in range(0, len(hosts)):
                backend.del_section('dhcp', '@host[%d]'%i)

            for host in data['ipmac_binds']:
                backend.add_section('dhcp','host')
                backend.set_option('dhcp','@host[-1]','ip',host['ip'])
                backend.set_option('dhcp', '@host[-1]', 'mac', host['mac'])
                backend.set_option('dhcp', '@host[-1]', 'name', host['name'])

        return True
