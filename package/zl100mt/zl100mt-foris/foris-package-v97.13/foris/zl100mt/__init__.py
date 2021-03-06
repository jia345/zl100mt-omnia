
from datetime import datetime
import base64
import logging
import time
import uuid
import os, hashlib
import json
import logging

logger = logging.getLogger(__name__)

from bottle import Bottle, request, template, response, jinja2_template
import bottle
from foris import BASE_DIR
from foris.utils import login_required, messages, is_safe_redirect
from foris.middleware.bottle_csrf import get_csrf_token

from foris.zl100mt.Login import cmdLogin, cmdGetUserInfo, cmdSetPwd, cmdResetPwd
from foris.zl100mt.Routing import cmdRoutingInfor, cmdGetRoutingInfo
from foris.zl100mt.System import cmdReboot, cmdGetLogLink, cmdSyncNtpTime, cmdSetLocalTime, cmdGetHostStatusInfo, cmdGetNetworkCfgInfo
from foris.zl100mt.System import cmdGetAllSysInfo, cmdSetHwId, cmdSetHostCfg
from foris.zl100mt.ipmacbind import cmdIpmacbind
from foris.zl100mt.testAjax import run_ajax_test
from foris.zl100mt.wan import cmdSetWanOnOff
from foris.zl100mt.gnss import cmdGnssSetRemoteCfg
from foris.zl100mt.Lan import cmdLanCfg
from foris.zl100mt.dhcp import cmdDhcpCfg
from foris.zl100mt.rtmp import cmdSetRtmpServerIp, cmdSetRtmpChannel
from foris.zl100mt.portmapping import setportmapping, channelmapping
from foris.zl100mt.proto_forward import cmdProtoForward
from foris.zl100mt.firewall import cmdSetFirewall, cmdSetIpFilter, cmdSetMacFilter

CONFIG_COMMANDS = {
    'login': cmdLogin,
    'getUserInfor': cmdGetUserInfo,
    'setPWD': cmdSetPwd,
    'resetDefaultPwd': cmdResetPwd,
    #'resetToDefault': cmdResetToFactoryDefault,
    'reBoot': cmdReboot,
    'getLogLink': cmdGetLogLink,
    'getSysInfor': cmdGetAllSysInfo,
    'getNetworkCfgInfor': cmdGetNetworkCfgInfo,
    'getHostStatusInfo': cmdGetHostStatusInfo,
    'setRouting': cmdRoutingInfor,
    'getRoutingInfor': cmdGetRoutingInfo,
    'operateModul': cmdSetWanOnOff,
    'setLanCfg': cmdLanCfg,
    'setDhcpCfg': cmdDhcpCfg,
    #'connectVPN': cmdDhcpCfg,
    'setHostCfg': cmdSetHostCfg,
    'syncDatetime': cmdSyncNtpTime,
    'setLocalDateTime': cmdSetLocalTime,
    'updateHwCode': cmdSetHwId,
    'setFirewall': cmdSetFirewall,
    'setIPFilterTable': cmdSetIpFilter,
    'setMacFilterTable': cmdSetMacFilter,
    'setPortMapping': setportmapping,
    'setProtoForward': cmdProtoForward,
    'setSlotChannelMapping': channelmapping,
    'setMacIPMapping': cmdIpmacbind,
    'setRtmpChannel': cmdSetRtmpChannel,
    'setRtmpServerIP': cmdSetRtmpServerIp,
    'setGnssTargetSim': cmdGnssSetRemoteCfg
}


@bottle.view("index.html")
def zl100mt_top_index():
    print("zl100mt top index")
    session = bottle.request.environ['foris.session']
    if session.is_anonymous:
        session.recreate()
        session["user_authenticated"] = True
        session.save()

def static_img(filename):
    return bottle.static_file(filename, os.path.join(BASE_DIR, "templates/web-app/img"))

def static_js(filename):
    return bottle.static_file(filename, os.path.join(BASE_DIR, "templates/web-app/js"))

