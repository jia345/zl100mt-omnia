from foris.zl100mt.ipmacbind import cmdIpmacbind
from foris.zl100mt.portmapping import channelmapping,setportmapping
from foris.zl100mt.dhcp import cmdDhcpCfg
from foris.zl100mt.fireall import cmdGetFirewall

from foris.state import current_state

class RoutingInforCmd() :
    def __init__(self) :
        self.action = 'getRoutingInfor'
        self.default_data = {}

    def implement(self, data, session):
        print 'RoutingInforCmd: {}'.format(data)
        routes = []
        if data['dat']['operation'] == "add" :
            route = data["dat"]["routingData"]
            print 'routingData : {}'.format(route)
            action = "route_add"
            if data["dat"]["operation"] == 'del':
                action = "route_del"
            else :
                action = "route_add"
            routes.append({
                "interface": route["ifName"],
                "target": route["dstNet"],
                "netmask": route["subMask"],
                "gateway": route["gwIP"],
                "metric": int(route["Metric"])
            })

        print routes
        rc = current_state.backend.perform("network", "update_settings", {"action": "route_add", "routes":routes})
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
                "data":{"interface": data['dat']['modulType']}
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
            "LAN":{
		"LAN":[
			{"port":"LAN1", "MAC":"01-21-09", "IP":"10.1.1.10", "subMask":"255.0.0.0"},
                	{"port":"LAN2", "MAC":"01-21-19", "IP":"10.1.1.12", "subMask":"255.255.0.0"},
                        {"port":"LAN3", "MAC":"01-21-29", "IP":"10.1.1.13", "subMask":"255.255.255.0"}
                     ],
                "accessList":[
                        {"port":"LAN3","MAC":"01-29-03", "IP":"128.0.1.2", "type":"xiaomi"},
                        {"port":"LAN1","MAC":"01-29-04", "IP":"128.0.1.22", "type":"ibm"},
                        {"port":"LAN2","MAC":"01-29-05", "IP":"128.0.1.12", "type":"pc"}
                     ]
                },
            "RTMP":{
                "ServerIP":"10.1.1.12",
                "channelList":[
                        {"Name":"Cam01", "Code":"left-1"},
                        {"Name":"Cam02", "Code":"right-1"},
                        {"Name":"Cam03", "Code":"top-2"}
                     ]
                },
            "VPN":{
                "vpnAddress":"124.1.2.1/vpn/", "vpnUser":"zhang", "vpnPwd":"zhangpwd",
                "vpnProtocol":"L2TP", # PPTP or L2TP/IPSec
                "vpnKey":"34sd4",
                "vpnStatus":"on"
                }, # on/off
            "FireWall": cmdGetFirewall.implement(),
            '''
            "FireWall":{
                "ipFilter":"off",
                "macFilter":"on",
                "DMZ":{"IP":"123.3.3.1", "Status":"on"},
                "ipList":[
                    {
                        "Validation":"11",
                        "LanIPs":"127.1.1.2 - 127.1.1.20",
                        "LanPort":"3122",
                        "WLanIPs":"10.1.1.2", "WLanPort":"213", "Protocol":"SNMP", "Status":"disable"
                    },
                    {
                        "Validation":"12",
                        "LanIPs":"127.1.1.3 - 127.1.1.30", "LanPort":"3123","WLanIPs":"10.1.1.3", "WLanPort":"214", "Protocol":"UDP",
                        "Status":"enable"
                    }
                    ],
                "macList":[
                    {
                        "MAC":"01-29-03", "Status":"enable", # status value: enable or disable
                        "Desc":"mock-xx-Max40"
                    },
                    {
                        "MAC":"01-29-04", "Status":"disable","Desc":"mock-xx-Max40"
                    }
                    ]
                },
            '''
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

