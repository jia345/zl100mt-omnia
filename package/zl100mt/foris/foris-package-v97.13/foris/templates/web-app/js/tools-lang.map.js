var enHtmlMap = {
    lgSubmitBtn:"Login", footerTitle:"ZL100MT | All right reserved, 2018. ", titleRefreshBtn:"Refresh All",
    dashboardEntry: "Dashboard",
    sysStatusViewEntry: "System Status",
    networkViewEntry: "Network Config", 
    txtSystemToolsItem: "System Tools",
    userMgtViewEntryTxt: "User Management",
    sysMaintViewEntryTxt:"System Maintain",
    videoViewEntryTxt: "Video view",
    dsvSysTitleTxt: "System Status",
    dsvLocTimeTxt: "Local Time",
    dsvDurationTimeTxt:"Duration Time",
    dsvIMEITxt: "IMEI",
    dsvFWVerTxt:"Firmware Ver.",
    dsvModTitleTxt:"Module Status",
    dsvModTblTxt:"Module",
    dsvConnTblTxt:"Connection", dsvSignalTxt:"Signal(dBm)", dsvOperaTxt:"Operation",dsvmtZConnectBtn:"Connect",dsvmtZDisconBtn:"Disconnect",dsvmt4GConnectBtn:"Connect",dsvmt4GDisconBtn:"Disconnect",
    ssvTitleIntCfgTxt:"Internet Configuration",
    ssvTitleNetStatTxt:"Networking Status",
    ssvTypeTxt:"Module Type",
    ssvConnectStatTxt:"Connection Status",
    ssvWLanIP:"WLAN IP",
    ssvUSim:"USIM Status",
    ssvDefaultGW:"Default Gateway",
    ssvMDns:"Master DNS",
    ssvSDns:"Slave DNS",
    ssvSignal:"Signal(dBm)",
    ssvMac:"MAC Address",
    ssvFrq:"Frq. pnt.",
    ssvRSRQ:"Signal RSRQ",
    ssvSNR:"SNR(dB)",
    ssvtgnssInforTitle:"GNSS Information",ssvTabGnssSatNum:"Satellites",ssvTabGnssSendNum:"Send",ssvTabGnssSuccNum:"Succ",ssvTabGnssFailNum:"Fail",ssvTabGnssDstSim:"Dst. SIM",ssvTabGnssLocSim:"Loc SIM",
    ssvtlanInforTitle:"LAN Information",ssvTabLanDevLst:"Accessed List",ssvTabLanDevType:"Device Type", 
    ntwvTabRouting:"Routing",ntwvTabPortF:"Firewall/Filter",ntwvTabMappinf:"Mapping",
    nvtlanCfgTitle:"LAN Configuration", nvtlanDHCPCfgTitle:"DHCP Configuration",netvTabLanSubmask:"Network mask",netvTabLanSIP:"Start IP address",netvTabLanEIP:"End IP address",netvTabLanLease:"Lease Term(min)",netvTabLanSubmask2:"Network mask",netvTabLanDefaultGW:"Default Gateway",netvTabLanApplyBtn:"Apply All",
    netvTabVpnTitle:"VPN Passthrough",
    netvTabVpnAddr:"VPN Address",
    netvTabVpnName:"VPN User Name",
    netvTabVpnPwd:"VPN Password",
    netvTabVpnProtocol:"Protocol",
    netvTabVpnKey:"Sec. Key",
    netvTabVpnStatus:"Connection",
    netvTabVpnConnectBtn:"Connect",
    netvTabRoutingM:"Module:", netvTabRoutingRefreshBtn:"Refresh", ntvtrAddBtn:"ADD",ntvtrDelBtn:"DEL",ntvtrChgBtn:"CHG",
    firewall:"Firewall",firewallIPFilterTable:"IP Filter table",firewallMacFilterTable:"MAC Filter table", nvtIPFilterTXt:"IP Filter",nvtMacFilterTXt:"MAC Filter",
    swIPFilter:"Turn on IP filter",  swMacFilter:"MAC filter",
    nvtpfValidation:"Validation", nvtpfLanIP:"LAN IP",nvtpfLanPort:"LAN Port",nvtpfWLanIP:"WLAN IP",nvtpfWLanPort:"WLAN Port",nvtpfProtocol:"Protocol",nvtpfStatus:"Status",
    nvTPFNewBtn:"New", nvTPFModifyBtn:"Modify", nvTPFDelBtn:"Delete", nvTPFApplyallBtn:"Apply All",
    nvTMFNewBtn:"New", nvTMFModifyBtn:"Modify", nvTMFDelBtn:"Delete", nvTMFApplyallBtn:"Apply All",
    nvTMFStatus:"Status",nvTMFMemo:"Memo(Max40 char.)",
    nvtMDMZ:"DMZ host IP",nvtMDMZEnable:"Enable", nvtMApplyBtn:"Apply",nvtMChannel:"Channel", nvtMSrc:"Source",nvtPortmapApplyBtn:"Apply All",nvtMMemo:"The IP (marked & monitor data) can be transfered on GNSS",
    umvTitle:"User Management",umvName:"User",umvPWD:"Password",umvNewPWD:"New Password",umvCmPWD:"Confirm Password", uvResetBtn:"Reset Default",uvSaveBtn:"Save",
    smvTime:"Correct time",smvRefreshBtn:"Rrefresh",smvLog:"Log Record",smvHWIMEI:"Hardware Serial",smvFWVer:"Firmware",smvUpFW:"Upgrade FW",smvBrowseFileBtn:"Browse",smvUploadFileBtn:"Upload FW",smvNewFW:"New FW",smvRebootBtn:"Reset",
    vvVCtrlErr:"This browser can support [video], please try IE 9+,Firefox,Opera,Chrome or Safari.",
    vvPlayBtn:"Play", vvPauseBtn:"Pause", vvStopBtn:"Stop", vvExitBtn:"Exit",

  };
