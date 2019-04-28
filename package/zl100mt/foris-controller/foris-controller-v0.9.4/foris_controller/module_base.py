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

import types


class UnknownAction(Exception):
    pass


class BaseModule(object):

    def __init__(self, handler, notify, reset_notify):
        """ Inits base module (sets the handler)

        :param handler: handler to be set
        :type handler: handler instance
        :param notify: a function to send notifications back to bus
        :type notify: callable
        :param reset_notify: a function which resets the notification connection
        :type reset_notify: callable
        """
        self.handler = handler
        # Add a bound methods (first arg of the callable should be the instance)
        self.notify = types.MethodType(notify, self)
        self.reset_notify = types.MethodType(reset_notify, self)

    def perform_action(self, action, data):
        """ Perfoms the specified action a returns result

        :param action: actions to be performed
        :type action: str
        :param data: data of the action
        :type data: dict
        :returns: response to action and data
        :rtype: dict
        """
        action_function = getattr(self, "action_%s" % action)
        if not action_function:
            self.logger.error("Unkown action '%s'!" % action)
            raise UnknownAction(action)

        self.logger.debug("Starting to perform '%s' action" % action)
        res = action_function(data)
        self.logger.debug("Action '%s' finished" % action)
        return res
