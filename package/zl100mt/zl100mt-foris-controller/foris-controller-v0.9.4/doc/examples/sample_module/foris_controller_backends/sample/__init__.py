import logging

from foris_controller_backends.cmdline import BaseCmdLine

logger = logging.getLogger(__name__)


class SampleCmds(BaseCmdLine):
    def get_sample(self):
        return self._run_command("pwd")[1]
