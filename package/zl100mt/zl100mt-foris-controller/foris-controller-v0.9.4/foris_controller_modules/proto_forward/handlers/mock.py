import logging

from foris_controller.handler_base import BaseMockHandler
from foris_controller.utils import logger_wrapper

from .. import Handler

logger = logging.getLogger(__name__)

class MockProtoForwardHandler(Handler, BaseMockHandler):
    port_forward_list = []

    @logger_wrapper(logger)
    def get_settings(self):
        result = {
            "port_forward_list": MockProtoForwardHandler.port_forward_list,
        }
        return result

    @logger_wrapper(logger)
    def set_proto_forward(self, data):
        MockProtoForwardHandler.port_forward_list = data.port_forward_list
        return True
