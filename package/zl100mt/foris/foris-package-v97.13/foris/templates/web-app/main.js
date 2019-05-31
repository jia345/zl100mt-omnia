// main.js
// include release version
tools.includeScript('version.js');
// include muti-language
// tools.includeScript('js/tools-lang.map.js');

// include views
tools.includeScript('views/CDashboardView.js');
tools.includeScript('views/CLogView.js');
tools.includeScript('views/CNetworkView.js');
tools.includeScript('views/CSysMaintView.js');
tools.includeScript('views/CSysStatusView.js');
tools.includeScript('views/CUserMgtView.js');
tools.includeScript('views/CVideoView.js');

//------------------------
var gDebug = 0;
var gMock = 0;
function getURL(){
    if(gDebug){
        if(gMock)
            return './debug/mock';
        else
            return './debug/action/action.test.php';
    } else {
        var cur_url = window.location.href.substring(0, location.href.indexOf("web-app"))
        return cur_url+'zl_main'
    }
}

// var csrf_token = ''
// function update_csrf(callback){
//     $.ajax({
//         type:"GET",
//         url: window.location.href.substring(0, location.href.indexOf("web-app"))+'get_csrf',
//         data:'',
//         success: function(res){
//             console.log(res)
//             csrf_token = res.dat
//             $('#csrf_token').val(csrf_token)
//             console.log($('#csrf_token').val())
//             callback()
//         }
//     })
// }

gAllView = {}; // 包括所有的view,用于全局刷新操作
gMainView = {}; // 包含所有的MainView对象，用于View hidden操作
//
// the main entry
var oLeftSideBar;
var oStore;
function Init()
{
    /* 浏览器会伪装自己为Chrome或FF,所以以下代码不可靠.
    let browser = tools.getBrowser(); 
    console.log('Browser=>'+browser);
    if(('Firefox' != browser)&&('Chrome' != browser)){
        // if(!confirm(tools.jsSwitchLang(enJsMap, cnJsMap,'smvRebootConfirm'))){ //'[重启]将重新启动设备, 确认是否继续!'
        if(!confirm('本设备的RTMP功能要求Firfox和Chrome浏览器,使用其他浏览器会导致该功能不可用。\n是否继续？')){ //'[重启]将重新启动设备, 确认是否继续!'
            // 点击了[取消]
    　　　　　window.opener = null; 
    　　　　　window.open(' ', '_self', ' '); 
    　　　　　window.close();
        }
    }
    */
    // 全局数据
    oStore = new CStore();
    //
    oMainFrm = new CMainFrm();
    oLoginView = new CLoginView();
    oLeftSideBar = new CLeftSideBar();
    // 构建MainView对象数组
    gMainView.oDashboardView = new CDashboardView();
    gMainView.oSysStatusView = new CSysStatusView();
    gMainView.oNetworkView = new CNetworkView();
    gMainView.oUserMgtView = new CUserMgtView();
    gMainView.oSysMaintView = new CSysMaintView();
    gMainView.oVideoView = new CVideoView();
    // save to glist
    // TODO: 需要更优雅的方式处理全局操作
    gAllView.oMainFrm = oMainFrm;
    gAllView.oLoginView = oLoginView;
    gAllView.oLeftSideBar = oLeftSideBar;
    gAllView.oDashboardView = gMainView.oDashboardView;
    gAllView.oSysStatusView = gMainView.oSysStatusView;
    gAllView.oNetworkView = gMainView.oNetworkView;
    gAllView.oUserMgtView = gMainView.oUserMgtView;
    gAllView.oSysMaintView = gMainView.oSysMaintView;
    gAllView.oVideoView = gMainView.oVideoView;
    //
    oLeftSideBar.deactiveMyView();
    oLoginView.activeMyView();
}

