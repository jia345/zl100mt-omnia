from foris.state import current_state
import ubus

class GetLteZCmd():
    def implement(self, session):
        rc = ubus.call('wan', 'get_lte_z', {})[0]
        return {
            'type': 'LTE-Z',
            'connection': rc['connection_status'],
            'signal': rc['signal_strength'],
            'wlanIP': rc['ipaddr'],
            'defaultGwIP': rc['gw'],
            'mDnsIP': rc['dns1'],
            'sDnsIP': rc['dns2'],
            'MAC': 'N/A',
            'usim': rc['sim_status'],
            'IMSI': rc['imsi'],
            'PLMN': rc['plmn'],
            'frq': rc['band'],
            'RSRQ': rc['rsrq'],
            'SNR': rc['snr']
        }

class GetLte4GCmd():
    def implement(self, session):
        rc = ubus.call('wan', 'get_lte_4g', {})[0]
        return {
            'type': 'LTE-4G',
            'connection': rc['connection_status'],
            'signal': rc['signal_strength'],
            'wlanIP': rc['ipaddr'],
            'defaultGwIP': rc['gw'],
            'mDnsIP': rc['dns1'],
            'sDnsIP': rc['dns2'],
            'MAC': 'N/A',
            'usim': rc['sim_status'],
            'IMSI': rc['imsi'],
            'PLMN': rc['plmn'],
            'frq': rc['band'],
            'RSRQ': rc['rsrq'],
            'SNR': rc['snr']
        }

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

cmdGetLteZ = GetLteZCmd()
cmdGetLte4G = GetLte4GCmd()
cmdSetWanOnOff = SetWanCmd()

