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
import glob
import os

from foris_controller_backends.files import BaseMatch
from foris_controller_backends.uci import UciBackend, get_option_named
from foris_controller.exceptions import UciException, UciRecordNotFound

logger = logging.getLogger(__name__)

DEFAULT_LANGUAGE = "en"


class WebUciCommands(object):

    def get_language(self):

        with UciBackend() as backend:
            data = backend.read("foris")

        try:
            return get_option_named(data, "foris", "settings", "lang")
        except UciRecordNotFound:
            return DEFAULT_LANGUAGE

    def set_language(self, language):
        if language not in Languages.list_languages():
            return False

        with UciBackend() as backend:
            backend.add_section("foris", "config", "settings")
            backend.set_option("foris", "settings", "lang", language)
            # try to update LUCI as well (best effort)
            try:
                backend.add_section("luci", "core", "main")
                backend.set_option("luci", "main", "lang", language)
            except UciException:
                pass

        return True


class Languages(object):
    INSTALLED_LANG_MATCH = "/usr/lib/python2.7/site-packages/foris/langs/??.py"

    @staticmethod
    def list_languages():
        """ List installed languages
        :returns: list of installed languages
        :rtype: list of str
        """

        return [DEFAULT_LANGUAGE] + [
            os.path.basename(e)[:2]
            for e in BaseMatch.list_files(Languages.INSTALLED_LANG_MATCH)
        ]
