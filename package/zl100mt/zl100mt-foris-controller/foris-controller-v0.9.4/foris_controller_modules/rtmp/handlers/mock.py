import logging

from foris_controller.handler_base import BaseMockHandler
from foris_controller.utils import logger_wrapper

from .. import Handler

logger = logging.getLogger(__name__)

class MockRtmpHandler(Handler, BaseMockHandler):
    @logger_wrapper(logger)
    def set_channel_list(self, data):
        return True

    @logger_wrapper(logger)
    def get_info(self):
        return {}

    @logger_wrapper(logger)
    def set_server_ip(self, data):
        return True
