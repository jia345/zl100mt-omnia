#
# foris-controller
# Copyright (C) 2017 CZ.NIC, z.s.p.o. (http://www.nic.cz/)
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software Foundation,
# Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301  USA
#

import logging
import random

from datetime import datetime

from foris_controller.handler_base import BaseMockHandler
from foris_controller.utils import logger_wrapper

from .. import Handler

logger = logging.getLogger("diagnostics.handlers.mock")


class MockDiagnosticsHandler(Handler, BaseMockHandler):
    diagnostics = {}

    @logger_wrapper(logger)
    def list_modules(self):
        return ["atsha", "processes", "uname"]

    @logger_wrapper(logger)
    def list_diagnostics(self):
        return sorted(
            [dict(diag_id=k, **v) for k, v in self.diagnostics.items()], key=lambda x: x["diag_id"])

    @logger_wrapper(logger)
    def prepare_diagnostic(self, *modules):
        diag_id = "%s_%08x" % (datetime.now().strftime("%Y-%m-%d"), random.randrange(0x100000000))
        self.diagnostics[diag_id] = {
            "status": random.choice(["ready", "preparing"]),
            "path": "/tmp/diagnostics-%s.out" % diag_id,
        }
        return diag_id

    @logger_wrapper(logger)
    def remove_diagnostic(self, diag_id):
        try:
            del self.diagnostics[diag_id]
        except:
            return False
        return True
