import logging
import subprocess
import re
import os

from foris_controller_backends.uci import UciBackend, get_option_named
from foris_controller_backends.cmdline import BaseCmdLine
from foris_controller_backends.files import BaseFile, inject_file_root
from foris_controller.exceptions import (
    FailedToParseFileContent, FailedToParseCommandOutput, BackendCommandFailed
)

logger = logging.getLogger(__name__)


class SettingsUci(BaseCmdLine, BaseFile):
    def get_srv(self):

        with UciBackend() as backend:
            data = backend.read("storage")

        uuid = get_option_named(data, "storage", "srv", "uuid", "")
        # get mountpoint of /srv
        srv_mount_point = self._trigger_and_parse(
            ['/usr/bin/stat', '-c', '%m', '/srv'], r"\s*(.*)\s*"
        )

        try:
            old_device = self._read_and_parse(
                "/proc/mounts",
                r'^(/dev/[^ ]*|ubi[^ ]*) {} .*'.format(srv_mount_point)
            )
        except FailedToParseFileContent:
            raise LookupError(
                "Can't find device that mounts as '{}' and thus can't decide what provides /srv!"
                .format(srv_mount_point)
            )

        if srv_mount_point == "/":
            old_uuid = "rootfs"
        else:
            # use blkid to obtain old uuid
            cmd = ['/usr/sbin/blkid', old_device]
            try:
                blkid, old_uuid = self._trigger_and_parse(
                    cmd,
                    r'^/dev/([^:]*):.* UUID="([^"]*)".* TYPE="([^"]*)".*',
                    (0, 2),
                )
            except (FailedToParseCommandOutput) as exc:
                raise LookupError(
                    "Can't get UUID for device '{}' from '{}'!".format(old_device, exc.message)
                )
            except (BackendCommandFailed) as exc:
                raise LookupError(
                    "Can't get UUID for device '{}'. Command '{}' has failed! ({})".format(
                        old_device, " ".join(cmd), exc
                    )
                )

        return {
            'uuid': uuid,
            'old_uuid': old_uuid,
            'old_device': old_device,
            'formating': os.path.isfile(inject_file_root('/tmp/formating'))
        }

    def update_srv(self, srv):

        with UciBackend() as backend:
            backend.set_option("storage", "srv", "uuid", srv['uuid'])
            backend.set_option("storage", "srv", "old_uuid", srv['old_uuid'])

        return True


class DriveManager(BaseCmdLine, BaseFile):
    def get_drives(self):
        ret = []
        drive_dir = '/sys/class/block'

        for dev in os.listdir(inject_file_root(drive_dir)):
            # skip some device
            if not dev.startswith("sd"):
                continue

            retval, stdout, _ = self._run_command('/usr/sbin/blkid', "/dev/%s" % dev)
            if retval == 0:
                # found using blkid
                # parse blockid output
                # remove "/dev/...:"
                stdout = stdout.decode("utf-8")
                parsed = stdout[stdout.index(":") + 1:].strip()
                # -> ['TYPE="brtfs"', ...]
                parsed = [e for e in parsed.split(" ") if e]
                # -> {"TYPE": "btrfs", ...}

                parsed = dict([(x.strip('"') for x in e.split("=")) for e in parsed if "=" in e])
                uuid = parsed.get("UUID", "")
                fs = parsed.get("TYPE", "")

                # prepare description data
                label = parsed.get("LABEL", "")
            else:
                fs = ""
                uuid = ""
                label = ""
            try:
                vendor = self._file_content("/sys/class/block/%s/device/vendor" % dev).strip()
            except IOError:
                vendor = ""
            try:
                model = self._file_content("/sys/class/block/%s/device/model" % dev).strip()
            except IOError:
                model = ""
            size = int(self._file_content("/sys/class/block/%s/size" % dev).strip())
            size = size / float(2 * (1024 ** 2))
            size = "{0:,.1f}".format(size).replace(',', ' ') if size > 0.0 else "0"

            # build description
            description = " - ".join([e for e in [label, vendor] if e])
            description = " ".join([e for e in [description, model] if e])
            description = "%s (%s GiB)" % (description, size) if description \
                else "Size %s GiB" % size

            ret.append({"dev": dev, "description": description, "fs": fs, "uuid": uuid})
        return {"drives": ret}

    def prepare_srv_drive(self, srv):
        self._run_command_and_check_retval(
            ["/usr/libexec/format_and_set_srv.sh", "/dev/%s" % srv['drive']],
            0
        )
        return {}
