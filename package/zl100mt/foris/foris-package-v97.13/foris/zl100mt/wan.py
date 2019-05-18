from foris.state import current_state

class GetSettingsCmd():
    def implement(self, session):
        res = current_state.backend.perform('network', 'get_settings', {})

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

class SetWanCmd():
    def implement(self, data, session):
        msg = {
                'ip_filter_enabled': True if data['dat']['FireWall']['ipFilter'] == 'on' else False,
                'mac_filter_enabled': True if data['dat']['FireWall']['macFilter'] == 'on' else False,
                'dmz_enabled': True if data['dat']['FireWall']['DMZ']['Status'] == 'on' else False,
                'dmz_ip': data['dat']['FireWall']['DMZ']['IP']
        }
        res = current_state.backend.perform('firewall', 'set_firewall', msg)
        return res

cmdGetWan = GetSettingsCmd()
cmdSetWanOnOff = SetWanCmd()

