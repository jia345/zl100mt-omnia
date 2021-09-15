<?php
// phpinfo();
/**
 * PHP 调试注意事项！
 * 1. 确保 main.js/index.js 中的调试标记已经打开并正确设置php脚本位置。
 * // set debug flag
 * var data = {'noDebug':'/cgi-bin/cgi.cgi',
 *            'mock':'./debug/mock',
 *            'php':'./debug/action/action.test.php'};
 * yutls.setGlobalDebugFlg(data, 'php');
 * 
*/
// header("Access-Control-Allow-Origin:*"); 
// header('Access-Control-Allow-Headers:x-requested-with,content-type'); 

//action.login.php
function fillResCodeTxt($rc, $errCode, $dat)
{
    $res['rc'] = $rc;
    $res['errCode'] = $errCode;
    $res['dat'] = $dat;
    return $res;
}
/*
* work on user requirement
*/

// $rawCommand = json_decode($HTTP_RAWmyPost_DATA);
// echo json_encode($rawCommand);
$myPost = '';
$command = 'NA';
// if(empty($_POST['command'])){}
$rawdata = file_get_contents("php://input");
$myPost = json_decode($rawdata,true);
if(true == empty($_POST['command'])){
    $command = $myPost['command'];
}else{
    $command = $_POST['command'];
}
//
if($command == 'login')
{
    $params = array(
        'username' => $myPost['name'],
        'password' => $myPost['pwd']);
    $res = fillResCodeTxt(0,'NULL',$params);
    //
    $res = json_encode($res);
    //print_r($res);
    echo $res;
}
else if($command == 'getSystemValue')
{
    // { 'rc': 0/1, 'errCode': 'xxx',
    //     'dat':[
    //         {'address':'xxx'},
    //         {'serial':'xxx'},
    //         {'version':'xxx'}
    //     ]
    //    }
    $params = array(    
        'address' => '10.10.0.1',
        'serial' => 'TEST.001.002.003.004',
        'version'=> '1.0.12.1');
    $res = fillResCodeTxt(0,'NULL',$params);
    //
    $res = json_encode($res);
    //print_r($res);
    echo $res;
}else if($command == 'resetToDefault')
{
    $res = fillResCodeTxt(0,'resetToDefault','');
    //
    $res = json_encode($res);
    //print_r($res);
    echo $res;
}else if($command == 'getHostStatusInfo')
{
    $hostIP = array('IP' => '10.1.1.13', 'subMask' => '255.255.0.0');
    $system = array('localDatetime' => '1531817800000', 'currDuration' => '17800000', 'hostIP'=>$hostIP,'hwMAC' => 'ED-DD-4D-45-01-01','hwIMEI' => 'ABC12345','swVersion' => '1.1.0');
    $LTEZ = array('type'=>'LTE-Z','connection'=>'on', 'signal'=>'1.2','wlanIP'=>'10.1.1.100', 'defaultGwIP'=>'10.2.1.1','mDnsIP'=>'10.2.1.1', 'sDnsIP'=>'10.2.1.2', 'MAC'=>'867223022323208','usim'=>'Ready','IMSI'=>'08509123', 'PLMN'=>'18509123','frq'=>'23.7', 'RSRQ'=>'3.2');
    $LTE4G = array('type'=>'LTE-4G','connection'=>'on', 'signal'=>'1.2','wlanIP'=>'10.1.1.109', 'defaultGwIP'=>'10.2.1.1','mDnsIP'=>'10.2.1.1', 'sDnsIP'=>'10.2.1.2', 'MAC'=>'867223022323209','usim'=>'Invalid', 'IMSI'=>'08509123', 'PLMN'=>'9854509123','frq'=>'73.32', 'RSRQ'=>'33.2');
    $GPS = array('longitude'=>'-216.42', 'latitude'=>'39.93','altitude'=>'135.2','speed'=>'23','heading'=>'23.2');
    $GNSS = array('GPS'=>$GPS,'connection'=>'on', 'signal'=>'1.01','satelliteNum'=>'9', 'totalMsg'=>'4531','succMsg'=>'4500', 'failMsg'=>'31','targetSim'=>'01897', 'localSim'=>'02654','beam1'=>'11','beam2'=>'12','beam3'=>'13','beam4'=>'14','beam5'=>'15','beam6'=>'16');
    $DHCP = array('dhcpStatus'=>'DHCp','startIP'=>'12.2.2.1', 'endIP'=>'12.2.2.100', 'leaseTerm'=>'120','subMask'=>'255.255.0.0', 'defaultGwIP'=>'12.2.2.1','DNS1'=>'12.2.2.2', 'DNS2'=>'12.2.2.1');

        $lan1 = array('port'=>'LAN1','MAC'=>'ED-DD-4D-45-5A-9E', 'IP'=>'128.0.1.22', 'subMask'=>'255.255.0.0', 'type'=>'ibm');
        $lan2 = array('port'=>'LAN3','MAC'=>'ED-DD-4D-45-5A-9D', 'IP'=>'128.0.1.2', 'subMask'=>'255.0.0.0', 'type'=>'fpr');
        $lan3 = array('port'=>'LAN2','MAC'=>'ED-DD-4D-45-5A-9F', 'IP'=>'128.0.1.12', 'subMask'=>'255.0.0.0', 'type'=>'pc');
        $accessList = array($lan1,$lan2,$lan3);
    $LAN = array('accessList'=>$accessList);
    $NTP = array('serverIP'=>'10.1.1.12');
    $params = array('system'=>$system,'LTEZ'=>$LTEZ,'LTE4G'=>$LTE4G,'GNSS'=>$GNSS,'DHCP'=>$DHCP,'LAN'=>$LAN,'NTP'=>$NTP);
    // $params = array('system'=>'1','LTEZ'=>'2','LTE4G'=>'3','GNSS'=>'4','DHCP'=>'5','LAN'=>'6','NTP'=>'7');
    $res = fillResCodeTxt(0,$command,$params);
    //
    $res = json_encode($res);
    // print_r($res);
    echo $res;
}else if($command == 'getLogLink')
{
    // { "rc": 0/1, "errCode": "xxx",
    //     "dat":[
    //       {"filePath":"xxx", "fileName":"xxx"},
    //       {...}
    //     ]
    //   }
    $dat1 = array('filePath' => '/web-app/debug/idxfile/', 'fileName' => 'TEST.001.zip');
    $dat2 = array('filePath' => '/web-app/debug/idxfile/', 'fileName' => 'TEST.002.zip');
    $dat3 = array('filePath' => '/web-app/debug/idxfile/', 'fileName' => 'TEST.003.zip');
    $dat4 = array('filePath' => '/web-app/debug/idxfile/', 'fileName' => 'TEST.004.zip');
    $params = array($dat1,$dat2,$dat3,$dat4);
    $res = fillResCodeTxt(0,'',$params);
    //
    $res = json_encode($res);
    echo $res;
}else if($command == 'uploadFile')
{
     // 因为type不是jason，所以php需要用$command = $_POST['command'];来获取正确的内容。
    // if ($_FILES["fileData"]["error"] > 0)
    // {
    //     echo "Error: " . $_FILES["fileData"]["error"] . "<br />";
    // }
    // else
    // {
    //     echo "Upload: " . $_FILES["fileData"]["name"] . "<br />";
    //     echo "Type: " . $_FILES["fileData"]["type"] . "<br />";
    //     echo "Size: " . ($_FILES["fileData"]["size"] / 1024) . " Kb<br />";
    //     echo "Stored in: " . $_FILES["fileData"]["tmp_name"];
    // }
    $fileName = $_FILES["fileData"]["name"];
    $params = array('fileName' => $fileName, 'version' => '1.0.2', 'MD5' => 'TEST00102');
    $res = fillResCodeTxt(0,'',$params);
    //
    $res = json_encode($res);
    echo $res;
}
return;

echo json_encode('POST failed from PHP!');

?>
