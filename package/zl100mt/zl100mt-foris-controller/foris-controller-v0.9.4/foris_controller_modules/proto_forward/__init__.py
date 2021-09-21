import logging

from foris_controller.module_base import BaseModule
from foris_controller.handler_base import wrap_required_functions
from foris_controller.utils import logger_wrapper

class ProtoForwardModule(BaseModule):
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)

    @logger_wrapper(logger)
    def action_get_settings(self, data):
        return self.handler.get_settings()

    @logger_wrapper(logger)
    def action_set_proto_forward(self, data):
        res = self.handler.set_proto_forward(data)
        return {"result": res}

@wrap_required_functions([
    'get_settings',
    'set_proto_forward'
])

class Handler(object):
    pass
