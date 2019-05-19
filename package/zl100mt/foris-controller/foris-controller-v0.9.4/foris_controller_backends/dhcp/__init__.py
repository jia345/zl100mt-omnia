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

def calc_range(ip, netmask, start_ip, end_ip):
    ip_arr       = list(map(lambda x: int(x), ip.split('.')))
    mask_arr     = list(map(lambda x: int(x), netmask.split('.')))
    start_ip_arr = list(map(lambda x: int(x), start_ip.split('.')))
    end_ip_arr   = list(map(lambda x: int(x), end_ip.split('.')))
    network_arr  = list(map(lambda x: x[0] & x[1], zip(ip_arr, mask_arr)))

    network_int  = (network_arr[0] << 24) | (network_arr[1] << 16) | (network_arr[2] << 8) | network_arr[3]
    start_ip_int = (start_ip_arr[0] << 24) | (start_ip_arr[1] << 16) | (start_ip_arr[2] << 8) | start_ip_arr[3]
    end_ip_int   = (end_ip_arr[0] << 24) | (end_ip_arr[1] << 16) | (end_ip_arr[2] << 8) | end_ip_arr[3]
    print 'xijia network_int %s start %s end %s' % (network_int, start_ip_int, end_ip_int)

    if (network_int <= start_ip_int):
        start = start_ip_int - network_int
    if (start_ip_int <= end_ip_int):
        limit = end_ip_int - start_ip_int

    good_input = (start_ip <= end_ip) and (network_int <= start_ip_int)

    return [start, limit] if good_input else []

