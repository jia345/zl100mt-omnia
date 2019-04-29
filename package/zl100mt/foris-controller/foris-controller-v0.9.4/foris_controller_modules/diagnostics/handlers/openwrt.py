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

from foris_controller.handler_base import BaseOpenwrtHandler
from foris_controller.utils import logger_wrapper

from foris_controller_backends.diagnostics import DiagnosticsCmds

from .. import Handler

logger = logging.getLogger("sample.handlers.diagnostics")


class OpenwrtDiagnosticsHandler(Handler, BaseOpenwrtHandler):

    diagnostics_cmds = DiagnosticsCmds()

    @logger_wrapper(logger)
    def list_modules(self):
        return sorted(self.diagnostics_cmds.list_modules().keys())

    @logger_wrapper(logger)
    def list_diagnostics(self):
        return self.diagnostics_cmds.list_diagnostics()

    @logger_wrapper(logger)
    def prepare_diagnostic(self, *modules):
        return self.diagnostics_cmds.prepare_diagnostic(*modules)

    @logger_wrapper(logger)
    def remove_diagnostic(self, diag_id):
        return self.diagnostics_cmds.remove_diagnostic(diag_id)
