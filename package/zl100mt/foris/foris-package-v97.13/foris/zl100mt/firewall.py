from foris.state import current_state

class GetSettingsCmd():
    def implement(self, data, session):
        res = current_state.backend.perform('firewall', 'get_settings', data)
        return res

class SetFirewallCmd():
    def implement(self, data, session):
        msg = {
                'ip_filter_enabled': True if data['dat']['FireWall']['ipFilter'] == 'on' else False,
                'mac_filter_enabled': True if data['dat']['FireWall']['macFilter'] == 'on' else False,
                'dmz_enabled': True if data['dat']['FireWall']['DMZ']['Status'] == 'on' else False,
                'dmz_ip': data['dat']['FireWall']['DMZ']['IP']
        }
        res = current_state.backend.perform('firewall', 'set_firewall', msg)
        return res

class SetIpFilterCmd():
    def implement(self, data, session):
        ip_list = []
        for ip in data['dat']['FireWall']['ipList']:
            item = {
                    'timeout': ip['Validation'],
                    'lan_ip': ip['LanIPs'],
                    'lan_port': ip['LanPort'],
                    'wan_ip': ip['WLanIPs'],
                    'wan_port': ip['WLanPort'],
                    'protocol': ip['Protocol'],
                    'enabled': True if ip['Status'] == 'Enable' else False
            }
            ip_list.append(item)
        msg = { 'ip_list': ip_list }
        res = current_state.backend.perform('firewall', 'set_ip_filter', msg)
        return res

class SetMacFilterCmd():
    def implement(self, data, session):
        mac_list = []
        for mac in data['dat']['FireWall']['macList']:
            item = {
                    "mac": mac['MAC'],
                    'enabled': True if mac['Status'] == 'Enable' else False,
                    "desc": mac['Desc']
            }
            mac_list.append(item)
        msg = { 'mac_list': mac_list }
        res = current_state.backend.perform('firewall', 'set_mac_filter', msg)
        return res

cmdGetFirewall = GetSettingsCmd()
cmdSetFirewall = SetFirewallCmd()
cmdSetIpFilter = SetIpFilterCmd()
cmdSetMacFilter = SetMacFilterCmd()