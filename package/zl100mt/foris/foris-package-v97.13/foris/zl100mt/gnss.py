from foris.state import current_state
import ubus, logging

logger = logging.getLogger(__name__)

class GetGnssInfoCmd():
    def implement(self, session):
        return ubus.call('zl100mt', 'get_gnss_info', {})[0]

class SetGnssRemoteCmd():
    def implement(self, data, session):
        remote_sim_no = data['dat']['GNSS']['targetSim']
        logger.debug('xijia gnss %s' % remote_sim_no)
        if remote_sim_no.isdigit():
            #res = current_state.backend.perform('gnss', 'update_settings', { 'remote_sim_no': data['dat']['GNSS']['targetSim'] })
            msg = { 'target_sim': int(remote_sim_no) }
            res = ubus.call('zl100mt', 'set_gnss_target_sim', msg)[0]
            return {'rc': 0, 'errCode': 'success', 'dat': None} if (res['result'] == 'ok') else {'rc': 1, 'errCode': 'failure', 'dat': None}
        else:
            return {'rc': 1, 'errCode': 'failure', 'dat': None}

cmdGnssSetRemoteCfg = SetGnssRemoteCmd()
cmdGetGnssInfo = GetGnssInfoCmd()
