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

from traceback import format_exc

from jsonschema import ValidationError

from foris_controller.app import app_info

logger = logging.getLogger(__name__)


class Router(object):
    def _build_error_msg(self, orig_msg, errors):
        """ prepare error response

        :param orig_msg: original message
        :type orig_msg: dict
        :param errors: list of errors
        :type errors: list of str
        :returns: error message
        :rtype: dict
        """
        return {
            "module": orig_msg.get("module", "?"),
            "kind": "reply",
            "action": orig_msg.get("action", "?"),
            "data": {"errors": errors},
        }

    def validate(self, message):
        """ validates whether the message fits current schema and tries to obtain
            more verbose info if it does not

        :param message: message to be validated
        :type message: dict
        """

        try:
            app_info["validator"].validate(message)
        except ValidationError:
            app_info["validator"].validate_verbose(message)

    def process_message(self, message):
        """ handles the incomming message, makes sure that msg content is validated,
            routes message to corresponding module, validates output and returns reply

        :param message: incomming message
        :type message: dict
        :returns: reply to incomming message
        :rtype: dict
        """
        # validate input message
        logger.debug("Starting to validate input message.")
        try:
            self.validate(message)
        except ValidationError as exc:
            logger.warning("Failed to validate input message.")
            logger.debug("Error: \n%s" % str(exc))
            return self._build_error_msg(message, [{
                "description": "Incorrect input. %s" % str(message),
                "stacktrace": format_exc(),
            }])
        logger.debug("Input message validated.")

        if message["kind"] != "request":
            logger.warning("Wrong message kind (only requests allowed) (=%s)." % message["kind"])
            return self._build_error_msg(
                message, [{"description": "Wrong message kind (only request are allowed)."}])

        # check whether the module is loaded
        if message["module"] not in app_info["modules"]:
            logger.error(
                "Module not found '%s'" % message["module"])
            return self._build_error_msg(message, [{
                "description": "Internal error (module not found '%s')." % message["module"]
            }])

        module_instance = app_info["modules"][message["module"]]
        try:
            data = module_instance.perform_action(message["action"], message.get("data", {}))
        except Exception as e:
            logger.error("Internal error occured %s('%s'):" % (type(e), str(e)))
            logger.debug(format_exc())
            return self._build_error_msg(message, [{
                "description": "Internal error %s('%s')" % (str(e), type(e)),
                "stacktrace": format_exc(),
            }])

        reply = {
            "kind": "reply",
            "module": message["module"],
            "action": message["action"],
            "data": data,
        }

        logger.debug("Starting to validate output message.")
        try:
            self.validate(reply)
        except ValidationError as exc:
            logger.error("Failed to validate output message.")
            logger.debug("Error: \n%s" % str(exc))
            return self._build_error_msg(message, [{
                "description": "Incorrect output. %s" % str(reply),
                "stacktrace": format_exc(),
            }])

        logger.debug("Output message validated.")
        return reply
