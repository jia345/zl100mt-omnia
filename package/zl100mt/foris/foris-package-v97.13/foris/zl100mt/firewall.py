#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Tue Apr 30 11:27:42 2019

@author: jia345
"""

from foris.state import current_state

class SetFirewallCmd():
    def implement(self, data, session):
        res = current_state.backend.perform("firewall", "setFirewall", data)
        return res

class SetIpFilterCmd():
    def implement(self, data, session):
        res = current_state.backend.perform("firewall", "setIpFilter", data)
        return res

class SetMacFilterCmd():
    def implement(self, data, session):
        res = current_state.backend.perform("firewall", "setMacFilter", data)
        return res

cmdSetFirewall = SetFirewallCmd()
cmdSetIpFilter = SetIpFilterCmd()
cmdSetMacFilter = SetMacFilterCmd()