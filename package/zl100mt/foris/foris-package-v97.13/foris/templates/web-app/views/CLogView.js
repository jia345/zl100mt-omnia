/**
 * Login View的主Class定义
 */
function CLoginView(){
    // 构造函数
    var _this = this;
    //初始化中使用原生DOM操作，避免引入库冲突
    document.getElementById("lgSubmitBtn").onclick = function(){
        //login view业务流程
        var str = {
            "command":"login",
            "name":$("#lgUserNameInput").val(),
            "pwd":$("#lgPWDInput").val()
        }
        parameters = JSON.stringify(str);
        $.ajax({
            type:"POST",
            url: getURL(), //"/cgi-bin/cgi.cgi",
            data:parameters,
            contentType: "application/json",
            dataType: 'json',
            success: function(res){
                /* 返回参数格式
                    {"rc":0/1,  //0 =>成功/1=>失败
                    "errCode": error msg txt //错误代码或消息文本
                    }
                */
                //var data = JSON.parse(res);
                var data = res;
                console.log(data);
                if(0 == data.rc)
                {
                    //1.hide loginview;
                    //2. active maincontent + active sidebar;
                    //3. active SystemView;
                    _this.deactiveMyView();
                    oLeftSideBar.activeMyView();
                    tools.viewShow(document.getElementById('mainContent'), true);
                }
            },
            error: function (errorThrown) { tools.msgBoxFailed(errorThrown);}
        });
    }
    //3.初始化对象和成员函数
    _this.node  =  document.getElementById( 'loginView' );

}
//因为当前模式下各个view的html是onload之后动态加载的，所以有加载不及时问题。解决方法就是在第一个页面login view之后来做必要的初始化工作。如：探测语言
CLoginView.prototype.activeMyView = function(){
    tools.viewShow(this.node, true);
}
CLoginView.prototype.deactiveMyView = function(){
    tools.viewShow(this.node, false);
}
CLoginView.prototype.loadHtml = function(){
    // 多语言实现
    var enHtmlMap = {lgSubmitBtn:"Login"};
    var cnHtmlMap = {lgSubmitBtn:"用户登陆"};
    tools.language = $('#langSelector').children('option:selected').val();
    tools.htmlSwitchLang(enHtmlMap, cnHtmlMap);
}