def static_css(filename):
    return bottle.static_file(filename, os.path.join(BASE_DIR, "templates/web-app/css"))

def static_views(filename):
    return bottle.static_file(filename, os.path.join(BASE_DIR, "templates/web-app/views"))

def static_main(filename):
    return bottle.static_file(filename, os.path.join(BASE_DIR, "templates/web-app"))

def zl100mt_main():
    print("zl100mt main")
    session = bottle.request.environ['foris.session']
    # bottle.static_file("start.html",os.path.join(BASE_DIR, "templates/web-app/"))
    # print("GET: {0}".format(bottle.request.GET))
    # print("form: {0}".format(bottle.request.forms))
    # print("par: {0}".format(bottle.request.params))
    # print("JSON: {0}".format(bottle.request.json))

    logger.debug(bottle.request)
    logger.debug(bottle.request.POST.items())
    logger.debug(bottle.request.json)
    #str = bottle.request.POST.get('data_str')
    #data = json.loads(str)
    data = bottle.request.json
    if data is None:
        # form data 
        command = bottle.request.forms['command']
        if command == "uploadFile":
            file_name = bottle.request.forms['fileName']
            file_size = bottle.request.forms['fileSize']
            logger.debug("name {}".format(file_name))
            logger.debug("size {}".format(file_size))
            file_data = bottle.request.files['fileData']
            name, ext = os.path.splitext(file_name)
            if ext not in ('.tar.gz', '.zip'):
                return {
                    "rc": 1,
                    "errCode": "Only .tar.gz or .zip file extension will be allowed",
                    "dat": ""
                }    
            file_path = "/tmp/{file}".format(file=file_name)
            file_data.save(file_path, overwrite=True)
            return {
                "rc": 0,
                "errCode": "success",
                "dat": {
                    "fileName": file_name,
                    "version": "1.0",
                    "MD5": get_file_md5(file_path)
                }
            }
    else:
        command = data['command']
        if command in CONFIG_COMMANDS:
            handle = bottle.request.POST
            res = CONFIG_COMMANDS[command].implement(data,session)
            return res

    return { "rc": 0, "errCode": "success", "dat": "" } 

    def get_file_md5(file_path):
        md5 = None 
        if os.path.isfile(file_path):
            f = open(file_path,'rb')
            md5_obj = hashlib.md5()
            md5_obj.update(f.read())
            hash_code = md5_obj.hexdigest()
            f.close()
            md5 = str(hash_code).lower()
        return md5

def enable_cors():
    response.headers['Access-Control-Allow-Origin'] = '*'

def get_csrf():
    token = get_csrf_token()
    return {"rc": 0, "errCode": "sucess", "dat":token}

def ts_form():
    token = get_csrf_token()
    return '''
        <form action="/foris/config/ts_post" method="post">
	    <input name="csrf_token" type="hidden" value={0}>
            Username: <input name="username" type="text" />
            Password: <input name="password" type="password" />
            <input value="Login" type="submit" />
        </form>
    '''.format(token)

def ts_post():
    print(request.forms)
    return "<p>Your login information was correct.</p>"


def init_zl100mt(app):
    print("init_zl100mt")
    app.route("/zl_index",method=('POST','GET'),name="index", callback=zl100mt_top_index)
    app.route("/zl_main", method='POST', callback=zl100mt_main)
    app.route("/get_csrf", methond='GET', callback=get_csrf)

    app.route("/ts_post", method='POST', callback=ts_post)
    app.route("/ts_form", method='GET', callback=ts_form)
    app.route("/tsAjax", method=('POST','GET'), callback=run_ajax_test)

    app.route("/web-app/img/<filename:re:.*>", name='img', callback=static_img)
    app.route("/web-app/js/<filename:re:.*>", name='js', callback=static_js)
    app.route("/web-app/css/<filename:re:.*>", name='css', callback=static_css)
    app.route("/web-app/views/<filename:re:.*>", name='views', callback=static_views)
    app.route("/web-app/<filename:re:.*>", name='main', callback=static_main)
    app.add_hook("after_request",enable_cors)
    return app
