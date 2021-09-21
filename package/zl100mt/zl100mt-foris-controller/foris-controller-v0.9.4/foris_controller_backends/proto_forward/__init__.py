import logging, re

from foris_controller_backends.uci import (
    UciBackend, get_option_anonymous, get_option_named, parse_bool, store_bool, get_sections_by_type
)
from foris_controller_backends.services import OpenwrtServices
from foris_controller.exceptions import UciRecordNotFound

logger = logging.getLogger(__name__)

class ProtoForwardUciCommands(object):

    def get_settings(self):

        with UciBackend() as backend:
            proto_forward_data = backend.read("socat")
            try:
                ports = get_sections_by_type(proto_forward_data, "socat", "socat")
            except:
                ports = []

        forward_list = []
        '''
        config socat
	        option enable '1'
	        option SocatOptions '-d -d TCP6-LISTEN:8000,fork TCP4:192.168.1.20:80'
        '''
        for port in ports:
            # TODO
            options = port['data']['SocatOptions']
            m = re.match(r'^-d -d\s(.+)-LISTEN:(\d+),fork (.+):(.+):(\d+)$', options)

            if m:
                forward_list.append({
                    "proto": "udp",
                    "port": m.group(1),
                    "dest_proto": "tcp",
                    "dest_ip": m.group(4),
                    "dest_port": m.group(5)
                })

        res = {
            "proto_forward_list": forward_list
        }

        return res

    def update_settings(self, data):
        print('protocol forward update_settings :')
        with UciBackend() as backend:
            data = backend.read("socat")
            try:
                items = get_sections_by_type(data, "socat", "socat")
                for i in range(len(items)):
                    section_name = '@socat[0]'
                    backend.del_section('socat', section_name)
            except:
                pass

            for item in data['proto_forward_list']:
                options = '-d -d UDP4-LISTEN:%d,fork TCP4:%s:%d' % (item['port'], item['dest_ip'], item['dest_port'])
                backend.add_section('socat','socat')
                backend.set_option('socat','@host[-1]','SocatOptions', options)
                backend.set_option('socat', '@host[-1]', 'enable', '1')

        return True
