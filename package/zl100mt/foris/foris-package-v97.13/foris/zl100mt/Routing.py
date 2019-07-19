from foris.zl100mt.ipmacbind import cmdIpmacbind
from foris.zl100mt.portmapping import channelmapping,setportmapping
from foris.zl100mt.dhcp import cmdDhcpCfg
from foris.zl100mt.rtmp import cmdGetRtmpInfo
from foris.zl100mt.firewall import cmdGetFirewall
from foris.zl100mt.System import cmdGetSysInfo, cmdGetNtpServerIp
from foris.zl100mt.gnss import cmdGetGnssInfo
from foris.zl100mt.wan import cmdGetLteZ, cmdGetLte4G

from foris.state import current_state

class RoutingInforCmd() :
    def __init__(self) :
        self.action = 'getRoutingInfor'
        self.default_data = {}

    def implement(self, data, session):
        print 'RoutingInforCmd: {}'.format(data)
        routes = []
        route = data["dat"]["routingData"]
        print 'routingData : {}'.format(route)
        routes.append({
            "interface": route["ifName"],
            "target": route["dstNet"],
            "netmask": route["subMask"],
            "gateway": route["gwIP"],
            "metric": int(route["Metric"])
        })
        if data['dat']['operation'] == "add" :
            action = "route_add"
        elif data['dat']['operation'] == "del":
            action = "route_del"
        else:
            return {"rc": 1, "errCode": "fail", "dat": 'Unsupported operation'}

        print routes
        rc = current_state.backend.perform("network", "update_settings", {"action": action, "routes":routes})
        print rc
        res = {"rc": 0, "errCode": "success", "dat": None}
        return res

    def get_routes(self):
        data = current_state.backend.perform("network", "get_settings", {})
        routes = []
        for route in data["routes"]:
            routes.append({
                "ifName": route['interface'],
                "dstNet": route["target"],
                "subMask": route["netmask"],
                "gwIp": route["gateway"],
                "Metric": route["metric"]
            })
        print routes
        return routes

cmdRoutingInfor = RoutingInforCmd()

class GetRoutingInforCmd() :
    def __init__(self) :
        self.action = 'getRoutingInfor'
        self.default_data = {}

    def implement(self, data, session):
        data = current_state.backend.perform(
            "network", "get_settings",
            {
                "action":"route",
                "data":{"interface": data['dat']['modulType'].lower()}
            })
        print 'GetRoutingInforCmd : \n'
        routes = []
        for route in data["data"]:
            routes.append({
                "ifName": route['interface'],
                "dstNet": route["target"],
                "subMask": route["netmask"],
                "gwIP": route["gateway"],
                "Metric": route["metric"]
            })
        print routes
        return  {"rc": 0, "errCode": "success", "dat": {"routing":routes}}

cmdGetRoutingInfo = GetRoutingInforCmd()

class GetSysInforCmd() :
    def __init__(self) :
        self.action = 'getSysInfor'
        self.default_data = {}

    def implement(self, handle,session):
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
            "NTP": cmdGetNtpServerIp.implement(session)
        }

        res = {
                "rc": 0,
                "errCode": "success",
                "dat": data
              }
        return res

cmdSysInfor = GetSysInforCmd()
