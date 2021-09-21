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
from foris_controller_backends.ipmacbind import IpmacbindUciCommands

from .. import Handler

logger = logging.getLogger(__name__)


class OpenwrtIpmacbindHandler(Handler, BaseOpenwrtHandler):
    uci_ipmac_cmds = IpmacbindUciCommands()

    @logger_wrapper(logger)
    def get_settings(self):
        """ get dns settings

        :returns: current dns settings
        :rtype: dict
        """
        return OpenwrtIpmacbindHandler.uci_ipmac_cmds.get_settings()

    @logger_wrapper(logger)
    def update_settings(self, ipmac_binds):
        """ updates current dns settings

        :param forwarding_enabled: set whether the forwarding is enabled
        :type forwarding_enabled: bool
        :param dnssec_enabled: set whether dnssec is enabled
        :type dnssec_enabled: bool
        :param dns_from_dhcp_enabled: set whether dns from dhcp is enabled
        :type dns_from_dhcp_enabled: bool
        :param dns_from_dhcp_domain: set whether dns from dhcp is enabled
        :type dns_from_dhcp_domain: str
        :rtype: str
        """
        return OpenwrtIpmacbindHandler.uci_ipmac_cmds.update_settings(ipmac_binds)
