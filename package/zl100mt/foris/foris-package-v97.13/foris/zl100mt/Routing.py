from foris.zl100mt.ipmacbind import cmdIpmacbind
from foris.zl100mt.portmapping import channelmapping,setportmapping
from foris.zl100mt.dhcp import cmdDhcpCfg
from foris.zl100mt.rtmp import cmdGetRtmpInfo
from foris.zl100mt.firewall import cmdGetFirewall
from foris.zl100mt.gnss import cmdGetGnssInfo
from foris.zl100mt.wan import cmdGetLteZ, cmdGetLte4G

from foris.state import current_state

import logging, os

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

    #def get_routes(self):
    #    data = current_state.backend.perform("network", "get_settings", {})
    #    routes = []
    #    for route in data["routes"]:
    #        routes.append({
    #            "ifName": route['interface'],
    #            "dstNet": route["target"],
    #            "subMask": route["netmask"],
    #            "gwIp": route["gateway"],
    #            "Metric": route["metric"]
    #        })
    #    print routes
    #    return routes

cmdRoutingInfor = RoutingInforCmd()

class GetRoutingInforCmd():
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
            ip, prefix = route["target"].split('/')
            ipcalc_cmd = "ipcalc.sh %s %s|cut -d'=' -f 2" % (ip, prefix)
            ipcalc_output = os.popen(ipcalc_cmd).read()
            ip, netmask, broadcast, network, prefix = ipcalc_output.split()
            routes.append({
                "ifName": route['interface'].upper().replace('_', '-'),
                "dstNet": ip,
                "subMask": netmask,
                "gwIP": route["gateway"],
                "Metric": route["metric"]
            })
        print routes
        return  {"rc": 0, "errCode": "success", "dat": {"routing":routes}}

cmdGetRoutingInfo = GetRoutingInforCmd()

