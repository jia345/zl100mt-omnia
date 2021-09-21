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

from foris_controller_backends.uci import (
    UciBackend, get_option_anonymous, get_option_named, parse_bool, store_bool
)
from foris_controller_backends.services import OpenwrtServices
from foris_controller.exceptions import UciRecordNotFound

logger = logging.getLogger(__name__)


class DnsUciCommands(object):

    def get_settings(self):

        with UciBackend() as backend:
            resolver_data = backend.read("resolver")
            dhcp_data = backend.read("dhcp")

        forwarding_enabled = parse_bool(
            get_option_named(resolver_data, "resolver", "common", "forward_upstream"))
        dnssec_enabled = not parse_bool(
            get_option_named(resolver_data, "resolver", "common", "ignore_root_key", "0"))
        dns_from_dhcp_enabled = parse_bool(
            get_option_named(resolver_data, "resolver", "common", "dynamic_domains", "0"))
        res = {
            "forwarding_enabled": forwarding_enabled, "dnssec_enabled": dnssec_enabled,
            "dns_from_dhcp_enabled": dns_from_dhcp_enabled
        }
        try:
            dns_from_dhcp_domain = get_option_anonymous(
                dhcp_data, "dhcp", "dnsmasq", 0, "local")
            res["dns_from_dhcp_domain"] = dns_from_dhcp_domain.strip("/")
        except UciRecordNotFound:
            pass
        return res

    def update_settings(
            self, forwarding_enabled, dnssec_enabled, dns_from_dhcp_enabled,
            dns_from_dhcp_domain=None):

        with UciBackend() as backend:
            backend.set_option(
                "resolver", "common", "forward_upstream", store_bool(forwarding_enabled))
            backend.set_option(
                "resolver", "common", "ignore_root_key", store_bool(not dnssec_enabled))
            backend.set_option(
                "resolver", "common", "dynamic_domains", store_bool(dns_from_dhcp_enabled))
            if dns_from_dhcp_domain:
                backend.set_option(
                    "dhcp", "@dnsmasq[0]", "local", "/%s/" % dns_from_dhcp_domain.strip("/"))

        with OpenwrtServices() as services:
            services.restart("resolver")

        return True
