
/**
 * CVideoView View的主Class定义
 */
function CVideoView(){
    //-- 构造函数
    var _this = this;
    //--1.内部变量+内部函数
    var privateParameter;//private
    //--2.初始化对象和成员函数
    _this.node  =  document.getElementById( 'videoView' );
    _this.jqNode = $('#videoView'); // jQuery node object
    _this.player;
    _this.rtmpUrl = '';
    // 保存原始 : 自适应宽高-浏览器大小改变时重置大小, 退出时回复
    _this.originalOnSizeHandle = window.onresize;
    // 1.加载本view的html 2.注册控件回调函数 3.多语言实现
    _this.loadHtml();
}
CVideoView.prototype.node;
CVideoView.prototype.jqNode;
CVideoView.prototype.activeMyView = function(){
    tools.ActivateViewByNodeInContainer(gMainView, this.node);
    // resize
    window.onresize = this.adjustShowAreaSize;

    // gDebug = 0;
    if(gDebug){
        this.rtmpUrl =  "rtmp://127.0.0.1:1935/live/fqr";
        $("#vvRtmpUrlSelector").empty();
        let tr = "<option id='vvRtmpUrlSelector" + 0 +"'" + " value=" + this.rtmpUrl + ">" + this.rtmpUrl + "</option>";
        $("#vvRtmpUrlSelector").append(tr);
        this.rtmpUrl =  "rtmp://127.0.0.1:1935/live/fqr";
    }
    else{
        // 初始化rtmp链接
        $("#vvRtmpUrlSelector").empty();
        oStore.store.RTMP.channelList.forEach(function(value,index){
            let rtmpUrl = "rtmp://" + oStore.store.RTMP.ServerIP + ":1935/live/" + value.Code;
            let tr = "<option id='vvRtmpUrlSelector" + index +"'" + " value=" + rtmpUrl + ">" + rtmpUrl + "</option>";
            $("#vvRtmpUrlSelector").append(tr);
        });
        //获得RTMP流频道地址
        this.rtmpUrl = $('#vvRtmpUrlSelector').val();
    }
    
}
CVideoView.prototype.deactiveMyView = function(){
    tools.viewShow(this.node, false);
}
CVideoView.prototype.initCtrl = function(){
    var nodeParent = document.getElementById("vvVideoContent");
    var nodeChild =  document.getElementById("videoCtrl");
    if(null != nodeParent)
    {
        //如果有video ctrl则删除它重建
        if(null != nodeChild){
            if(this.player){
                console.log('video dispose');
                this.player.pause();
                this.player.dispose();
            }
            // nodeParent.removeChild(nodeChild);
        }
        let videoCtrStr = "<video id='videoCtrl' class='video-js' preload='auto' >" + 
        "<p class='vjs-no-js'>To view this video please enable flash and be sure web browser that supports HTML5 video." +
        "<a href='http://videojs.com/html5-video-support/' target='_blank'> </a> </p> </video>";
        $("#vvVideoContent").append(videoCtrStr);
    }
};
CVideoView.prototype.loadHtml = function(){
    // 1.加载本view的html 2.注册控件回调函数 3.多语言实现
    var enJsMap = {
        vvRtmpAddress:'Please, input the correct RTMP server URL',
    }
    var cnJsMap = {
        vvRtmpAddress:'请输入正确的流服务器地址！',
    }

    this.jqNode.load('views/CVideoView.html', ()=>{
        tools.language = $('#langSelector').children('option:selected').val();
        tools.htmlSwitchLang(this.enHtmlMap, this.cnHtmlMap);

        // 注册回调
        // 注册select ctrl监听
        $('#vvRtmpUrlSelector').change(()=>{
            this.rtmpUrl = $('#vvRtmpUrlSelector').val();
        });
        //
        $('#vvPlayBtn').click(()=>{
            // srcUrl = "rtmp://127.0.0.1:1935/live/fqr";
            if('' != this.rtmpUrl){
                // 初始化video ctrl
                this.initCtrl();
                //https://blog.csdn.net/q610376681/article/details/82947321
                var options = {
                    // height: '300',  
                    sources: [{  
                        type: "rtmp/flv",  
                        src: this.rtmpUrl //"rtmp://127.0.0.1:1935/live/fqr"  //this.rtmpUrl
                    }],  
                    techOrder: ['flash'],  
                    autoplay: true,  
                    controls: true,
                    flash: {
                        swf: 'js/video-js.5.20.1.swf'
                        // swf: 'js/VideoJS.swf'
                    }
            };
            // videojs.options.flash.swf = "js/video-js.5.20.1.swf";
            this.player = videojs('videoCtrl', options, ()=>{
                    console.log('video ctrl is ready.');
                    this.player.play();
                    //
                    this.player.on('playing', ()=>{
                        // console.log('loadedmetadata::'+aHeight+'X'+aWidth);
                        this.adjustShowAreaSize( );
                    });
                });
            }
            else{
                tools.msgBox(tools.jsSwitchLang(enJsMap, cnJsMap, 'vvRtmpAddress'));  //'请输入正确的流服务器地址！'
            }
            //
        });
        //注册退出本页面button
        $('#vvExitBtn').click(()=>{
            // $('#vvStopBtn').click();
            if(this.player){
                this.player.pause();
                this.player.dispose();
            }
            //回复原始的windows onsize 处理函数
            window.onresize = this.originalOnSizeHandle;
            //
            //解决切换语言后页面不会再次加载数据问题,强制所有mainView隐藏.
            tools.DeactivateAllViewInContainer(gMainView);
            // tools.ActivateViewByNodeInContainer(gMainView, gMainView.oDashboardView.node);
        });
    });
}
CVideoView.prototype.adjustShowAreaSize = function(){
    var aHeight = document.getElementById("videoCtrl").clientHeight;
    var aWidth = document.getElementById("videoCtrl").clientWidth;
    if(aHeight == 0 || aWidth == 0)
        return;
    //
    let vHeight = 0;
    let vWidth = 0;
    let ratioVideo = aWidth / aHeight;
    // if(ratio > 4)
    //     return;
    //
    var playbackviewNode = document.getElementById("videoView");
    // var pbvShowareaNode = document.getElementById("vvShowarea");
    let clientDomHeight = playbackviewNode.clientHeight - 100 - document.getElementById("vvVideoHeader").clientHeight - document.getElementById("vvVideoFooter").clientHeight;
    let clientDomWidth = document.getElementById("vvOperationView").clientWidth; // vvVideoContent
    let ratioFrame = clientDomWidth / clientDomHeight;
    // console.log('fRate:vRate('+ratioFrame+':'+ratioVideo+')<>frame('+clientDomWidth+'x'+clientDomHeight+')');

    //1. 设置为video随动框架尺寸，避免video尺寸不随窗口拖动变化
    vHeight = clientDomHeight; vWidth = clientDomWidth; 
    if(ratioFrame > ratioVideo ){ 
        //2. 此为: 窗口横向很扁情况(按照height为基准拉抻调整)
        vHeight = clientDomHeight;
    }else{ 
        //3. 此为: 窗口纵向很扁情况(按照width为基准拉抻调整)
        vWidth = clientDomWidth;
    }
    //4. 重新设置video尺寸
    document.getElementById("videoCtrl").style.height = vHeight +'px';
    document.getElementById("videoCtrl").style.width = vWidth +'px';
    // console.log('frame('+clientDomWidth+'X'+clientDomHeight+')=>(video::'+vWidth+'X'+vHeight+')');
}
// 多语言实现
CVideoView.prototype.enHtmlMap = {
    //vvVCtrlErr:"This browser can support [video], please try IE 9+,Firefox,Opera,Chrome or Safari.",
    vvPlayBtn:"Play", vvExitBtn:"Exit",//vvPauseBtn:"Pause", vvStopBtn:"Stop", 
};
CVideoView.prototype.cnHtmlMap = {
    //vvVCtrlErr:"浏览器不支持播放video,请试用以下浏览器IE 9+、Firefox、Opera、Chrome 和 Safari.",
    vvPlayBtn:"播放", vvExitBtn:"退出", //, vvPauseBtn:"暂停", vvStopBtn:"停止"
};

