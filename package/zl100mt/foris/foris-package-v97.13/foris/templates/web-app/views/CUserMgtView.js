
/**
 * CUserMgtView View的主Class定义
 */
function CUserMgtView(){
    //-- 构造函数
    var _this = this;
    //--1.内部变量+内部函数
    var privateParameter;//private
    //--2.初始化对象和成员函数
    _this.node  =  document.getElementById( 'userMgtView' );
    _this.jqNode = $('#userMgtView'); // jQuery node object
    _this.store = {};
    // 1.加载本view的html 2.注册控件回调函数 3.多语言实现
    _this.loadHtml();
}
CUserMgtView.prototype.node;
CUserMgtView.prototype.jqNode;
CUserMgtView.prototype.activeMyView = function(){
    tools.ActivateViewByNodeInContainer(gMainView, this.node);
    this.render();
}
CUserMgtView.prototype.deactiveMyView = function(){
    tools.viewShow(this.node, false);
}
CUserMgtView.prototype.store;
CUserMgtView.prototype.render = function(){
    var str = {
        "command":"getUserInfor"
    }
    parameters = JSON.stringify(str);
    $.ajax({
        type:"POST",
        url: getURL(), //"/cgi-bin/cgi.cgi",
        data: {
                  "csrf_token": csrf_token,
	          "data_str": parameters
            },
	contentType: 'application/json',
        success: (res)=>{
            // 返回参数格式
            //     { "rc":0/1, "errCode": error msg tx,
            //     "dat":  {"pwd":"xxx"}
            //    }
            // var data = JSON.parse(res);
            var data = res;
            if(0 == data.rc){
                console.log('getUserInfor, succ.=>'+data.dat.pwd);
                this.store.user = 'admin';
                this.store.pwd = data.dat.pwd;
            }
            else{
                tools.msgBox(data.errCode);
            }
        },
        error: function (errorThrown) { alert("error");}
    });

}
CUserMgtView.prototype.loadHtml = function(){
    // 多语言实现
    var enHtmlMap = {umvTitle:"User Management",umvName:"User",umvPWD:"Current Password",umvNewPWD:"New Password",umvCmPWD:"Confirm Password", uvResetBtn:"Reset Default",uvSaveBtn:"Save",
        };
    var cnHtmlMap = {umvTitle:"用户管理",umvName:"用户名",umvPWD:"当前密码",umvNewPWD:"新密码",umvCmPWD:"确认新密码", uvResetBtn:"重置为缺省值",uvSaveBtn:"保存",
        };
    var enJsMap = {
        umvResetPwdSucc:'Success to reset password!',umvPwdCheckFail:'Failed to verify the password!',umvSetPwdSucc:'Success to set password!',
    }
    var cnJsMap = {
        umvResetPwdSucc:'重置密码成功!',umvPwdCheckFail:'密码校验未通过！', umvSetPwdSucc:'密码设置成功！',
    }
    // 1.加载本view的html 2.注册控件回调函数 3.多语言实现
    this.jqNode.load('views/CUserMgtView.html', ()=>{
        tools.language = $('#langSelector').children('option:selected').val();
        tools.htmlSwitchLang(enHtmlMap, cnHtmlMap);
        //*********** 注册回调
        // 重置为缺省值
        $('#uvResetBtn').click(()=>{
            var str = {
                "command":"resetDefaultPwd"
            }
            parameters = JSON.stringify(str);
            $.ajax({
                type:"POST",
                url: getURL(), //"/cgi-bin/cgi.cgi",
                data: {
                          "csrf_token": csrf_token,
	                  "data_str": parameters
                     },
		contentType: 'application/json',
                success: (res)=>{
                    // 返回参数格式
                    //    { "rc": 0/1, "errCode": "xxx"}  //0 =>成功/1=>失败
                    // var data = JSON.parse(res);
                    var data = (res);
                    if(0 == data.rc){
                        console.log('resetDefaultPwd, succ.=>'+data.dat);
                        this.store.pwd = data.dat.pwd;
                        $('#uvNewPWDInput').val('');
                        $('#uvConfirmNewPWDInput').val('');
                        tools.msgBox(tools.jsSwitchLang(enJsMap, cnJsMap, 'umvResetPwdSucc')); //'重置密码成功!'
                    }
                    else{
                        tools.msgBox(data.errCode);
                    }
                },
                error: function (errorThrown) { alert("error");}
            });
    
        });
        $('#uvSaveBtn').click(()=>{
            let oldPwd = $('#uvOldPWDInput').val();
            let newPwd = $('#uvNewPWDInput').val();
            let confirmPwd = $('#uvConfirmNewPWDInput').val();
            // if((oldPwd != this.store.pwd) || (newPwd != confirmPwd) || ('' == newPwd) || ('' == confirmPwd)){
            if((newPwd != confirmPwd) || ('' == newPwd) || ('' == confirmPwd)){
                tools.msgBox(tools.jsSwitchLang(enJsMap, cnJsMap, 'umvPwdCheckFail'));//'密码校验未通过！'
                return;
            }
            // setPWD
            var str = {
                "command":"setPWD",
                "dat": {
                    "old": oldPwd,
                    "new": newPwd
                }
            }
            parameters = JSON.stringify(str);
            $.ajax({
                type:"POST",
                url: getURL(), //"/cgi-bin/cgi.cgi",
                data: {
                          "csrf_token": csrf_token,
	                  "data_str": parameters
                     },
		contentType: 'application/json',
                success: function(res){
                    // 返回参数格式
                    //    { "rc": 0/1, "errCode": "xxx"}  //0 =>成功/1=>失败
                    // var data = JSON.parse(res);
                    var data = (res);
                    if(0 == data.rc){
                        console.log('setPWD, succ.=>'+data.errCode);
                        tools.msgBox(tools.jsSwitchLang(enJsMap, cnJsMap, 'umvSetPwdSucc'));//'密码设置成功！'
                    }
                    else{
                        tools.msgBox(data.errCode);
                    }
                },
                error: function (errorThrown) { alert("error");}
            });
        });
    });
}
