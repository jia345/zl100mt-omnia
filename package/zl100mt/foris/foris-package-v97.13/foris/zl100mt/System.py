import bottle, os, ubus
from foris.state import current_state
from foris.zl100mt.wan import cmdGetLteZ, cmdGetLte4G
from foris.zl100mt.gnss import cmdGetGnssInfo
from foris.zl100mt.dhcp import cmdDhcpCfg
from foris.zl100mt.rtmp import cmdGetRtmpInfo
from foris.zl100mt.Routing import cmdGetRoutingInfo 
from foris.zl100mt.firewall import cmdGetFirewall
from foris.zl100mt.portmapping import channelmapping,setportmapping
from foris.zl100mt.ipmacbind import cmdIpmacbind

class SysReboot():
    def __init__(self):
        self.action = 'reBoot'
        self.default_data = {}

    def implement(self, data,session=None):
        ret = current_state.backend.perform("maintain", "reboot", {})
        res = {"rc": 0, "errCode": "success", "dat": None}
        if bottle.request.is_xhr:
            # return a list of ip addresses where to connect after reboot is performed
            res = bottle.response.copy(cls=bottle.HTTPResponse)
            res.content_type = 'application/json'
            res.body = json.dumps(ret)
            res.status = 200
            raise res
        else:
            bottle.redirect(reverse("/"))
        return res

#class NtpSyncDatetime():
#    def __init__(self):
#        self.action = 'syncDatetime'
#        self.default_data = {}
#
#    def implement(self, data,session=None):
#        cfg = {
#            "city": "Shanghai",
#            "region": "Asia",
#            "timezone": "CST-8",
#            "time_settings": {
#                "how_to_set_time": "ntp",
#            }
#        }
#        rc = current_state.backend.perform("time", "update_settings", cfg)
#        print rc
#        rc = current_state.backend.perform("time", "ntpdate_trigger", {})
#        print rc
#        getdata = current_state.backend.perform("time", "get_settings", {})
#        print getdata
#        res = {
#            "rc": 0,
#            "errCode": "success",
#            "dat": {"localDatetime": getdata["time_settings"]["time"]}
#        }
#
#        return res

class GetLogLinkCmd():
    def implement(self, data, session=None):
        res = current_state.backend.perform("maintain", "get_log_links", {})
        return res

class GetSysInfoCmd():
    def implement(self, session=None):
        system = ubus.call('system', 'info', {})[0]
        print 'xijia sys %s' % system
        version = os.popen('cat /etc/zl100mt-version').read().splitlines()[0]
        return {
            'localDatetime': system['localtime'] * 1000,
            'currDuration': system['uptime'] * 1000,
            'hwIMEI': '---todo---',
            'hostIP': '192.168.3.1',
            'swVersion': version
        }

class NtpSyncDatetime():
    def __init__(self):
        self.action = 'syncDatetime'
        self.default_data = {}

    def implement(self, data,session=None):
        #rc = current_state.backend.perform("zl100mt-ntp", "refresh", {'server_ip': data['serverIP'] if 'serverIP' in data else '210.72.145.44'})
        rc = ubus.call("zl100mt-ntp", "refresh", {'server_ip': ''})[0]
        res = {
            "rc": 0,
            "errCode": "success",
            "dat": {"localDatetime": rc["time"]}
        }

        return res

class GetNtpServerIpCmd():
    def implement(self, session=None):
        #rc = ubus.call("zl100mt-ntp", "refresh", {'server_ip':'xxx'})[0]
        return {
            'serverIP': '210.72.145.44'
        }

class GetNetworkCfgInfoCmd():
    def implement(self, handle, session):
        routingItf = {
            'dat': {
                'modulType': 'lte-z'
            }
        }
        data = {
            "GNSS": {
                "connection":"on",
                "signal":"1.01",
                "satelliteNum":"9",
                "totalMsg":"4531", 
                "succMsg":"4500",
                "failMsg":"31", 
                "targetSim":"01897",
                "localSim":"02654"
            },
            "LAN": cmdDhcpCfg.get_lan_cfg(),
            "RTMP": cmdGetRtmpInfo.implement(session),
            "VPN":{
                "vpnAddress":"124.1.2.1/vpn/",
                "vpnUser":"zhang",
                "vpnPwd":"zhangpwd",
                "vpnProtocol":"L2TP", # PPTP or L2TP/IPSec
                "vpnKey":"34sd4",
                "vpnStatus":"on"
            },
            "routing": cmdGetRoutingInfo.implement(routingItf, session),
            "FireWall": cmdGetFirewall.implement(session),
            "Mapping":{
                "slotLTEZ":channelmapping.get_slotLTEZ(),
                "slotLTE4G":channelmapping.get_slotLTE4G(),
                "mac2ip": cmdIpmacbind.get_ip2mac(),
                "portMapping":setportmapping.get_portmapping(),
            },
        }

        res = {
                "rc": 0,
                "errCode": "success",
                "dat": data
              }
        return res

