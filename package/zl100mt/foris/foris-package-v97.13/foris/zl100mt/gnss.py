from foris.state import current_state

class GetGnssSettingsCmd():
    def implement(self, data, session):
        res = {'rc': 0, 'errCode': 'success', 'dat': None}
        return res

class SetGnssRemoteCmd():
    def implement(self, data, session):
        remote_sim_no = data['dat']['GNSS']['targetSim']
        if remote_sim_no.isdigi():
            res = current_state.backend.perform('gnss', 'update_settings', { 'remote_sim_no': data['dat']['GNSS']['targetSim'] })
            return {'rc': 0, 'errCode': 'success', 'dat': None} if res else {'rc': 1, 'errCode': 'failure', 'dat': None}
        else:
            return {'rc': 1, 'errCode': 'failure', 'dat': None}

cmdGnssSetRemoteCfg = SetGnssRemoteCmd()
