import logging

from foris_controller.handler_base import BaseOpenwrtHandler
from foris_controller.utils import logger_wrapper

from foris_controller_backends.about import AtshaCmds
from foris_controller_backends.sample import SampleCmds

from .. import Handler

logger = logging.getLogger(__name__)


class OpenwrtSampleHandler(Handler, BaseOpenwrtHandler):

    atsha_cmds = AtshaCmds()
    sample = SampleCmds()

    @logger_wrapper(logger)
    def get_sample(self):
        return {
            "data": {
                "sample": self.sample.get_sample(), "atsha": self.atsha_cmds.get_serial()
            }
        }
