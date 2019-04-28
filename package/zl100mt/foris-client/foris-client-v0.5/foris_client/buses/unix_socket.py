#
# foris-client
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

import json
import logging
import os
import socket
import struct
import sys
import threading

if sys.version_info < (3, 0):
    import SocketServer
else:
    import socketserver
    SocketServer = socketserver

from .base import BaseSender, BaseListener

logger = logging.getLogger(__name__)


def _normalize_timeout(timeout):
    return None if not timeout else float(timeout) / 1000  # 0 makes non-blocking socket


class UnixSocketSender(BaseSender):


    def connect(self, socket_path, default_timeout=0):
        """ connects to unix-socket

        :param socket_path: path to unix-socket
        :type socket_path: str
        :param default_timeout: default timeout for send operations (in ms)
        :type default_timeout: int
        """
        self.default_timeout = _normalize_timeout(default_timeout)
        logger.debug("Trying to connect to '%s'." % socket_path)
        self.sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.sock.connect(socket_path)
        logger.debug(
            "Connected to '%s' (default_timeout=%d)." % (
                socket_path, 0 if not default_timeout else default_timeout
            )
        )

    def send(self, module, action, data, timeout=None):
        """ send request

        :param module: module which will be used
        :type module: str
        :param action: action which will be called
        :type action: str
        :param data: data for the request
        :type data: dict
        :param timeout: timeout for the request in ms (0=wait forever)
        :returns: reply
        """
        timeout = self.default_timeout if timeout is None else timeout
        timeout = _normalize_timeout(timeout)
        message = {
            "kind": "request",
            "module": module,
            "action": action,
        }

        if data is not None:
            message["data"] = data

        raw_message = json.dumps(message).encode("utf8")
        logger.debug("Sending message (len=%d): %s" % (len(raw_message), raw_message))
        length_bytes = struct.pack("I", len(raw_message))
        self.sock.sendall(length_bytes + raw_message)
        logger.debug("Message was send. Waiting for response.")

        length = struct.unpack("I", self.sock.recv(4))[0]
        logger.debug("Response length = %d." % length)

        self.sock.settimeout(timeout)
        received = self.sock.recv(length)
        recv_len = len(received)
        while recv_len < length:
            received += self.sock.recv(length)
            recv_len = len(received)
            logger.debug("Partial message recieved.")

        logger.debug("Message received: %s", received)

        res = json.loads(received.decode("utf8")).get("data", {})

        # Raise exception on error
        self._raise_exception_on_error(res)

        return res

    def disconnect(self):
        logger.debug("Closing connection.")
        self.sock.close()
        logger.debug("Connection closed.")


class UnixSocketListener(BaseListener):

    def connect(self, socket_path, handler, module=None, timeout=0):
        """ connects to ubus and starts to listen

        :param socket_path: path to ubus socket
        :type socket_path: str
        :param handler: handler which will be called on obtained data
        :type handler: callable
        :param timeout: how log is the listen period (in ms)
        :type timeout: int
        """
        self.timeout = _normalize_timeout(timeout)
        lock = threading.Lock()

        class Server(SocketServer.ThreadingMixIn, SocketServer.UnixStreamServer):
            pass
        Server.timeout = self.timeout

        class Handler(SocketServer.StreamRequestHandler):
            def handle(self):
                while True:
                    length_raw = self.rfile.read(4)
                    if len(length_raw) != 4:
                        break
                    length = struct.unpack("I", length_raw)[0]
                    data = json.loads(self.rfile.read(length))
                    logger.debug("Notification recieved %s." % data)
                    if not module or data["module"] == module:
                        with lock:
                            logger.debug("Triggering handler.")
                            handler(data)

        self.server = Server(socket_path, Handler)

    def listen(self):
        logger.debug("Starting to listen.")
        if self.timeout:
            self.server.handle_request()
        else:
            self.server.serve_forever()

    def disconnect(self):
        logger.debug("Disconnecting from socket.")
        try:
            self.server.shutdown()
        except:
            pass
        try:
            self.server.server_close()
        except:
            pass
