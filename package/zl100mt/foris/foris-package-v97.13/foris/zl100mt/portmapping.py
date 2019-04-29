from foris.state import current_state

class SetPortMappingCmd():
    def __init__(self):
        self.action = 'setPortMapping'
        self.default_data = {}

    def implement(self, data, session):
        print 'set port mapping :: {}'.format(data)

        portMapping = data['dat']["Mapping"]["portMapping"]
        redirects = []
        for redirect in portMapping:
            redirects.append({
                "target": "DNAT",
                "proto": "tcp udp",
                "src_zone": "wan",  # redirect["WLanSlot"],
                "src_ip": '',
                "src_dport": redirect["WLanPort"],
                "dest_zone": "lan",
                "dest_port": redirect["LanPort"],
                "dest_ip": redirect["LanIP"],
                "name": redirect["Desc"]
            })

        rc = current_state.backend.perform("redirect", "update_settings", {"action": "add", "redirects": redirects})
        res = {"rc": rc, "errCode": "success", "dat": None}
        return res

    def get_portmapping(self):
        rc = current_state.backend.perform("redirect", "get_settings", {})

        portmaps = []
        for redirect in rc["redirects"]:
            portmaps.append({
                "WLanSlot": "LTE-Z",  # redirect["WLanSlot"]
                "WLanPort": redirect["src_dport"],
                "LanSlot": "LAN1",  # LanSlot value: LAN1 to LAN3
                "LanIP": redirect["dest_ip"],
                "LanPort": redirect["dest_port"],
                "Desc": redirect["name"]
            })
        return portmaps

setportmapping = SetPortMappingCmd()

class ChannelUpdateCmd() :
    def __init__(self):
        self.action = 'setSlotChannelMapping'
        self.default_data = {}

    def implement(self, data, session):
        print 'update channel information :: {}'.format(data)
        slotLTEZ = data['dat']['Mapping']['slotLTEZ']
        slotLTE4G = data['dat']['Mapping']['slotLTE4G']

        lans = []
        for lan,state in slotLTEZ.items():
            name = "LTEZ_%s" % lan
            lans.append({
                    "src_zone": '' if state == 'on' else 'lan',
                    "dest_zone": 'wan',
                    "src_ip": "" if state == 'on' else '192.168.3.101',
                    "name": name,
                    "operate": 'add' if state == 'off' else 'del',
                })

        for lan,state in slotLTE4G.items():
            name = "LTE4G_%s" % lan
            lans.append({
                "src_zone": '' if state == 'on' else 'lan',
                "dest_zone": 'wan',
                "src_ip": "" if state == 'on' else '192.168.3.101',
                "name": name,
                "operate": 'add' if state == 'off' else 'del',
            })

        rc = current_state.backend.perform("channelmap", "update_settings", {"lans": lans})
        res = {"rc": rc, "errCode": "success", "dat": None}
        return res

    def get_slotLTEZ(self):
        lans = [{'name':"LTEZ_LAN1"},{'name':"LTEZ_LAN2"},{'name':"LTEZ_LAN3"}]
        res = current_state.backend.perform("channelmap", "get_settings", {"lans": lans})
        data = {"LAN1":"on", "LAN2":"on", "LAN3":"on"}
        for lan in res["lans"]:
            slot = lan['name'].split('_')
            if slot[0] == 'LTEZ' :
                data[slot[1]] = "off"
        print "get_slotLTEZ {}".format(data)
        return data

    def get_slotLTE4G(self):
        lans = [{'name': "LTE4G_LAN1"}, {'name': "LTE4G_LAN2"}, {'name': "LTE4G_LAN3"}]
        res = current_state.backend.perform("channelmap", "get_settings", {"lans": lans})
        data = {"LAN1":"on", "LAN2":"on", "LAN3":"on"}
        for lan in res["lans"]:
            slot = lan['name'].split('_')
            if slot[0] == 'LTE4G' :
                data[slot[1]] = "off"

        print "get_slotLTE4G {}".format(data)
        return data

channelmapping = ChannelUpdateCmd()