import logging

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
        dmz_ip = get_option_named(cfg, 'firewall', 'dmz_host', 'dest_ips')

        rules = get_sections_by_type(cfg, 'firewall', 'rule')
        ip_filter_data = [e['data'] for e in rules if e['name'].startswith('ip_filter_')]
        mac_filter_data = [e['data'] for e in rules if e['name'].startswith('mac_filter_')]

        ip_filter_table = [dict(d) for d in ip_filter_data]
        mac_filter_table = [dict(d) for d in mac_filter_data]

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
                    backend.set_option('firewall', e['name'], 'enabled', data['ip_filter_enabled'])
                if e['name'].startswith('mac_filter_'):
                    backend.set_option('firewall', e['name'], 'enabled', data['mac_filter_enabled'])

            backend.set_option('firewall', 'global', 'ip_filter_enabled', data['ip_filter_enabled'])
            backend.set_option('firewall', 'global', 'mac_filter_enabled', data['mac_filter_enabled'])
            backend.set_option('firewall', 'dmz_host', 'dmz_enabled', data['enabled'])
            backend.set_option('firewall', 'dmz_host', 'dmz_ip', data['dest_ips'])

        with OpenwrtServices() as services:
            services.restart("network", delay=2)

        return True

    @logger_wrapper(logger)
    def set_ip_filter(self, data):
        with UciBackend() as backend:
            cfg = backend.read('firewall')
            rules = get_sections_by_type(cfg, 'firewall', 'rule')
            ipsets = get_sections_by_type(cfg, 'firewall', 'ipset')

            for e in rules:
                if e['name'].startswith('ip_filter_'):
                    backend.del_section('firewall', e['name'])

            for e in ipsets:
                if e['name'].startswith('ip_filter_ipset_'):
                    backend.del_section('firewall', e['name'])

            for e in data:
                for i in range(2):
                    lan_iprange, lan_portrange, wan_iprange, wan_portsrange, proto = e['lan_ips'], e['lan_ports'], e['wan_ips'], e['wan_ports'], e['proto']
                    content = '%s %s %s %s %s' % (lan_iprange, lan_portrange, wan_iprange, wan_portsrange, proto)
                    rule_section_name = 'ip_filter_%s' % hashlib.md5(content).hexdigest()
                    ipset_section_name = 'ip_filter_ipset_%s' % hashlib.md5(content).hexdigest()
                    backend.add_section('firewall', 'ipset', ipset_section_name)
                    backend.set_option('firewall', ipset_section_name, 'name', ipset_section_name)
                    backend.set_option('firewall', ipset_section_name, 'match', 'src_net')
                    backend.set_option('firewall', ipset_section_name, 'storage', 'hash')
                    backend.set_option('firewall', ipset_section_name, 'timeout', e['timeout'])
                    backend.add_to_list('firewall', ipset_section_name, 'iprange', '%s %s' % (lan_iprange, wan_iprange))
                    backend.add_to_list('firewall', ipset_section_name, 'portrange', '%s %s' % (lan_portrange, wan_portrange))

                    backend.add_section('firewall', 'rule', rule_section_name)
                    backend.set_option('firewall', rule_section_name, 'target', 'REJECT')
                    backend.set_option('firewall', rule_section_name, 'enabled', e['enabled'])
                    backend.set_option('firewall', rule_section_name, 'ipset', '%s src' % ipset_section_name)
                    backend.set_option('firewall', rule_section_name, 'ipset', '%s dest' % ipset_section_name)
                    backend.set_option('firewall', rule_section_name, 'proto', proto)
                    '''
                    if i == 0:
                        src_ips, src_portrange, dest_ips, dest_port, proto = e['lan_ip'], e['lan_port'], e['wan_ip'], e['wan_ports'], e['proto']
                    else:
                        src_ips, src_portrange, dest_ips, dest_port, proto = e['wan_ip'], e['wan_ports'], e['lan_ip'], e['lan_port'], e['proto']
                    content = '%s %s %s %s %s' % (src_ips, src_portrange, dest_ips, dest_port, proto)
                    section_name = 'ip_filter_%s' % hashlib.md5(content).hexdigest()
                    backend.add_section('firewall', 'rule', section_name)
                    backend.set_option('firewall', section_name, 'target', 'REJECT')
                    backend.set_option('firewall', section_name, 'enabled', e['enabled'])
                    backend.set_option('firewall', section_name, 'src_ips', src_ips)
                    backend.set_option('firewall', section_name, 'src_portrange', src_portrange)
                    backend.set_option('firewall', section_name, 'dest_ips', dest_ips)
                    backend.set_option('firewall', section_name, 'dest_port', dest_port)
                    backend.set_option('firewall', section_name, 'proto', proto)
                    '''
        with OpenwrtServices() as services:
            services.restart("network", delay=2)

        return True

    @logger_wrapper(logger)
    def set_mac_filter(self, data):
        with UciBackend() as backend:
            cfg = backend.read('firewall')
            rules = get_sections_by_type(cfg, 'firewall', 'rule')

            for e in rules:
                if e['name'].startswith('mac_filter_'):
                    backend.del_section('firewall', e['name'])

            for e in data:
                for i in range(2):
                    zone = 'lan' if i == 0 else 'wan'
                    content = '%s %s' % (zone, e['mac'])
                    section_name = 'mac_filter_%s' % hashlib.md5(content).hexdigest()
                    backend.add_section('firewall', 'rule', section_name)
                    backend.set_option('firewall', section_name, 'target', 'REJECT')
                    backend.set_option('firewall', section_name, 'proto', 'all')
                    backend.set_option('firewall', section_name, 'enabled', e['enabled'])
                    backend.set_option('firewall', section_name, 'src', zone)
                    backend.set_option('firewall', section_name, 'src_mac', e['mac'])
                    backend.set_option('firewall', section_name, 'name', e['desc'])

        with OpenwrtServices() as services:
            services.restart("network", delay=2)

        return True
