/**
 * system configuration for this app
 * some predifinations to control the app
 * 1. set debug flag
 * --------------
 * YangYutong
 * 2019-6-3
 ***********/ 
var cur_url = window.location.href.substring(0, location.href.indexOf("web-app")) + 'zl_main'; //for real url
console.log('Current webapp url=>' + cur_url);

var appCfg = {
    //1. set debug flag -------
    // @param 'type' => define the enable type of the server link for this app
    // @param 'link' => define the multi lines of server link, in case of multi debug/running server data
    debugCfg:{
        //type: 'mock',   //!!! IMPORTANT, 根据您的需求设置该值. e.g.实际量产时填写 'real'
        type: 'real',   //!!! IMPORTANT, 根据您的需求设置该值. e.g.实际量产时填写 'real'
        link: {         //!!! 请将以下链接填写为自己的真实链接 !!!
            'real': cur_url,
            // 'mock':'./debug/mock',
            // 'php':'./debug/action/action.test.php'}
        }
    },
    //
    //2. timerout value, which to control the 'pull data from device' button
    max_timeout_s: 10, //MAC_COUNTER_S
};
