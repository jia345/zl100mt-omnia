
/**
 * CSysMaintView View的主Class定义
 */
function CSysMaintView(){
    //-- 构造函数
    var _this = this;
    //--1.内部变量+内部函数
    var privateParameter;//private
    //--2.初始化对象和成员函数
    _this.node  =  document.getElementById( 'sysMaintView' );
    _this.jqNode = $('#sysMaintView'); // jQuery node object
    _this.store = {};
    // 1.加载本view的html 2.注册控件回调函数 3.多语言实现
    _this.loadHtml();
}
CSysMaintView.prototype.store;
CSysMaintView.prototype.node;
CSysMaintView.prototype.jqNode;
CSysMaintView.prototype.activeMyView = function(){
    tools.ActivateViewByNodeInContainer(gMainView, this.node);
    //
    this.render();
}
CSysMaintView.prototype.deactiveMyView = function(){
    tools.viewShow(this.node, false);
}
CSysMaintView.prototype.render = function(){
    $('#smvTimeVal').text(tools.getDateByYMD(oStore.system.localDatetime));
    $('#smvHwMacVal').val(oStore.system.hwMAC);
    $('#smvHWIMEIVal').val(oStore.system.hwIMEI);
    $('#smvFWVerVal').text(oStore.system.swVersion);
    if('' == oStore.NTP.serverIP){
        $('#smvNTPServerIP').val('210.72.145.44');
    }
    else{
        $('#smvNTPServerIP').val(oStore.NTP.serverIP);
    }
}
CSysMaintView.prototype.loadHtml = function(){
    var enJsMap = this.enJsMap;
    var cnJsMap = this.cnJsMap;
    // 多语言实现
    var enHtmlMap = {
            smvNTPTitle:"NTP Syn.",smvTime:"Correct time",smvRefreshBtn:"Rrefresh",
            smvTitleGJWH:'Firmware',smvHwMac:'Mac Address',smvHWIMEI:"Hardware Serial",smvUpdateHwCodeBtn:"Update HW Code",smvFWVer:"Firmware Ver.",smvUpFW:"Upgrade FW",smvNewFW:"New FW",
            smvSetDefaultBtn:"Set default",smvBrowseFileBtn:"Browse",smvUploadFileBtn:"Upload FW",smvRebootBtn:"Reset",
            smvTitleLog:"Log",smvLogTH:"Log Link",smvLog:"Log List",smvLogStartDate:"Start Datetime",smvLogEndDate:"End Datetime",smvLogOperation:"Operation",smvRefreshLogBtn:"Rrefresh",
        };
    var cnHtmlMap = {
            smvNTPTitle:"NTP网络对时",smvTime:"网络对时",smvRefreshBtn:"刷新",
            smvTitleGJWH:'固件维护',smvHwMac:'本机硬件地址',smvHWIMEI:"本机设备号",smvUpdateHwCodeBtn:"刷新设备编码",smvFWVer:"固件版本号",smvUpFW:"升级固件",smvNewFW:"新固件",
            smvSetDefaultBtn:"恢复出厂设置",smvBrowseFileBtn:"选取文件",smvUploadFileBtn:"上传新固件",smvRebootBtn:"重启升级",
            smvTitleLog:"日志维护",smvLogTH:"Log记录链接",smvLog:"Log记录",smvLogStartDate:"开始时间",smvLogEndDate:"结束时间",smvLogOperation:"操作",smvRefreshLogBtn:"刷新日志",
        };
    // 1.加载本view的html 2.注册控件回调函数 3.多语言实现
    this.jqNode.load('views/CSysMaintView.html', ()=>{
        tools.language = $('#langSelector').children('option:selected').val();
        tools.htmlSwitchLang(enHtmlMap, cnHtmlMap);

        //------------ 注册回调-----------
        /**  NTP同步时间
         *     { "command":"syncDatetime",
         *     "dat":{
         *          "NTP": {"serverIP": "xx" }
         */
        $('#smvRefreshBtn').click(()=>{
            var ip = $('#smvNTPServerIP').val();
            if(false == tools.chkIpAddress(ip)){
                tools.msgBox(tools.jsSwitchLang(enJsMap, cnJsMap, 'invalidMacVal')); //发现无效的IP地址 
                return;
            }
            //
            var selectedData = { "serverIP": ip };
            var str = {
                "command":"syncDatetime",
                "dat": {
                    "NTP": selectedData
                }
            }
            parameters = JSON.stringify(str);
            $.ajax({
                type:"POST",
                url: getURL(), //"/cgi-bin/cgi.cgi",
                data:parameters,
                contentType: 'application/json',
                dataType: 'json',
                success: (res)=>{
                    // 返回参数格式
                    // "dat":  {"localDatetime":"xxx"} // ms数
                    //var data = JSON.parse(res);
                    var data = res;
                    console.log(data);
                    if(0 == data.rc){
                        oStore.system.localDatetime = data.dat.localDatetime;
                        oStore.NTP = selectedData;
                        $('#smvTimeVal').text(tools.getDateByYMD(oStore.system.localDatetime));
                        gAllView.oDashboardView.render();
                        tools.msgBox(tools.jsSwitchLang(enJsMap, cnJsMap, 'dsvOptSucc') + " code: " + data.errCode);
                    }
                    else{
                        tools.msgBox(data.errCode);
                    }
                },
                error: function (errorThrown) { tools.msgBoxFailed(errorThrown);}
            });
        });
        /** 刷新设备编码
         *     {"command":"updateHwCode",
         *     "dat": {
         *         "system":{ "hwMAC": "xxx", "hwIMEI": "xxx"}
         *       }
         */
        $('#smvUpdateHwCodeBtn').click(()=>{
            var mac = $('#smvHwMacVal').val();
            var imei = $('#smvHWIMEIVal').val();
            // check parameters
            if(false == tools.chkMacAddress(mac)){
                tools.msgBox(tools.jsSwitchLang(enJsMap, cnJsMap, 'invalidMacVal')); //发现无效的MAC地址 
                return;
            }
            if(false == tools.chkImeiAddress(imei)){
                tools.msgBox(tools.jsSwitchLang(enJsMap, cnJsMap, 'invalidImeiVal')); //发现无效的IMEI地址 
                return;
            }
            // POST
            var selectedData = { "hwMAC": mac, "hwIMEI": imei};
            var str = {
                "command":"updateHwCode",
                "dat": {
                    "system": selectedData
                }
            }
            parameters = JSON.stringify(str);
            $.ajax({
                type:"POST",
                url: getURL(), //"/cgi-bin/cgi.cgi",
                data:parameters,
                contentType: 'application/json',
                dataType: 'json',
                success: (res)=>{
                    // 返回参数格式
                    //var data = JSON.parse(res);
                    var data = res;
                    console.log(data);
                    if(0 == data.rc){
                        oStore.system.hwMAC = selectedData.hwMAC;
                        oStore.system.hwIMEI = selectedData.hwIMEI;
                        // gAllView.oDashboardView.render();
                        tools.msgBox(tools.jsSwitchLang(enJsMap, cnJsMap, 'dsvOptSucc') + " code: " + data.errCode);
                    }
                    else{
                        tools.msgBox(data.errCode);
                    }
                },
                error: function (errorThrown) { tools.msgBoxFailed(errorThrown);}
            });
        });
        /**
         * 恢复出厂设置
         *  */
        $('#smvSetDefaultBtn').click(function(){
            if(!confirm(tools.jsSwitchLang(enJsMap, cnJsMap,'smvSetDefaultCfg'))){ //'[恢复出厂设置]将擦除所有个人信息, 确认是否继续!'
                // 点击了[取消]
                return;
            }
            //
            let str = 
            {
                "command":"resetToDefault"
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
                console.log(data);
                if(0 == data.rc){
                        tools.msgBox(tools.jsSwitchLang(enJsMap, cnJsMap, 'dsvOptSucc') + " code: " + data.errCode);
                    }
                    else{
                        tools.msgBox(res);
                    }
                }
            });
        });
        /**
         * 选取文件
         *  */
        $('#smvBrowseFileBtn').click(function(){
            // trigger隐藏的input [file] ctrl,显示openfile对话框
            $("#smvUpgradeFileObj").trigger("click");
            // 获取选取的文件信息
            $("#smvUpgradeFileObj").change(function(){
                $("#smvUpgradeFilePath").val($("#smvUpgradeFileObj").get(0).files[0].name);
            });
        });
        // TODO: mock调试未通过！
        //上传新固件 TODO：如果不能立即返回，要考虑类似下载链接的轮询处理手段
        //使用 ajax + H5 FormData 类实现
        $('#smvUploadFileBtn').click(function(){
            // check fileObj is ready
            if(('' == $("#smvUpgradeFilePath").val())){
                tools.msgBox(tools.jsSwitchLang(enJsMap, cnJsMap, 'smvUpgradeFileNull'));
                return false;
            }
            //
            var fd = new FormData();
            fd.append("command", "uploadFile");
            var fileDat = {
                "fileName": $("#smvUpgradeFileObj").get(0).files[0].name, 
                "fileSize": $("#smvUpgradeFileObj").get(0).files[0].size,
                "fileData": $("#smvUpgradeFileObj").get(0).files[0]
            }
            fd.append("dat", fileDat);
            // let str = 
            // {
            //     "command":"uploadFile",
            //     "dat": { "fileName": "xx", "fileSize":"xx", //size: byte
            //              "fileData": "bin of FormData" }
            // }
            // let parameters = JSON.stringify(str);
            $.ajax({
                url: getURL(),
                type: "POST",
                processData: false,
                contentType: false,
                data: fd,
                success: function(res){
                    /* 返回参数格式
                        "dat":{"fileName":"xxx",
                            "version":"xxx",
                            "MD5":"xxx"
                            }
                    */
                    //var data = JSON.parse(res);
                    var data = res;
                    console.log(data);
                    if(0 == data.rc)
                    {
                        if(data.dat.fileName == $("#smvUpgradeFilePath").val())
                        {
                            console.log('uploadFile, succ.=>'+data.dat.version);
                            this.store.user = data.dat.version;
                            this.store.pwd = data.dat.MD5;
                            $("#smvNewFWVer").text(data.dat.version);
                            $("#smvNewFWMd5").text(data.dat.MD5);
                            tools.msgBox(tools.jsSwitchLang(enJsMap, cnJsMap, 'smvUpgradeSucc'));//("升级文件已成功上传服务器, 请检查Ver/MD5是否不一致.<br />准备就绪后请点击[重启]完成升级!");
                        }
                        else
                            tools.msgBox(tools.jsSwitchLang(enJsMap, cnJsMap, 'smvUpgradeFileErr'));
                        }
                    else{
                        tools.msgBox(data.errCode);
                    }
                }
            });
        });
        /**
         * 重启升级
         *  */
        $('#smvRebootBtn').click(function(){
            if(!confirm(tools.jsSwitchLang(enJsMap, cnJsMap,'smvRebootConfirm'))){ //'[重启]将重新启动设备, 确认是否继续!'
                // 点击了[取消]
                return;
            }
            //
            let str = 
            {
                "command":"reBoot"
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
                    console.log(data);
                    if(0 == data.rc){
                        tools.msgBox(tools.jsSwitchLang(enJsMap, cnJsMap, 'dsvOptSucc') + " code: " + data.errCode);
                    }
                    else{
                        tools.msgBox(res);
                    }
                }
            });
        });
        /**
         * 刷新log记录
         *  */
        $('#smvRefreshLogBtn').click(function(){
            // get data from server
            var str = 
            {
                "command": "getLogLink",
                "dat": {
                    "startDatetime": tools.getTimestamp($('#smvStartDateInput').val()),
                    "endDatetime": tools.getTimestamp($('#smvEndDateInput').val())
                }
            }
            parameters = JSON.stringify(str);
            $.ajax(
            { url: getURL(), // "/cgi-bin/cgi.cgi",
                type: "POST", 
                data: parameters,
                contentType: 'application/json',
                dataType: 'json',
                success: function (res) {
                        //var data = JSON.parse(res);
                        var data = res;
                        console.log(data);
                        if(0 == data.rc)
                        {
                            refreshTable(data.dat);
                        }
                        else{
                            tools.msgBox(res);
                        }
                },
                error: function (errorThrown) { tools.msgBoxFailed(errorThrown);}
            });
            
            function refreshTable(data){
                //construct the data table by the res data from server
                //1.清除表格内容
                $("#smvLogFileListTbl  tr:not(:first)").empty("");
                //2.构建表格内容
                /** 返回数据格式
                    "dat":[
                        {"filePath":"xxx", "fileName":"xxx"},
                        {...}]
                ** html 格式
                    <tr> <td colspan="3"><a id="smvLog">Log记录Link</a></td> </tr>
                ***/
                data.forEach(function(value,index){
                    // var logFileName = value.fileName.replace(/.zip/,'') ;
                    // var DownloadFileName = value.fileName.replace(/.zip/,'.fqr') ;
                    let logFileName = value.fileName;
                    let tr = "<tr>"+
                            " <td colspan=\""+3+"\"><a href=\"" + value.filePath + value.fileName + "\">" + "LinkTo: "+ logFileName + "</a></td> </tr>";
                    $("#smvLogFileListTbl").append(tr);
                })

            }
        });
    });
}
CSysMaintView.prototype.enJsMap = {
    dsvOptSucc:"Command is successful！", smvUpgradeFileErr:"The upgrade file is incrroect!",  smvUpgradeFileNull:'Please, pick up a upgrade file!', smvUpgradeSucc:'Success to upgrade the FW file, please check the Ver/MD5 before reboot the device!',
    smvRebootConfirm:'[reboot] will reboot the device, please confirm this operation!', smvSetDefaultCfg:'[SetDefault] will delete all personal date from the device, please confirm this operation!',
    invalidIPVal:"!! Invalid ip address is found !!", invalidMacVal:"'!! Invalid MAC address is found !!",invalidImeiVal:"!! Invalid IMEI address is found !!",
}
CSysMaintView.prototype.cnJsMap = {
    dsvOptSucc:"操作成功！", smvUpgradeFileErr:"服务器收到的升级文件名不一致，请检查！", smvUpgradeFileNull:'上载文件未正确选取!', smvUpgradeSucc:"升级文件已成功上传服务器, 请检查Ver/MD5是否不一致. \n准备就绪后请点击[重启]完成升级!",
    smvRebootConfirm:'[重启]将导致当前业务中断, 确认是否继续!', smvSetDefaultCfg:'[恢复出厂设置]将擦除所有个人信息, 确认是否继续!',
    invalidIPVal:"!! 无效的IP地址 !!", invalidMacVal:"!! 无效的MAC地址  !!",invalidImeiVal:"!! 无效的IMEI地址  !!",
}
