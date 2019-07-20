/**
 * CDashboardView View的主Class定义
 */
function CDashboardView(){
    // 构造函数
    var _this = this;
    //1.内部变量+内部函数
    //2.初始化对象和成员函数
    _this.node  =  document.getElementById( 'dashboardView' );
    _this.jqNode = $('#dashboardView'); // jQuery node object
    // 1.加载本view的html 2.注册控件回调函数 3.多语言实现
    _this.loadHtml();
}
CDashboardView.prototype.node;
CDashboardView.prototype.jqNode;
CDashboardView.prototype.activeMyView = function(){
    tools.ActivateViewByNodeInContainer(gMainView, this.node);
    this.render();
}
CDashboardView.prototype.deactiveMyView = function(){
    tools.viewShow(this.node, false);
}
CDashboardView.prototype.render = function(){
    $('#dsvLocTimeVal').text(tools.getDateByYMD(oStore.system.localDatetime)); 
    $('#dsvDurationTimeVal').text(tools.getDateByHMS(oStore.system.currDuration));
    $('#dsvHwMacVal').text(oStore.system.hwMAC);
    //$('#dsvHwIPVal').text(oStore.LAN.LAN[0].IP);
    $('#dsvHwIPVal').text(oStore.system.hostIP);
    $('#dsvIMEIVal').text(oStore.system.hwIMEI);
    $('#dsvFWVerVal').text(oStore.system.swVersion);
    //
    $('#dsvModTblZConnectVal').text(oStore.LTEZ.connection);
    $('#dsvLteZSignalVal').text(oStore.LTEZ.signal);
    $('#dsvModTbl4GConnectVal').text(oStore.LTE4G.connection);
    $('#dsvLte4GSignalVal').text(oStore.LTE4G.signal);
    $('#dsvModTblGnssConnectVal').text(oStore.GNSS.connection);
    $('#dsvGnssSignalVal').text(oStore.GNSS.signal);
}
CDashboardView.prototype.loadHtml = function(){
    // 1.加载本view的html 2.注册控件回调函数 3.多语言实现
    var enHtmlMap = this.enHtmlMap;
    var cnHtmlMap = this.cnHtmlMap;
    var enJsMap = this.enJsMap;
    var cnJsMap = this.cnJsMap;
    this.jqNode.load('views/CDashboardView.html', ()=>{
        tools.language = $('#langSelector').children('option:selected').val();
        tools.htmlSwitchLang(enHtmlMap, cnHtmlMap);
        //
        //LTE-Z 连接网络BTN
        $('#dsvmtZConnectBtn').click(function(){
            let str = 
            {
                "command":"operateModul",
                "dat": {
                    "modulType": "LTE-Z",
                    "operation": "on"
                  }
            }
            let parameters = JSON.stringify(str);
            $.ajax({
                type:"POST",
                url: getURL(), //"/cgi-bin/cgi.cgi",
                data:parameters,
                contentType: 'application/json',
                dataType: 'json',
                success: function(res){
                    /* 返回参数格式
                        { "rc": 0/1, "errCode": "xxx"}
                    */
                    //var data = JSON.parse(res);
                    var data = res;
                    if(0 == data.rc){
                        tools.msgBox(tools.jsSwitchLang(enJsMap, cnJsMap, 'dsvOptSucc') + " code: " + data.errCode);
                        console.log(data.dat);
                    }
                    else{
                        tools.msgBox(res);
                    }
                }
            });
        });
        //LTE-Z dis连接网络BTN
        $('#dsvmtZDisconBtn').click(function(){
            let str = 
            {
                "command":"operateModul",
                "dat": {
                    "modulType": "LTE-Z",
                    "operation": "off"
                    }
            }
            let parameters = JSON.stringify(str);
            $.ajax({
                type:"POST",
                url: getURL(), //"/cgi-bin/cgi.cgi",
                data:parameters,
                contentType: 'application/json',
                dataType: 'json',
                success: function(res){
                    /* 返回参数格式
                        { "rc": 0/1, "errCode": "xxx"}
                    */
                    //var data = JSON.parse(res);
                    var data = res;
                    if(0 == data.rc){
                        console.log(data.dat);
                        tools.msgBox(tools.jsSwitchLang(enJsMap, cnJsMap, 'dsvOptSucc') + " code: " + data.errCode);
                    }
                    else{
                        tools.msgBox(res);
                    }
                }
            });
        });
        //LTE-4G 连接网络BTN
        $('#dsvmt4GConnectBtn').click(function(){
            let str = 
            {
                "command":"operateModul",
                "dat": {
                    "modulType": "LTE-4G",
                    "operation": "on"
                  }
            }
            let parameters = JSON.stringify(str);
            $.ajax({
                type:"POST",
                url: getURL(), //"/cgi-bin/cgi.cgi",
                data:parameters,
                contentType: 'application/json',
                dataType: 'json',
                success: function(res){
                    /* 返回参数格式
                        { "rc": 0/1, "errCode": "xxx"}
                    */
                    //var data = JSON.parse(res);
                    var data = res;
                    if(0 == data.rc){
                        tools.msgBox(tools.jsSwitchLang(enJsMap, cnJsMap, 'dsvOptSucc') + " code: " + data.errCode);
                        console.log(data.dat);
                    }
                    else{
                        tools.msgBox(res);
                    }
                }
            });
        });
        //LTE-4G dis连接网络BTN
        $('#dsvmt4GDisconBtn').click(function(){
            let str = 
            {
                "command":"operateModul",
                "dat": {
                    "modulType": "LTE-4G",
                    "operation": "off"
                    }
            }
            let parameters = JSON.stringify(str);
            $.ajax({
                type:"POST",
                url: getURL(), //"/cgi-bin/cgi.cgi",
                data:parameters,
                contentType: 'application/json',
                dataType: 'json',
                success: function(res){
                    /* 返回参数格式
                        { "rc": 0/1, "errCode": "xxx"}
                    */
                    //var data = JSON.parse(res);
                    var data = res;
                    if(0 == data.rc){
                        tools.msgBox(tools.jsSwitchLang(enJsMap, cnJsMap, 'dsvOptSucc') + " code: " + data.errCode);
                        console.log(data.dat);
                    }
                    else{
                        tools.msgBox(res);
                    }
                }
            });
        });  
    });
}
// 多语言实现
CDashboardView.prototype.enHtmlMap = {dsvSysTitleTxt: "System Status", dsvLocTimeTxt: "Local Time", dsvDurationTimeTxt:"Duration Time",dsvHwMacTxt:"Mac Address",dsvHwIPTxt:"IP Address",dsvIMEITxt: "IMEI",dsvFWVerTxt:"Firmware Ver.",
        dsvModTitleTxt:"Module Status",dsvModTblTxt:"Module",dsvConnTblTxt:"Connection", dsvSignalTxt:"Signal(dBm)", dsvOperaTxt:"Operation",dsvmtZConnectBtn:"Connect",dsvmtZDisconBtn:"Disconnect",dsvmt4GConnectBtn:"Connect",dsvmt4GDisconBtn:"Disconnect",
}
CDashboardView.prototype.cnHtmlMap = {dsvSysTitleTxt:"系统状态",dsvLocTimeTxt:"本机时间",dsvDurationTimeTxt:"本次开机持续时间",dsvHwMacTxt:"本机硬件地址",dsvHwIPTxt:"本机IP地址",dsvIMEITxt:"本机设备号",dsvFWVerTxt:"固件版本号",
        dsvModTitleTxt:"模块状态",dsvModTblTxt:"模块",dsvConnTblTxt:"连接状态", dsvSignalTxt:"信号强度(dBm)", dsvOperaTxt:"操作",dsvmtZConnectBtn:"连接",dsvmtZDisconBtn:"断开",dsvmt4GConnectBtn:"连接",dsvmt4GDisconBtn:"断开",
}
CDashboardView.prototype.enJsMap = {
    dsvOptSucc:"Command is successful！",
}
CDashboardView.prototype.cnJsMap = {
    dsvOptSucc:"操作成功！",
}
