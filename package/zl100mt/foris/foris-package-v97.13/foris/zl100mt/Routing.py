from foris.zl100mt.ipmacbind import cmdIpmacbind
from foris.zl100mt.portmapping import channelmapping,setportmapping
from foris.zl100mt.dhcp import cmdDhcpCfg
from foris.zl100mt.rtmp import cmdGetRtmpInfo
from foris.zl100mt.firewall import cmdGetFirewall

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
            "system": {
                "localDatetime":"1531817800000", # ms
                "currDuration":"17800000",
                "hwIMEI": "1.0.1",
                "swVersion":"1.1.0"
                },
            "LTEZ":{
                "type":"LTE-Z",
                "connection":"on",
                "signal":"1.2",
                "wlanIP":"10.1.1.100",
                "defaultGwIP":"10.2.1.1",
                "mDnsIP":"10.2.1.1",
                "sDnsIP":"10.2.1.2",
                "MAC":"12-43-54",
                "usim":"Ready", # Ready or Invalid
                "IMSI":"08509123",
                "PLMN":"18509123",
                "frq":"23.7",
                "RSRQ":"3.2",
                "SNR":"1.03"
                },
            "LTE4G":{
                "type":"LTE-4G",
                "connection":"on",
                "signal":"1.2",
                "wlanIP":"10.1.1.109",
                "defaultGwIP":"10.2.1.1",
                "mDnsIP":"10.2.1.1",
                "sDnsIP":"10.2.1.2",
                "MAC":"32-43-54",
                "usim":"Invalid",
                "IMSI":"08509123",
                "PLMN":"9854509123",
                "frq":"73.32",
                "RSRQ":"33.2",
                "SNR":"2.03"
                },
            "GNSS":{
                "connection":"on",
                "signal":"1.01",
                "satelliteNum":"9", "totalMsg":"4531",
                "succMsg":"4500", "failMsg":"31",
                "targetSim":"01897", "localSim":"02654"
                },
            "DHCP":cmdDhcpCfg.get_dhcp(),
            "LAN": cmdDhcpCfg.get_lan_cfg(),
            "RTMP": cmdGetRtmpInfo.implement(session),
            "VPN":{
                "vpnAddress":"124.1.2.1/vpn/", "vpnUser":"zhang", "vpnPwd":"zhangpwd",
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
              }

        res = {
                "rc": 0,
                "errCode": "success",
                "dat": data
              }
        return res

cmdSysInfor = GetSysInforCmd()

