
/**
 * System View的主Class定义
 */
function CSysStatusView(){
    // 构造函数
    var _this = this;
    //--1.内部变量+内部函数
    var privateParameter;//private
    //--2.初始化对象和成员函数
    _this.node  =  document.getElementById( 'sysStatusView' );
    _this.jqNode = $('#sysStatusView'); // jQuery node object
    // 1.加载本view的html 2.注册控件回调函数 3.多语言实现
    _this.loadHtml();

}
CSysStatusView.prototype.node;
CSysStatusView.prototype.jqNode;
CSysStatusView.prototype.activeMyView = function(){
    tools.ActivateViewByNodeInContainer(gMainView, this.node);
    this.render();
}
CSysStatusView.prototype.deactiveMyView = function(){
    tools.viewShow(this.node, false);
}
CSysStatusView.prototype.render = function(){
    //获取当前active的TabView
    var tabID = 0;
    tabID = $('#ssvTab .tab-header .tab-header-item').siblings('.tab-header-selected').attr('id');
    if(0 == tabID)
        tabID = 'ssvTabHeaderZ';
    // console.log(tabID);
    //
    switch(tabID)
    {
    case 'ssvTabHeaderZ':
        $('#ssvTypeVal').text(oStore.LTEZ.type);
        $('#ssvConnectStatVal').text(oStore.LTEZ.connection);
        $('#ssvWLanIPVal').text(oStore.LTEZ.wlanIP);
        $('#ssvUSimVal').text(oStore.LTEZ.usim);
        $('#ssvDefaultGWVal').text(oStore.LTEZ.defaultGwIP);
        $('#ssvIMSIVal').text(oStore.LTEZ.IMSI);
        $('#ssvMDnsVal').text(oStore.LTEZ.mDnsIP);
        $('#ssvPlmnVal').text(oStore.LTEZ.PLMN);
        $('#ssvSDnsVal').text(oStore.LTEZ.sDnsIP);
        $('#ssvSignalVal').text(oStore.LTEZ.signal);
        $('#ssvMacVal').text(oStore.LTEZ.MAC);
        $('#ssvFrqVal').text(oStore.LTEZ.frq);
        $('#ssvRSRQVal').text(oStore.LTEZ.RSRQ);
        // $('#ssvSNRVal').text(oStore.LTEZ.SNR);
    break;
    case 'ssvTabHeader4G':
        $('#ssvTypeVal').text(oStore.LTE4G.type);
        $('#ssvConnectStatVal').text(oStore.LTE4G.connection);
        $('#ssvWLanIPVal').text(oStore.LTE4G.wlanIP);
        $('#ssvUSimVal').text(oStore.LTE4G.usim);
        $('#ssvDefaultGWVal').text(oStore.LTE4G.defaultGwIP);
        $('#ssvIMSIVal').text(oStore.LTE4G.IMSI);
        $('#ssvMDnsVal').text(oStore.LTE4G.mDnsIP);
        $('#ssvPlmnVal').text(oStore.LTE4G.PLMN);
        $('#ssvSDnsVal').text(oStore.LTE4G.sDnsIP);
        $('#ssvSignalVal').text(oStore.LTE4G.signal);
        $('#ssvMacVal').text(oStore.LTE4G.MAC);
        $('#ssvFrqVal').text(oStore.LTE4G.frq);
        $('#ssvRSRQVal').text(oStore.LTE4G.RSRQ);
        // $('#ssvSNRVal').text(oStore.LTE4G.SNR);
break;
    case 'ssvTabHeaderGnss':
        $('#ssvTabGnssSatNumVal').text(oStore.GNSS.satelliteNum);
        $('#ssvTabGnssSendNumVal').text(oStore.GNSS.totalMsg);
        $('#ssvTabGnssSuccNumVal').text(oStore.GNSS.succMsg);
        $('#ssvTabGnssFailNumVal').text(oStore.GNSS.failMsg);
        $('#ssvTabGnssDstSimVal').text(oStore.GNSS.targetSim);
        $('#ssvTabGnssLocSimVal').text(oStore.GNSS.localSim);
        //
        $('#ssvtgnssBeamInfor1Val').text(oStore.GNSS.beam1);
        $('#ssvtgnssBeamInfor2Val').text(oStore.GNSS.beam2);
        $('#ssvtgnssBeamInfor3Val').text(oStore.GNSS.beam3);
        $('#ssvtgnssBeamInfor4Val').text(oStore.GNSS.beam4);
        $('#ssvtgnssBeamInfor5Val').text(oStore.GNSS.beam5);
        $('#ssvtgnssBeamInfor6Val').text(oStore.GNSS.beam6);
        break;
    case 'ssvTabHeaderLan':
        $('#ssvTabDHCPStatus').text(oStore.DHCP.dhcpStatus);
        // fill LAN
        oStore.LAN.LAN.forEach(function(value,index){
            if(('lan1' == value.port)||('LAN1' == value.port)){
                $('#ssvTabLan1IP').text(value.IP);
            }
            else if(('lan2' == value.port)||('LAN2' == value.port)){
                $('#ssvTabLan2IP').text(value.IP);
            }
            else if(('lan3' == value.port)||('LAN3' == value.port)){
                $('#ssvTabLan3IP').text(value.IP);
            }
        });
        //1.清除表格内容
        $("#ssvTabLanAccessListTbl tr:gt(1)").empty("");
        //2.构建表格内容
        /** 返回数据格式
            "LAN":{ "LAN":[{"port":"lan1", "IP":"10.1.1.10", "subMask":"255.255.255.0"}, {..}],
                    "accessList":[{"MAC":"xx", "IP":"xx", "type":"xx"},{..}]}
        ** html 格式
            <tr> <td><a>1</a></td><td><a>LAN1</a></td><td><a>01-02-01</a></td> <td><a>129.1.1.2</a></td> <td><a>mobile</a></td></tr>
        ***/
        oStore.LAN.accessList.forEach(function(value,index){
            let number = index + 1;
            let tr = "<tr>"+
                    " <td><a>" + number + "</a></td> <td><a>"+value.port+"</a></td> <td><a>"+ value.MAC + "</a></td> <td><a>" + value.IP + "</a></td> <td><a>" + value.type + "</a></td></tr>";
            $("#ssvTabLanAccessListTbl").append(tr);
        })
    
    break;
    default:
    
    }
}
CSysStatusView.prototype.loadHtml = function(){
    // 多语言实现
    var enHtmlMap = {ssvTitleIntCfgTxt:"Internet Configuration",ssvTitleNetStatTxt:"Networking Status",ssvTypeTxt:"Module Type",ssvConnectStatTxt:"Connection Status",
            ssvWLanIP:"WLAN IP",ssvUSim:"USIM Status",ssvDefaultGW:"Default Gateway",ssvMDns:"Master DNS",ssvSDns:"Slave DNS",ssvSignal:"Signal(dBm)",ssvMac:"MAC/IMEI Address",ssvFrq:"Band",ssvRSRQ:"Signal RSRQ",//ssvSNR:"SNR(dB)",
            ssvtgnssInforTitle:"GNSS Information",ssvTabGnssSatNum:"Satellites",ssvTabGnssSendNum:"Send",ssvTabGnssSuccNum:"Succ",ssvTabGnssFailNum:"Fail",ssvTabGnssDstSim:"Dst. SIM",ssvTabGnssLocSim:"Loc SIM",
            ssvtlanInforTitle:"LAN Information",ssvTabLanDevLst:"Accessed List",ssvTabLanDevMac:'Device MAC',ssvTabLanDevIP:'Device IP',ssvTabLanDevType:"Device Type", 
            ssvtgnssBeamInfor1Txt:"Beam1",ssvtgnssBeamInfor2Txt:"Beam2",ssvtgnssBeamInfor3Txt:"Beam3",ssvtgnssBeamInfor4Txt:"Beam4",ssvtgnssBeamInfor5Txt:"Beam5",ssvtgnssBeamInfor6Txt:"Beam6",
        };
    var cnHtmlMap = {ssvTitleIntCfgTxt:"Internet 配置状态",ssvTitleNetStatTxt:"网络状态",ssvTypeTxt:"联机型态",ssvConnectStatTxt:"连接状态",
            ssvWLanIP:"广域网络IP地址",ssvUSim:"USIM卡状态",ssvDefaultGW:"默认网关",ssvMDns:"主DNS",ssvSDns:"次DNS",ssvSignal:"信号强度(dBm)",ssvMac:"MAC/IMEI地址",ssvFrq:"频点(Band)",ssvRSRQ:"信号接收质量RSRQ",//ssvSNR:"信噪比(dB)",
            ssvtgnssInforTitle:"GNSS 信息",ssvTabGnssSatNum:"卫星数量",ssvTabGnssSendNum:"发送总条数",ssvTabGnssSuccNum:"发送成功次数",ssvTabGnssFailNum:"发送失败数",ssvTabGnssDstSim:"目标SIM卡号",ssvTabGnssLocSim:"本机SIM卡号",
            ssvtlanInforTitle:"LAN 信息",ssvTabLanDevLst:"设备接入列表",ssvTabLanDevMac:'设备MAC',ssvTabLanDevIP:'设备IP',ssvTabLanDevType:"设备类型", 
            ssvtgnssBeamInfor1Txt:"波束1",ssvtgnssBeamInfor2Txt:"波束2",ssvtgnssBeamInfor3Txt:"波束3",ssvtgnssBeamInfor4Txt:"波束4",ssvtgnssBeamInfor5Txt:"波束5",ssvtgnssBeamInfor6Txt:"波束6",
        };
    // 1.加载本view的html 2.注册控件回调函数 3.多语言实现
    this.jqNode.load('views/CSysStatusView.html', ()=>{
        tools.language = $('#langSelector').children('option:selected').val();
        tools.htmlSwitchLang(enHtmlMap, cnHtmlMap);
        // 注册回调
        //init: tab control
        var parentObj = this;
        $('#ssvTab').delegate(".tab-header-item", "click", function(){
            //set this tab to ".tab-header-selected",others to none
            $(".tab-header .tab-header-item").siblings().removeClass("tab-header-selected");
            var selected = $(this)
            selected.addClass("tab-header-selected");
            var targetid = selected.attr("target");
            //get the "target"
            $(".tab-content .tab-content-view").siblings().addClass("hide");
            $("#" + targetid).removeClass("hide");
            //刷新控件
            parentObj.render();
        });
    });
}