//
var cnHtmlMap = {
    lgSubmitBtn:"用户登陆", footerTitle:"ZL100MT 数据融合仪 | 版权所有XXX, 2018. ", titleRefreshBtn:"刷新数据",
    dashboardEntry: "仪表盘",
    sysStatusViewEntry: "系统状态",
    networkViewEntry: "网络配置",
    txtSystemToolsItem: "系统工具",
    userMgtViewEntryTxt: "用户管理",
    sysMaintViewEntryTxt:"系统维护",
    videoViewEntryTxt: "视频视图",
    dsvSysTitleTxt:"系统状态",
    dsvLocTimeTxt:"本机时间",
    dsvDurationTimeTxt:"本次开机持续时间",
    dsvIMEITxt:"硬件设备号",
    dsvFWVerTxt:"固件版本号",
    dsvModTitleTxt:"模块状态",
    dsvModTblTxt:"模块",
    dsvConnTblTxt:"连接状态", dsvSignalTxt:"信号强度(dBm)", dsvOperaTxt:"操作",dsvmtZConnectBtn:"连接",dsvmtZDisconBtn:"断开",dsvmt4GConnectBtn:"连接",dsvmt4GDisconBtn:"断开",
    ssvTitleIntCfgTxt:"Internet 配置状态",
    ssvTitleNetStatTxt:"网络状态",
    ssvTypeTxt:"联机型态",
    ssvConnectStatTxt:"连接状态",
    ssvWLanIP:"广域网络IP地址",
    ssvUSim:"USIM卡状态",
    ssvDefaultGW:"默认网关",
    ssvMDns:"主DNS",
    ssvSDns:"次DNS",
    ssvSignal:"信号强度(dBm)",
    ssvMac:"MAC地址",
    ssvFrq:"频点",
    ssvRSRQ:"信号RSRQ",
    ssvSNR:"信噪比(dB)",
    ssvtgnssInforTitle:"GNSS 信息",ssvTabGnssSatNum:"卫星数量",ssvTabGnssSendNum:"发送总条数",ssvTabGnssSuccNum:"发送成功次数",ssvTabGnssFailNum:"发送失败数",ssvTabGnssDstSim:"目标SIM卡号",ssvTabGnssLocSim:"本机SIM卡号",
    ssvtlanInforTitle:"LAN 信息",ssvTabLanDevLst:"设备接入列表",ssvTabLanDevType:"设备类型", 
    ntwvTabRouting:"路由",ntwvTabPortF:"防火墙/过滤器",ntwvTabMappinf:"端口映射",
    nvtlanCfgTitle:"LAN 配置", nvtlanDHCPCfgTitle:"DHCP 配置", netvTabLanSubmask:"子网掩码", netvTabLanSIP:"起始IP地址",netvTabLanEIP:"终止IP地址",netvTabLanLease:"地址租期(分钟)",netvTabLanSubmask2:"子网掩码",netvTabLanDefaultGW:"默认网关",netvTabLanApplyBtn:"应用修改",
    netvTabVpnTitle:"VPN 穿透",
    netvTabVpnAddr:"VPN地址",
    netvTabVpnName:"VPN用户名",
    netvTabVpnPwd:"VPN密码",
    netvTabVpnProtocol:"协议",
    netvTabVpnKey:"连接身份密钥",
    netvTabVpnStatus:"VPN连接状态",
    netvTabVpnConnectBtn:"连接",
    netvTabRoutingM:"模块: ", netvTabRoutingRefreshBtn:"刷新", ntvtrAddBtn:"新加",ntvtrDelBtn:"删除",ntvtrChgBtn:"修改",
    firewall:"防火墙设置", firewallIPFilterTable:"IP过滤表",firewallMacFilterTable:"MAC过滤表", nvtIPFilterTXt:"IP 过滤",nvtMacFilterTXt:"MAC 过滤",
    swIPFilter:"开启IP地址过滤", swMacFilter:"MAC过滤",
    nvtpfValidation:"有效期", nvtpfLanIP:"局域网IP地址段",nvtpfLanPort:"局域网端口",nvtpfWLanIP:"广域网IP地址段",nvtpfWLanPort:"广域网端口",nvtpfProtocol:"协议类型",nvtpfStatus:"状态",
    nvTPFNewBtn:"新建", nvTPFModifyBtn:"修改", nvTPFDelBtn:"删除", nvTPFApplyallBtn:"应用所有",
    nvTMFNewBtn:"新建", nvTMFModifyBtn:"修改", nvTMFDelBtn:"删除", nvTMFApplyallBtn:"应用所有",
    nvTMFStatus:"状态",nvTMFMemo:"描述(Max40字符)",
    nvtMDMZ:"DMZ主机IP", nvtMDMZEnable:"激活", nvtMApplyBtn:"应用",nvtMChannel:"传输通道", nvtMSrc:"数据源",nvtPortmapApplyBtn:"应用所有",nvtMMemo:"GNSS通道只传输特殊IP包(段标识+监控数据)",
    umvTitle:"用户管理",umvName:"用户名",umvPWD:"密码",umvNewPWD:"新密码",umvCmPWD:"确认新密码", uvResetBtn:"重置为缺省值",uvSaveBtn:"保存",
    smvTime:"网络对时",smvRefreshBtn:"刷新",smvLog:"Log记录",smvHWIMEI:"硬件设备号",smvFWVer:"固件版本号",smvUpFW:"升级固件",smvBrowseFileBtn:"选取文件",smvUploadFileBtn:"上传新固件",smvNewFW:"新固件",smvRebootBtn:"重启升级",
    vvVCtrlErr:"浏览器不支持播放video,请试用以下浏览器IE 9+、Firefox、Opera、Chrome 和 Safari.",
    vvPlayBtn:"播放", vvPauseBtn:"暂停", vvStopBtn:"停止", vvExitBtn:"退出",
};

var enJsMap = {
};
    
var cnJsMap = {
};
