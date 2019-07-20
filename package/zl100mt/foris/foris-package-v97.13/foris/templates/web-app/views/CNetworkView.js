
/**
 * CNetworkView View的主Class定义
 */
function CNetworkView(){
    //-- 构造函数
    var _this = this;
    //--1.内部变量+内部函数
    var privateParameter;//private
    //--2.初始化对象和成员函数
    _this.node  =  document.getElementById( 'networkView' );
    _this.jqNode = $('#networkView'); // jQuery node object
    // 加载本view的html实现
    _this.loadHtml();

}
CNetworkView.prototype.node;
CNetworkView.prototype.jqNode;
CNetworkView.prototype.activeMyView = function(){
    // get networkcfg
    oStore.getNetworkCfgInfor();
    // active windows
    tools.ActivateViewByNodeInContainer(gMainView, this.node);
    $('#netvTabRoutingTextarea').text("No.  Dst.Net       SubMask    Gateway       Interface     Metric" + " \n ");
    this.render();
}
CNetworkView.prototype.deactiveMyView = function(){
    tools.viewShow(this.node, false);
}
CNetworkView.prototype.render = function(){
    var enJsMap = this.enJsMap;
    var cnJsMap = this.cnJsMap;
    //获取当前active的TabView
    var tabID = 0;
    tabID = $('#netvTab .tab-header .tab-header-item').siblings('.tab-header-selected').attr('target');
    if(0 == tabID)
        tabID = 'netvTabLan';
    // console.log(tabID);
    //
    switch(tabID)
    {
    case 'netvTabGnss':
        //GNSS
        $('#netvTabGnssTargetSimVal').val(oStore.GNSS.targetSim);
    break;
    case 'netvTabLan':
        // fill LAN
        if((undefined != oStore.LAN.accessList) && (0 != oStore.LAN.accessList.length)){
            //1.清除表格内容
            $("#netvTabLanCfgListTable tr:gt(1)").empty("");
            //2.构建表格内容
            /** 数据格式
                "LAN":{ "LAN":[{"port":"lan1", "MAC":"01-21-09", "IP":"10.1.1.10", "subMask":"255.255.255.0", "RTMP":"1/0"}, {..}],
            ***/
            oStore.LAN.accessList.forEach(function(value,index){
                let number = index + 1;
                let tr = "<tr class='cfglines'><td id='netvTabLanCfgListTablePort'>"+ value.port+"</td> <td id='netvTabLanCfgListTableMac'>"+ value.MAC+"</td> <td><input id='netvTabLanCfgListTableIP' type='IP' placeholder='10.10.10.11' style='width: 150px;' value="+ value.IP + "></td>" +
                        " <td><select class='netvTabLanCfgListTableSelect' id='netvTabLanCfgListTableSelect" + index +"'" +"> <option value='255.255.255.0'>255.255.255.0</option> <option value='255.255.0.0'>255.255.0.0</option> <option value='255.0.0.0'>255.0.0.0</option> </select></td>" +
                        // " <td><input type='radio' name='lan-rtmp' id='netvTabLanCfgListTableRadio" + index +"'" +"/>RTMP Server:1935</td>" +
                        "</tr>";
                $("#netvTabLanCfgListTable").append(tr);
                $("#"+"netvTabLanCfgListTableSelect"+ index).find("option:contains('" + value.subMask + "')").attr("selected",true);
                // if(1 == parseInt(value.RTMP)){
                //     $("#"+"netvTabLanCfgListTableRadio"+ index).prop("checked", true);
                // }
                // else{
                //     $("#"+"netvTabLanCfgListTableRadio"+ index).prop("checked", false);
                // }
            })
            // reg ctrl
            $(".netvTabLanCfgListTableSelect").change(this.netvTabLanCfgListTableSelectOnChange);
            // trigger the last selector onchange; align to the SAME submask
            // onchange func will be triggered by three times.
            $(".netvTabLanCfgListTableSelect").trigger("change");
        }
        else{
            tools.msgBox(tools.jsSwitchLang(enJsMap, cnJsMap, 'nvPortCfgErr'));//'端口配置异常，请检查设备！'
            return;
        }
        //DHCP
        $('#netvTabLanSIPVal').val(oStore.DHCP.startIP);
        $('#netvTabLanEIPVal').val(oStore.DHCP.endIP);
        $('#netvTabLanLeaseVal').val(oStore.DHCP.leaseTerm);
        $('#netvTabLanDefaultGWVal').val(oStore.DHCP.defaultGwIP);
        $('#netvTabLanDhcpDNS1Val').val(oStore.DHCP.DNS1);
        $('#netvTabLanDhcpDNS2Val').val(oStore.DHCP.DNS2);
        $("#netvTabLanDhcpSubmaskSelector").find("option:contains('" + oStore.DHCP.subMask + "')").attr("selected",true);
        // $("#netvTabLan input[name=netvTabLanDHCPRadio][value='" + oStore.DHCP.dhcpStatus + "']").attr('checked','checked');
        // 20190720: 为避免下层送上的参数有大小写失误，选用以下代码
        let dhcpStatus = oStore.DHCP.dhcpStatus;
        if((dhcpStatus == 'DHCP')||(dhcpStatus == 'Dhcp')||(dhcpStatus == 'dhcp')){
            $('#netvTabLanDHCPRadioStaticsCtrl').removeAttr("checked");
            $('#netvTabLanDHCPRadioDhcpCtrl').attr('checked','checked');
        }else{ // if((dhcpStatus == 'Statics')||(dhcpStatus == 'STATICS')||(dhcpStatus == 'statics')){
            $('#netvTabLanDHCPRadioDhcpCtrl').removeAttr("checked");
            $('#netvTabLanDHCPRadioStaticsCtrl').attr('checked','checked');
        }

    break;
    case 'netvTabRTMP':
        //1. init the RTMP server table. rtmp://127.0.0.1:1935/live/fqr
        let defaultPortNum = oStore.store.defaultRtmpSrvPortNum, defaultAppName = oStore.store.defaultRtmpSrvAppName;
        $("#RTMPInforIPValSelector").empty();
        //<option value=''>10.0.11.1(LAN1)</option>
        let rtmpUrl = "rtmp://";
        oStore.LAN.accessList.forEach(function(value,index){
            let tr = "<option id='RTMPInforIPValSelector" + index +"'" + " value=" + value.IP + ">" + value.IP + " (" + value.port + ")" + "</option>";
            $("#RTMPInforIPValSelector").append(tr);
            if(oStore.RTMP.ServerIP == value.IP){
                $("#"+"RTMPInforIPValSelector"+ index).attr("selected",true);
                rtmpUrl = rtmpUrl + oStore.RTMP.ServerIP + ":" + defaultPortNum + "/" + defaultAppName + "/";//":1935/live/";
            }
        });
        $('#RTMPInforAddrVal').text(rtmpUrl);
        $('#RTMPInforAppVal').val(defaultAppName);
        //注册text监听
        $("#RTMPInforAppVal").bind("input propertychange",function(event){
            let strApp = $('#RTMPInforAppVal').val();
            if(strApp == ""){
                defaultAppName = "live";
            }else{
                defaultAppName = $('#RTMPInforAppVal').val();
            }
            oStore.store.defaultRtmpSrvAppName = defaultAppName;
            $('#RTMPInforAppVal').val(defaultAppName);
            //
            let strIP = $('#RTMPInforIPValSelector').val();
            rtmpUrl = "rtmp://" + strIP + ":" + defaultPortNum + "/" + defaultAppName + "/";// ":1935/live/";
            $('#RTMPInforAddrVal').text(rtmpUrl);
            $('#RTMPInforAddrVal').css({"color": "red"});
        });
        //注册select ctrl监听
        $('#RTMPInforIPValSelector').change(()=>{
            $('#RTMPInforAddrVal').text(''); //清空
            //
            let strApp = $('#RTMPInforAppVal').val();
            if(strApp == ""){
                defaultAppName = "live";
            }else{
                defaultAppName = $('#RTMPInforAppVal').val();
            }
            oStore.store.defaultRtmpSrvAppName = defaultAppName;
            $('#RTMPInforAppVal').val(defaultAppName);
            //
            let strIP = $('#RTMPInforIPValSelector').val();
            rtmpUrl = "rtmp://" + strIP + ":" + defaultPortNum + "/" + defaultAppName + "/";// ":1935/live/";
            $('#RTMPInforAddrVal').text(rtmpUrl);
            $('#RTMPInforAddrVal').css({"color": "red"});
        });
        //2. init the channel list table
        if((undefined != oStore.RTMP.channelList) && (0 != oStore.RTMP.channelList.length)){
            $("#netvTabRTMPChannelTable tr:gt(1)").empty("");
            // *** HTML
            // <tr> <td><input type='checkbox' checked='' /></td> <td><input class='netvTabRTMPChannelNameVal'/></td> <td><input class='netvTabRTMPChannelCodeVal'/></td> <td><a id='netvTabRTMPChannelRefVal'></a></td></tr>
            oStore.RTMP.channelList.forEach(function(value,index){
                let rtmpRefUrl = "rtmp://" + oStore.RTMP.ServerIP + ":1935/live/";
                let tr =  "<tr> <td><input type='checkbox' /></td>" +
                    "<td><input class='netvTabRTMPChannelNameVal' value=" + value.Name + "></td>" +
                    "<td><input class='netvTabRTMPChannelCodeVal' value="+ value.Code+"></td>" +
                    "<td><a>" + rtmpRefUrl + value.Code + "</a></td></tr>"
                $("#netvTabRTMPChannelTable").append(tr);
            });
        }
    break;
    case 'netvTabVpn':
        $('#netvTabVpnAddrVal').val(oStore.VPN.vpnAddress);
        $('#netvTabVpnNameVal').val(oStore.VPN.vpnUser);
        $('#netvTabVpnPwdVal').val(oStore.VPN.vpnPwd);
        $('#netvTabVpnKeyVal').val(oStore.VPN.vpnKey);
        $('#netvTabVpnStatusVal').text(oStore.VPN.vpnStatus);
        $("#netvTabVpnProtocolSelector").find("option:contains('" + oStore.VPN.vpnProtocol + "')").attr("selected",true);
    break;
    case 'netvTabRouting':
        // netvTabRoutingRefreshBtn 触发刷新！
    break;
    case 'netvTabFWFilter':
        // $('#ssvTabGnssSatNumVal').text(oStore.GNSS.satelliteNum);
        var ipFilter, macFilter, DMZ;
        ('on' == oStore.FireWall.ipFilter)? ipFilter = true : ipFilter = false;
        ('on' == oStore.FireWall.macFilter)? macFilter = true : macFilter = false;
        ('on' == oStore.FireWall.DMZ.Status)? DMZ = true : DMZ = false;
        //
        $("#netvTabFWFilterTable").find("tr").each(function(idx, item){
            $(item).find("#swIPFilterCkb").attr("checked",ipFilter);
            $(item).find("#swMacFilterCkb").attr("checked",macFilter);
            $(item).find("#nvtMDMZEnableCkb").attr("checked",DMZ);
            $(item).find("#nvtMDMZIPAddressVal").val(oStore.FireWall.DMZ.IP);
        });
        // IP 过滤表
        // 20190521: remove Validation parameter
        if((undefined != oStore.FireWall.ipList) && (0 != oStore.FireWall.ipList.length)){
            $("#firewallIPFilterTbl tr:gt(1)").empty("");
            //"ipList":[{"LanIPs":"127.1.1.2", "LanPort":"3122","WLanIPs":"10.1.1.2", "WLanPort":"213", "Status":"enable"},
            // {"LanIPs":"127.1.1.3", "LanPort":"3123","WLanIPs":"10.1.1.3", "WLanPort":"214", "Status":"diabale"}],
            // ** html 格式
            // <tr> <td><input type='checkbox' checked='' /></td> <td><input class='nvtpfLanIPVal'/></td> <td><input class='nvtpfLanPortVal'/></td>
            //  <td><input class='nvtpfWLanIPVal'/></td> <td><input class='nvtpfWLanPortVal'/></td>
            //   <td><select id='nvtpfProtocolValSelector'><option value='enable'>enable</option><option value='disbale'>disbale</option></select></td></tr>
            oStore.FireWall.ipList.forEach(function(value,index){
                let tr = "<tr> <td><input type='checkbox' /></td>" + // <td><input class='nvtpfValiVal'  style='width:35px' value=" + value.Validation + "></td>
                        "<td><input class='nvtpfLanIPVal' style='width:100px' value=" + value.LanIPs +"></td> <td><input  style='width:100px' class='nvtpfLanPortVal' value=" + value.LanPort +"></td>" +
                        "<td><input class='nvtpfWLanIPVal' style='width:100px' value="+ value.WLanIPs+"></td> <td><input style='width:100px' class='nvtpfWLanPortVal' value="+value.WLanPort +"></td>" +
                        "<td><select style='width:100px' id='nvtpfProtocolValSelector"+index+ "'"+"><option value='enable'>Enable</option><option value='disbale'>Disbale</option></select></td></tr>";
                $("#firewallIPFilterTbl").append(tr);
                $("#"+"nvtpfProtocolValSelector"+ index).find("option:contains('" + value.Status + "')").attr("selected",true);
            })
        }
        // MAC 过滤表
        if((undefined != oStore.FireWall.macList) && (0 != oStore.FireWall.macList.length)){
            $("#firewallMacFilterTbl tr:gt(1)").empty("");
            //"macList":[{"MAC":"01-29-03", "Status":"enable","Desc":"xx-Max40字符"},
            //           {"MAC":"01-29-04", "Status":"disable","Desc":"xx-Max40字符"}]
            // ** html 格式
            // <tr> <td><input type="checkbox" checked='' /></td> <td><input class='nvTMFMacVal'  value=''/>MAC</td>
            // <td><select id="nvTMFStatusSelector" > <option value="enable">Enable</option> <option value="disable">Disable</option> </select></td>
            // <td><input class='nvTMFMemoVal' value=''/>描述</td> </tr>
                oStore.FireWall.macList.forEach(function(value,index){
                let tr = "<tr> <td><input type='checkbox' /></td> <td><input class='nvTMFMacVal'  value=" + value.MAC + "></td>" +
                        "<td><select id='nvTMFStatusSelector"+index+ "'"+"><option value='enable'>Enable</option> <option value='disable'>Disable</option> </select></td>" +
                        "<td><input class='nvTMFMemoVal' style='width:300px' value="+ value.Desc+"></td></tr>";
                $("#firewallMacFilterTbl").append(tr);
                $("#"+"nvTMFStatusSelector"+ index).find("option:contains('" + value.Status + "')").attr("selected",true);
            })
        }
    break;
    case 'netvTabMapping':
        // 端口映射
        if((undefined != oStore.Mapping.portMapping) && (0 != oStore.Mapping.portMapping.length)){
            $("#netvTabMappingPortTbl tr:gt(1)").empty("");
            // "portMapping":[{"WLanSlot":"LTE-Z", "WLanPort":"12000","LanSlot":"LAN3", "LanIP":"10.2.1.3", "LanPort":"80","Desc":"mock-xx-Max40字符"},
            oStore.Mapping.portMapping.forEach(function(value,index){
                let wlanOptionStr = '';
                ('LTE-4G' == value.WLanSlot)? wlanOptionStr = "<option value='LTE-4G' selected >LTE-4G</option><option value='LTE-Z'>LTE-Z</option>" : wlanOptionStr = "<option value='LTE-4G' >LTE-4G</option><option value='LTE-Z' selected>LTE-Z</option>" ;
                let tr = "<tr> <td><input type='checkbox' /></td>" +
                        "<td><select style='width:70px' class='netvTabMappingPortTblWlanSelector'>" + wlanOptionStr + "</select>" +
                        "    <a>:</a><input class='netvTabMappingPortTblWlanPortVal' value='" + value.WLanPort + "' placeholder='10000 - 20000' style='width:90px'/></td> " +
                        "<td><select style='width:100px' class='netvTabMappingPortTblLanSelector' id='netvTabMappingPortTblLanSelector"+index+"' ></select>" +
                        "    <a>:</a><input class='netvTabMappingPortTblLanPortVal' value='"+ value.LanPort +"' style='width:70px'/></td>" +
                        "<td><a style='width:30px' class='netvTabMappingPortTblLanSlot' id='netvTabMappingPortTblLanSlot"+index+"'>"+ value.LanSlot +"</a></td>" +
                        "<td><input class='netvTabMappingMemoVal' value='"+ value.Desc +"' style='width:200px'/></td> </tr> "
                $("#netvTabMappingPortTbl").append(tr);
                let trIndex = index;
                // insert LAN:IP list
                oStore.LAN.accessList.forEach((element, index)=>{ // create lan:ip select->options
                    let lanOptionStr = ''; //<option value=128.0.1.22 selected>128.0.1.22</option>
                    if(value.LanIP == element.IP){
                        lanOptionStr = "<option value='"+element.IP+"' selected>"+element.IP+"</option>";
                    }
                    else{
                        lanOptionStr = "<option value='"+element.IP+"'>"+element.IP+"</option>";
                    }
                    $('#netvTabMappingPortTblLanSelector'+trIndex).append(lanOptionStr);
                });
            })
            //regist select callback.
            //取值变化时进行hightlight => red 处理
            $('.netvTabMappingPortTblWlanSelector').change(this.netvTabMappingPortTblWlanSelectorOnChange);
            $('.netvTabMappingPortTblLanSelector').change(this.netvTabMappingPortTblLanSelectorOnChange);

            $('.netvTabMappingPortTblWlanPortVal').change(this.netvTabMappingPortTblXXPortValOnChange);
            $('.netvTabMappingPortTblLanPortVal').change(this.netvTabMappingPortTblXXPortValOnChange);
        }
        //
        // 通道映射
        // "slotLTEZ":{"LAN1":"on", "LAN2":"off", "LAN3":"on"},
        // "slotLTE4G":{"LAN1":"on", "LAN2":"off", "LAN3":"on"},
        var changedFlg = false;
        var lan1Z, lan2Z, lan3Z, lan14G, lan24G, lan34G;
        //--slotLTEZ
        if((('on' == oStore.Mapping.slotLTEZ.LAN1)&&(true == this.checkSlotMappingRule('LAN1', 'LTE-Z')))
            ||(('on' != oStore.Mapping.slotLTEZ.LAN1)&&(false == this.checkSlotMappingRule('LAN1', 'LTE-Z')))){
            //
            changedFlg = false;
        }
        else{
            changedFlg = true;
            if('on' == oStore.Mapping.slotLTEZ.LAN1){
                oStore.Mapping.slotLTEZ.LAN1 = 'off';
            }
            else{
                oStore.Mapping.slotLTEZ.LAN1 = 'on';
            }
        }
        ('on' == oStore.Mapping.slotLTEZ.LAN1)? lan1Z = true : lan1Z = false;
        //
        if((('on' == oStore.Mapping.slotLTEZ.LAN2)&&(true == this.checkSlotMappingRule('LAN2', 'LTE-Z')))
            ||(('on' != oStore.Mapping.slotLTEZ.LAN2)&&(false == this.checkSlotMappingRule('LAN2', 'LTE-Z')))){
            //
            changedFlg = false;
        }
        else{
            changedFlg = true;
            if('on' == oStore.Mapping.slotLTEZ.LAN2){
                oStore.Mapping.slotLTEZ.LAN2 = 'off';
            }
            else{
                oStore.Mapping.slotLTEZ.LAN2 = 'on';
            }
        }
        ('on' == oStore.Mapping.slotLTEZ.LAN2)? lan2Z = true : lan2Z = false;
        //
        if((('on' == oStore.Mapping.slotLTEZ.LAN3)&&(true == this.checkSlotMappingRule('LAN3', 'LTE-Z')))
            ||(('on' != oStore.Mapping.slotLTEZ.LAN3)&&(false == this.checkSlotMappingRule('LAN3', 'LTE-Z')))){
            //
            changedFlg = false;
        }
        else{
            changedFlg = true;
            if('on' == oStore.Mapping.slotLTEZ.LAN3){
                oStore.Mapping.slotLTEZ.LAN3 = 'off';
            }
            else{
                oStore.Mapping.slotLTEZ.LAN3 = 'on';
            }
        }
        ('on' == oStore.Mapping.slotLTEZ.LAN3)? lan3Z = true : lan3Z = false;
        //--slotLTE4G
        if((('on' == oStore.Mapping.slotLTE4G.LAN1)&&(true == this.checkSlotMappingRule('LAN1', 'LTE-4G')))
            ||(('on' != oStore.Mapping.slotLTE4G.LAN1)&&(false == this.checkSlotMappingRule('LAN1', 'LTE-4G')))){
            //
            changedFlg = false;
        }
        else{
            changedFlg = true;
            if('on' == oStore.Mapping.slotLTE4G.LAN1){
                oStore.Mapping.slotLTE4G.LAN1 = 'off';
            }
            else{
                oStore.Mapping.slotLTE4G.LAN1 = 'on';
            }
        }
        ('on' == oStore.Mapping.slotLTE4G.LAN1)? lan14G = true : lan14G = false;
        //
        if((('on' == oStore.Mapping.slotLTE4G.LAN2)&&(true == this.checkSlotMappingRule('LAN2', 'LTE-4G')))
            ||(('on' != oStore.Mapping.slotLTE4G.LAN2)&&(false == this.checkSlotMappingRule('LAN2', 'LTE-4G')))){
            changedFlg = false;
        }
        else{
            changedFlg = true;
            if('on' == oStore.Mapping.slotLTE4G.LAN2){
                oStore.Mapping.slotLTE4G.LAN2 = 'off';
            }
            else{
                oStore.Mapping.slotLTE4G.LAN2 = 'on';
            }
        }
        ('on' == oStore.Mapping.slotLTE4G.LAN2)? lan24G = true : lan24G = false;
        //
        if((('on' == oStore.Mapping.slotLTE4G.LAN3)&&(true == this.checkSlotMappingRule('LAN3', 'LTE-4G')))
            ||(('on' != oStore.Mapping.slotLTE4G.LAN3)&&(false == this.checkSlotMappingRule('LAN3', 'LTE-4G')))){
            changedFlg = false;
        }
        else{
            changedFlg = true;
            if('on' == oStore.Mapping.slotLTE4G.LAN3){
                oStore.Mapping.slotLTE4G.LAN3 = 'off';
            }
            else{
                oStore.Mapping.slotLTE4G.LAN3 = 'on';
            }
        }
        ('on' == oStore.Mapping.slotLTE4G.LAN3)? lan34G = true : lan34G = false;
        $("#netvTabMappingSlotTbl").find("tr").each(function(idx, item){
            $(item).find("#nvtMChannelZLan1Ckb").attr("checked",lan1Z);
            $(item).find("#nvtMChannelZLan2Ckb").attr("checked",lan2Z);
            $(item).find("#nvtMChannelZLan3Ckb").attr("checked",lan3Z);
            $(item).find("#nvtMChannel4GLan1Ckb").attr("checked",lan14G);
            $(item).find("#nvtMChannel4GLan2Ckb").attr("checked",lan24G);
            $(item).find("#nvtMChannel4GLan3Ckb").attr("checked",lan34G);
        });
        //如端口映射和通道映射有不一致，发生了自动修正操作，将结果上送服务器保存
        if(true == changedFlg){
            // "dat": {
            //   "Mapping":{ "slotLTEZ":{"LAN1":"on", "LAN2":"off", "LAN3":"on"},
            //               "slotLTE4G":{"LAN1":"off", "LAN2":"on", "LAN3":"off"},
            //   }
            var selectedData = {
                "slotLTEZ" :oStore.Mapping.slotLTEZ,
                "slotLTE4G":oStore.Mapping.slotLTE4G
            };
            var str = {
                "command":"setSlotChannelMapping",
                "dat":{
                    "Mapping": selectedData
                }
            }
            parameters = JSON.stringify(str);
            $.ajax({
                type:"POST",
                url: getURL(), //"/cgi-bin/cgi.cgi",
                data:parameters,
                contentType: "application/json",
                dataType: 'json',
                success: (res)=>{
                    // 返回参数格式
                    // { "rc": 0/1, "errCode": "xxx" }
                    //var data = JSON.parse(res);
                    var data = res;
                    console.log(data);
                    if(0 == data.rc){
                        oStore.Mapping.slotLTEZ = selectedData.slotLTEZ;
                        oStore.Mapping.slotLTE4G = selectedData.slotLTE4G;
                    }
                    else{
                        tools.msgBox(tools.jsSwitchLang(enJsMap, cnJsMap, 'operationSucc') + '  Code:' +data.errCode);//操作成功
                        tools.msgBox(data.errCode);
                    }
                },
                error: function (errorThrown) { tools.msgBoxFailed(errorThrown);}
            });
        }

        // IP/MAC绑定
        if((undefined != oStore.Mapping.mac2ip) && (0 != oStore.Mapping.mac2ip.length)){
            $("#netvTabMappingMacIPTbl tr:gt(1)").empty("");
            // "macVSip":[{"MAC":"01-29-03", "IP":"123.4.3.1","Desc":"xx-Max40字符"},
            //             {"MAC":"01-29-04", "IP":"123.4.3.2","Desc":"xx-Max40字符"}]
            oStore.Mapping.mac2ip.forEach(function(value,index){
                let tr = "<tr> <td><input type='checkbox' /></td> <td><input class='netvTabMappingMacVal' value=" + value.MAC + "></td>" +
                        "<td><input class='netvTabMappingIPVal' type='IP' placeholder='10.10.10.11' value="+ value.IP+"></td>" +
                        "<td><input class='netvTabMappingMacIpMemoVal' style='width:300px' value="+ value.Desc+"></td></tr>";
                $("#netvTabMappingMacIPTbl").append(tr);
            })
            }
    break;
    default:

    }
}
//即时检查是否符合映射规则
CNetworkView.prototype.checkSlotMappingRule = function(aLan, aWlan){
    var rc = false; // false => 两者没有映射关系
    for(let i = 0; i < oStore.Mapping.portMapping.length; i++){
        // console.log(oStore.Mapping.portMapping[i].WLanSlot+'<>'+oStore.Mapping.portMapping[i].LanSlot);
        if((oStore.Mapping.portMapping[i].WLanSlot == aWlan)&&(oStore.Mapping.portMapping[i].LanSlot == aLan)){
            // console.log(oStore.Mapping.portMapping[i].WLanSlot+'<>'+oStore.Mapping.portMapping[i].LanSlot);
            rc = true; //有映射关系
            break;
        }
    }
    // console.log('checkSlotMappingRule.rc='+rc);
    return rc;
}
CNetworkView.prototype.loadHtml = function(){
    var enJsMap = this.enJsMap;
    var cnJsMap = this.cnJsMap;
    // 1.加载本view的html 2.注册控件回调函数 3.多语言实现
    this.jqNode.load('views/CNetworkView.html', ()=>{
        tools.language = $('#langSelector').children('option:selected').val();
        tools.htmlSwitchLang(this.enHtmlMap, this.cnHtmlMap);
        //注册控件回调函数
        //init: tab control
        var parentObj = this;
        $('#netvTab').delegate(".tab-header-item", "click", function(){
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
        //
        //注册通道映射SlotMapping的Checkbox回调函数
        //即时检查是否符合映射规则
        // LTE-Z 配置
        $('#nvtMChannelZLan1Ckb').change(()=>{
            let rc = this.checkSlotMappingRule('LAN1', 'LTE-Z');
            if(true == rc){
                $('#nvtMChannelZLan1Ckb').prop('checked', true);
                $('#nvtMChannelZAlertTxt').text(tools.jsSwitchLang(enJsMap, cnJsMap, 'nvPortMapLAN12ZErr') ); //[端口映射]表中已经建立LAN1<->LTE-Z高优先级映射!'
                $('#nvtMChannelZAlertTxt').css({'color':'red'});
            }
            else{
                // $('#nvtMChannelZLan1Ckb').prop('checked', false);
                $('#nvtMChannelZAlertTxt').text(tools.jsSwitchLang(enJsMap, cnJsMap, 'nvSetPortMap') );//('[设置映射]');
                $('#nvtMChannelZAlertTxt').css({'color':'black'});
            }
        });
        $('#nvtMChannelZLan2Ckb').change(()=>{
            let rc = this.checkSlotMappingRule('LAN2', 'LTE-Z');
            if(true == rc){
                $('#nvtMChannelZLan2Ckb').prop('checked', true);
                $('#nvtMChannelZAlertTxt').text(tools.jsSwitchLang(enJsMap, cnJsMap, 'nvPortMapLAN22ZErr') ); //'[端口映射]表中已经建立LAN2<->LTE-Z高优先级映射!'
                $('#nvtMChannelZAlertTxt').css({'color':'red'});
            }
            else{
                // $('#nvtMChannelZLan2Ckb').prop('checked', false);
                $('#nvtMChannelZAlertTxt').text(tools.jsSwitchLang(enJsMap, cnJsMap, 'nvSetPortMap') );//('[设置映射]');
                $('#nvtMChannelZAlertTxt').css({'color':'black'});
            }
        });
        $('#nvtMChannelZLan3Ckb').change(()=>{
            let rc = this.checkSlotMappingRule('LAN3', 'LTE-Z');
            if(true == rc){
                $('#nvtMChannelZLan3Ckb').prop('checked', true);
                $('#nvtMChannelZAlertTxt').text(tools.jsSwitchLang(enJsMap, cnJsMap, 'nvPortMapLAN32ZErr')); //'[端口映射]表中已经建立LAN3<->LTE-Z高优先级映射!'
                $('#nvtMChannelZAlertTxt').css({'color':'red'});
            }
            else{
                // $('#nvtMChannelZLan3Ckb').prop('checked', false);
                $('#nvtMChannelZAlertTxt').text(tools.jsSwitchLang(enJsMap, cnJsMap, 'nvSetPortMap') );//('[设置映射]');
                $('#nvtMChannelZAlertTxt').css({'color':'black'});
            }
        });
        // LTE-4G 配置
        $('#nvtMChannel4GLan1Ckb').change(()=>{
            let rc = this.checkSlotMappingRule('LAN1', 'LTE-4G');
            if(true == rc){
                $('#nvtMChannel4GLan1Ckb').prop('checked', true);
                $('#nvtMChannel4GAlertTxt').text(tools.jsSwitchLang(enJsMap, cnJsMap, 'nvPortMapLAN12GErr')); //'[端口映射]表中已经建立LAN1<->LTE-4G高优先级映射!'
                $('#nvtMChannel4GAlertTxt').css({'color':'red'});
            }
            else{
                // $('#nvtMChannel4GLan1Ckb').prop('checked', false);
                $('#nvtMChannel4GAlertTxt').text(tools.jsSwitchLang(enJsMap, cnJsMap, 'nvSetPortMap') );//('[设置映射]');
                $('#nvtMChannel4GAlertTxt').css({'color':'black'});
            }
        });
        $('#nvtMChannel4GLan2Ckb').change(()=>{
            let rc = this.checkSlotMappingRule('LAN2', 'LTE-4G');
            if(true == rc){
                $('#nvtMChannel4GLan2Ckb').prop('checked', true);
                $('#nvtMChannel4GAlertTxt').text(tools.jsSwitchLang(enJsMap, cnJsMap, 'nvPortMapLAN22GErr')); //'[端口映射]表中已经建立LAN2<->LTE-4G高优先级映射!'
                $('#nvtMChannel4GAlertTxt').css({'color':'red'});
            }
            else{
                // $('#nvtMChannel4GLan2Ckb').prop('checked', false);
                $('#nvtMChannel4GAlertTxt').text(tools.jsSwitchLang(enJsMap, cnJsMap, 'nvSetPortMap') );//('[设置映射]');
                $('#nvtMChannel4GAlertTxt').css({'color':'black'});
            }
        });
        $('#nvtMChannel4GLan3Ckb').change(()=>{
            let rc = this.checkSlotMappingRule('LAN3', 'LTE-4G');
            if(true == rc){
                $('#nvtMChannel4GLan3Ckb').prop('checked', true);
                $('#nvtMChannel4GAlertTxt').text(tools.jsSwitchLang(enJsMap, cnJsMap, 'nvPortMapLAN32GErr')); //'[端口映射]表中已经建立LAN3<->LTE-4G高优先级映射!'
                $('#nvtMChannel4GAlertTxt').css({'color':'red'});
            }
            else{
                // $('#nvtMChannel4GLan3Ckb').prop('checked', false);
                $('#nvtMChannel4GAlertTxt').text(tools.jsSwitchLang(enJsMap, cnJsMap, 'nvSetPortMap')); //'[设置映射]'
                $('#nvtMChannel4GAlertTxt').css({'color':'black'});
            }
        });
        //
        //配置页面button回调函数
        //
        // netvTabGnssTargetSimSaveBtn
        $('#netvTabGnssTargetSimSaveBtn').click(()=>{
        //     {"command":"setGnssTargetSim",
        //     "dat": {
        //         "GNSS":{ "targetSim": "xxx"}
        //       }
        //   }
            var selectedData =  {
                "targetSim": $('#netvTabGnssTargetSimVal').val(),
            }
            var str = {
                "command":"setGnssTargetSim",
                "dat":{
                    "GNSS":selectedData
                }
            }
            parameters = JSON.stringify(str);
            $.ajax({
                type:"POST",
                url: getURL(), //"/cgi-bin/cgi.cgi",
                data:parameters,
                contentType: "application/json",
                dataType: 'json',
                success: (res)=>{
                    // 返回参数格式
                    // { "rc": 0/1, "errCode": "xxx" }
                    //var data = JSON.parse(res);
                    var data = res;
                    if(0 == data.rc){
                        oStore.GNSS.targetSim = selectedData.targetSim;
                        console.log(data.dat);
                        tools.msgBox(tools.jsSwitchLang(enJsMap, cnJsMap, 'operationSucc')+ ' code:' + data.errCode); //'操作成功!
                    }
                    else{
                        tools.msgBox(data.errCode);
                    }
                },
                error: function (errorThrown) { tools.msgBoxFailed(errorThrown);}
            });
        });
        // netvTabLanApplyLanCfgBtn
        $('#netvTabLanApplyLanCfgBtn').click(()=>{
            var parametersErr = '';
            var maskVal = ''; // just support ONE VLAN, so the mask should be SAME for all LANs.
            var selectedData = [];
            $("#netvTabLanCfgListTable").find("tr").each(function(idx, item){
                var port = $(item).find("#netvTabLanCfgListTablePort").text();
                if('' != port){
                    var mac = $("#netvTabLanCfgListTable").find("tr:eq("+ idx +")").find("#netvTabLanCfgListTableMac").text();
                    let ip = $("#netvTabLanCfgListTable").find("tr:eq("+ idx +")").find("#netvTabLanCfgListTableIP").val();
                    let mask = $(item).find("select").children('option:selected').val();
                    if(maskVal == ''){ // check if the mask are same.
                        maskVal = mask;
                    }
                    else if(maskVal != mask){
                        parametersErr = tools.jsSwitchLang(enJsMap, cnJsMap, 'nvMaskValErr')+ (idx-2) +")"; //""
                        return false; // 用此方法退出jQuery each loop
                    }
                    if(undefined != ip){
                        if(('' == ip)||(false == tools.chkIpAddress(ip))){
                            // alert("IP不能为空!");
                            parametersErr = tools.jsSwitchLang(enJsMap, cnJsMap, 'nvIPValErr')+ (idx-2) +")"; //"IP地址取值异常(无效行号="
                            return false; // 用此方法退出jQuery each loop
                        }
                        // let rtmp = '';
                        // if($(item).find("input").is(":checked")){
                        //     rtmp = '1';
                        // }
                        // else{
                        //     rtmp = '0';
                        // }
                        var cfg = {"port": port,"MAC": mac,"IP": ip, "subMask": mask}; //, "RTMP": rtmp
                        selectedData.push(cfg);
                    }
                }
            });
            if('' != parametersErr){
                alert(parametersErr);
                return;
            }
            // "dat": {
            //     "LAN":{ "LAN":[{"port":"lan1/2/3", "IP":"xx", "subMask":"xxx", "RTMP":"0"},{..}]}
            //   }
            var str = {
                "command":"setLanCfg",
                "dat":{
                    "LAN": {
                        "LAN": selectedData
                    }
                }
            }
            parameters = JSON.stringify(str);
            $.ajax({
                type:"POST",
                url: getURL(), //"/cgi-bin/cgi.cgi",
                data:parameters,
                contentType: "application/json",
                dataType: 'json',
                success: (res)=>{
                    // 返回参数格式
                    // { "rc": 0/1, "errCode": "xxx" }
                    //var data = JSON.parse(res);
                    var data = res;
                    if(0 == data.rc){
                        oStore.LAN.LAN = selectedData;
                        tools.msgBox(tools.jsSwitchLang(enJsMap, cnJsMap, 'operationSucc')+ ' code:' + data.errCode); //'操作成功!
                        console.log(data.dat);
                    }
                    else{
                        tools.msgBox(data.errCode);
                    }
                },
                error: function (errorThrown) { tools.msgBoxFailed(errorThrown);}
            });
        });
        // netvTabLanApplyDhcpBtn
        $('#netvTabLanApplyDhcpBtn').click(()=>{
            // "dat": {
            //     "DHCP":{"dhcpStatus":"DHCP/Statics",
            //           "startIP":"xx", "endIP":"xx", "leaseTerm":"xx"
            //           "subMask":"xx", "defaultGwIP":"xx","DNS1":"xxx", "DNS2":"xxx"}
            //    }
            var startIP = $('#netvTabLanSIPVal').val();
            var endIP = $('#netvTabLanEIPVal').val();
            var defaultGwIP = $('#netvTabLanDefaultGWVal').val();
            var DNS1 = $('#netvTabLanDhcpDNS1Val').val();
            var DNS2 = $('#netvTabLanDhcpDNS2Val').val();
            if((false == tools.chkIpAddress(startIP))||
                (false == tools.chkIpAddress(endIP))||
                (false == tools.chkIpAddress(defaultGwIP))||
                (false == tools.chkIpAddress(DNS1))||
                (false == tools.chkIpAddress(DNS2))){
                tools.msgBox(tools.jsSwitchLang(enJsMap, cnJsMap, 'invalidIPVal')); //发现无效的IP地址
                return;
            }
            var selectedData =  {
                "dhcpStatus": $("#netvTabLan input[name=netvTabLanDHCPRadio]:checked").val(),
                "startIP": startIP,
                "endIP": endIP,
                "leaseTerm": $('#netvTabLanLeaseVal').val(),
                "subMask": $("#netvTabLanDhcpSubmaskSelector").children('option:selected').val(),
                "defaultGwIP": defaultGwIP,
                "DNS1": DNS1,
                "DNS2": DNS2
            }
            var str = {
                "command":"setDhcpCfg",
                "dat":{
                    "DHCP":selectedData
                }
            }
            parameters = JSON.stringify(str);
            $.ajax({
                type:"POST",
                url: getURL(), //"/cgi-bin/cgi.cgi",
                data:parameters,
                contentType: "application/json",
                dataType: 'json',
                success: (res)=>{
                    // 返回参数格式
                    // { "rc": 0/1, "errCode": "xxx" }
                    //var data = JSON.parse(res);
                    var data = res;
                    if(0 == data.rc){
                        oStore.DHCP = selectedData;
                        console.log(data.dat);
                        tools.msgBox(tools.jsSwitchLang(enJsMap, cnJsMap, 'operationSucc')+ ' code:' + data.errCode); //'操作成功!
                    }
                    else{
                        tools.msgBox(data.errCode);
                    }
                },
                error: function (errorThrown) { tools.msgBoxFailed(errorThrown);}
            });
        });
        // netvTabRTMPApplyCfgBtn
        $('#netvTabRTMPApplyCfgBtn').click(()=>{
            var selectedData =  $('#RTMPInforIPValSelector').children('option:selected').val();
        //   {"command":"setRtmpServerIP",
        //     "dat": {
        //         "RTMP":{ "ServerIP": "xxx"}
        //       }
        //   }
            var str = {
                "command":"setRtmpServerIP",
                "dat":{
                    "RTMP": {
                        "ServerIP": selectedData
                    }
                }
            }
            parameters = JSON.stringify(str);
            $.ajax({
                type:"POST",
                url: getURL(), //"/cgi-bin/cgi.cgi",
                data:parameters,
                contentType: "application/json",
                dataType: 'json',
                success: (res)=>{
                    // 返回参数格式
                    // { "rc": 0/1, "errCode": "xxx" }
                    //var data = JSON.parse(res);
                    var data = res;
                    if(0 == data.rc){
                        console.log(data.dat);
                        oStore.RTMP.ServerIP = selectedData;
                        //2. refresh the channel list table
                        $("#netvTabRTMPChannelTable tr:gt(1)").empty("");
                        // *** HTML
                        // <tr> <td><input type='checkbox' checked='' /></td> <td><input class='netvTabRTMPChannelNameVal'/></td> <td><input class='netvTabRTMPChannelCodeVal'/></td> <td><a id='netvTabRTMPChannelRefVal'></a></td></tr>
                        oStore.RTMP.channelList.forEach(function(value,index){
                            let rtmpRefUrl = "rtmp://" + oStore.RTMP.ServerIP +  ":" + oStore.store.defaultRtmpSrvPortNum + "/" + oStore.store.defaultRtmpSrvAppName + "/";//":1935/live/";
                            let tr =  "<tr> <td><input type='checkbox' /></td>" +
                                "<td><input class='netvTabRTMPChannelNameVal' value=" + value.Name + "></td>" +
                                "<td><input class='netvTabRTMPChannelCodeVal' value="+ value.Code+"></td>" +
                                "<td><a style='color: red'>" + rtmpRefUrl + value.Code + "</a></td></tr>"
                            $("#netvTabRTMPChannelTable").append(tr);
                        });

                        tools.msgBox('操作成功! code:' + data.errCode);
                    }
                    else{
                        tools.msgBox(data.errCode);
                    }
                },
                error: function (errorThrown) { tools.msgBoxFailed(errorThrown);}
            });
        });
        // netvTabRTMPNewBtn
        $('#netvTabRTMPNewBtn').click(()=>{
            let tr =  "<tr> <td><input type='checkbox' /></td>" +
                "<td><input class='netvTabRTMPChannelNameVal' value=''></td>" +
                "<td><input class='netvTabRTMPChannelCodeVal' value=''></td>" +
                "<td><a></a></td></tr>"
            $("#netvTabRTMPChannelTable").append(tr);

        });
        // netvTabRTMPDelBtn
        $('#netvTabRTMPDelBtn').click(()=>{
            tools.msgBox(tools.jsSwitchLang(enJsMap, cnJsMap, 'nvDelLinesWarning'));//alert('所有选中的行将被删除！');
            // get the selected idx file information
            $(":checkbox:checked","#netvTabRTMPChannelTable").each(function(){
                idx = $(this).parents("tr").index();  // 获取checkbox所在行的顺序
                $("#netvTabRTMPChannelTable").find("tr:eq("+ idx +")").remove();
            });

        });
        // netvTabRTMPApplyBtn
        $('#netvTabRTMPApplyBtn').click(()=>{
            var parametersErr = '';
            var selectedData = [];
            $("#netvTabRTMPChannelTable").find("tr").each(function(idx, item){
                var name = $(item).find(".netvTabRTMPChannelNameVal").val();
                var code = $(item).find(".netvTabRTMPChannelCodeVal").val();
                if((undefined != name) && (undefined != code)){
                    if('' == name || '' == code){
                        parametersErr = tools.jsSwitchLang(enJsMap, cnJsMap, 'nvChannelValErr')+ (idx-2) +")"; //"频道名称和频道编码取值无效(无效行号="
                        return false; // 用此方法退出jQuery each loop
                    }

                    let cfg = {
                        "Name": name,
                        "Code": code,
                        };
                    selectedData.push(cfg);
                }
            });
            if('' != parametersErr){
                alert(parametersErr);
                return;
            }
        //     {"command":"setRtmpChannel",
        //     "dat": {
        //         "RTMP":{
        //           "channelList": [ {"Name":"Cam01", "Code":"left-1"}, {...}
        //             ]}
        //       }
        //   }
            var str = {
                "command":"setRtmpChannel",
                "dat":{
                    "RTMP": {
                        "channelList": selectedData
                    }
                }
            }
            parameters = JSON.stringify(str);
            $.ajax({
                type:"POST",
                url: getURL(), //"/cgi-bin/cgi.cgi",
                data:parameters,
                contentType: "application/json",
                dataType: 'json',
                success: (res)=>{
                    // 返回参数格式
                    // { "rc": 0/1, "errCode": "xxx" }
                    //var data = JSON.parse(res);
                    var data = res;
                    if(0 == data.rc){
                        oStore.RTMP.channelList = selectedData;
                        tools.msgBox(tools.jsSwitchLang(enJsMap, cnJsMap, 'operationSucc')+ ' code:' + data.errCode); //'操作成功!
                        console.log(data.dat);
                    }
                    else{
                        tools.msgBox(data.errCode);
                    }
                },
                error: function (errorThrown) { tools.msgBoxFailed(errorThrown);}
            });
        });
        // netvTabVpnConnectBtn
        $('#netvTabVpnConnectBtn').click(()=>{
            // "dat": {
            //     "VPN":{"vpnAddress":"xx", "vpnUser":"xx", "vpnPwd":"xx",
            //         "vpnProtocol":"PPTP/L2TP","vpnKey":"xx"}
            var selectedData =  {
                    "vpnAddress": $('#netvTabVpnAddrVal').val(),
                    "vpnUser": $('#netvTabVpnNameVal').val(),
                    "vpnPwd": $('#netvTabVpnPwdVal').val(),
                    "vpnProtocol": $('#netvTabVpnProtocolSelector').children('option:selected').val(),
                    "vpnKey": $('#netvTabVpnKeyVal').val()
                }
                var str = {
                "command":"connectVPN",
                "dat":{
                    "VPN": selectedData
                }
            }
            parameters = JSON.stringify(str);
            $.ajax({
                type:"POST",
                url: getURL(), //"/cgi-bin/cgi.cgi",
                data:parameters,
                contentType: "application/json",
                dataType: 'json',
                success: (res)=>{
                    // 返回参数格式
                    // "dat": {
                    //     "VPN":{"vpnStatus":"on/off"}
                    //   }
                    //var data = JSON.parse(res);
                    var data = res;
                    if(0 == data.rc){
                        oStore.VPN = selectedData;
                        oStore.VPN.vpnStatus = data.dat.VPN.vpnStatus;
                        $('#netvTabVpnStatusVal').text(oStore.VPN.vpnStatus);
                        tools.msgBox(tools.jsSwitchLang(enJsMap, cnJsMap, 'operationSucc')+ ' code:' + data.errCode); //'操作成功!
                    }
                    else{
                        tools.msgBox(data.errCode);
                    }
                },
                error: function (errorThrown) { tools.msgBoxFailed(errorThrown);}
            });
        });
        // netvTabRoutingRefreshBtn
        $('#netvTabRoutingRefreshBtn').click(()=>{
            // "dat": {
            //     "modulType": "LTE-Z/LTE-4G"
            //   }
            var str = {
                "command":"getRoutingInfor",
                "dat":{
                    "modulType":  $('#netvTabRoutingModuleSelector').children('option:selected').val()
                }
            }
            parameters = JSON.stringify(str);
            $.ajax({
                type:"POST",
                url: getURL(), //"/cgi-bin/cgi.cgi",
                data:parameters,
                contentType: "application/json",
                dataType: 'json',
                success: (res)=>{
                    // 返回参数格式
                    //   "dat": {
                    //     "routing":[
                    //         {"dstNet":"xx", "subMask":"xx", "gwIP":"xx", "ifName":"xx", "Metric":"xx"},
                    //         {..} ]  }
                    //var data = JSON.parse(res);
                    var data = res;
                    if(0 == data.rc){
                        console.log(data.dat);
                        let text = "No.  Dst.Net       SubMask    Gateway       Interface     Metric" + " \n ";
                        data.dat.routing.forEach(function(value,index){
                            let cnt = index + 1;
                            let line = cnt + '    ' + value.dstNet + '    ' + value.subMask + '    ' + value.gwIP + '    ' + value.ifName + '    ' + value.Metric + " \n ";
                            text = text + line;
                        });
                        $('#netvTabRoutingTextarea').text(text);
                    }
                    else{
                        tools.msgBox(data.errCode);
                    }
                },
                error: function (errorThrown) { tools.msgBoxFailed(errorThrown);}
            });
        });
        // routing operation
        function routingOperation(action){
            var dstNet = $('#netvTabRoutingInputDstNet').val();
            var subMask = $('#netvTabRoutingInputSubmask').val();
            var gwIP = $('#netvTabRoutingInputGW').val();
            var ifName = $('#netvTabRoutingInputIf').val();
            var Metric = $('#netvTabRoutingInputMetric').val();
            var parametersErr = '';
            if((undefined == dstNet)||(undefined == subMask)||(undefined == gwIP)||(undefined == ifName)||(undefined == Metric)
                ||('' == dstNet)||('' == subMask)||('' == gwIP)||(false == tools.chkIpAddress(gwIP))||('' == ifName)||('' == Metric)){
                // alert("WLAN Port不能为空!");
                parametersErr = tools.jsSwitchLang(enJsMap, cnJsMap, 'nvAbortErr1')+action+tools.jsSwitchLang(enJsMap, cnJsMap, 'nvAbortErr2');//"取值无效,放弃["+action+"]操作！";
                alert(parametersErr);
                return;
            }
            // "dat": {
            //     "operation": "add/modify/del",
            //     "routingData": {"dstIP":"xx", "subMask":"xx", "gwIP":"xx", "ifName":"xx", "Metric":"xx"}
            var str = {
                "command":"setRouting",
                "dat":{
                    "operation": action,
                    "routingData": {
                        "dstNet": dstNet,
                        "subMask": subMask,
                        "gwIP": gwIP,
                        "ifName": ifName,
                        "Metric": Metric
                    }
                }
            }
            parameters = JSON.stringify(str);
            $.ajax({
                type:"POST",
                url: getURL(), //"/cgi-bin/cgi.cgi",
                data:parameters,
                contentType: "application/json",
                dataType: 'json',
                success: (res)=>{
                    // 返回参数格式
                    // { "rc": 0/1, "errCode": "xxx" }
                    //var data = JSON.parse(res);
                    var data = res;
                    if(0 == data.rc){
                        console.log(data.dat);
                        tools.msgBox(tools.jsSwitchLang(enJsMap, cnJsMap, 'operationSucc')+ ' code:' + data.errCode); //'操作成功!
                    }
                    else{
                        tools.msgBox(data.errCode);
                    }
                },
                error: function (errorThrown) { tools.msgBoxFailed(errorThrown);}
            });
        }
        $('#ntvtrAddBtn').click(()=>{
            routingOperation('add');
        });
        $('#ntvtrDelBtn').click(()=>{
            routingOperation('del');
        });
        /* removed: 20190521, it's difficult to locate the data line and modify it in the table.
        $('#ntvtrChgBtn').click(()=>{
            routingOperation('modify');
        });
        */
        // Firewall and Filter
        // nvtMApplyBtn
        $('#nvtMApplyBtn').click(()=>{
            var selectedData = {
                "ipFilter": '', "macFilter": '', "DMZ":{"IP":'', "Status":''}
            };
            // $("#netvTabFWFilterTable").find("tr").each(function(idx, item){
                $("#swIPFilterCkb").is(':checked') ? selectedData.ipFilter = 'on' : selectedData.ipFilter = 'off';
                $("#swMacFilterCkb").is(':checked')? selectedData.macFilter = 'on' : selectedData.macFilter = 'off';
                $("#nvtMDMZEnableCkb").is(':checked')? selectedData.DMZ.Status = 'on' : selectedData.DMZ.Status = 'off';
            // });
            var dmzIP = $('#nvtMDMZIPAddressVal').val();
            if(false == tools.chkIpAddress(dmzIP)){
                tools.msgBox(tools.jsSwitchLang(enJsMap, cnJsMap, 'invalidIPVal')); //发现无效的IP地址
                return;
            }
            selectedData.DMZ.IP = dmzIP;
            // "dat": {
            //     "FireWall":{
            //          "ipFilter":"off", "macFilter":"on", "DMZ":{"IP":"123.3.3.1", "Status":"on"}}
            //   }
            var str = {
                "command":"setFirewall",
                "dat":{
                    "FireWall": selectedData
                }
            }
            parameters = JSON.stringify(str);
            $.ajax({
                type:"POST",
                url: getURL(), //"/cgi-bin/cgi.cgi",
                data:parameters,
                contentType: "application/json",
                dataType: 'json',
                success: (res)=>{
                    // 返回参数格式
                    // { "rc": 0/1, "errCode": "xxx" }
                    //var data = JSON.parse(res);
                    var data = res;
                    if(0 == data.rc){
                        oStore.FireWall.ipFilter = selectedData.ipFilter;
                        oStore.FireWall.macFilter = selectedData.macFilter;
                        oStore.FireWall.DMZ = selectedData.DMZ;
                        tools.msgBox(tools.jsSwitchLang(enJsMap, cnJsMap, 'operationSucc')+ ' code:' + data.errCode); //'操作成功!
                        console.log(data.dat);
                    }
                    else{
                        tools.msgBox(data.errCode);
                    }
                },
                error: function (errorThrown) { tools.msgBoxFailed(errorThrown);}
            });
        });
        // IP filter
        // nvTPFWIPFilterNewBtn
        $('#nvTPFWIPFilterNewBtn').click(()=>{
            // let lines = $("#firewallIPFilterTbl").find("tr").length;
            // let index = lines + 10;
            let tr = "<tr> <td><input type='checkbox' /></td> " +
                "<td><input class='nvtpfLanIPVal' style='width:100px' value=''></td> <td><input  style='width:100px' class='nvtpfLanPortVal' value=''></td>" +
                "<td><input class='nvtpfWLanIPVal' style='width:100px' value=''></td> <td><input style='width:100px' class='nvtpfWLanPortVal' value=''></td>" +
                "<td><select style='width:100px'><option value='enable'>Enable</option><option selected value='disbale'>Disbale</option></select></td></tr>";
            $("#firewallIPFilterTbl").append(tr);
        });
        // nvTPFWIPFilterDelBtn
        $('#nvTPFWIPFilterDelBtn').click(()=>{
            tools.msgBox(tools.jsSwitchLang(enJsMap, cnJsMap, 'nvDelLinesWarning')); //alert('所有选中的行将被删除！'); //TODO:是否发给服务器再删除？
            // get the selected idx file information
            $(":checkbox:checked","#firewallIPFilterTbl").each(function(){
                // alert('所有选中的行都会被删除！');
                idx = $(this).parents("tr").index();  // 获取checkbox所在行的顺序
                $("#firewallIPFilterTbl").find("tr:eq("+ idx +")").remove();
            });
        });
        // nvTPFWIPFilterApplyallBtn
        // 20190521: remove 'Validation' parameter.
        $('#nvTPFWIPFilterApplyallBtn').click(()=>{
            var parametersErr = '';
            var selectedData = [];
            $("#firewallIPFilterTbl").find("tr").each(function(idx, item){
                //var Validation = $(item).find(".nvtpfValiVal").val();
                var LanIPs = $(item).find(".nvtpfLanIPVal").val();
                var LanPort = $(item).find(".nvtpfLanPortVal").val();
                var WLanIPs = $(item).find(".nvtpfWLanIPVal").val();
                var WLanPort= $(item).find(".nvtpfWLanPortVal").val();
                //var Protocol= $(item).find(".nvtpfProtocolVal").val();
                var Status = $(item).find("select").children('option:selected').val();
                if(/*(undefined != Validation) && */(undefined != LanIPs) && (undefined != LanPort) && (undefined != WLanIPs) && (undefined != WLanPort) && /*(undefined != Protocol) && */ (undefined != Status)){
                    if(('' == LanIPs) || (false == tools.chkIpAddress(LanIPs)) || ('' == LanPort) || ('' == WLanIPs) || (false == tools.chkIpAddress(WLanIPs)) || ('' == WLanPort) || /*('' == Protocol) ||*/ ('' == Status)){
                        // alert("WLAN Port不能为空!");
                        parametersErr = tools.jsSwitchLang(enJsMap, cnJsMap, 'nvIcorrectValErr')+ (idx-2) +")";//"取值无效(无效行号="
                        return false; // 用此方法退出jQuery each loop
                    }
                    // let mask = $(item).find("select").children('option:selected').val();
                    let cfg = {//"Validation": Validation,
                            "LanIPs": LanIPs,
                            "LanPort": LanPort,
                            "WLanIPs": WLanIPs,
                            "WLanPort":WLanPort,
                            //"Protocol":Protocol,
                            "Status": Status
                        };
                    selectedData.push(cfg);
                }
            });
            if('' != parametersErr){
                alert(parametersErr);
                return;
            }
            // "dat": {
            //     "FireWall":{
            //       "ipList":[{"LanIPs":"xx", "LanPort":"xx",
            //                  "WLanIPs":"xx", "WLanPort":"xx", "Status":xx"}
            //         ]}
            //   }
            var str = {
                "command":"setIPFilterTable",
                "dat":{
                    "FireWall": {
                        "ipList": selectedData
                    }
                }
            }
            parameters = JSON.stringify(str);
            $.ajax({
                type:"POST",
                url: getURL(), //"/cgi-bin/cgi.cgi",
                data:parameters,
                contentType: "application/json",
                dataType: 'json',
                success: (res)=>{
                    // 返回参数格式
                    // { "rc": 0/1, "errCode": "xxx" }
                    //var data = JSON.parse(res);
                    var data = res;
                    if(0 == data.rc){
                        oStore.FireWall.ipList = selectedData;
                        tools.msgBox(tools.jsSwitchLang(enJsMap, cnJsMap, 'operationSucc')+ ' code:' + data.errCode); //'操作成功!
                        console.log(data.dat);
                    }
                    else{
                        tools.msgBox(data.errCode);
                    }
                },
                error: function (errorThrown) { tools.msgBoxFailed(errorThrown);}
            });
        });
        // Mac Filter
        // nvTMFMacFilterNewBtn
        $('#nvTMFMacFilterNewBtn').click(()=>{
            let tr = "<tr> <td><input type='checkbox' /></td> <td><input class='nvTMFMacVal'  value=''></td>" +
                "<td><select><option value='enable'>Enable</option> <option selected value='disable'>Disable</option> </select></td>" +
                "<td><input class='nvTMFMemoVal' style='width:300px' value=''></td></tr>";
            $("#firewallMacFilterTbl").append(tr);

        });
        // nvTMFMacFilterDelBtn
        $('#nvTMFMacFilterDelBtn').click(()=>{
            tools.msgBox(tools.jsSwitchLang(enJsMap, cnJsMap, 'nvDelLinesWarning'));//alert('所有选中的行将被删除！'); //TODO:是否发给服务器再删除？
            // get the selected idx file information
            $(":checkbox:checked","#firewallMacFilterTbl").each(function(){
                // alert('所有选中的行都会被删除！');
                idx = $(this).parents("tr").index();  // 获取checkbox所在行的顺序
                $("#firewallMacFilterTbl").find("tr:eq("+ idx +")").remove();
            });
        });
        // nvTMFMacFilterApplyallBtn
        $('#nvTMFMacFilterApplyallBtn').click(()=>{
            var parametersErr = '';
            var selectedData = [];
            $("#firewallMacFilterTbl").find("tr").each(function(idx, item){
                var mac = $(item).find(".nvTMFMacVal").val();
                var Desc = $(item).find(".nvTMFMemoVal").val();
                var Status = $(item).find("select").children('option:selected').val();
                if((undefined != mac)&&(undefined != Desc)&&(undefined != Status)){
                    if(('' == mac)||(false == tools.chkMacAddress(mac))||('' == Status)/*||('' == Desc)*/){
                        // alert("WLAN Port不能为空!");
                        parametersErr = tools.jsSwitchLang(enJsMap, cnJsMap, 'nvIcorrectValErr')+ (idx-2) +")";//"取值无效(无效行号="
                        return false; // 用此方法退出jQuery each loop
                    }
                    let cfg = {"MAC": mac,
                            "Desc": Desc,
                            "Status": Status
                        };
                    selectedData.push(cfg);
                }
            });
            if('' != parametersErr){
                alert(parametersErr);
                return;
            }
            // "dat": {
            //     "FireWall":{
            //      "macList":[{"MAC":"xx", "Status":"Enable/Disable","Desc":"xx-Max40字符"}]}
            //   }
            var str = {
                "command":"setMacFilterTable",
                "dat":{
                    "FireWall": {
                        "macList": selectedData
                    }
                }
            }
            parameters = JSON.stringify(str);
            $.ajax({
                type:"POST",
                url: getURL(), //"/cgi-bin/cgi.cgi",
                data:parameters,
                contentType: "application/json",
                dataType: 'json',
                success: (res)=>{
                    // 返回参数格式
                    // { "rc": 0/1, "errCode": "xxx" }
                    //var data = JSON.parse(res);
                    var data = res;
                    if(0 == data.rc){
                        oStore.FireWall.macList = selectedData;
                        tools.msgBox(tools.jsSwitchLang(enJsMap, cnJsMap, 'operationSucc')+ ' code:' + data.errCode); //'操作成功!
                        console.log(data.dat);
                    }
                    else{
                        tools.msgBox(data.errCode);
                    }
                },
                error: function (errorThrown) { tools.msgBoxFailed(errorThrown);}
            });
        });
        // porting mapping
        $('#netvTabMappingPortTblNewBtn').click(()=>{
            // get line index of table
            let tab = document.getElementById("netvTabMappingPortTbl") ;
            let newLineIndex = tab.rows.length - 3; //因为jquery在清除表格时留下一行空tr，所以要多减1
            let tr = "<tr> <td><input type='checkbox' /></td>" +
                    "<td><select class='netvTabMappingPortTblWlanSelector' style='width:70px'><option value='LTE-4G'>LTE-4G</option><option value='LTE-Z'>LTE-Z</option></select>" +
                    "    <a>:</a><input class='netvTabMappingPortTblWlanPortVal' placeholder='10000 - 20000' style='width:90px'/></td> " +
                    "<td><select class='netvTabMappingPortTblLanSelector' style='width:100px' id='netvTabMappingPortTblLanSelector"+newLineIndex+"' ></select>" +
                    "    <a>:</a><input class='netvTabMappingPortTblLanPortVal' style='width:70px'/></td>" +
                    "<td><a style='width:30px' class='netvTabMappingPortTblLanSlot' id='netvTabMappingPortTblLanSlot"+newLineIndex+"'></a></td>" +
                    "<td><input class='netvTabMappingMemoVal' style='width:200px'/></td> </tr> "
            $("#netvTabMappingPortTbl").append(tr);
            // insert LAN:IP list
            oStore.LAN.accessList.forEach((element, index)=>{ // create lan:ip select->options
                let lanOptionStr = "<option value='"+element.IP+"'>"+element.IP+"</option>";
                $('#netvTabMappingPortTblLanSelector'+newLineIndex).append(lanOptionStr);
            });
            //
            //取值变化时进行hightlight => red 处理
            $('.netvTabMappingPortTblWlanSelector').change(this.netvTabMappingPortTblWlanSelectorOnChange);
            $('.netvTabMappingPortTblLanSelector').change(this.netvTabMappingPortTblLanSelectorOnChange);

            $('.netvTabMappingPortTblWlanPortVal').change(this.netvTabMappingPortTblXXPortValOnChange);
            $('.netvTabMappingPortTblLanPortVal').change(this.netvTabMappingPortTblXXPortValOnChange);
        });
        $('#netvTabMappingPortTblDelBtn').click(()=>{
            tools.msgBox(tools.jsSwitchLang(enJsMap, cnJsMap, 'nvDelLinesWarning'));//alert('所有选中的行将被删除！'); //TODO:是否发给服务器再删除？
            // get the selected idx file information
            $(":checkbox:checked","#netvTabMappingPortTbl").each(function(){
                // alert('所有选中的行都会被删除！');
                idx = $(this).parents("tr").index();  // 获取checkbox所在行的顺序
                $("#netvTabMappingPortTbl").find("tr:eq("+ idx +")").remove();
            });
        });
        $('#netvTabMappingPortTblApplyBtn').click(()=>{
            var parametersErr = '';
            var selectedData = [];
            $("#netvTabMappingPortTbl").find("tr").each(function(idx, item){
                // var wlan =  $('#netvTabMappingPortTblWlanSelector').children('option:selected').val();
                let wlan = $(item).find(".netvTabMappingPortTblWlanSelector").children('option:selected').val();
                let wlanPort = $(item).find('.netvTabMappingPortTblWlanPortVal').val();
                let slot = $(item).find('.netvTabMappingPortTblLanSlot').text();
                let ip = $(item).find(".netvTabMappingPortTblLanSelector").children('option:selected').val();
                let lanPort = $(item).find('.netvTabMappingPortTblLanPortVal').val();
                if(undefined != wlanPort){
                    if('' == wlanPort || (parseInt(wlanPort)<10000) ||(parseInt(wlanPort) > 20000)){
                        // alert("WLAN Port不能为空!");
                        parametersErr = tools.jsSwitchLang(enJsMap, cnJsMap, 'nvIcorrectWLanPortErr1')+ (idx-2) +tools.jsSwitchLang(enJsMap, cnJsMap, 'nvIcorrectWLanPortErr2');//"WLAN Port取值无效(无效行号="+ (idx-2) +"), 请确保取值范围[10000 - 20000]";
                        return false; // 用此方法退出jQuery each loop
                    }
                let cfg = {"WLanSlot": wlan,
                            "WLanPort": wlanPort,
                            "LanSlot": slot,
                            "LanIP": ip,
                            "LanPort": lanPort,
                            "Desc": $(item).find(".netvTabMappingMemoVal").val(),
                        };
                    selectedData.push(cfg);
                }
            });
            if('' != parametersErr){
                alert(parametersErr);
                return;
            }
            // "Mapping":{
            //     "portMapping":[{"WLanSlot":"LTE-4G", "WLanPort":"11000","LanSlot":"LAN1", "LanIP":"192.1.1.3", "LanPort":"110","Desc":"mock-xx-Max40字符"}, {...}]
            // }
            var str = {
                "command":"setPortMapping",
                "dat":{
                    "Mapping": {
                        "portMapping": selectedData
                    }
                }
            }
            parameters = JSON.stringify(str);
            //console.log('Send=>'+parameters);
            $.ajax({
                type:"POST",
                url: getURL(), //"/cgi-bin/cgi.cgi",
                data:parameters,
                contentType: "application/json",
                dataType: 'json',
                success: (res)=>{
                    // 返回参数格式
                    // { "rc": 0/1, "errCode": "xxx" }
                    //var data = JSON.parse(res);
                    var data = res;
                    console.log(data);
                    if(0 == data.rc){
                        oStore.Mapping.portMapping = selectedData;
                        // console.log(data.dat);
                        tools.msgBox(tools.jsSwitchLang(enJsMap, cnJsMap, 'operationSucc')+ ' code:' + data.errCode); //'操作成功!
                    }
                    else{
                        tools.msgBox(data.errCode);
                    }
                },
                error: function (errorThrown) { tools.msgBoxFailed(errorThrown);}
            });
        });
        // nvtnvtMChannelMapApplyBtn
        $('#nvtnvtMChannelMapApplyBtn').click(()=>{
            var selectedData = {
                "slotLTEZ":{"LAN1":"", "LAN2":"", "LAN3":""},
                "slotLTE4G":{"LAN1":"", "LAN2":"", "LAN3":""}
            };
            $("#nvtMChannelZLan1Ckb").is(':checked') ? selectedData.slotLTEZ.LAN1 = 'on' : selectedData.slotLTEZ.LAN1 = 'off';
            $("#nvtMChannelZLan2Ckb").is(':checked') ? selectedData.slotLTEZ.LAN2 = 'on' : selectedData.slotLTEZ.LAN2 = 'off';
            $("#nvtMChannelZLan3Ckb").is(':checked') ? selectedData.slotLTEZ.LAN3 = 'on' : selectedData.slotLTEZ.LAN3 = 'off';
            $("#nvtMChannel4GLan1Ckb").is(':checked') ? selectedData.slotLTE4G.LAN1 = 'on' : selectedData.slotLTE4G.LAN1 = 'off';
            $("#nvtMChannel4GLan2Ckb").is(':checked') ? selectedData.slotLTE4G.LAN2 = 'on' : selectedData.slotLTE4G.LAN2 = 'off';
            $("#nvtMChannel4GLan3Ckb").is(':checked') ? selectedData.slotLTE4G.LAN3 = 'on' : selectedData.slotLTE4G.LAN3 = 'off';
            // "dat": {
            //   "Mapping":{ "slotLTEZ":{"LAN1":"on", "LAN2":"off", "LAN3":"on"},
            //               "slotLTE4G":{"LAN1":"off", "LAN2":"on", "LAN3":"off"},
            //      }
            //   }
            var str = {
                "command":"setSlotChannelMapping",
                "dat":{
                    "Mapping": selectedData
                }
            }
            parameters = JSON.stringify(str);
            $.ajax({
                type:"POST",
                url: getURL(), //"/cgi-bin/cgi.cgi",
                data:parameters,
                contentType: "application/json",
                dataType: 'json',
                success: (res)=>{
                    // 返回参数格式
                    // { "rc": 0/1, "errCode": "xxx" }
                    //var data = JSON.parse(res);
                    var data = res;
                    if(0 == data.rc){
                        oStore.Mapping.slotLTEZ = selectedData.slotLTEZ;
                        oStore.Mapping.slotLTE4G = selectedData.slotLTE4G;
                        tools.msgBox(tools.jsSwitchLang(enJsMap, cnJsMap, 'operationSucc')+ ' code:' + data.errCode); //'操作成功!
                        console.log(data.dat);
                    }
                    else{
                        tools.msgBox(data.errCode);
                    }
                },
                error: function (errorThrown) { tools.msgBoxFailed(errorThrown);}
            });
        });
        // netvTabMappMacIPNewBtn
        $('#netvTabMappMacIPNewBtn').click(()=>{
            let tr = "<tr> <td><input type='checkbox' /></td> <td><input class='netvTabMappingMacVal' value=''></td>" +
                    "<td><input class='netvTabMappingIPVal' type='IP' placeholder='10.10.10.11' value=''></td>" +
                    "<td><input class='netvTabMappingMacIpMemoVal' style='width:300px' value=''></td></tr>";
            $("#netvTabMappingMacIPTbl").append(tr);
        });
        // netvTabMappMacIPDelBtn
        $('#netvTabMappMacIPDelBtn').click(()=>{
            tools.msgBox(tools.jsSwitchLang(enJsMap, cnJsMap, 'nvDelLinesWarning'));//alert('所有选中的行将被删除！'); //TODO:是否发给服务器再删除？
            // get the selected idx file information
            $(":checkbox:checked","#netvTabMappingMacIPTbl").each(function(){
                // alert('所有选中的行都会被删除！');
                idx = $(this).parents("tr").index();  // 获取checkbox所在行的顺序
                $("#netvTabMappingMacIPTbl").find("tr:eq("+ idx +")").remove();
            });
        });
        // netvTabMappMacIPApplyBtn
        $('#netvTabMappMacIPApplyBtn').click(()=>{
            var parametersErr = '';
            var selectedData = [];
            $("#netvTabMappingMacIPTbl").find("tr").each(function(idx, item){
                var mac = $(item).find(".netvTabMappingMacVal").val();
                var ip = $(item).find(".netvTabMappingIPVal").val();
                // if(('' != mac) && (undefined != mac)){
                if((undefined != mac)&&(undefined != ip)){
                    if(('' == mac)||(false == tools.chkMacAddress(mac))||
                        ('' == ip)||(false == tools.chkIpAddress(ip))){
                        // alert("WLAN Port不能为空!");
                        parametersErr = tools.jsSwitchLang(enJsMap, cnJsMap, 'nvIcorrectValErr')+ (idx-2) +")";//"取值无效(无效行号="+ (idx-2) +")";
                        return false; // 用此方法退出jQuery each loop
                    }
                    let cfg = {"MAC": mac,
                        "IP": ip,
                        "Desc": $(item).find(".netvTabMappingMacIpMemoVal").val(),
                    };
                    selectedData.push(cfg);
                }
            });
            if('' != parametersErr){
                alert(parametersErr);
                return;
            }
            // "dat": {
            //     "Mapping":{
            //           "mac2ip":[{"MAC":"01-29-03", "IP":"123.4.3.1","Desc":"xx-Max40字符"},
            //                     {"MAC":"01-29-04", "IP":"123.4.3.2","Desc":"xx-Max40字符"}]
            //         }
            //   }
            var str = {
                "command":"setMacIPMapping",
                "dat":{
                    "Mapping": {
                        "mac2ip": selectedData
                    }
                }
            }
            parameters = JSON.stringify(str);
            $.ajax({
                type:"POST",
                url: getURL(), //"/cgi-bin/cgi.cgi",
                data:parameters,
                contentType: "application/json",
                dataType: 'json',
                success: (res)=>{
                    // 返回参数格式
                    // { "rc": 0/1, "errCode": "xxx" }
                    //var data = JSON.parse(res);
                    var data = res;
                    if(0 == data.rc){
                        oStore.Mapping.mac2ip = selectedData;
                        console.log(data.dat);
                        tools.msgBox(tools.jsSwitchLang(enJsMap, cnJsMap, 'operationSucc')+ ' code:' + data.errCode); //'操作成功!
                    }
                    else{
                        tools.msgBox(data.errCode);
                    }
                },
                error: function (errorThrown) { tools.msgBoxFailed(errorThrown);}
            });
        });
    });
}
//networks LAN submask设置为一个值, 即只支持一个VLAN.
CNetworkView.prototype.netvTabLanCfgListTableSelectOnChange = function(node){
    let submask = $(this).children('option:selected').val();
    $(".netvTabLanCfgListTableSelect").val(submask);
    // for(let index=0; index < 3; index++){
    //     $("#"+"netvTabLanCfgListTableSelect"+ index).val(submask);
    // }
}
//取值变化时进行hightlight => red 处理
CNetworkView.prototype.netvTabMappingPortTblLanSelectorOnChange = function(node){
    let ipVal = $(this).children('option:selected').val();
    let selectID = $(this).attr("id");
    let ipID = '#netvTabMappingPortTblLanSlot' + selectID.replace("netvTabMappingPortTblLanSelector","");
    oStore.LAN.accessList.forEach((element, index)=>{ // create lan:ip select->options
        if(ipVal == element.IP){
            $(ipID).text(element.port);
            $(ipID).css({"color": "red"});
        }
        // console.error('No SLot is found!');
    });
}
CNetworkView.prototype.netvTabMappingPortTblWlanSelectorOnChange = function(node){
    $(this).css({"color": "red"});
}
CNetworkView.prototype.netvTabMappingPortTblXXPortValOnChange = function(node){
    $(this).css({"color": "red"});
}
CNetworkView.prototype.enHtmlMap = {
    ntwvTabRouting:"Routing",ntwvTabPortF:"Firewall/Filter",ntwvTabMappinf:"Mapping",
    netvTabGnssTitleTxt:"GNSS Configuration", netvTabGnssTargetSimTxt:"Dest. SIM Number", netvTabGnssTargetSimSaveBtn:"Save",
    netvTabLanApplyLanCfgBtn:"Apply",nvtlanCfgTitle:"LAN Configuration", nvtlanDHCPCfgTitle:"DHCP Configuration",netvTabLanSubmask:"Network mask",/*netvTabLanRTMPServer:"RTMP Server IP",*/netvTabLanSIP:"Start IP address",netvTabLanEIP:"End IP address",netvTabLanLease:"Lease Term(min)",netvTabLanSubmask2:"Network mask",netvTabLanDefaultGW:"Default Gateway",netvTabLanApplyDhcpBtn:"Apply All",
    netvTabVpnTitle:"VPN Passthrough",netvTabVpnAddr:"VPN Address",netvTabVpnName:"VPN User Name",netvTabVpnPwd:"VPN Password",netvTabVpnProtocol:"Protocol",netvTabVpnKey:"Sec. Key",netvTabVpnStatus:"Connection",netvTabVpnConnectBtn:"Connect",
    netvTabRoutingM:"Module:", netvTabRoutingRefreshBtn:"Refresh", ntvtrAddBtn:"ADD",ntvtrDelBtn:"DEL",//ntvtrChgBtn:"CHG",
    firewall:"Firewall",firewallIPFilterTblTxt:"IP Filter table",firewallMacFilterTable:"MAC Filter table", nvtIPFilterTXt:"IP Filter",nvtMacFilterTXt:"MAC Filter",
    swIPFilter:" Turn on IP filter",  swMacFilter:" MAC filter",nvtMDMZ:"DMZ host IP",nvtMDMZEnable:" Enable",nvtMApplyBtn:"Apply",
    /*nvtpfValidation:"Validation",*/ nvtpfLanIP:"LAN IP",nvtpfLanPort:"LAN Port",nvtpfWLanIP:"WLAN IP",nvtpfWLanPort:"WLAN Port",nvtpfProtocol:"Protocol",nvtpfStatus:"Status",
    nvTPFWIPFilterNewBtn:"New", nvTPFWIPFilterDelBtn:"Delete", nvTPFWIPFilterApplyallBtn:"Apply All",
    nvTMFMacFilterNewBtn:"New", nvTMFMacFilterDelBtn:"Delete", nvTMFMacFilterApplyallBtn:"Apply All",
    nvTMFStatus:"Status",nvTMFMemo:"Memo(Max40 char.)",
    netvTabMappingPortTblTitle:"Port mapping",netvTabMappingPortTblNewBtn:"New", netvTabMappingPortTblDelBtn:"Del", netvTabMappingPortTblApplyBtn:"Apply All",netvTabMappingPortTblDesc:"Memo(Max40 char.)",
    netvTabMappingSlotTblTitle:"Slot Mapping",nvtMChannel:"WLAN", nvtMSrc:"LAN",/*nvtMSlotOpt:"操作",*/nvtnvtMChannelMapApplyBtn:"Apply All",nvtMMemo:"The IP (marked & monitor data) can be transfered on GNSS",
    netvTabMappingMacIPTblTitle:"IP/MAC pair",netvTabMappMacIPNewBtn:"New", netvTabMappMacIPDelBtn:"Delete", netvTabMappMacIPApplyBtn:"Apply All",netvTabMappingMacIPTblDesc:"Memo(Max40 char.)",
    netvTabRTMPApplyCfgBtn:"Apply Cfg",RTMPInforTitle:"RTMP Configuration",RTMPInforIPTxt:"Server IP",RTMPInforPortTxt:"Port",RTMPInforAppTxt:"APP",RTMPInforAddrTxt:"Push URL",RTMPInforIPValSelectorWarning:"Attention：If selecte one, LAN_IP will be set to 'Static', DHCP will be disbaled!",netvTabRTMPNewBtn:"New", netvTabRTMPDelBtn:"Del", netvTabRTMPApplyBtn:"Apply All",netvTabRTMPChannelTableTitle:"RTMP Channel conf.",netvTabRTMPChannelNameTxt:"Channel Name",netvTabRTMPChannelNoTxt:"Channel Code",netvTabRTMPChannelRefTxt:"Full Address",
};
CNetworkView.prototype.cnHtmlMap = {
    ntwvTabRouting:"路由",ntwvTabPortF:"防火墙/过滤器",ntwvTabMappinf:"端口映射",
    netvTabGnssTitleTxt:"GNSS配置", netvTabGnssTargetSimTxt:"目标SIM卡号", netvTabGnssTargetSimSaveBtn:"保存",
    netvTabLanApplyLanCfgBtn:"应用LAN修改",nvtlanCfgTitle:"LAN 配置", nvtlanDHCPCfgTitle:"DHCP 配置", netvTabLanSubmask:"子网掩码",/*netvTabLanRTMPServer:"设置为RTMP服务器IP",*/ netvTabLanSIP:"起始IP地址",netvTabLanEIP:"终止IP地址",netvTabLanLease:"地址租期(分钟)",netvTabLanSubmask2:"子网掩码",netvTabLanDefaultGW:"默认网关",netvTabLanApplyDhcpBtn:"应用DHCP修改",
    netvTabVpnTitle:"VPN 穿透",netvTabVpnAddr:"VPN地址",netvTabVpnName:"VPN用户名",netvTabVpnPwd:"VPN密码",netvTabVpnProtocol:"协议",netvTabVpnKey:"连接身份密钥",netvTabVpnStatus:"VPN连接状态",netvTabVpnConnectBtn:"连接",
    netvTabRoutingM:"模块: ", netvTabRoutingRefreshBtn:"刷新", ntvtrAddBtn:"新加",ntvtrDelBtn:"删除",//ntvtrChgBtn:"修改",
    firewall:"防火墙设置", firewallIPFilterTblTxt:"IP过滤表",firewallMacFilterTable:"MAC过滤表", nvtIPFilterTXt:"IP 过滤",nvtMacFilterTXt:"MAC 过滤",
    swIPFilter:" 开启IP地址过滤", swMacFilter:" MAC过滤",nvtMDMZ:"DMZ主机IP", nvtMDMZEnable:" 激活",nvtMApplyBtn:"应用",
    /*nvtpfValidation:"有效期",*/ nvtpfLanIP:"局域网IP地址段",nvtpfLanPort:"局域网端口",nvtpfWLanIP:"广域网IP地址段",nvtpfWLanPort:"广域网端口",nvtpfProtocol:"协议类型",nvtpfStatus:"状态",
    nvTPFWIPFilterNewBtn:"新建", nvTPFWIPFilterDelBtn:"删除", nvTPFWIPFilterApplyallBtn:"应用所有",
    nvTMFMacFilterNewBtn:"新建", nvTMFMacFilterDelBtn:"删除", nvTMFMacFilterApplyallBtn:"应用所有",
    nvTMFStatus:"状态",nvTMFMemo:"描述(Max40字符)",
    netvTabMappingPortTblTitle:"端口映射",netvTabMappingPortTblNewBtn:"新建", netvTabMappingPortTblDelBtn:"删除", netvTabMappingPortTblApplyBtn:"应用所有",netvTabMappingPortTblDesc:"描述(Max40字符)",
    netvTabMappingSlotTblTitle:"通道映射",nvtMChannel:"WLAN通道", nvtMSrc:"LAN通道",/*nvtMSlotOpt:"操作",*/nvtnvtMChannelMapApplyBtn:"应用所有",nvtMMemo:"GNSS通道只传输特殊IP包(段标识+监控数据)",
    netvTabMappingMacIPTblTitle:"IP/MAC绑定",netvTabMappMacIPNewBtn:"新建", netvTabMappMacIPDelBtn:"删除", netvTabMappMacIPApplyBtn:"应用所有",netvTabMappingMacIPTblDesc:"描述(Max40字符)",
    netvTabRTMPApplyCfgBtn:"应用配置修改",RTMPInforTitle:"RTMP Server设置",RTMPInforIPTxt:"Server IP",RTMPInforPortTxt:"端口号",RTMPInforAppTxt:"推流APP名",RTMPInforAddrTxt:"推流地址",RTMPInforIPValSelectorWarning:"注意：选中后IP地址对应的LAN口会被设置为Static, DHCP将失效！",netvTabRTMPNewBtn:"新建", netvTabRTMPDelBtn:"删除", netvTabRTMPApplyBtn:"应用所有",netvTabRTMPChannelTableTitle:"RTMP频道配置表",netvTabRTMPChannelNameTxt:"频道名称",netvTabRTMPChannelNoTxt:"频道编码",netvTabRTMPChannelRefTxt:"频道引用地址",
};
CNetworkView.prototype.enJsMap = {
    operationSucc:'Operation is successful.',nvPortCfgErr:'Incorrect port cfg, please check the device.', nvPortMapLAN12ZErr:'[PortMapping]LAN1<->LTE-Z is already allocated in PORT table!',nvPortMapLAN22ZErr:'[PortMapping]LAN2<->LTE-Z is already allocated in PORT table!',nvPortMapLAN32ZErr: '[PortMapping]LAN3<->LTE-Z is already allocated in PORT table!',nvPortMapLAN12GErr: '[PortMapping]LAN1<->LTE-4G is already allocated in PORT table!',nvPortMapLAN22GErr:'[PortMapping]LAN2<->LTE-4G is already allocated in PORT table!',nvPortMapLAN32GErr:'[PortMapping]LAN3<->LTE-4G is already allocated in PORT table!',nvSetPortMap:'[Set Mapping]',
    nvMaskValErr:'All MASK should be same!incorrect(line=',nvIPValErr: "IP value is incorrect(line=", nvDelLinesWarning:'All selected lines will be deleted!',nvChannelValErr:"Channel name or code is incorrect.(line=",nvAbortErr1:"Incorrect value,abort[",nvAbortErr2:"] operation!",nvIcorrectValErr:"Incorrect value(Line=",nvIcorrectWLanPortErr1:"WLAN Port is incorrect(Line=",nvIcorrectWLanPortErr2:"), be sure the values[10000 - 20000]",
    invalidIPVal:"!! Invalid ip address is found !!", invalidMacVal:"'!! Invalid MAC address is found !!",
}
CNetworkView.prototype.cnJsMap = {
    operationSucc:'操作成功.',nvPortCfgErr:'端口配置异常，请检查设备！', nvPortMapLAN12ZErr:'[端口映射]表中已经建立LAN1<->LTE-Z高优先级映射!',nvPortMapLAN22ZErr:'[端口映射]表中已经建立LAN2<->LTE-Z高优先级映射!',nvPortMapLAN32ZErr: '[端口映射]表中已经建立LAN3<->LTE-Z高优先级映射!',nvPortMapLAN12GErr: '[端口映射]表中已经建立LAN1<->LTE-4G高优先级映射!',nvPortMapLAN22GErr:'[端口映射]表中已经建立LAN2<->LTE-4G高优先级映射!',nvPortMapLAN32GErr:'[端口映射]表中已经建立LAN3<->LTE-4G高优先级映射!',nvSetPortMap:'[设置映射]',
    nvMaskValErr:'所有MASK应该相同(无效行号=',nvIPValErr: "IP地址取值异常(无效行号=", nvDelLinesWarning:'所有选中的行将被删除！', nvChannelValErr:"频道名称和频道编码取值无效(无效行号=",nvAbortErr1:"取值无效,放弃[",nvAbortErr2:"]操作！",nvIcorrectValErr:"取值无效(无效行号=",nvIcorrectWLanPortErr1:"WLAN Port取值无效(无效行号=",nvIcorrectWLanPortErr2:"), 请确保取值范围[10000 - 20000]",
    invalidIPVal:"!! 无效的IP地址 !!", invalidMacVal:"!! 无效的MAC地址  !!",
}
