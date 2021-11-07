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
        <<<example:>>>
        config socat
	        option enable '1'
	        option SocatOptions '-u -T3 TCP6-LISTEN:8000,fork TCP4:192.168.1.20:80'
        '''
        for port in ports:
            if port['data']['enable'] == '1':
                #options = port['data']['SocatOptions']
                src_addr = port['data']['src']
                dst_addr = port['data']['dst']
                print("src %s dst %s" % (src_addr, dst_addr))
                m1 = re.match(r'^-T3\s(.+)-LISTEN:(\d+),.+,fork$', src_addr)
                m2 = re.match(r'^SYSTEM:"(.+)\| while true; do socat - \'TCP4:(.+):(\d+)\';.+"$', dst_addr)

                proto = 'udp'
                dest_proto = 'tcp'
                if m1:
                    port = int(m1.group(2))
                else:
                    port = 0
                if m2:
                    dest_ip = m2.group(2)
                    dest_port = int(m2.group(3))
                else:
                    dest_ip = '255.255.255.255'
                    dest_port = 0

                forward_list.append({
                    "proto": "udp",
                    "port": port,
                    "dest_proto": "tcp",
                    "dest_ip": dest_ip,
                    "dest_port": dest_port
                })
                '''
                if m:
                    forward_list.append({
                        "proto": "udp",
                        "port": int(m.group(2)),
                        #"dest_proto": "tcp",
                        #"dest_ip": m.group(4),
                        #"dest_port": int(m.group(5))
                    })
                '''

        res = {
            "proto_forward_list": forward_list
        }

        return res

    def set_proto_forward(self, data):
        print('protocol forward update_settings :')
        with UciBackend() as backend:
            cfg = backend.read("socat")
            try:
                items = get_sections_by_type(cfg, "socat", "socat")
                for i in range(len(items)):
                    section_name = '@socat[0]'
                    backend.del_section('socat', section_name)
            except:
                pass

            for item in data['proto_forward_list']:
                #options = '-u -T3 UDP4-LISTEN:%d,fork TCP4:%s:%d' % (item['port'], item['dest_ip'], item['dest_port'])
                system_cmd = "tee -a /root/udp_%d_tcp_%s_%d.socat | while true; do socat - \'TCP4:%s:%d\'; sleep 1; done" % (item['port'], item['dest_ip'], item['dest_port'], item['dest_ip'], item['dest_port'])
                #options = '-u -T3 UDP4-LISTEN:%d,reuseaddr,ignoreeof,fork SYSTEM:\"%s\"' % (item['port'], system_cmd)
                src_addr = '-T3 UDP4-LISTEN:%d,reuseaddr,ignoreeof,fork' % item['port']
                # system:"tee -a /root/udp_8181_tcp_49.51.96.94_3389.socat | socat - 'TCP4:49.51.96.94:3389'"
                dst_addr = 'SYSTEM:"%s"' % system_cmd
                backend.add_section('socat','socat')
                #backend.set_option('socat','@socat[-1]','SocatOptions', options)
                backend.set_option('socat','@socat[-1]','src', src_addr)
                backend.set_option('socat','@socat[-1]','dst', dst_addr)
                backend.set_option('socat', '@socat[-1]', 'enable', '1')

        with OpenwrtServices() as services:
            services.restart("socat")

        return True