class DhcpUciCommands(object):

    def get_settings(self):
        with UciBackend() as backend:
            dhcp_data = backend.read("dhcp")
            dhcp_lan = get_section(dhcp_data, "dhcp", "lan")
            network_data = backend.read("network")
            network_lan = get_section(network_data, "network", "lan")

        leasetime_unit = dhcp_lan['data']['leasetime'][-1]
        leasetime_num  = int(dhcp_lan['data']['leasetime'][0:-1])
        if leasetime_unit == 'd':
            leasetime_m = leasetime_num * 24 * 60
        elif leasetime_unit == 'h':
            leasetime_m = leasetime_num * 60
        else:
            leasetime_m = leasetime_num

        dhcp_option = dhcp_lan['data']['dhcp_option']
        logger.debug('xijia %s' % dhcp_option)
        lan_ip  = network_lan['data']['ipaddr']
        netmask = network_lan['data']['netmask']
        gw_ip   = ''
        dns1    = ''
        dns2    = ''
        for e in dhcp_option:
            kv = e.split(',')
            key = int(kv[0])
            value = kv[1] if (len(kv) > 1) else ''
            if key == 1:
                netmask = kv[1]
            if key == 3:
                gw_ip = kv[1] if (len(kv) > 1) else ''
            if key == 6:
                dns1 = kv[1] if (len(kv) > 1) else ''
                dns2 = kv[2] if (len(kv) > 2) else ''

        ipcalc_cmd = "ipcalc.sh %s %s %s %s|cut -d'=' -f 2" % (lan_ip, netmask, dhcp_lan['data']['start'], dhcp_lan['data']['limit'])
        ipcalc_output = os.popen(ipcalc_cmd).read()
        lan_ip, netmask, broadcast, network, prefix, start_ip, end_ip = ipcalc_output.split()

        dhcpCfg = {
            "ignore": int(dhcp_lan['data'].get('ignore', 0)),
            "start_ip": start_ip,
            "end_ip": end_ip,
            "leasetime_m": leasetime_m,
            "netmask": netmask,
            "gw_ip": gw_ip,
            "dns1": dns1,
            "dns2": dns2
        }
        res = {
            "dhcp_cfg": dhcpCfg
        }
        return res

    def get_lan_cfg(self):
        with UciBackend() as backend:
            dhcp_data = backend.read("dhcp")
            dhcp_hosts = get_sections_by_type(dhcp_data, "dhcp", "host")
            dhcp_lan = get_section(dhcp_data, "dhcp", "lan")
            dhcp_option = dhcp_lan['data']['dhcp_option']
            netmask = ''
            for e in dhcp_option:
                kv = e.split(',')
                key = int(kv[0])
                value = kv[1] if (len(kv) > 1) else ''
                netmask = value if key == 1 else '255.255.255.0'

            lan_cfg = []
            port = 0
            for e in dhcp_hosts:
                print 'xijia eeeee %s' % e
                data = e['data']
                if 'mac' in data and 'ip' in data:
                    port += 1
                    lan_cfg.append({
                        'mac': data['mac'],
                        'ip': data['ip'],
                        'port': 'LAN%d' % port,
                        'netmask': netmask if netmask else '255.255.255.0'
                    })

            cmd = "cut -d' ' -f 2,3,4 /tmp/dhcp.leases"
            cmd_output = os.popen(cmd).read().split('\n')
            access_list = []
            port = 0
            for e in cmd_output:
                if e:
                    mac, ip, type = e.split()
                    port += 1
                    access_list.append({
                        'port': 'LAN%s' % port,
                        'mac': mac,
                        'ip': ip,
                        'type': type
                    })

        print 'xijia xxxxxx %s %s' % (lan_cfg, access_list)
        return { 'lan_cfg': lan_cfg, 'access_list': access_list }

    def update_settings(self, data):
        print "dhcp update_settings :"

        with UciBackend() as backend:
            #backend.del_section('dhcp', 'lan')

            #dhcp_data = backend.read("dhcp")
            #dhcp_lan = get_section(dhcp_data, "dhcp", "lan")
            #if not dhcp_lan:
            #    backend.add_section('dhcp', 'dhcp', 'lan')
            #    backend.set_option('dhcp', 'lan', 'interface', 'lan')

            network_data = backend.read("network")
            network_lan  = get_section(network_data, "network", "lan")
            lan_ip  = network_lan['data']['ipaddr']
            netmask = network_lan['data']['netmask']

            dhcp_cfg    = data['dhcp_cfg']
            ignore      = dhcp_cfg['ignore']
            start_ip    = dhcp_cfg['start_ip']
            end_ip      = dhcp_cfg['end_ip']
            leasetime_m = dhcp_cfg['leasetime_m']
            netmask     = dhcp_cfg['netmask']
            gw_ip       = dhcp_cfg['gw_ip']
            dns1        = dhcp_cfg['dns1']
            dns2        = dhcp_cfg['dns2']

            backend.add_section('dhcp', 'dhcp', 'lan')
            print '%s %s %s %s %s %s %s' % (lan_ip, netmask, start_ip, end_ip, gw_ip, dns1, dns2)
            ip_range = calc_range(lan_ip, netmask, start_ip, end_ip)
            dhcp_option = []
            if netmask:
                dhcp_option.append('1,%s' % netmask)
            if gw_ip:
                dhcp_option.append('3,%s' % gw_ip)
            if dns1 or dns1:
                dns_str  = '6'
                dns_str += ',%s' % dns1 if dns1 else ''
                dns_str += ',%s' % dns2 if dns2 else ''
                dhcp_option.append(dns_str)

            #dhcp_option += '3,%s' % netmask if netmask else ''
            print 'xijia dddd %s %s' % (ip_range, dhcp_option)
            if len(ip_range) == 2:
                start, limit = ip_range
                backend.set_option('dhcp', 'lan', 'ignore', ignore)
                backend.set_option('dhcp','lan','start', start)
                backend.set_option('dhcp', 'lan', 'limit', limit)
                backend.set_option('dhcp', 'lan', 'leasetime', '%sm' % leasetime_m)
                backend.replace_list('dhcp', 'lan', 'dhcp_option', dhcp_option)
                print 'okokok'
                return True
            else:
                print 'nonono'
                return False

