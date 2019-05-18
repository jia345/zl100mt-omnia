
import bottle
from foris.state import current_state

class SysReboot():
    def __init__(self):
        self.action = 'reBoot'
        self.default_data = {}

    def implement(self, data,session=None):
        ret = current_state.backend.perform("maintain", "reboot", {})
        res = {"rc": 0, "errCode": "success", "dat": None}
        if bottle.request.is_xhr:
            # return a list of ip addresses where to connect after reboot is performed
            res = bottle.response.copy(cls=bottle.HTTPResponse)
            res.content_type = 'application/json'
            res.body = json.dumps(ret)
            res.status = 200
            raise res
        else:
            bottle.redirect(reverse("/"))
        return res



class NtpSyncDatetime():
    def __init__(self):
        self.action = 'syncDatetime'
        self.default_data = {}

    def implement(self, data,session=None):
        cfg = {
            "city": "Shanghai",
            "region": "Asia",
            "timezone": "CST-8",
            "time_settings": {
                "how_to_set_time": "ntp",
            }
        }
        rc = current_state.backend.perform("time", "update_settings", cfg)
        print rc
        rc = current_state.backend.perform("time", "ntpdate_trigger", {})
        print rc
        getdata = current_state.backend.perform("time", "get_settings", {})
        print getdata
        res = {
            "rc": 0,
            "errCode": "success",
            "dat": {"localDatetime": getdata["time_settings"]["time"]}
        }

        return res

class GetLogLinkCmd():
    def implement(self, data, session=None):
        res = current_state.backend.perform("maintain", "get_log_links", msg)
        return res

cmdReboot = SysReboot()
cmdTime = NtpSyncDatetime()
cmdGetLogLink = GetLogLinkCmd()
