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

import logging, os, hashlib

from foris_controller_backends.uci import (
    UciBackend, get_option_anonymous, get_option_named, parse_bool, store_bool, get_sections_by_type
)
from foris_controller_backends.services import OpenwrtServices
from foris_controller.exceptions import UciRecordNotFound

logger = logging.getLogger(__name__)


class RedirectUciCommands(object):

    def get_settings(self):
        res = {
            "redirects": None
        }
        with UciBackend() as backend:
            try:
                firewall_data = backend.read("firewall")
                redirects = get_sections_by_type(firewall_data, "firewall", "redirect")
            except:
                return res

        print "redirect profile get setting!!"
        print redirects
        rules = []
        for redirect in redirects:
            if redirect['name'] != 'dmz_host':
                rules.append(redirect['data'])
        print rules
        res["redirects"] = rules

        return res

    def get_port_mapping(self):
        with UciBackend() as backend:
            try:
                firewall_data = backend.read("firewall")
                redirects = get_sections_by_type(firewall_data, "firewall", "redirect")
            except:
                redirects = []

        port_mapping_data = [e['data'] for e in redirects if e['name'].startswith('port_mapping_')]
        print 'xijia port %s' % port_mapping_data

        return { 'redirects': port_mapping_data }

    def update_settings(self, data):
        print 'redirect update_settings :'
        with UciBackend() as backend:
            # firewall_data = backend.read("firewall")
            # redirects = get_sections_by_type(firewall_data, "firewall", "redirect")
            if data["action"] == "set_port_mapping":
                try:
                    redirects = get_sections_by_type(firewall_data, "firewall", "redirect")
                    port_mapping_data = [e['data'] for e in redirects if e['name'].startswith('port_mapping_')]
                except:
                    port_mapping_data = []

                for e in port_mapping_data:
                    backend.del_section('firewall', e['name'])

                for redirect in data["redirects"]:
                    content = '%s_%s_%s%s' %(redirect["target"],redirect["src_zone"],redirect["src_ip"].replace('.',''),redirect["src_dport"])
                    section_name = 'port_mapping_%s' % hashlib.md5(content).hexdigest()
                    backend.add_section('firewall', 'redirect', section_name)
                    backend.set_option('firewall', section_name, 'proto', redirect['proto'])
                    backend.set_option('firewall', section_name, 'src', redirect['src_zone'])
                    backend.set_option('firewall', section_name, 'target', 'DNAT')
                    backend.set_option('firewall', section_name, 'src_dport', redirect['src_dport'])
                    backend.set_option('firewall', section_name, 'dest', redirect['dest_zone'])
                    backend.set_option('firewall', section_name, 'dest_ip', redirect['dest_ip'])
                    backend.set_option('firewall', section_name, 'dest_port', redirect['dest_port'])
                    backend.set_option('firewall', section_name, 'name', redirect['name'])
            elif data["action"] == "del":
                for redirect in data["redirects"]:
                    section_name = '%s_%s_%s%s' % (redirect["target"], redirect["src_zone"], redirect["src_ip"].replace('.', ''), redirect["src_dport"])
                    backend.del_section("firewall", section_name)

        with OpenwrtServices() as services:
            services.restart("resolver")

        return True
