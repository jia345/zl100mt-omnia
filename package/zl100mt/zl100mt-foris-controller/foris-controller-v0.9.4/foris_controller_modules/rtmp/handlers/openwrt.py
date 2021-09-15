import logging

from foris_controller.handler_base import BaseOpenwrtHandler
from foris_controller.utils import logger_wrapper
from foris_controller_backends.rtmp import RtmpUciCommands

from .. import Handler

logger = logging.getLogger(__name__)

class OpenwrtRtmpHandler(Handler, BaseOpenwrtHandler):
    uci_Rtmp_cmds = RtmpUciCommands()

    @logger_wrapper(logger)
    def get_info(self):
        return OpenwrtRtmpHandler.uci_Rtmp_cmds.get_info()

    @logger_wrapper(logger)
    def set_server_ip(self, data):
        return OpenwrtRtmpHandler.uci_Rtmp_cmds.set_server_ip(data)

    @logger_wrapper(logger)
    def set_channel_list(self, data):
        return OpenwrtRtmpHandler.uci_Rtmp_cmds.set_channel_list(data)
