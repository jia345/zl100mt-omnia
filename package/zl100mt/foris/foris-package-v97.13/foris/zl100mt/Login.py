
import base64
from foris.utils import check_password
from foris.middleware.bottle_csrf import update_csrf_token
from foris.state import current_state
import logging
logger = logging.getLogger(__name__)

class LoginCmd():
    def __init__(self):
        self.action = 'login'
        self.default_data = {'password':'admin'}

    def implement(self, data,session):
        res = {'rc': 0,'errCode': 'password is wrong!!'}
        print data['name']
        if data['name'] != 'admin':
            return res

        print data['pwd']
        if check_password(data['pwd']):
            session.recreate()
            session['user_authenticated'] = True

            update_csrf_token(save_session=False)
            session.save()
            res = {'rc': 0,'errCode': 'success','dat': None}

        return res

class GetUserInfoCmd():
    def __init__(self):
        self.action = 'getUserInfor'
        self.default_data = {}
    
    def implement(self, data,session=None):
        res = {'rc': 0,'errCode': 'success','dat': {'pwd':'password is set'}}
	return res

class SetPwdCmd():
    def __init__(self):
        self.action = 'setPWD'
        self.default_data = {}

    def implement(self, data, session=None):
        res = {'rc': 0,'errCode': 'success','dat': None}
        print data['dat']
	
        old_password = data['dat']['old'] if 'old' in data['dat'] else None
        new_password = data['dat']['new'] if 'new' in data['dat'] else ''
        
        if len(new_password) < 6:
            return {'rc': 1,'errCode': 'new passwrod length shoud be >= 6!','dat': None}

        if old_password == None :
            return {'rc': 1,'errCode': 'old passwrod is wrong!','dat': None}

        if check_password(old_password):
            encoded_password = base64.b64encode(new_password.encode('utf-8')).decode('utf-8')
            result = current_state.backend.perform(
                          'password', 'set', {'password': encoded_password, 'type': 'foris'})['result']
            logger.debug('SetPwdCmd %s',result)
            res = {'rc': 1,'errCode': 'Wrong new password','dat': None} if not result else res
        else:
            res = {'rc': 1,'errCode': 'Wrong old password','dat': None}
        return res

class ResetPwdCmd():
    def implement(self, data, session=None):
        encoded_password = base64.b64encode('admin'.encode('utf-8')).decode('utf-8')
        current_state.backend.perform('password', 'set', {'password': encoded_password, 'type': 'foris'})
        return {'rc': 0, 'errCode': 'success', 'dat': None}

cmdLogin = LoginCmd()
cmdGetUserInfo = GetUserInfoCmd()
cmdSetPwd = SetPwdCmd()
cmdResetPwd = ResetPwdCmd()
