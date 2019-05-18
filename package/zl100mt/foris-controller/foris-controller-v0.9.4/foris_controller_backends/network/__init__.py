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

import logging, hashlib

from foris_controller_backends.uci import (
    UciBackend, get_option_anonymous, get_option_named, parse_bool, store_bool, get_sections_by_type
)
from foris_controller_backends.services import OpenwrtServices
from foris_controller.exceptions import UciRecordNotFound

logger = logging.getLogger(__name__)


class NetworkUciCommands(object):

    def get_settings(self, data):
        res = {
            "action": '',
            "data": []
        }
        with UciBackend() as backend:
            network_data = backend.read("network")
            print "NetworkUciCommands : action = %s" % data["action"]
            if data['action'] == 'route' :
                print "route info get setting!!"
                try:
                    routes = get_sections_by_type(network_data, "network", "route")
                    routes = [
                        e for e in routes if e['data']['interface'] == data['data']['interface']
                    ]
                except:
                    routes = []

                routesInfo = []
                for route in routes:
                    routesInfo.append(route['data'])
                print routesInfo

                res["action"] = 'routes'
                res["data"] = routesInfo

        return res

    def update_settings(self, data):
        print 'network info update_settings :'
        with UciBackend() as backend:
            network_data = backend.read("network")
            print data
            '''
            for route in routes:
                backend.del_section('network', route.section)
            '''
            if data['action'] == 'route_add':
                # routes = get_sections_by_type(network_data, "network", "route")
                for route in data['routes']:
                    print route
                    route['section'] = "%s_%s" % (route["interface"], route['target'].replace('.',''))
                    content = '%s_%s_%s_%s_%s' % (route['interface'], route['target'], route['netmask'], route['gateway'], route['metric'])
                    section_name = 'route_%s' % hashlib.md5(content).hexdigest()
                    backend.add_section('network','route', section_name)
                    backend.set_option('network', section_name, 'interface', route['interface'])
                    backend.set_option('network', section_name, 'target', route['target'])
                    backend.set_option('network', section_name, 'netmask', route['netmask'])
                    backend.set_option('network', section_name, 'gateway', route['gateway'])
                    backend.set_option('network', section_name, 'metric', route['metric'])
            elif data['action'] == "route_del":
                for route in data['routes']:
                    content = '%s_%s_%s_%s_%s' % (route['interface'], route['target'], route['netmask'], route['gateway'], route['metric'])
                    section_name = 'route_%s' % hashlib.md5(content).hexdigest()
                    #section_name = "%s_%s" % (route["interface"], route['target'].replace('.',''))
                    backend.del_section("network",section_name)

            elif data['action'] == "interface_add":
                interface = data['interface']
                interface['section'] = "IFlan_%s_%s" % (interface['ifname'],interface['ipaddr'])
                backend.add_section('network', 'interface', interface['section'])
                backend.set_option('network', interface['section'], 'ifname', interface['ifname'])
                backend.set_option('network', interface['section'], 'proto', interface['proto'])
                backend.set_option('network', interface['section'], 'netmask', interface['netmask'])
                backend.set_option('network', interface['section'], 'ipaddr', interface['ipaddr'])
                # backend.set_option('network', interface['section'], 'metric', interface['metric'])

            elif data['action'] == "interface_del":
                # interfaces = get_sections_by_type(network_data, "network", "interface")
                interface = data['interface']
                section_name = "IFlan_%s_%s" % (interface['ifname'], interface['ipaddr'])
                backend.del_section("network",section_name)

            elif data['action'] == "zone_add":
                zone = data['zone']
                zone['section'] = "zone_%s" % (zone['name'])
                backend.add_section('network', 'zone', zone['section'])
                backend.set_option('network', zone['section'], 'name', zone['name'])
                backend.set_option('network', zone['section'], 'network', zone['network'])
                backend.set_option('network', zone['section'], 'input', zone['input'])
                backend.set_option('network', zone['section'], 'output', zone['output'])
                backend.set_option('network', zone['section'], 'forward', zone['forward'])
                backend.set_option('network', zone['section'], 'masq', 1)
                backend.set_option('network', zone['section'], 'mtu-fix',1)

            elif data['action'] == "zone_del":
                zone = data['interface']
                section_name = "IFlan_%s_%s" % (zone['ifname'], zone['ipaddr'])
                backend.del_section("network",section_name)

            elif data["action"] == "redirect_add":
                redirect = data['redirect']
                if redirect['target'] == 'DNAT':
                    redirect['section'] = "redirect_%s_%s:%s_To_%s:%s" % (
                    redirect['target'], redirect['src'], redirect['src_dport'], redirect['dest_ip'],
                    redirect['dest_port'])
                else:
                    redirect['section'] = "redirect_%s_%s:%s_To_%s:%s" % (
                    redirect['target'], redirect['src_ip'], redirect['src_dport'], redirect['dest'],
                    redirect['dest_port'])
                backend.add_section('network', 'redirect', redirect['section'])
                backend.set_option('network', redirect['section'], 'target', redirect['target'])
                backend.set_option('network', redirect['section'], 'proto', 'tcp')
                backend.set_option('network', redirect['section'], 'src', redirect['src'])
                backend.set_option('network', redirect['section'], 'src_dport', redirect['src_dport'])
                backend.set_option('network', redirect['section'], 'dest', redirect['dest'])
                backend.set_option('network', redirect['section'], 'dest_port', redirect['dest_port'])
                backend.set_option('network', redirect['section'], 'dest_ip',redirect['dest_ip'])
            elif data['action'] == "zone_del":
                redirect = data['redirect']
                if redirect['target'] == 'DNAT':
                    section_name = "redirect_%s_%s:%s_To_%s:%s" % (
                    redirect['target'], redirect['src'], redirect['src_dport'], redirect['dest_ip'],
                    redirect['dest_port'])
                else:
                    section_name = "redirect_%s_%s:%s_To_%s:%s" % (
                    redirect['target'], redirect['src_ip'], redirect['src_dport'], redirect['dest'],
                    redirect['dest_port'])
                backend.del_section("network",section_name)
            elif data['action'] == "forwarding_add" :
                forwarding = data['forwarding']
                forwarding['section'] = "forward_%s" % (forwarding['name'])
                backend.add_section('network', 'forwarding', forwarding['section'])
                backend.set_option('network', forwarding['section'], 'name', forwarding['name'])
                backend.set_option('network', forwarding['section'], 'src', forwarding['src'])
                backend.set_option('network', forwarding['section'], 'dest', forwarding['dest'])
            elif data['action'] == "forwarding_del" :
                forwarding = data['forwarding']
                section_name = "forward_%s" % (forwarding['name'])
                backend.del_section("network", section_name)

        return True
