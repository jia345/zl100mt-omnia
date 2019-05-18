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

import logging, os

from foris_controller_backends.uci import (
    UciBackend, get_option_anonymous, get_option_named, parse_bool, store_bool, get_sections_by_type, get_section
)
from foris_controller_backends.services import OpenwrtServices
from foris_controller.exceptions import UciRecordNotFound

logger = logging.getLogger(__name__)

class GnssUciCommands(object):

    def get_settings(self):
        with UciBackend() as backend:
            dhcp_data = backend.read("dhcp")
            dhcp_lan = get_section(dhcp_data, "dhcp", "lan")
            network_data = backend.read("network")
            network_lan = get_section(network_data, "network", "lan")

        cmd = "sed -n 's/number=\(.*\)/\1/p' /etc/zl100mt-app/zl100mt-app.conf"
        remote_sim_no = os.popen(cmd)
        return {
            "gnss_cfg": { 'remote_sim_no': remote_sim_no }
        }

    def update_settings(self, data):
        cmd = "sed -i 's/number=\(.*\)/number=%s/' /etc/zl100mt-app/zl100mt-app.conf" % data['gnss_cfg']['remote_sim_no']
        os.popen(cmd)
        return True

