#
# foris-controller-diagnostics-module
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

from foris_controller.module_base import BaseModule
from foris_controller.handler_base import wrap_required_functions


class DiagnosticsModule(BaseModule):
    logger = logging.getLogger("modules.diagnostics")

    def action_list_modules(self, data):
        return {"modules": self.handler.list_modules()}

    def action_list_diagnostics(self, data):
        return {"diagnostics": self.handler.list_diagnostics()}

    def action_prepare_diagnostic(self, data):
        modules = data["modules"]
        return {"diag_id": self.handler.prepare_diagnostic(*modules)}

    def action_remove_diagnostic(self, data):
        diag_id = data["diag_id"]
        return {"result": self.handler.remove_diagnostic(diag_id), "diag_id": diag_id}


@wrap_required_functions([
    'list_modules',
    'list_diagnostics',
    'prepare_diagnostic',
    'remove_diagnostic',
])
class Handler(object):
    pass