class GetHostStatusInfoCmd():
    def implement(self, handle,session):
        data = {
            "system": cmdGetSysInfo.implement(session),
            "LTEZ": cmdGetLteZ.implement(session),
            "LTE4G": cmdGetLte4G.implement(session),
            "GNSS": {
                "connection":"on",
                "signal":"1.01",
                "satelliteNum":"9",
                "totalMsg":"4531", 
                "succMsg":"4500",
                "failMsg":"31", 
                "targetSim":"01897",
                "localSim":"02654"
            },
            "LAN": cmdDhcpCfg.get_lan_cfg(),
            "DHCP": cmdDhcpCfg.get_dhcp(),
            "NTP": { "serverIP":"10.1.1.12" }
        }

        res = {
                "rc": 0,
                "errCode": "success",
                "dat": data
              }
        return res

class GetAllSysInforCmd() :
    def __init__(self) :
        self.action = 'getSysInfor'
        self.default_data = {}

    def implement(self, handle,session):
        data = {
            "system": cmdGetSysInfo.implement(session),
            "LTEZ": cmdGetLteZ.implement(session),
            "LTE4G": cmdGetLte4G.implement(session),
            "GNSS": {
                "connection":"on",
                "signal":"1.01",
                "satelliteNum":"9",
                "totalMsg":"4531", 
                "succMsg":"4500",
                "failMsg":"31", 
                "targetSim":"01897",
                "localSim":"02654"
            },
            "DHCP": cmdDhcpCfg.get_dhcp(),
            "LAN": cmdDhcpCfg.get_lan_cfg(),
            "RTMP": cmdGetRtmpInfo.implement(session),
            "VPN":{
                "vpnAddress":"124.1.2.1/vpn/",
                "vpnUser":"zhang",
                "vpnPwd":"zhangpwd",
                "vpnProtocol":"L2TP", # PPTP or L2TP/IPSec
                "vpnKey":"34sd4",
                "vpnStatus":"on"
            }, # on/off
            "FireWall": cmdGetFirewall.implement(session),
            "Mapping":{
                "slotLTEZ":channelmapping.get_slotLTEZ(), # LAN value: on or off
                "slotLTE4G":channelmapping.get_slotLTE4G(),
                "mac2ip": cmdIpmacbind.get_ip2mac(),
                "portMapping":setportmapping.get_portmapping(),
            },
            #"NTP": cmdGetNtpServerIp.implement(session)
            "NTP": { "serverIP":"10.1.1.12" }
        }
        '''
        data = {
            "system": cmdGetSysInfo.implement(session),
            "LTEZ": cmdGetLteZ.implement(session),
            "LTE4G": cmdGetLte4G.implement(session),
            "GNSS": cmdGetGnssInfo.implement(session),
            "DHCP": cmdDhcpCfg.get_dhcp(),
            "LAN": cmdDhcpCfg.get_lan_cfg(),
            "RTMP": cmdGetRtmpInfo.implement(session),
            "VPN":{
                "vpnAddress":"124.1.2.1/vpn/",
                "vpnUser":"zhang",
                "vpnPwd":"zhangpwd",
                "vpnProtocol":"L2TP", # PPTP or L2TP/IPSec
                "vpnKey":"34sd4",
                "vpnStatus":"on"
            }, # on/off
            "FireWall": cmdGetFirewall.implement(session),
            "Mapping":{
                "slotLTEZ":channelmapping.get_slotLTEZ(), # LAN value: on or off
                "slotLTE4G":channelmapping.get_slotLTE4G(),
                "mac2ip": cmdIpmacbind.get_ip2mac(),
                "portMapping":setportmapping.get_portmapping(),
            },
            #"NTP": cmdGetNtpServerIp.implement(session)
            "NTP": { "serverIP":"10.1.1.12" }
        }
        '''

        res = {
                "rc": 0,
                "errCode": "success",
                "dat": data
              }
        return res

cmdGetAllSysInfo = GetAllSysInforCmd()
cmdReboot = SysReboot()
cmdTime = NtpSyncDatetime()
cmdGetLogLink = GetLogLinkCmd()
cmdGetSysInfo = GetSysInfoCmd()
cmdGetNtpServerIp = GetNtpServerIpCmd()
cmdGetHostStatusInfo = GetHostStatusInfoCmd()
cmdGetNetworkCfgInfo = GetNetworkCfgInfoCmd()
