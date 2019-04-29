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
    UciBackend, get_option_anonymous, get_option_named, parse_bool, store_bool, get_sections_by_type, get_section
)
from foris_controller_backends.services import OpenwrtServices
from foris_controller.exceptions import UciRecordNotFound

logger = logging.getLogger(__name__)


class DhcpUciCommands(object):

    def get_settings(self):
        with UciBackend() as backend:
            dhcp_data = backend.read("dhcp")
            dhcp_lan = get_section(dhcp_data, "dhcp", "lan")
        print "dhcp get setting!!"
        print dhcp_lan
        dhcpCfg = []
        dhcpCfg.append( {
            'ignore': int(dhcp_lan['data']['ignore']),
            "start": int(dhcp_lan['data']['start']),
            "limit": int(dhcp_lan['data']['limit']),
            "leasetime": dhcp_lan['data']['leasetime'],
            "dhcp_option": dhcp_lan['data']['dhcp_option']
            }
        )
        res = {
            "dhcp_cfg": dhcpCfg
        }
        return res

    def update_settings(self, data):
        print "dhcp update_settings :"
        with UciBackend() as backend:
            dhcp_data = backend.read("dhcp")
            dhcp_lan = get_section(dhcp_data, "dhcp", "lan")
            if not dhcp_lan:
                backend.add_section('dhcp', 'dhcp', 'lan')
                backend.set_option('dhcp', 'lan', 'interface', 'lan')
            dhcp = data['dhcp_cfg'][0]
            backend.set_option('dhcp', 'lan', 'ignore', dhcp['ignore'])
            backend.set_option('dhcp','lan','start', dhcp['start'])
            backend.set_option('dhcp', 'lan', 'limit', dhcp['limit'])
            backend.set_option('dhcp', 'lan', 'leasetime', dhcp['leasetime'])
            backend.set_option('dhcp', 'lan', 'dhcp_option', dhcp['dhcp_option'])

        return True
