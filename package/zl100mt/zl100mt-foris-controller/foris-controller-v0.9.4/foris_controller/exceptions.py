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


class BackendCommandFailed(Exception):
    def __init__(self, retval, args, strerr=None):
        """ exception which indicates the command failed

        :param args: argumenst of the command
        :type args: iterable
        :param retval: reval of the commend
        :type output: int
        :param strerr: extra string
        :type strerr: str
        """
        if strerr:
            msg = "Retval=%d(%s) for %s" % (retval, strerr, args)
        else:
            msg = "Retval=%d for %s" % (retval, args)
        super(BackendCommandFailed, self).__init__(msg)


class FailedToParseCommandOutput(Exception):
    def __init__(self, args, output):
        """ exception which indicates the output of the cmd was somehow incorrect

        :param args: argumenst of the command
        :type args: iterable
        :param output: program output
        :type output: str
        """
        super(FailedToParseCommandOutput, self).__init__("%s: %s" % (args, output))


class FailedToParseFileContent(Exception):
    def __init__(self, path, content):
        """ exception which inicates the there's something wrong with the content of a file

        :param path: path to file
        :type path: str
        :param content: the content of the file
        :type content: str
        """
        super(FailedToParseFileContent, self).__init__("%s: %s" % (path, content))


class UciException(Exception):
    def __init__(self, cmdline_args, stderr):
        """ exception which is raise when an uci cmd fails

        :param cmdline_args: cmd line arguments
        :type cmdline_args: str
        :param stderr: error output
        :type stderr: str
        """
        super(UciException, self).__init__("%s: command failed (%s)" % (cmdline_args, stderr))


class UciTypeException(Exception):
    def __init__(self, value, required_types):
        """ exception which is raised when a values are incorrectly parsed from uci
        :param value: value that was matched
        :type value: str
        :param required_types: types which were required
        :type required_types: list of strings
        """
        super(UciTypeException, self).__init__(
            "'%s' doesn't match any of required types %s" % (value, required_types)
        )


class UciRecordNotFound(Exception):
    def __init__(self, config, section=None, section_type=None, section_idx=None, option=None):
        """ excecption which is raised when a field is not found within uci config

        :param config: config name
        :type config: str
        :param section: uci section
        :type section: str or None
        :param section_type: uci section type
        :type section_type: str or None
        :param section_idx: uci section index
        :type section_idx: int or None
        :param option: uci section
        :type option: str or None
        """
        uci_path = config
        if section:
            uci_path += ".%s" % section
        elif section_type:
            uci_path += ".@%s" % section_type
            if section_idx is not None:
                uci_path += "[%d]" % section_idx
        if option:
            uci_path += ".%s" % option

        super(UciRecordNotFound, self).__init__("Uci record was not found '%s'." % uci_path)


class ServiceCmdFailed(Exception):
    def __init__(self, service, cmd, explanation=None):
        """ exception which is raised during service cmd

        :param service: the name of the service
        :type service: str
        :param cmd: service command
        :type cmd: str
        """
        explanation = " (%s)" % explanation if explanation else ""
        super(ServiceCmdFailed, self).__init__(
            "Calling '%s' for service '%s' failed.%s" % (cmd, service, explanation))
