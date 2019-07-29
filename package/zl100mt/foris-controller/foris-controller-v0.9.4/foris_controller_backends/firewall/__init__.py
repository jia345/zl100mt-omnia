import os, logging, hashlib

from foris_controller_backends.uci import (
    UciBackend, get_option_anonymous, get_option_named, parse_bool, store_bool, get_sections_by_type
)
from foris_controller_backends.services import OpenwrtServices
from foris_controller.exceptions import UciRecordNotFound
from foris_controller.utils import logger_wrapper

logger = logging.getLogger(__name__)

class FirewallUciCommands(object):
    @logger_wrapper(logger)
    def get_settings(self):
        with UciBackend() as backend:
            cfg = backend.read('firewall')

        ip_filter_enabled = parse_bool(get_option_named(cfg, 'firewall', 'global', 'ip_filter_enabled'))
        mac_filter_enabled = parse_bool(get_option_named(cfg, 'firewall', 'global', 'mac_filter_enabled'))
        dmz_enabled = parse_bool(get_option_named(cfg, 'firewall', 'dmz_host', 'enabled'))
        dmz_ip = get_option_named(cfg, 'firewall', 'dmz_host', 'dest_ip')

        try:
            rules = get_sections_by_type(cfg, 'firewall', 'rule')
        except:
            rules = []
        ip_filter_data = [e['data'] for e in rules if e['name'].startswith('ip_filter_')]
        mac_filter_data = [e['data'] for e in rules if e['name'].startswith('mac_filter_')]

        ip_filter_table = []
        for e in [dict(d) for d in ip_filter_data]:
            ip_filter_table.append({
                'enabled': parse_bool(e['enabled']),
                'lan_ips': e['src_ip'],
                'lan_ports': e['src_port'],
                'wan_ips': e['dest_ip'],
                'wan_ports': e['dest_port'],
                'proto': e['proto'],
            })

        mac_filter_table = []
        for e in [dict(d) for d in mac_filter_data]:
            mac_filter_table.append({
                'enabled': parse_bool(e['enabled']),
                'mac': e['src_mac'],
                'desc': e['name'],
            })


        res= {
            'ip_filter_enabled': ip_filter_enabled,
            'mac_filter_enabled': mac_filter_enabled,
            'dmz_enabled': dmz_enabled,
            'dmz_ip': dmz_ip,
            'ip_filter_table': ip_filter_table,
            'mac_filter_table': mac_filter_table
        }
        return res

    @logger_wrapper(logger)
    def set_firewall(self, data):
        with UciBackend() as backend:
            cfg = backend.read('firewall')
            rules = get_sections_by_type(cfg, 'firewall', 'rule')

            for e in rules:
                if e['name'].startswith('ip_filter_'):
                    backend.set_option('firewall', e['name'], 'enabled', store_bool(data['ip_filter_enabled']))
                if e['name'].startswith('mac_filter_'):
                    backend.set_option('firewall', e['name'], 'enabled', store_bool(data['mac_filter_enabled']))

            backend.set_option('firewall', 'global', 'ip_filter_enabled', store_bool(data['ip_filter_enabled']))
            backend.set_option('firewall', 'global', 'mac_filter_enabled', store_bool(data['mac_filter_enabled']))
            backend.set_option('firewall', 'dmz_host', 'enabled', store_bool(data['dmz_enabled']))
            backend.set_option('firewall', 'dmz_host', 'dest_ip', data['dmz_ip'])

        with OpenwrtServices() as services:
            services.restart("network", delay=2)

        return True

    @logger_wrapper(logger)
    def set_ip_filter(self, data):
        with UciBackend() as backend:
            cfg = backend.read('firewall')

            try:
                rules = get_sections_by_type(cfg, 'firewall', 'rule')
            except:
                rules = []

            '''
            try:
                ipsets = get_sections_by_type(cfg, 'firewall', 'ipset')
            except:
                ipsets = []
            '''

            for e in rules:
                if e['name'].startswith('ip_filter_'):
                    backend.del_section('firewall', e['name'])

            '''
            for e in ipsets:
                if e['name'].startswith('ip_filter_ipset_'):
                    backend.del_section('firewall', e['name'])
            '''

            for e in data['ip_filter_table']:
                lan_iprange, lan_portrange, wan_iprange, wan_portrange, proto = e['lan_ips'], e['lan_ports'], e['wan_ips'], e['wan_ports'], e['proto']
                content = '%s %s %s %s %s' % (lan_iprange, lan_portrange, wan_iprange, wan_portrange, proto)

                '''
                ipset_lan_section_name = 'ip_filter_ipset_lan_%s' % hashlib.md5(content).hexdigest()
                backend.add_section('firewall', 'ipset', ipset_lan_section_name)
                backend.set_option('firewall', ipset_lan_section_name, 'match', 'src_net')
                backend.set_option('firewall', ipset_lan_section_name, 'storage', 'hash')
                backend.set_option('firewall', ipset_lan_section_name, 'timeout', e['timeout'])
                backend.add_to_list('firewall', ipset_lan_section_name, 'entry', lan_iprange)

                ipset_wan_section_name = 'ip_filter_ipset_wan_%s' % hashlib.md5(content).hexdigest()
                backend.add_section('firewall', 'ipset', ipset_wan_section_name)
                backend.set_option('firewall', ipset_wan_section_name, 'match', 'src_net')
                backend.set_option('firewall', ipset_wan_section_name, 'storage', 'hash')
                backend.set_option('firewall', ipset_wan_section_name, 'timeout', e['timeout'])
                backend.add_to_list('firewall', ipset_wan_section_name, 'entry', wan_iprange)

                rule_section_name = 'ip_filter_%s' % hashlib.md5(content).hexdigest()
                backend.add_section('firewall', 'rule', rule_section_name)
                backend.set_option('firewall', rule_section_name, 'target', 'DROP')
                backend.set_option('firewall', rule_section_name, 'enabled', store_bool(e['enabled']))
                backend.set_option('firewall', rule_section_name, 'ipset', '%s src' % ipset_lan_section_name)
                backend.set_option('firewall', rule_section_name, 'src_port', lan_portrange)
                backend.set_option('firewall', rule_section_name, 'ipset', '%s dest' % ipset_wan_section_name)
                backend.set_option('firewall', rule_section_name, 'dest_port', wan_portrange)
                backend.set_option('firewall', rule_section_name, 'proto', proto)
                '''

                rule_section_name = 'ip_filter_%s' % hashlib.md5(content).hexdigest()
                backend.add_section('firewall', 'rule', rule_section_name)
                backend.set_option('firewall', rule_section_name, 'target', 'DROP')
                backend.set_option('firewall', rule_section_name, 'enabled', store_bool(e['enabled']))
                backend.set_option('firewall', rule_section_name, 'src', 'lan')
                backend.set_option('firewall', rule_section_name, 'src_ip', lan_iprange)
                backend.set_option('firewall', rule_section_name, 'src_port', lan_portrange)
                backend.set_option('firewall', rule_section_name, 'dest', 'wan')
                backend.set_option('firewall', rule_section_name, 'dest_ip', wan_iprange)
                backend.set_option('firewall', rule_section_name, 'dest_port', wan_portrange)
                backend.set_option('firewall', rule_section_name, 'proto', proto)
                #backend.set_option('firewall', rule_section_name, 'timeout', e['timeout'])

        with OpenwrtServices() as services:
            services.restart("firewall", delay=2)

        return True

    @logger_wrapper(logger)
    def set_mac_filter(self, data):
        with UciBackend() as backend:
            cfg = backend.read('firewall')
            rules = get_sections_by_type(cfg, 'firewall', 'rule')

            for e in rules:
                if e['name'].startswith('mac_filter_'):
                    backend.del_section('firewall', e['name'])

            for e in data['mac_filter_table']:
                zone = 'lan'
                content = '%s_%s' % (zone, e['mac'])
                section_name = 'mac_filter_%s' % hashlib.md5(content).hexdigest()
                backend.add_section('firewall', 'rule', section_name)
                backend.set_option('firewall', section_name, 'target', 'REJECT')
                backend.set_option('firewall', section_name, 'proto', 'all')
                backend.set_option('firewall', section_name, 'enabled', store_bool(e['enabled']))
                backend.set_option('firewall', section_name, 'src', zone)
                backend.set_option('firewall', section_name, 'src_mac', e['mac'])
                backend.set_option('firewall', section_name, 'name', e['desc'])

        with OpenwrtServices() as services:
            services.restart("network", delay=2)

        return True
