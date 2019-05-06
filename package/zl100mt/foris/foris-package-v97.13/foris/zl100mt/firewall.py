from foris.state import current_state

class GetSettingsCmd():
    def implement(self, data, session):
        res = current_state.backend.perform("firewall", "get_settings", data)
        return res

class SetFirewallCmd():
    def implement(self, data, session):
        res = current_state.backend.perform("firewall", "set_firewall", data)
        return res

class SetIpFilterCmd():
    def implement(self, data, session):
        res = current_state.backend.perform("firewall", "set_ip_filter", data)
        return res

class SetMacFilterCmd():
    def implement(self, data, session):
        res = current_state.backend.perform("firewall", "set_mac_filter", data)
        return res

cmdGetFirewall = GetSettingsCmd()
cmdSetFirewall = SetFirewallCmd()
cmdSetIpFilter = SetIpFilterCmd()
cmdSetMacFilter = SetMacFilterCmd()