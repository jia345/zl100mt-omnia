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
from foris.zl100mt.proto_forward import cmdProtoForward

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

class GetLogLinkCmd():
    def implement(self, data, session=None):
        #res = current_state.backend.perform("maintain", "get_log_links", {})
        start = data['dat']['startDatetime']
        end   = data['dat']['endDatetime']
        f_list = list(filter(re.compile("/var/log/zl100mt-\d{8}\.log(\.gz)?$").match, globl.glob("/var/log/zl100mt-*.log*")))

        log_list = []
        filepath = 'log'
        if start == "":
            # get all the logs before end time
            start_date = 0
            end_date = int(time.localtime(time.strftime("%Y%m%d", time.localtime(end))))
            for f in f_list:
                filename = os.path.basename(f)
                match = re.search("zl100mt-(\d{8})\.log(\.gz)?$", filename)
                log_date = int(match.group(1))
                if log_date <= end_date:
                    log_list.append({
                        'filePath': filepath,
                        'fileName': filename
                    })
        elif end == "":
            # get all the logs after start time
            start_date = int(time.localtime(time.strftime("%Y%m%d", time.localtime(start))))
            end_date = 0
            for f in f_list:
                filename = os.path.basename(f)
                match = re.search("zl100mt-(\d{8})\.log(\.gz)?$", filename)
                log_date = int(match.group(1))
                if log_date >= start_date:
                    log_list.append({
                        'filePath': filepath,
                        'fileName': filename
                    })
        elif start == "" and end == "":
            # get today's log
            log_list.append({
                'filePath': filepath,
                'fileName': 'zl100mt.log'
            })
        else:
            # get the logs between start and end time
            start_date = int(time.localtime(time.strftime("%Y%m%d", time.localtime(start))))
            end_date = int(time.localtime(time.strftime("%Y%m%d", time.localtime(end))))
            for f in f_list:
                filename = os.path.basename(f)
                match = re.search("zl100mt-(\d{8})\.log(\.gz)?$", filename)
                log_date = int(match.group(1))
                if log_date >= start_date and log_date <= end_date:
                    log_list.append({
                        'filePath': filepath,
                        'fileName': filename
                    })

        return  { "rc": 0, "errCode": "success", "dat": log_list }

class GetSysInfoCmd():
    def implement(self, session=None):
        system = ubus.call('system', 'info', {})[0]
        version = os.popen('cat /etc/zl100mt-version').read().splitlines()[0]
        hwId = ubus.call('zl100mt-rpcd', 'get_hw_id', {})[0]
        hostIp = ubus.call('zl100mt-rpcd', 'get_host_ip', {})[0]
        return {
            'localDatetime': system['localtime'] * 1000,
            'currDuration': system['uptime'] * 1000,
            'hwIMEI': hwId['imei'],
            'hwMAC': hwId['mac'],
            'hostIP': {
                'IP': hostIp['ip'],
                'subMask': hostIp['submask']
            },
            'swVersion': version
        }

class NtpSyncDatetime():
    def __init__(self):
        self.action = 'syncDatetime'
        self.default_data = {}

    def implement(self, data, session=None):
        server_ip = data['dat']['NTP']['serverIP']
        rc = ubus.call("zl100mt-rpcd", "sync_ntp_time", {"server": server_ip})[0]
        res = {
            "rc": 0,
            "errCode": "success",
            "dat": {"localDatetime": rc["ts"]}
        }

        return res

class SetLocalTime():
    def __init__(self):
        self.action = 'setLocalDateTime'
        self.default_data = {}

    def implement(self, data, session=None):
        time_str = data['dat']['LocalDateTime']
        rc = ubus.call("zl100mt-rpcd", "set_local_time", {"time_str": time_str})[0]
        print rc
        res = {
            "rc": 0,
            "errCode": "success",
            "dat": {"localDatetime": rc["ts"]}
        }
        return res

class SetHwId():
    def implement(self, data, session=None):
        mac = data['dat']['system']['hwMAC']
        imei = data['dat']['system']['hwIMEI']
        rc = ubus.call("zl100mt-rpcd", "set_hw_id", {'mac': mac, 'imei': imei})
        return {
            "rc": 0,
            "errCode": "success",
        }

class GetNtpServerIpCmd():
    def implement(self, session=None):
        rc = ubus.call("zl100mt-rpcd", "get_ntp_info", {})[0]
        return {
            'serverIP': rc['server']
        }

class GetNetworkCfgInfoCmd():
    def implement(self, handle, session):
        routingItf = {
            'dat': {
                'modulType': 'lte-z'
            }
        }
        data = {
            "GNSS": cmdGetGnssInfo.implement(session),
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
            "ProtoForward": cmdProtoForward.get_proto_forward()
        }

        res = {
                "rc": 0,
                "errCode": "success",
                "dat": data
              }
        return res

class GetHostStatusInfoCmd():
    def implement(self, handle,session):
        ntp = ubus.call("zl100mt-rpcd", "get_ntp_info", {})[0]
        data = {
            "system": cmdGetSysInfo.implement(session),
            "LTEZ": cmdGetLteZ.implement(session),
            "LTE4G": cmdGetLte4G.implement(session),
            "GNSS": cmdGetGnssInfo.implement(session),
            "LAN": cmdDhcpCfg.get_lan_cfg(),
            "DHCP": cmdDhcpCfg.get_dhcp(),
            "NTP": { "serverIP": ntp['server'] }
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
        ntp = ubus.call("zl100mt-rpcd", "get_ntp_info", {})[0]
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
            "NTP": { "serverIP": ntp['server'] }
        }
        '''
        data = {
            "system": cmdGetSysInfo.implement(session),
            "LTEZ": cmdGetLteZ.implement(session),
            "LTE4G": cmdGetLte4G.implement(session),
            "GNSS": cmdGetGnssInfo.implement(session),
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

        res = {
                "rc": 0,
                "errCode": "success",
                "dat": data
              }
        return res

class SetHostCfg():
    def __init__(self):
        self.action = 'setHostCfg'
        self.default_data = {}

    def implement(self, data, session=None):
        host_ip = data['dat']['hostCfg']['hostIP']
        host_netmask = data['dat']['hostCfg']['subMask']
        cfg = {
            "action": "set_host_cfg",
            "host_ip": host_ip,
            "host_netmask": host_netmask
        }
        current_state.backend.perform('network', 'update_settings', cfg)

        res = {
            "rc": 0,
            "errCode": "success"
        }
        return res


cmdGetAllSysInfo = GetAllSysInforCmd()
cmdReboot = SysReboot()
cmdSyncNtpTime = NtpSyncDatetime()
cmdSetLocalTime = SetLocalTime()
cmdSetHostCfg = SetHostCfg()
cmdGetLogLink = GetLogLinkCmd()
cmdGetSysInfo = GetSysInfoCmd()
cmdGetNtpServerIp = GetNtpServerIpCmd()
cmdGetHostStatusInfo = GetHostStatusInfoCmd()
cmdGetNetworkCfgInfo = GetNetworkCfgInfoCmd()
cmdSetHwId = SetHwId()
