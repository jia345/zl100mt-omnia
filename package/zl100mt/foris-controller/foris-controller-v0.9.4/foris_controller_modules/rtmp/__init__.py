import logging

from foris_controller.module_base import BaseModule
from foris_controller.handler_base import wrap_required_functions

class RtmpModule(BaseModule):
    logger = logging.getLogger(__name__)

    def action_get_info(self, data):
        return self.handler.get_info()

    def action_set_server_ip(self, data):
        res = self.handler.set_server_ip(data)
        return {"result": res}

    def action_set_channel_list(self, data):
        res = self.handler.set_channel_list(data)
        return {"result": res}

@wrap_required_functions([
    'get_info',
    'set_server_ip',
    'set_channel_list'
])
class Handler(object):
    pass
