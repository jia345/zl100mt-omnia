from foris.state import current_state
import ubus, logging

logger = logging.getLogger(__name__)

class GetGnssInfoCmd():
    def implement(self, session):
        res = ubus.call('zl100mt', 'get_gnss_info', {})[0]
        if res['result'] == 'ok':
            data = {
                'rc': 0,
                'errCode': 'success',
                'GPS': {
                    'altitude': res['altitude'],
                    'longitude': res['longitude'],
                    'latitude': res['latitude'],
                    'heading': res['heading'],
                    'speed': res['speed']
                },
                'beam1': res['beam1'],
                'beam2': res['beam2'],
                'beam3': res['beam3'],
                'beam4': res['beam4'],
                'beam5': res['beam5'],
                'beam6': res['beam6'],
                'connection': res['connection'],
                'failMsg': res['failMsg'],
                'localSim': res['localSim'],
                'satelliteNum': res['satelliteNum'],
                'signal': res['signal'],
                'succMsg': res['succMsg'],
                'targetSim': res['targetSim'],
                'totalMsg': res['totalMsg']
            }
            return data
        else:
            return {'rc': 1, 'errCode': 'failure', 'dat': None}

class SetGnssRemoteCmd():
    def implement(self, data, session):
        remote_sim_no = data['dat']['GNSS']['targetSim']
        if remote_sim_no.isdigit():
            #res = current_state.backend.perform('gnss', 'update_settings', { 'remote_sim_no': data['dat']['GNSS']['targetSim'] })
            msg = { 'target_sim': int(remote_sim_no) }
            res = ubus.call('zl100mt', 'set_gnss_target_sim', msg)[0]
            return {'rc': 0, 'errCode': 'success', 'dat': None} if (res['result'] == 'ok') else {'rc': 1, 'errCode': 'failure', 'dat': None}
        else:
            return {'rc': 1, 'errCode': 'failure', 'dat': None}

cmdGnssSetRemoteCfg = SetGnssRemoteCmd()
cmdGetGnssInfo = GetGnssInfoCmd()