/**
 * main frame 主类定义
*/
function CMainFrm(){
    // 构造函数
    var _this = this;
    //1.内部变量+内部函数
    _this.node =  document.getElementById( 'mainFrm' );
    //2.注册控件回调函数
    _this.loadHtml();

    //3.初始化对象和成员函数
    let verString = '';
    if(gDebug){
        verString = 'Debug';
        if(gMock){
            verString = verString + ':Mock';
        }
        else{
            verString = verString + ':PHP';
        }
        $('#titleVer').css("color","red");
    }
    else{
        verString = 'release V' + releaseVer;
    }
    $('#titleVer').text(verString);

}
CMainFrm.prototype.init = function(){
    //
};
CMainFrm.prototype.loadHtml = function(){
    // 多语言实现
    var enHtmlMap = {footerTitle:"ZL100MT | All right reserved, 2018. ", titleRefreshBtn:"Refresh All",};
    var cnHtmlMap = {footerTitle:"ZL100MT 数据融合仪 | 版权所有XXX, 2018. ", titleRefreshBtn:"刷新数据",};
    tools.language = $('#langSelector').children('option:selected').val();
    tools.htmlSwitchLang(enHtmlMap, cnHtmlMap);
    //2.注册控件回调函数
    // 语言selector
    $('#langSelector').change(()=>{ 
        for(element in gAllView)
        {
            // console.log(element);
            gAllView[element].loadHtml();
            //解决切换语言后页面不会再次加载数据问题,强制所有mainView隐藏.
            tools.DeactivateAllViewInContainer(gMainView);
        }
    });
    // 全局刷新Btn
    $('#titleRefreshBtn').click(()=>{
        if(window.oStore){
            oStore.render();
        }
    });
}

/**
 * leftSideBar 的主Class定义
 */
function CLeftSideBar(){
    // 构造函数
    var _this = this;
    //1.内部变量+内部函数
    //3.初始化对象和成员函数
    _this.node =  document.getElementById( 'sideBarContent' );
    //2.注册控件回调函数
    _this.loadHtml();
}
CLeftSideBar.prototype.node;
CLeftSideBar.prototype.activeMyView = function(){
    tools.viewShow(this.node, true);
}
CLeftSideBar.prototype.deactiveMyView = function(){
    tools.viewShow(this.node, false);
}
CLeftSideBar.prototype.loadHtml = function(){
    // 多语言实现
    var enHtmlMap = {dashboardEntry: "Dashboard",sysStatusViewEntry: "System Status",networkViewEntry: "Network Config", txtSystemToolsItem: "System Tools",userMgtViewEntryTxt: "User Management",sysMaintViewEntryTxt:"System Maintain",videoViewEntryTxt: "Video view",};
    var cnHtmlMap = {dashboardEntry: "仪表盘",sysStatusViewEntry: "系统状态",networkViewEntry: "网络配置",txtSystemToolsItem: "系统工具",userMgtViewEntryTxt: "用户管理",sysMaintViewEntryTxt:"系统维护",videoViewEntryTxt: "视频视图",};
    tools.language = $('#langSelector').children('option:selected').val();
    tools.htmlSwitchLang(enHtmlMap, cnHtmlMap);
    //2.注册控件回调函数
    $('#dashboardEntry').click(function(){ gMainView.oDashboardView.activeMyView(); });
    $('#sysStatusViewEntry').click(function(){ gMainView.oSysStatusView.activeMyView(); });
    $('#networkViewEntry').click(function(){ gMainView.oNetworkView.activeMyView(); });
    $('#userMgtViewEntry').click(function(){ gMainView.oUserMgtView.activeMyView(); });
    $('#sysMaintViewEntry').click(function(){ gMainView.oSysMaintView.activeMyView(); });
    $('#videoViewEntry').click(function(){ gMainView.oVideoView.activeMyView(); });
}

/**
 * 全局的Store类定义
 */
function CStore(){
    // 构造函数
    var _this = this;
    //1.内部变量+内部函数
    //3.初始化对象和成员函数
    _this.store =  {
        "defaultRtmpSrvPortNum": 1935,
        "defaultRtmpSrvAppName": "live"
    };
    // get this global var
    _this.render();
    //update_csrf(_this.render);

}
CStore.prototype.store;
CStore.prototype.render = function(){
    let that = this.oStore;
    var str = {
        "command":"getSysInfor"
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
                // console.log('getSysInfor, succ.=>'+data.errCode);
                // this.store = data.dat;
                //data = '';
                this.system = data.dat.system;
                this.LTEZ = data.dat.LTEZ;
                this.LTE4G = data.dat.LTE4G;
                this.GNSS = data.dat.GNSS;
                this.DHCP = data.dat.DHCP;
                this.LAN = data.dat.LAN;
                this.RTMP = data.dat.RTMP;
                this.VPN = data.dat.VPN;
                this.FireWall = data.dat.FireWall;
                this.Mapping = data.dat.Mapping;
                this.NTP = data.dat.NTP;
            }
            else{
                tools.msgBox(data.errCode);
            }
            // console.log('_this.system.=>'+this.system.localDatetime);
        },
        error: function (errorThrown) { alert("error");}
    });
}
