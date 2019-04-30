/**
 * MOCK 调试注意事项！
 * 因为要用file:///模拟服务器文件操作所以：
 * 1. 将 /web-app/.整个目录拷贝到 c: 或 d: 根目录下
 * 2. 确保 main.js 中的 gDebug / gMock 都预置为 1
 * 3. “文件下载”功能，只有Chrome能够在本地弹出save as对话框，所以测试文件下载功能只能使用Chrome浏览器
*/
function fillResCodeTxt(rc, errCode, dat){
    var res = {
        "rc": rc,
        "errCode": errCode,
        "dat": dat
    }
    return res;
}

//调用mock方法模拟数据
Mock.mock(
    './debug/mock', function(opt){
        var command = (JSON.parse(opt.body)).command;
        var dat = (JSON.parse(opt.body)).dat;
        // console.log(command);
        var params;
        var res;
        if(command == 'login')
        {
            params = {
                'username': 'test',
                'password': 'pwd'
            };
            res = fillResCodeTxt(0,'NULL', params);
            //
            // alert('This is MOCK unit test!');
            return res;
        }
        else if(command == 'getUserInfor')
        {
        //     { "rc":0/1, "errCode": error msg tx,
        //     "dat":  {"pwd":"xxx"}
        //    }
            params = {    
                'pwd' : 'pwd'
            };
            res = fillResCodeTxt(0,'NULL',params);
            //
            return res;
        }
        else if(command == 'resetDefaultPwd'){
            params = {    
                'pwd' : 'pwd'
            };
            res = fillResCodeTxt(0,'resetDefaultPwd',params);
            //
            return res;
        }else if(command == 'resetToDefault')
        {
            // { "rc": 0/1, "errCode": "xxx" } //0 =>成功/1=>失败
            params = 'resetToDefault';
            res = fillResCodeTxt(0,'resetToDefault',params);
            //
            return res;
        }else if(command == 'syncDatetime')
        {   //1531827890000
            // { "rc":0/1, "errCode": error msg tx,
            //  "dat":  {"localDatetime":"xxx"} // ms数
            // }
            params = {
                "localDatetime":1531827890000
            };
            res = fillResCodeTxt(0,'syncDatetime',params);
            //
            return res;
        }
        else if(command == 'setPWD')
        {
            params = dat.new;
            res = fillResCodeTxt(0,command,params);
            //
            return res;
        }
        else if(command == 'uploadFile')
        {
            // "dat":{"fileName":"xxx",
            // "version":"xxx",
            // "MD5":"xxx"
            // }
            params = {"fileName":"myfile",
                    "version":"1.0.2",
                    "MD5":"12345qazwsx"
                };
            res = fillResCodeTxt(0,command,params);
            //
            return res;
        }else if(command == 'getSysInfor')
        {
            //     {"rc": 0/1, "errCode": "xxx",
            //     "dat": {
            //          params
            //        } }
            params = {
                "system": {"localDatetime":"1531817800000", //ms数
                           "currDuration":"17800000", //本次开机时间
                           "hwIMEI": "1.0.1", "swVersion":"1.1.0"},
                "LTEZ":{"type":"LTE-Z","connection":"on", "signal":"1.2",
                        "wlanIP":"10.1.1.100", "defaultGwIP":"10.2.1.1",
                        "mDnsIP":"10.2.1.1", "sDnsIP":"10.2.1.2", "MAC":"12-43-54",
                        "usim":"Ready", /* Ready 或 Invalid */
                        "IMSI":"08509123", "PLMN":"18509123",
                        "frq":"23.7", "RSRQ":"3.2", "SNR":"1.03"},
                "LTE4G":{"type":"LTE-4G","connection":"on", "signal":"1.2",
                        "wlanIP":"10.1.1.109", "defaultGwIP":"10.2.1.1",
                        "mDnsIP":"10.2.1.1", "sDnsIP":"10.2.1.2", "MAC":"32-43-54",
                        "usim":"Invalid", "IMSI":"08509123", "PLMN":"9854509123",
                        "frq":"73.32", "RSRQ":"33.2", "SNR":"2.03"},
                "GNSS":{ "connection":"on", "signal":"1.01",
                        "satelliteNum":"9", "totalMsg":"4531", 
                        "succMsg":"4500", "failMsg":"31", 
                        "targetSim":"01897", "localSim":"02654"},
                "DHCP":{"dhcpStatus":'DHCP', /* DHCP 或 Statics */
                        "startIP":"12.2.2.1", "endIP":"12.2.2.100", "leaseTerm":"120",
                        "subMask":"255.255.0.0", "defaultGwIP":"12.2.2.1","DNS1":"12.2.2.2", "DNS2":"12.2.2.1"},
                "LAN":{ "LAN":[{"port":"LAN1", "MAC":"01-21-09", "IP":"10.1.1.10", "subMask":"255.0.0.0"},
                                {"port":"LAN2", "MAC":"01-21-19", "IP":"10.1.1.12", "subMask":"255.255.0.0"},
                                {"port":"LAN3", "MAC":"01-21-29", "IP":"10.1.1.13", "subMask":"255.255.255.0"} ],
                        "accessList":[{"port":"LAN3","MAC":"01-29-03", "IP":"128.0.1.2", "type":"xiaomi"},
                                        {"port":"LAN1","MAC":"01-29-04", "IP":"128.0.1.22", "type":"ibm"},
                                        {"port":"LAN2","MAC":"01-29-05", "IP":"128.0.1.12", "type":"pc"} ]},
                "RTMP":{"ServerIP":"10.1.1.12",
                        "channelList":[ {"Name":"Cam01", "Code":"left-1"},
                                        {"Name":"Cam02", "Code":"right-1"},
                                        {"Name":"Cam03", "Code":"top-2"} ] },
                "VPN":{"vpnAddress":"124.1.2.1/vpn/", "vpnUser":"zhang", "vpnPwd":"zhangpwd", 
                        "vpnProtocol":"L2TP", /* PPTP 或 L2TP/IPSec */
                        "vpnKey":"34sd4", "vpnStatus":"on"}, /* on/off */
                "FireWall":{"ipFilter":"off", "macFilter":"on", "DMZ":{"IP":"123.3.3.1", "Status":"on"},
                        "ipList":[{"Validation":"11", "LanIPs":"127.1.1.2 - 127.1.1.20", "LanPort":"3122","WLanIPs":"10.1.1.2", "WLanPort":"213", "Protocol":"SNMP", "Status":"disable"},
                                    {"Validation":"12", "LanIPs":"127.1.1.3 - 127.1.1.30", "LanPort":"3123","WLanIPs":"10.1.1.3", "WLanPort":"214", "Protocol":"UDP", "Status":"enable"}
                                ],
                        "macList":[{"MAC":"01-29-03", "Status":"enable","Desc":"mock-xx-Max40字符"}, /* status 取值: enable 或 disable */
                                {"MAC":"01-29-04", "Status":"disable","Desc":"mock-xx-Max40字符"}]},
                "Mapping":{ "slotLTEZ":{"LAN1":"on", "LAN2":"off", "LAN3":"on"}, /* LAN 取值: on 或 off */
                            "slotLTE4G":{"LAN1":"off", "LAN2":"on", "LAN3":"off"},
                            "mac2ip":[{"MAC":"01-29-03", "IP":"123.4.3.1","Desc":"mock-xx-Max40字符"},
                                {"MAC":"01-29-04", "IP":"123.4.3.2","Desc":"mock-xx-Max40字符"}],
                            "portMapping":[{"WLanSlot":"LTE-Z",/* WLanSlot 取值: LTE-Z 或 LTE-4G */
                                             "WLanPort":"11000","LanSlot":"LAN1",/* LanSlot 取值: LAN1 到 LAN3 */ "LanIP":"128.0.1.22","LanPort":"110","Desc":"mock-WLanSlot-Max40字符"},
                                {"WLanSlot":"LTE-4G", "WLanPort":"12000","LanSlot":"LAN3", "LanIP":"128.0.1.2","LanPort":"80","Desc":"mock-LanSlot-Max40字符"}],
                        },
                "NTP":{"serverIP":"10.1.1.12"},
             }; 
            res = fillResCodeTxt(0,'getSysInfor',params);
            //
            return res;
        }else if(command == 'reBoot')
        {
            params = 'reBoot';
            res = fillResCodeTxt(0,'reBoot',params);
            //
            return res;
        }else if(command == 'getLogLink')
        {        
        // { "rc": 0/1, "errCode": "xxx",
        //     "dat":[
        //       {"filePath":"xxx", "fileName":"xxx"},
        //       {...}
        //     ]
        //   }
            params = [
                {'filePath' : './debug/files/', 'fileName' : 'TEST.001.zip'},
                {'filePath' : './debug/files/', 'fileName' : 'TEST.002.zip'},
                {'filePath' : './debug/files/', 'fileName' : 'TEST.003.zip'},
            ];
            res = fillResCodeTxt(0,'getLogLink',params);
            //
            return res;
        }else if(command == 'operateModul')
        {
            params = dat;
            res = fillResCodeTxt(0,'operateModul',params);
            //
            return res;
        }else if(command == 'setRouting')
        {
            params = dat.operation;
            res = fillResCodeTxt(0, command ,params);
            //
            return res;
        }else if(command == 'getRoutingInfor')
        {
            // var code = 'Act::'+dat.operation +'<>' + dat.routingData.dstNet; 
            // "dat": {
            //     "routing":[
            //      {"dstNet":"xx", "subMask":"xx", "gwIP":"xx", "ifName":"xx", "Metric":"xx"},
            //      {..}
            //     ]
            params = {
                'routing':[
                    {"dstNet":"255.255.255.255", "subMask":"255.255.255.0", "gwIP":"10.0.0.1", "ifName":"局域网络(br0)", "Metric":"1"},
                    {"dstNet":"255.255.255.250", "subMask":"255.255.255.0", "gwIP":"0.0.0.0", "ifName":"局域网络(br0)", "Metric":"3"},
                    {"dstNet":"255.255.255.100", "subMask":"255.255.0.0", "gwIP":"0.0.0.0", "ifName":"局域网络(br0)", "Metric":"2"},
                ]
            };
            res = fillResCodeTxt(0,command,params);
            //
            return res;
        }else if(command == 'connectVPN')
        {
            // "dat": {
            //     "VPN":{"vpnStatus":"on/off"}
            //   }
            params = {"VPN":{"vpnStatus":"off"}};
            res = fillResCodeTxt(0,command,params);
            //
            return res;
        }else if(command == 'setGnssTargetSim')
        {
            params = dat.GNSS.targetSim;
            res = fillResCodeTxt(0,command,params);
            //
            return res;
        }else if(command == 'setLanCfg')
        {
            params = dat.LAN.LAN;
            res = fillResCodeTxt(0,command,params);
            //
            return res;
        }else if(command == 'setDhcpCfg')
        {
            params = dat.DHCP;
            res = fillResCodeTxt(0,command,params);
            //
            return res;
        }else if(command == 'setFirewall')
        {
            params = dat.FireWall;
            res = fillResCodeTxt(0,command,params);
            //
            return res;
        }else if(command == 'setSlotChannelMapping')
        {
            params = dat.Mapping;
            res = fillResCodeTxt(0,command,params);
            //
            return res;
        }else if(command == 'setPortMapping')
        {
            params = dat.Mapping.portMapping;
            res = fillResCodeTxt(0,command,params);
            //
            return res;
        }else if(command == 'setIPFilterTable')
        {
            params = dat.FireWall.ipList;
            res = fillResCodeTxt(0,command,params);
            //
            return res;
        }else if(command == 'setMacFilterTable')
        {
            params = dat.FireWall.macList;
            res = fillResCodeTxt(0,command,params);
            //
            return res;
        }else if(command == 'setMacIPMapping')
        {
            params = dat.Mapping.mac2ip;
            res = fillResCodeTxt(0,command,params);
            //
            return res;
        }else if(command == 'setRtmpChannel')
        {
            params = dat.RTMP.channelList;
            res = fillResCodeTxt(0,command,params);
            //
            return res;
        }else if(command == 'setRtmpServerIP')
        {
            params = dat.RTMP.ServerIP;
            res = fillResCodeTxt(0,command,params);
            //setRtmpServerIP
            return res;
        }
    }
);