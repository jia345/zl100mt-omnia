#!/usr/bin/python  
# -*- coding: utf-8 -*-

from foris.state import current_state
import ubus

def get_4g_frq(band):
    ts_band = {
        "00080000":"GSM 850",
        "00000080":"GSM DCS systems",
        "00000100":"Extended GSM 900",
        "00000200":"Primary GSM 900",
        "00100000":"Railway GSM 900",
        "00200000":"GSM PCS",
        "3FFFFFFF":"任何频带",
        "40000000":"频带不变化",
        "2000000" :"AWS",
        "00680380":"自动"
    }
    if ts_band.has_key(band):
        return ts_band[band]
    else:
        return "----"

def get_rc_data(rc, key):
    if rc.has_key(key):
        return rc[key]
    else:
        return "----"

def get_ip(v):
    if v == '--' or v == '----':
        return '----'
    num=len(v)/2
    data=[]
    i=0
    addr=v[-2:]
    while i<num:
        data.append(str(int(addr,16)))
        i+=1
        addr=v[-2-2*i:-2*i]
    return '.'.join(data)

class GetLteZCmd():
    def implement(self, session):
        rc = ubus.call('zl100mt-rpcd', 'get_lte_z', {})[0]
        print rc
        return {
            'type': 'LTE-Z',
            'connection': "on" if get_rc_data(rc,'connection_status')=="2" else "off",
            'signal': get_rc_data(rc,'signal_strength') if get_rc_data(rc,'connection_status')=="2" else "n/a",
            'wlanIP': rc['ipaddr'] if 'ipaddr' in rc else '----',
            'defaultGwIP': rc['gw'] if 'gw' in rc else '----',
            'mDnsIP': rc['dns1'] if 'dns1' in rc else '----',
            'sDnsIP': rc['dns2'] if 'dns2' in rc else '----',
            'MAC': 'N/A',
            'usim': rc['sim_status'] if 'sim_status' in rc else '----',
            'IMSI': rc['imsi'] if 'imsi' in rc else '----',
            'PLMN': rc['plmn'] if 'plmn' in rc else '----',
            'frq': rc['band'] if 'band' in rc else '----',
            'RSRQ': rc['rsrq'] if 'rsrq' in rc else '----',
            'SNR': rc['snr'] if 'snr' in rc else '----'
        }

class GetLte4GCmd():
    def implement(self, session):
        rc = ubus.call('zl100mt-rpcd', 'get_lte_4g', {})[0]
        print rc
        return {
            'type': 'LTE-4G',
            'connection': "on" if get_rc_data(rc,'connection_status')=="1" else "off",
            'signal': get_rc_data(rc,'signal_strength') if get_rc_data(rc,'connection_status')=="1" else "n/a",
            'wlanIP': get_ip(get_rc_data(rc,'ipaddr')),
            'defaultGwIP': get_ip(get_rc_data(rc,'gw')),
            'mDnsIP': get_ip(get_rc_data(rc,'dns1')),
            'sDnsIP': get_ip(get_rc_data(rc,'dns2')),
            'MAC': 'N/A',
            'usim': get_rc_data(rc,'sim_status'),
            'IMSI': get_rc_data(rc,'imsi'),
            'PLMN': get_rc_data(rc,'plmn'),
            'frq': get_4g_frq(get_rc_data(rc,'band')),
            'RSRQ': get_rc_data(rc,'rsrq'),
            'SNR': get_rc_data(rc,'snr')
        }

class SetWanCmd():
    def implement(self, data, session):
        msg = {
                'interface': data['dat']['modulType'].lower().replace('-', '_'),
                'on': 1 if data['dat']['operation'].lower() == 'on' else 0
        }
        rc = ubus.call('zl100mt-rpcd', 'set_interface_on', msg)[0]
        return {
            'rc': 0,
            'errCode': ''
        }

cmdGetLteZ = GetLteZCmd()
cmdGetLte4G = GetLte4GCmd()
cmdSetWanOnOff = SetWanCmd()

