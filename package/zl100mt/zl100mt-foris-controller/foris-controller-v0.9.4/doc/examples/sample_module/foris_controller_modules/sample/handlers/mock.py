import logging

from foris_controller.handler_base import BaseMockHandler
from foris_controller.utils import logger_wrapper

from .. import Handler

logger = logging.getLogger(__name__)


class MockSampleHandler(Handler, BaseMockHandler):

    @logger_wrapper(logger)
    def get_sample(self):
        return {
            "data": {
                "sample": "some/path",
                "atsha": "0011002233",
            }
        }
