
/**
 * CfgView的主Class定义
 */
function cCfgView(){
    // 构造函数
    var _this = this;
    //1.内部变量+内部函数
    //2.注册控件回调函数
    var privateParameter;//private
    $('#dvDownloadBtn').click(function(){
        /*
        { "command":"getFlyRecordSubPkgInfor",
            "dat":{
            "filePath":"xxx", "fileName":"xxx"}
        }
        */
        var str = 
        {
            "command": "getFlyRecordSubPkgInfor",
            "dat": 'selectedData'
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
                    if(0 == data.rc)
                    {
                        if(data.dat.length){
                            // 初始化下载视图
                            gMainView.oDownloadView.activeMyView(data.dat);
                        }else{
                            tools.msgBox('本航程文件为空，终止执行！');
                        }
                    }
                    else{
                        tools.msgBox(res);
                    }
                },
                error: function (errorThrown) { alert("error");}
        });

    });
    //3.初始化对象和成员函数
    _this.node  =  document.getElementById( 'cfgView' );
}
cCfgView.prototype.node;
cCfgView.prototype.activeMyView = function(){
    tools.ActivateViewByNodeInContainer(gMainView, this.node);
}
cCfgView.prototype.deactiveMyView = function(){
    tools.viewShow(this.node, false);
}

/**
 * Downloadview 主类定义
*/
function CDownloadView(){
    var _this = this;
    //1.内部变量+内部函数
    //2.注册控件回调函数
    //注册退出本页面button
    $('#dlvExitBtn').click(()=>{
        //清除表格内容
        $("#dlvFileListTbl  tr:not(:first)").empty("");
        gMainView.oCfgView.activeMyView();
    });
    //3.初始化对象和成员函数
    _this.node  =  document.getElementById( 'downloadview' );
    
}
CDownloadView.prototype.node;
CDownloadView.prototype.activeMyView = function(data){
    //construct the data table by the res data from server
    //1.清除表格内容
    $("#dlvFileListTbl  tr:not(:first)").empty("");
    //2.构建表格内容
    /** 返回数据格式
        "dat":[
            {"filePath":"xxx", "fileName":"xxx", "fileSize":"xxx"},//文件size单位为KB
            {...}]
    ** html 格式
        <td><a id="dlvFileNameTxt">xxx</a></td>
        <td><a id="dlvFileSizeTxt">xxx</a></td>
        <td><a id="dlvUrlTxt">xxx</a></td>
    ***/
    data.forEach(function(value,index){
        var flightRecordName = value.fileName.replace(/.zip/,'') ;
        var targetFileName = value.fileName.replace(/.zip/,'.fqr') ;
        if(index == 0){
            $('#dlvTitleTxt').text('航程名称:'+ flightRecordName);
        }
        var tr = "<tr>"+
                " <td><a id=\"dlvFileNameTxt\">" + flightRecordName + "</a></td>" +
                " <td><a id=\"dlvFileSizeTxt\">" + value.fileSize + " MB</a></td>" +
                " <td><a id=\"dlvUrlTxt\" href=\"" + value.filePath + "/" + value.fileName + "\"" + "download=" + targetFileName +  ">" + "LinkTo:"+flightRecordName + "</a></td> </tr>";
        $("#dlvFileListTbl").append(tr);
    })

    // restore the win_onsize handle to orig one
    // window.onresize = gWinOnSizeHandle;
    // show the view
    tools.ActivateViewByNodeInContainer(gMainView, this.node);
}
