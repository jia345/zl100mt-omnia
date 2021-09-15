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

import os
import logging


from foris_controller.utils import get_modules, get_handler, get_module_class, get_validator_dirs


logger = logging.getLogger(__name__)

app_info = {
}


def set_app_info(program_options):
    """ updates app_info variable according to cmd line options

    :param program_options: cmd line parameters
    :type program_options: argparse.Namespace
    """
    global app_info
    app_info["bus"] = program_options.bus
    app_info["debug"] = program_options.debug
    app_info["backend"] = program_options.backend
    app_info["filter_modules"] = [e[0] for e in program_options.module] \
        if program_options.module else None
    app_info["extra_module_paths"] = [e[0] for e in program_options.extra_module_path]

    import multiprocessing
    import threading
    app_info["lock_backend"] = multiprocessing if app_info["bus"] in ["ubus"] else threading
    if app_info["bus"] == "ubus":
        app_info["ubus_single_process"] = program_options.single


def _gen_notify(module_name):
    """ Generator for notify function which wrapps module name inside the notify call
    """
    def notify(self, action, data=None):
        self.logger.debug(
            "New notification (module=%s, action=%s, data=%s)" % (module_name, action, data))
        app_info["notification_sender"].notify(module_name, action, data, app_info["validator"])
    return notify


def _reset_notify(self):
    """ Resets current connection for notification sender
    """
    self.logger.debug("Resetting notification sender")
    app_info["notification_sender"].reset()


def prepare_app_modules(base_handler_class, extra_modules_paths=[]):
    """ updates app_info dictionary with loaded foris-controller modules

    :param base_handler_class: handler class to be used to initialize the modules
    :type base_handler_class: class
    :param extra_modules_paths: extra paths to dir containing modules
    """
    app_info["modules"] = {}

    # use root schema dir
    schema_dirs = [
        os.path.join(os.path.abspath(os.path.dirname(__file__)), "schemas"),
    ]

    # and global definitions
    definition_dirs = [
        os.path.join(os.path.abspath(os.path.dirname(__file__)), "schemas", "definitions"),
    ]

    for module_name, module in get_modules(app_info["filter_modules"], extra_modules_paths):
        logger.debug("Trying to load module '%s'." % module_name)
        handler = get_handler(module, base_handler_class)
        if not handler:
            logger.error(
                "Failed to find a handler '%s' for base '%s'. Skipping module."
                % (module_name, base_handler_class.__name__)
            )
            continue
        module_class = get_module_class(module)
        if not module_class:
            logger.error(
                "Failed to find a module class for module '%s'. Skipping module." % (module_name)
            )
            continue

        app_info["modules"][module_name] = module_class(
            handler, _gen_notify(module_name), _reset_notify)
        schema_dirs.append(os.path.join(module.__path__[0], "schema"))

    logger.debug("Modules loaded %s." % app_info["modules"].keys())
    from foris_schema import ForisValidator
    app_info["validator"] = ForisValidator(schema_dirs, definition_dirs)


def set_validator(filter_modules):
    """ updates app_info variable with validator object
    :param filter_modules: use only specific modules in the validator
    :type filter_modules: list of str
    """
    global app_info
    from foris_schema import ForisValidator
    app_info["validator"] = ForisValidator(*get_validator_dirs(filter_modules))


def prepare_notification_sender(sender_class, *args, **kwargs):
    """ adds notification sender to app_info variable

    :param sender_class: class which will be used for sending notification
    :type sender_class: type
    :param args: positional arguments
    :type args: iterable
    :param kwargs: named arguments
    :type kwargs: dict
    """
    global app_info
    app_info["notification_sender"] = sender_class(*args, **kwargs)
