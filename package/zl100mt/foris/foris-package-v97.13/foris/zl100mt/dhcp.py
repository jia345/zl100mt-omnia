
from foris.state import current_state

class DhcpCmd():
    def __init__(self):
        self.action = 'setMacIPMapping'
        self.default_data = {}

    def implement(self, data, session):
        print "DhcpCmd-implement"

        dhcp_data = data['dat']['DHCP']
        startIp = dhcp_data['startIP'].split('.')
        endIp = dhcp_data['endIP'].split('.')
        dhcpOption = "1," + dhcp_data['subMask']
        dhcpOption += " 3," + dhcp_data['defaultGwIP']
        if dhcp_data['DNS1']:
            dhcpOption += " 6," + dhcp_data['DNS1']
        if dhcp_data['DNS2']:
            dhcpOption += "," + dhcp_data['DNS2']

        dhcpCfg = []
        dhcpCfg.append({
            'ignore': 0 if dhcp_data['dhcpStatus']=="DHCP" else 1,
            "start": int(startIp[-1]),
            "limit": int(endIp[-1]) - int(startIp[-1]) + 1,
            "leasetime": dhcp_data['leaseTerm'] + 'm',
            "dhcp_option": dhcpOption
        })

        rc = current_state.backend.perform("dhcp", "update_settings", {"dhcp_cfg": dhcpCfg})
        print rc
        res = {"rc": 0, "errCode": "success", "dat": None}
        return res

    def get_dhcp(self):
        data = current_state.backend.perform("dhcp", "get_settings", {})

        dhcp_data= data['dhcp_cfg'][0]
        option_arr = dhcp_data['dhcp_option'].split(' ')
        for option in option_arr:
            arr = option.split(',')
            if int(arr[0]) == 1:
                submask = arr[1]
            if int(arr[0]) == 3:
                gwIp = arr[1]
            if int(arr[0]) == 6:
                dns1 = arr[1]
                dns2 = arr[2]

        ipArr = gwIp.split('.')
        ipArr[3] = str(dhcp_data['start'])
        startIP = '.'.join(ipArr)
        ipArr[3] = str(dhcp_data['start'] + dhcp_data['limit']-1)
        endIP = '.'.join(ipArr)

        dhcp = {}
        dhcp['dhcpStatus'] = u'Statics' if dhcp_data['ignore'] else u'DHCP'
        dhcp['startIP'] = startIP
        dhcp['endIP'] = endIP
        dhcp['leaseTerm'] = dhcp_data['leasetime'].replace('m', '')
        dhcp['subMask'] = submask
        dhcp['defaultGwIP'] = gwIp
        dhcp['DNS1'] = dns1
        dhcp['DNS2'] = dns2

        print dhcp
        return dhcp

cmdDhcpCfg = DhcpCmd()