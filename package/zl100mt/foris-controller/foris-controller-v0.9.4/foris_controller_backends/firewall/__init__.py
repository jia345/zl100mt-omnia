import logging

from foris_controller_backends.uci import (
    UciBackend, get_option_anonymous, get_option_named, parse_bool, store_bool, get_sections_by_type
)
from foris_controller_backends.services import OpenwrtServices
from foris_controller.exceptions import UciRecordNotFound
from foris_controller.utils import logger_wrapper

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logging.basicConfig(filename='/var/log/backend.log')

class FirewallUciCommands(object):

    @logger_wrapper(logger)
    def get_settings(self):
        '''
        with UciBackend() as backend:
            dhcp_data = backend.read("dhcp")
            hosts = get_sections_by_type(dhcp_data, "dhcp", "host")

        ipmacbinds = []
        for host in hosts:
            ipmacbinds.append(host['data'])
        print ipmacbinds

        res = {
            "ipmac_binds": ipmacbinds
        }
        '''
        logger.debug('firewall get_settings')

        #return res

    @logger_wrapper(logger)
    def set_firewall(self, data):
        '''
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
        '''
        logger.debug('firewall set_firewall')
        return True

    @logger_wrapper(logger)
    def set_ip_filter(self, data):
        '''
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
        '''
        logger.debug('firewall set_ip_filter')
        return True

    @logger_wrapper(logger)
    def set_mac_filter(self, data):
        '''
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
        '''
        logger.debug('firewall set_mac_filter')
        return True