from foris.state import current_state

class SetProtoForwardCmd():
    def __init__(self):
        self.action = 'setProtoForward'
        self.default_data = {}

    def implement(self, data, session):
        print('set protocol forwarding:: {}'.format(data))

        pfList = data['dat']["ProtoForwardList"]
        rc = current_state.backend.perform("proto_forward", "update_settings", {"action": "set_proto_forward", "proto_forward_list": pfList})
        res = {"rc": rc, "errCode": "success", "dat": None}
        return res

    def get_proto_forward(self):
        rc = current_state.backend.perform("proto_forward", "get_settings", {})
        return rc["proto_forward_list"]

cmdSetProtoForward = SetProtoForwardCmd()
