from foris.state import current_state

class GetSettingsCmd():
    def implement(self, session):
        res = current_state.backend.perform('firewall', 'get_settings', {})

        ipList = []
        for e in res['ip_filter_table']:
            item = {
                'Validation': e['timeout'],
                'LanIPs': e['lan_ips'],
                'LanPort': e['lan_ports'],
                'WLanIPs': e['wan_ips'],
                'WLanPort': e['wan_ports'],
                'Protocol': e['proto'],
                'Status': 'enabled' if e['enabled'] else 'disabled',
            }
            ipList.append(item)

        macList = []
        for e in res['mac_filter_table']:
            item = {
                'Desc': e['desc'],
                'MAC': e['mac'],
                'Status': 'enabled' if e['enabled'] else 'disabled',
            }
            macList.append(item)

        settings = {
            'ipFilter': 'on' if res['ip_filter_enabled'] else 'off',
            'macFilter': 'on' if res['mac_filter_enabled'] else 'off',
            'DMZ': {
                'IP': res['dmz_ip'],
                'Status': 'on' if res['dmz_enabled'] else 'off'
            },
            'ipList': ipList,
            'macList': macList 
        }
        return settings

class SetFirewallCmd():
    def implement(self, data, session):
        msg = {
                'ip_filter_enabled': True if data['dat']['FireWall']['ipFilter'] == 'on' else False,
                'mac_filter_enabled': True if data['dat']['FireWall']['macFilter'] == 'on' else False,
                'dmz_enabled': True if data['dat']['FireWall']['DMZ']['Status'] == 'on' else False,
                'dmz_ip': data['dat']['FireWall']['DMZ']['IP'] if data['dat']['FireWall']['DMZ']['IP'] else '10.10.10.11'
        }
        rc = current_state.backend.perform('firewall', 'set_firewall', msg)['result']
        res = {'rc': 0, 'errCode': 'success', 'dat': None} if rc else {'rc': 1, 'errCode': 'Wrong parameter, please check your input', 'dat': 'Wrong parameters'}
        return res

class SetIpFilterCmd():
    def implement(self, data, session):
        ip_filter_table = []
        for ip in data['dat']['FireWall']['ipList']:
            item = {
                    'timeout': int(ip['Validation']),
                    'lan_ips': ip['LanIPs'],
                    'lan_ports': ip['LanPort'],
                    'wan_ips': ip['WLanIPs'],
                    'wan_ports': ip['WLanPort'],
                    'proto': ip['Protocol'],
                    'enabled': True if ip['Status'] == 'Enable' else False
            }
            ip_filter_table.append(item)
        msg = { 'ip_filter_table': ip_filter_table }
        rc = current_state.backend.perform('firewall', 'set_ip_filter', msg)['result']
        res = {'rc': 0, 'errCode': 'success', 'dat': None} if rc else {'rc': 1, 'errCode': 'fail', 'dat': 'Wrong parameters'}
        return res

class SetMacFilterCmd():
    def implement(self, data, session):
        mac_filter_table = []
        for mac in data['dat']['FireWall']['macList']:
            item = {
                    'mac': mac['MAC'],
                    'enabled': True if mac['Status'] == 'Enable' else False,
                    'desc': mac['Desc']
            }
            mac_filter_table.append(item)
        msg = { 'mac_filter_table': mac_filter_table }
        rc = current_state.backend.perform('firewall', 'set_mac_filter', msg)['result']
        res = {'rc': 0, 'errCode': 'success', 'dat': None} if rc else {'rc': 1, 'errCode': 'fail', 'dat': 'Wrong parameters'}
        return res

cmdGetFirewall = GetSettingsCmd()
cmdSetFirewall = SetFirewallCmd()
cmdSetIpFilter = SetIpFilterCmd()
cmdSetMacFilter = SetMacFilterCmd()

