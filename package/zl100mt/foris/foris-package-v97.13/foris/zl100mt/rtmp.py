from foris.state import current_state

class SetRtmpChannelCmd():
    def implement(self, data, session):
        data = data['dat']['RTMP']['channelList']
        channel_list = []
        for e in data:
            channel_list.append({
                'name': e['Name'],
                'code': e['Code']
            })
        rc  = current_state.backend.perform('rtmp', 'set_channel_list', {'channel_list': channel_list})
        res = {'rc': 0, 'errCode': 'success', 'dat': None} if rc['result'] else {'rc': 1, 'errCode': 'fail', 'dat': 'Wrong parameters'}
        return res

class SetRtmpServerIpCmd():
    def implement(self, data, session):
        server_ip = data['dat']['RTMP']['ServerIP']
        rc = current_state.backend.perform('rtmp', 'set_server_ip', {'server_ip': server_ip})
        res = {'rc': 0, 'errCode': 'success', 'dat': None} if rc['result'] else {'rc': 1, 'errCode': 'fail', 'dat': 'Wrong parameters'}
        return res

class GetRtmpInfoCmd():
    def implement(self, session):
        data = current_state.backend.perform('rtmp', 'get_info', {})
        channel_list = []
        for e in data['channel_list']:
            channel_list.append({
                'Name': e['name'],
                'Code': e['code']
            })
        rtmp = {
            'ServerIP': data['server_ip'],
            'channelList': channel_list
        }
        return rtmp

cmdSetRtmpServerIp = SetRtmpServerIpCmd()
cmdSetRtmpChannel = SetRtmpChannelCmd()
cmdGetRtmpInfo = GetRtmpInfoCmd()
