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
    UciBackend, get_option_anonymous, get_option_named, parse_bool, get_section, get_sections_by_type
)
from foris_controller_backends.services import OpenwrtServices
from foris_controller.exceptions import UciRecordNotFound

logger = logging.getLogger(__name__)


class ChannelmapUciCommands(object):

    def get_settings(self,data):
        channelmap = []
        with UciBackend() as backend:
            firewall_data = backend.read("firewall")
            for lan in data["lans"]:
                try:
                    rule = get_section(firewall_data, "firewall", lan['name'])
                    channelmap.append({"name": lan['name']})
                except Exception as e :
                    print "didn't find channel mapping rule!!!"
                    pass

        res = {
            "lans": channelmap
        }

        return res

    def update_settings(self, data):
        print 'rule update_settings :'
        with UciBackend() as backend:
            firewall_data = backend.read("firewall")
            # print firewall_data
            for lan in data["lans"] :
                try:
                    rule = get_section(firewall_data, "firewall", lan['name'])
                except Exception as e:
                    if lan['operate'] == 'add' :
                        # print "didn't find this section, so add channel mapping rule: " + lan['name']
                        backend.add_section('firewall', 'rule', lan['name'])
                    else :
                        # print "delete channel mapping rule(%s), but didn't find it!!!" % lan['name']
                        continue
                print lan
                if lan['operate'] == 'add' :
                    # print "add channel mapping rule: " + lan['name']
                    section_name = lan['name']
                    backend.set_option('firewall', section_name, 'target', 'REJECT')
                    backend.set_option('firewall', section_name, 'src', lan['src_zone'])
                    backend.set_option('firewall', section_name, 'src_ip', lan['src_ip'])
                    backend.set_option('firewall', section_name, 'dest', lan['dest_zone'])
                    # backend.set_option('firewall', section_name, 'dest_ip', lan['dest_ip'])
                else :
                    # print "delete channel mapping rule: " + lan['name']
                    backend.del_section('firewall', lan['name'])

        with OpenwrtServices() as services:
            services.restart("resolver")

        return True
