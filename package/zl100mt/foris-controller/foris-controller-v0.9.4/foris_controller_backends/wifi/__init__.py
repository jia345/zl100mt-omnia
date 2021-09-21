#
# foris-controller
# Copyright (C) 2018 CZ.NIC, z.s.p.o. (http://www.nic.cz/)
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
import re

from foris_controller.exceptions import UciException, UciRecordNotFound
from foris_controller_backends.uci import (
    UciBackend, get_sections_by_type, store_bool, parse_bool, get_option_named
)

from foris_controller_backends.files import inject_file_root
from foris_controller_backends.cmdline import BaseCmdLine
from foris_controller_backends.services import OpenwrtServices

logger = logging.getLogger(__name__)


class WifiUci(object):
    @staticmethod
    def get_wifi_devices(backend):
        try:
            wifi_data = backend.read("wireless")
            return get_sections_by_type(wifi_data, "wireless", "wifi-device")
        except (UciException, UciRecordNotFound):
            return []  # no wifi sections -> no gest wifi is running -> we're done

    @staticmethod
    def set_guest_wifi_disabled(backend):
        """ Should disable all guest wifi networks
        :param backend: backend controller instance
        :type backend: foris_controller_backends.uci.UciBackend
        """
        for i, _ in enumerate(WifiUci.get_wifi_devices(backend), 0):
            section_name = "guest_iface_%d" % i
            backend.add_section("wireless", "wifi-iface", section_name)
            backend.set_option("wireless", section_name, "disabled", store_bool(True))

    @staticmethod
    def _get_band(lines):
        if not lines:
            return None

        htmodes = ["NOHT"]
        channels = []
        for line in lines:
            if re.search(r"HT20", line) and "HT20" not in htmodes:
                htmodes.append("HT20")
            if re.search(r"HT40", line) and "HT40" not in htmodes:
                htmodes.append("HT40")
            if re.search(r"VHT Capabilities", line):
                htmodes.extend(["VHT20", "VHT40", "VHT80"])
            freq_match = re.match(r'^\s+\* (\d+) MHz \[(\d+)\] .*$', line)
            if freq_match:
                if "disabled" in line:
                    continue
                freq, channel = freq_match.groups()
                freq = int(freq)
                channel = int(channel)
                channels.append({
                    "number": channel, "frequency": freq, "radar": "radar detection" in line,
                })

        # detect hwmode
        if len(channels) == len([e for e in channels if 2400 < e["frequency"] < 2500]):
            hwmode = "11g"
        elif len(channels) == len([e for e in channels if 5000 < e["frequency"] < 6000]):
            hwmode = "11a"
        else:
            return None

        return {
            "available_htmodes": htmodes,
            "available_channels": channels,
            "hwmode": hwmode,
        }

    @staticmethod
    def _get_device_bands(uci_device_path):
        # read wifi device
        path1 = inject_file_root(os.path.join("/", "sys", "devices", "platform", uci_device_path))
        path2 = inject_file_root(os.path.join("/", "sys", "devices", uci_device_path))
        phy_path = glob.glob(os.path.join(path1, "ieee80211", "*")) \
            + glob.glob(os.path.join(path2, "ieee80211", "*"))
        if len(phy_path) != 1:
            return None

        phy_name = os.path.basename(phy_path[0])  # now we have phy device for iw command
        retval, stdout, _ = BaseCmdLine._run_command("/usr/sbin/iw", "phy", phy_name, "info")
        if retval != 0:
            return None

        # read dat from iw command
        bands = []
        band_lines = []
        reached = False
        for line in stdout.split("\n"):

            if reached:
                band_lines.append(line)

            # Handle stored band lines
            if re.match(r'\s*Band \d+:$', line):
                reached = True
                band = WifiUci._get_band(band_lines)
                if band:
                    bands.append(band)
                band_lines = []

        if not reached:
            # Band not present, something went wrong
            return None
        else:
            band = WifiUci._get_band(band_lines)
            if band:
                bands.append(band)

        return bands

    def _prepare_wifi_device(self, device, interface, guest_interface):
        # read data from uci
        device_name = re.search(r"radio(\d+)$", device["name"])  # radioX -> X
        if not device_name:
            return None
        device_id = int(device_name.group(1))
        enabled = not (
            parse_bool(device["data"].get("disabled", "0")) or
            parse_bool(interface["data"].get("disabled", "0"))
        )
        ssid = interface["data"].get("ssid", "Turris")
        hidden = parse_bool(interface["data"].get("hidden", "0"))
        password = interface["data"].get("key", "")
        hwmode = device["data"].get("hwmode", "11g")
        htmode = device["data"].get("htmode", "NOHT")
        current_channel = device["data"].get("channel", "11" if hwmode == "11g" else "36")
        current_channel = 0 if current_channel == "auto" else int(current_channel)

        if guest_interface:
            guest_enabled = not parse_bool(guest_interface["data"].get("disabled", "0"))
            guest_ssid = guest_interface["data"].get("ssid", "%s-guest" % ssid)
            guest_password = guest_interface["data"].get("key", "")
        else:
            guest_enabled = False
            guest_ssid = "%s-guest" % ssid
            guest_password = ""

        # first we obtain available features
        path = device["data"].get("path", None)
        if not path:
            return None

        bands = WifiUci._get_device_bands(path)
        if not bands:
            # it doesn't make sense to display device without bands
            return None

        return {
            "id": device_id,
            "enabled": enabled,
            "SSID": ssid,
            "channel": current_channel,
            "hidden": hidden,
            "hwmode": hwmode,
            "htmode": htmode,
            "password": password,
            "guest_wifi": {
                "enabled": guest_enabled,
                "SSID": guest_ssid,
                "password": guest_password,
            },
            "available_bands": bands,
        }

    def _get_device_sections(self, data):
        return [
            e for e in get_sections_by_type(data, "wireless", "wifi-device")
            if not e["anonymous"]
        ]

    def _get_interface_sections_from_device_section(self, data, device_section):
        # first anonymous section is interface
        interface = [
            e for e in get_sections_by_type(data, "wireless", "wifi-iface")
            if e["data"].get("device") == device_section["name"] and e["anonymous"]
        ][0]
        # first non-anonymous section starting with 'guest_iface_' is guest wifi
        guest_interfaces = [
            e for e in get_sections_by_type(data, "wireless", "wifi-iface")
            if e["data"].get("device") == device_section["name"] and not e["anonymous"]
            and e["name"].startswith("guest_iface_")
        ]
        guest_interface = guest_interfaces[0] if guest_interfaces else None

        return interface, guest_interface

    def get_settings(self):
        """ Get current wifi settings
        :returns: {"devices": [{...}]}
        "rtype: dict
        """
        devices = []
        try:
            with UciBackend() as backend:
                data = backend.read("wireless")
            device_sections = self._get_device_sections(data)
            for device_section in device_sections:
                interface, guest_interface = self._get_interface_sections_from_device_section(
                    data, device_section)
                device = self._prepare_wifi_device(device_section, interface, guest_interface)
                if device:
                    devices.append(device)

        except (UciException, UciRecordNotFound):
            devices = []

        return {"devices": devices}

    def _update_wifi(
        self, backend, settings, device_section, interface_section,
        guest_interface_section
    ):
        """
        :returns: Name of the guest interface if guest interface is enabled otherwise None
        :rtype: None or str
        """
        # sections are supposed to exist so there is no need to create them

        if not settings["enabled"]:
            # disable everything
            backend.set_option("wireless", device_section["name"], "disabled", store_bool(True))
            backend.set_option("wireless", interface_section["name"], "disabled", store_bool(True))
            if guest_interface_section:
                backend.set_option(
                    "wireless", guest_interface_section["name"], "disabled", store_bool(True)
                )
            return None
        else:
            backend.set_option("wireless", device_section["name"], "disabled", store_bool(False))
            backend.set_option("wireless", interface_section["name"], "disabled", store_bool(False))
            # guest wifi is enabled elsewhere

        # device
        channel = "auto" if settings["channel"] == 0 else int(settings["channel"])
        backend.set_option("wireless", device_section["name"], "channel", channel)
        backend.set_option("wireless", device_section["name"], "hwmode", settings["hwmode"])
        backend.set_option("wireless", device_section["name"], "htmode", settings["htmode"])

        # interface
        backend.set_option("wireless", interface_section["name"], "ssid", settings["SSID"])
        backend.set_option("wireless", interface_section["name"], "network", "lan")
        backend.set_option("wireless", interface_section["name"], "mode", "ap")
        backend.set_option(
            "wireless", interface_section["name"], "hidden", store_bool(settings["hidden"]))
        backend.set_option("wireless", interface_section["name"], "encryption", "psk2+ccmp")
        backend.set_option("wireless", interface_section["name"], "wpa_group_rekey", "86400")
        backend.set_option("wireless", interface_section["name"], "key", settings["password"])

        # guest interface
        if not guest_interface_section:
            guest_name = "guest_iface_%d" % settings["id"]
            # prepare guest network if it doesn't exist
            backend.add_section("wireless", "wifi-iface", guest_name)
        else:
            guest_name = guest_interface_section["name"]

        if not settings["guest_wifi"]["enabled"]:
            # just add disabled and possibly update device if wifi-interface is newly created
            backend.set_option("wireless", guest_name, "disabled", store_bool(True))
            backend.set_option("wireless", guest_name, "device", device_section["name"])
            return None

        backend.set_option("wireless", guest_name, "disabled", store_bool(False))
        backend.set_option("wireless", guest_name, "device", device_section["name"])
        backend.set_option("wireless", guest_name, "mode", "ap")
        backend.set_option("wireless", guest_name, "ssid", settings["guest_wifi"]["SSID"])
        backend.set_option("wireless", guest_name, "network", "guest_turris")
        backend.set_option("wireless", guest_name, "encryption", "psk2+ccmp")
        backend.set_option("wireless", guest_name, "wpa_group_rekey", "86400")
        backend.set_option("wireless", guest_name, "key", settings["guest_wifi"]["password"])
        guest_ifname = "guest_turris_%d" % settings["id"]
        backend.set_option("wireless", guest_name, "ifname", guest_ifname)
        backend.set_option("wireless", guest_name, "isolate", store_bool(True))

        return guest_ifname

    def update_settings(self, new_settings):
        """ Updates current wifi settings
        :param new_settings: {"devices": [{...}]}
        "type new_settings: dict
        :returns: True on success False otherwise
        "rtype: bool
        """
        try:
            with UciBackend() as backend:
                data = backend.read("wireless")  # data were read to find corresponding sections
                device_sections = self._get_device_sections(data)

                guest_ifnames = []

                for device in new_settings["devices"]:
                    device_section = [
                        e for e in device_sections if e["name"] == "radio%d" % device["id"]
                    ][0]

                    if device["enabled"]:
                        # test configuration

                        # find corresponding band
                        bands = [
                            e for e in WifiUci._get_device_bands(device_section["data"]["path"])
                            if e["hwmode"] == device["hwmode"]
                        ]
                        if len(bands) != 1:
                            raise ValueError()
                        band = bands[0]

                        # test channels (0 means auto)
                        if device["channel"] not in \
                                [0] + [e["number"] for e in band["available_channels"]]:
                            raise ValueError()
                        if device["htmode"] not in band["available_htmodes"]:
                            raise ValueError()

                    interface, guest_interface = self._get_interface_sections_from_device_section(
                        data, device_section)
                    ifname = self._update_wifi(
                        backend, device, device_section, interface, guest_interface)
                    if ifname:
                        guest_ifnames.append(ifname)

                if guest_ifnames:
                    from foris_controller_backends.lan import LanUci
                    data = backend.read("network")

                    try:
                        get_option_named(data, "network", "guest_turris", 'proto', None)
                        # guest network present
                        LanUci.set_guest_network(backend, {"enabled": True}, guest_ifnames)
                    except (UciException, UciRecordNotFound):
                        # guest network missing - try to create initial configuration
                        LanUci.set_guest_network(
                            backend,
                            {
                                "enabled": True, "ip": LanUci.DEFAULT_GUEST_ADDRESS,
                                "netmask": LanUci.DEFAULT_GUEST_NETMASK,
                            },
                            guest_ifnames
                        )

        except (IndexError, ValueError):
            return False  # device not found changes were not commited - no partial changes passed

        with OpenwrtServices() as services:
            services.restart("network")

        return True


class WifiCmds(BaseCmdLine):
    def reset(self):
        # export wireless config in case of any error
        with UciBackend() as backend:
            try:
                backup = backend.export_data("wireless")
            except UciException:
                backup = ""  # in case the wireless config is missing

        try:
            # clear wireless config
            with UciBackend() as backend:
                # detection can be performed only when empty wireless is present
                # import_data write to final conf immediatelly (not affected by commits)
                backend.import_data("", "wireless")
                new_data, _ = self._run_command_and_check_retval(["/sbin/wifi", "detect"], 0)
                backend.import_data(new_data, "wireless")

        except Exception as e:
            logger.error("Exception occured during the reset '%s'" % str(e))
            # try to restore the backup
            with UciBackend() as backend:
                backend.import_data(backup, "wireless")
            return False

        return True
