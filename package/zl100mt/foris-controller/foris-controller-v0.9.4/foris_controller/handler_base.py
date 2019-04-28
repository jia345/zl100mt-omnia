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

import inspect


class HandlerFunctionNotImplemented(BaseException):
    pass


def wrap_required_functions(required_functions):
    """ make sure that wrapped class contains required functions

    param required_functions: list of names of required functions
    type required_functions: list of str
    """
    def wrapped(base_class):
        class MetaClass(type):
            def __init__(cls, name, bases, dct):
                # Check required_functions for all instances except for ancestors of base_class
                if name not in [e.__name__ for e in inspect.getmro(base_class)]:
                    for function_name in required_functions:
                        if function_name not in dct:
                            raise HandlerFunctionNotImplemented(function_name)

                super(MetaClass, cls).__init__(name, bases, dct)

        body = vars(base_class).copy()
        body.pop('__dict__', None)
        body.pop('__weakref__', None)

        return MetaClass(base_class.__name__, base_class.__bases__, body)

    return wrapped


class BaseOpenwrtHandler(object):
    pass


class BaseMockHandler(object):
    pass
