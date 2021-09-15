import logging

from foris_controller.module_base import BaseModule
from foris_controller.handler_base import wrap_required_functions


class SampleModule(BaseModule):
    logger = logging.getLogger(__name__)

    def action_get(self, data):
        res = {}
        res.update(self.handler.get_sample())
        self.notify("get", {"msg": "get triggered"})
        return res


@wrap_required_functions([
    'get_sample',
])
class Handler(object):
    pass
