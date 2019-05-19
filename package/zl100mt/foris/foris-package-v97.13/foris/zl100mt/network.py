
from foris.state import current_state

def validate_ip(s):
    a = s.split('.')
    if len(a) != 4:
        return False
    for x in a:
        if not x.isdigit():
            return False
        i = int(x)
        if i < 0 or i > 255:
            return False
    return True

class NetworkCmd():
    def implement(self, data, session):
        dhcp_data = data['dat']['DHCP']
        is_good_gw = validate_ip(dhcp_data['defaultGwIP']) or (dhcp_data['defaultGwIP'] == '')
        is_good_netmask = validate_ip(dhcp_data['subMask'])
        is_good_start_ip = validate_ip(dhcp_data['startIP'])
        is_good_end_ip = validate_ip(dhcp_data['endIP'])
        is_good_dns1_ip = validate_ip(dhcp_data['DNS1']) or (dhcp_data['DNS1'] == '')
        is_good_dns2_ip = validate_ip(dhcp_data['DNS2']) or (dhcp_data['DNS2'] == '')
        is_good_ip = (is_good_gw and is_good_netmask and is_good_start_ip
                        and is_good_end_ip and is_good_dns1_ip and is_good_dns2_ip)
        is_good_leasetime = dhcp_data['leaseTerm'].isdigit()

        if not is_good_ip:
            return {'rc': 1, 'errCode': 'fail', 'dat': 'Wrong IP format'}
        if not is_good_leasetime:
            return {'rc': 2, 'errCode': 'fail', 'dat': 'Wrong lease time'}

        dhcpCfg = {
            'ignore': 0 if dhcp_data['dhcpStatus']=='DHCP' else 1,
            'start_ip': dhcp_data['startIP'],
            'end_ip': dhcp_data['endIP'],
            'netmask': dhcp_data['subMask'],
            'leasetime_m': int(dhcp_data['leaseTerm']),
            'gw_ip': dhcp_data['defaultGwIP'],
            'dns1': dhcp_data['DNS1'],
            'dns2': dhcp_data['DNS2']
        }

        rc = current_state.backend.perform('dhcp', 'update_settings', {'dhcp_cfg': dhcpCfg})
        res = {'rc': 0, 'errCode': 'success', 'dat': None} if rc['result'] else {'rc': 1, 'errCode': 'fail', 'dat': 'Wrong parameters'}
        return res

    def get_dhcp(self):
        data = current_state.backend.perform('dhcp', 'get_settings', {})
        dhcp_data = data['dhcp_cfg']

        dhcp = {
            'dhcpStatus': 'Statics' if dhcp_data['ignore'] else 'DHCP',
            'startIP': dhcp_data['start_ip'],
            'endIP': dhcp_data['end_ip'],
            'leaseTerm': dhcp_data['leasetime_m'],
            'subMask': dhcp_data['netmask'],
            'defaultGwIP': dhcp_data['gw_ip'],
            'DNS1': dhcp_data['dns1'],
            'DNS2': dhcp_data['dns2']
        }

        return dhcp

    def get_lan_cfg(self):
        data        = current_state.backend.perform('dhcp', 'get_lan_cfg', {})
        lan_info    = []
        access_info = []

        for e in data['lan_cfg']:
            lan_info.append({
                'port': e['port'],
                'MAC': e['mac'],
                'IP': e['ip'],
                'subMask': e['netmask']
            })

        for e in data['access_list']:
            access_info.append({
                'port': e['port'],
                'MAC': e['mac'],
                'IP': e['ip'],
                'type': e['type']
            })

        res = {
            'LAN': lan_info,
            'accessList': access_info
        }

        return res

cmdNetworkCfg = NetworkCmd()
