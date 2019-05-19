import logging, os, hashlib

from foris_controller_backends.uci import (
    UciBackend, get_option_anonymous, get_option_named, parse_bool, store_bool, get_sections_by_type, get_section, get_section_idx
)
from foris_controller_backends.services import OpenwrtServices
from foris_controller.exceptions import UciRecordNotFound

logger = logging.getLogger(__name__)

class RtmpUciCommands(object):

    def get_info(self):
        with UciBackend() as backend:
            cfg = backend.read("rtmp")
            server = get_section_idx(cfg, "rtmp", "server", 0)
            try:
                channels = get_sections_by_type(cfg, "rtmp", "channel")
            except:
                channels = []

        server_ip = server['data']['ip']

        channel_list = []
        for e in channels:
            channel_list.append({
                'name': e['data']['name'],
                'code': e['data']['code']
            })

        return {
            'server_ip': server_ip,
            'channel_list': channel_list
        }

    def set_channel_list(self, data):
        with UciBackend() as backend:
            cfg = backend.read("rtmp")
            try:
                channels = get_sections_by_type(cfg, 'rtmp', 'channel')
            except:
                channels = []

            for e in channels:
                backend.del_section('rtmp', e['name'])

            for e in data['channel_list']:
                content = '%s_%s' % (e['name'], e['code'])
                channel_name = 'channel_%s' % hashlib.md5(content).hexdigest()
                backend.add_section('rtmp', 'channel', channel_name)
                backend.set_option('rtmp', channel_name, 'name', e['name'])
                backend.set_option('rtmp', channel_name, 'code', e['code'])
        return True

    def set_server_ip(self, data):
        with UciBackend() as backend:
            cfg    = backend.read("rtmp")
            server = get_section_idx(cfg, 'rtmp', 'server', 0)
            backend.set_option('rtmp', server['name'], 'ip', data['server_ip'])
            return True

