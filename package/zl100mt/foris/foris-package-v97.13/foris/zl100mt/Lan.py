
from foris.state import current_state

class LanCmd():
    def __init__(self):
        self.action = 'setMacIPMapping'
        self.default_data = {}

    def implement(self, data, session):
        hosts = []
        for host in data['dat']['Mapping']['mac2ip']:
            hosts.append({
                "ip": host['IP'],
                "mac": host['MAC'],
                "name": host['Desc']
            })
        print hosts
        rc = current_state.backend.perform("ipmacbind", "update_settings", {"ipmac_binds":hosts})
        print rc
        res = {"rc": 0, "errCode": "success", "dat": None}
        return res

    def get_ip2mac(self):
        data = current_state.backend.perform("ipmacbind", "get_settings", {})
        ip2macs = []
        for host in data["ipmac_binds"]:
            ip2macs.append({
                "MAC": host['mac'],
                "IP": host['ip'],
                "Desc": host['name'] if "name" in host.keys() else ''
            })
        print ip2macs
        return ip2macs

cmdLanCfg = LanCmd()
