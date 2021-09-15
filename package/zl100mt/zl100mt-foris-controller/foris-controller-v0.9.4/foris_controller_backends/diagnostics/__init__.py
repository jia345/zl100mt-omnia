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

import glob
import logging
import os
import random
import re

from datetime import datetime
from foris_controller_backends.cmdline import BaseCmdLine, BackendCommandFailed

logger = logging.getLogger("backends.diagnostics")

SCRIPT_PATH = "/usr/share/diagnostics/diagnostics.sh"


class DiagnosticsCmds(BaseCmdLine):
    @staticmethod
    def generate_diag_id():
        return "%s_%08x" % (datetime.now().strftime("%Y-%m-%d"), random.randrange(0x100000000))

    def list_modules(self):
        args = (SCRIPT_PATH, "help")
        retval, stdout, stderr = self._run_command(*args)
        if not retval == 0:
            logger.error("Listing diagnostics failed")
            logger.error("Error '%s':\n%s" % (args, stderr))
            raise BackendCommandFailed(retval, args)

        module_section_found = False
        modules = {}
        # parse output
        for line in stdout.split("\n"):
            if module_section_found:
                module_re = re.match(r"^\s{2}(\w+)$", line)
                if module_re:
                    current_module = module_re.group(1)
                    continue
                description_re = re.match(r"^\s{4}(.*)$", line)
                if description_re and current_module:
                    modules[current_module] = description_re.group(1)
            module_section_found = module_section_found or line.startswith("modules:")

        return modules

    def list_diagnostics(self):
        diagnostics = []
        for path in glob.glob("/tmp/diagnostics-*"):
            expr = re.match(r"^/tmp/diagnostics-([^\.]+).*\.([^\.]+)$", path)
            if expr:
                if expr.group(2) == "preparing":
                    diagnostics.append({
                        "diag_id": expr.group(1), "status": "preparing", "path": path
                    })
                elif expr.group(2) == "out":
                    diagnostics.append({
                        "diag_id": expr.group(1), "status": "ready", "path": path
                    })
        return sorted(diagnostics, key=lambda x: x["diag_id"])

    def prepare_diagnostic(self, *modules):

        diag_id = DiagnosticsCmds.generate_diag_id()
        args = (
            SCRIPT_PATH, "-b", "-o", "/tmp/diagnostics-%s.out" % diag_id
        ) + modules
        retval, stdout, stderr = self._run_command(*args)
        if not retval == 0:
            logger.error("Generating diagnostics has failed.")
            logger.debug("Error '%s' :\n%s" % (args, stderr))
            raise BackendCommandFailed(retval, args)

        return diag_id

    def remove_diagnostic(self, diag_id):
        try:
            os.remove("/tmp/diagnostics-%s.out" % diag_id)
        except:
            return False
        return True
