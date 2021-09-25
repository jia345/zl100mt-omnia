from foris.state import current_state

class ProtoForwardCmd():
    def __init__(self):
        self.action = 'setProtoForward'
        self.default_data = {}

    def implement(self, data, session):
        print('set protocol forwarding:: {}'.format(data))

        pfList = data['dat']["ProtoForwardList"]
        for item in pfList:
            item['port'] = int(item['port'])
            item['dest_port'] = int(item['dest_port'])
        rc = current_state.backend.perform("proto_forward", "set_proto_forward", {"proto_forward_list": pfList})
        res = {"rc": rc, "errCode": "success", "dat": None}
        return res

    def get_proto_forward(self):
        rc = current_state.backend.perform("proto_forward", "get_settings", {})
        return rc["proto_forward_list"]

cmdProtoForward = ProtoForwardCmd()
