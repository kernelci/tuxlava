# -*- coding: utf-8 -*-
#
# vim: set ts=4
#
# Copyright 2026-present Linaro Limited
#
# SPDX-License-Identifier: MIT

import shlex
from typing import Dict, List, Optional, Tuple

from tuxlava import templates
from tuxlava.devices import Device
from tuxlava.exceptions import InvalidArgument, MissingArgument
from tuxlava.utils import (
    compression,
    downloaded_name,
    slugify,
    url_name,
)


class UsbgDevice(Device):
    """
    Devices that boot a whole disk image exported over USB mass storage.
    The dispatcher attaches the image as a USB gadget, so the board boots
    from it as if it was a plugged in USB disk.
    """

    arch: str = ""
    lava_arch: str = ""
    template: str = "usbg.yaml.jinja2"

    # Downloads the job must be given, and defaults for the rest.
    required_downloads: List[str] = []
    default_downloads: Dict[str, Tuple[str, Optional[str]]] = {}

    # The download the board boots from. It goes to usbg-ms.
    boot_image: str = ""

    failure_retry: int = 3

    # Docker step that turns the downloads into boot_image. Each step is
    # formatted with the saved names. It cannot hold a literal brace.
    postprocess_docker: str = ""
    postprocess_steps: List[str] = []

    # The postprocess only runs when all of these were given. Without
    # them the default downloads it needs are not fetched either.
    postprocess_needs: List[str] = []

    # A wic rootfs has no nfs, so LAVA pushes the overlay over the network
    # after boot instead.
    transfer_overlay_download: str = ""

    # Where LAVA keeps its results on the board.
    overlay_dir: str = "/var/lib/"

    @property
    def transfer_overlay_unpack(self) -> str:
        # LAVA names the archive member after the last part of
        # lava_test_results_dir, so the tarball holds lava-N and not
        # var/lib/lava-N. It has to be unpacked in overlay_dir.
        return f"tar -C {self.overlay_dir} -xzvf"

    @property
    def lava_test_results_dir(self) -> str:
        return f"{self.overlay_dir}lava-%s"

    def postprocess_applies(self, downloads) -> bool:
        return all(k in downloads for k in self.postprocess_needs)

    def all_downloads(self, downloads):
        """The files the job downloads. The user wins over the defaults."""
        if not self.postprocess_applies(downloads):
            return dict(downloads)
        return {**self.default_downloads, **downloads}

    def compression_for(self, url, filename):
        """Worked out from the name LAVA downloads as."""
        return compression(filename or url_name(url))[1]

    def saved_name(self, url, filename):
        """The name the file has in the download directory.

        LAVA drops the compression suffix when it unpacks the file during
        the download, so the name on disk is not the name we asked for.
        """
        return downloaded_name(
            filename or url_name(url), self.compression_for(url, filename)
        )

    def validate(
        self,
        commands,
        downloads,
        parameters,
        prompt,
        tests,
        visibility,
        **kwargs,
    ):
        invalid_args = ["--" + k.replace("_", "-") for (k, v) in kwargs.items() if v]
        if len(invalid_args) > 0:
            raise InvalidArgument(
                f"Invalid option(s) for usbg devices: {', '.join(sorted(invalid_args))}"
            )

        if prompt and '"' in prompt:
            raise InvalidArgument('argument --prompt should not contain "')

        all_downloads = self.all_downloads(downloads)

        missing = [k for k in self.required_downloads if k not in all_downloads]
        if missing:
            raise MissingArgument(
                f"Missing {', '.join('--' + m for m in sorted(missing))} "
                f"for device {self.name}"
            )

        if self.boot_image not in all_downloads:
            raise MissingArgument(
                f"Missing --{self.boot_image}, the image {self.name} boots from"
            )

        # The parser checks the file name too, but a Job can be built directly.
        seen = {}
        for url, filename in all_downloads.values():
            if filename is not None and ("/" in filename or filename in (".", "..")):
                raise InvalidArgument(
                    f"file name '{filename}' for '{url}' must be a plain file name"
                )
            name = self.saved_name(url, filename)
            if name in seen:
                raise InvalidArgument(
                    f"'{seen[name]}' and '{url}' are both saved as '{name}', "
                    f"use a URL with another file name"
                )
            seen[name] = url

        for test in tests:
            test.validate(device=self, parameters=parameters, **kwargs)

    def default(self, options) -> None: ...  # noqa: E704

    def device_dict(self, context, d_dict_config=None) -> str:
        """The LAVA device dictionary.

        A usbg device is a real board. The power, serial and usbg-ms
        commands can only come from the worker that has it, and there is
        no standard dictionary to fall back to.
        """
        if not d_dict_config:
            raise MissingArgument(
                f"Missing --device-dict, {self.name} is a real device"
            )

        # LAVA reads these two out of the deploy method. Without them
        # the job cannot attach the image.
        commands = d_dict_config.get("usbg_ms_commands") or {}
        missing = [k for k in ("enable", "disable") if not commands.get(k)]
        if missing:
            raise MissingArgument(
                f"Device dict is missing usbg_ms_commands "
                f"{', '.join(sorted(missing))} for device {self.name}"
            )

        context = dict(context or {})
        context.setdefault("lava_arch", self.lava_arch)
        return self._render_device_dict(
            "usbg-device-dict.yaml.jinja2",
            context,
            d_dict_config,
            d_dict_defaults={"connection_command": "telnet localhost 2000"},
        )

    def definition(self, **kwargs):
        kwargs = kwargs.copy()

        kwargs["arch"] = self.arch
        kwargs["lava_arch"] = self.lava_arch
        applies = self.postprocess_applies(kwargs["downloads"])
        kwargs["downloads"] = self.all_downloads(kwargs["downloads"])

        names = {
            key: self.saved_name(url, filename)
            for key, (url, filename) in kwargs["downloads"].items()
        }
        # The usbg-ms deploy names the file, LAVA does not glob downloads://
        kwargs["boot_image_path"] = names[self.boot_image]
        quoted = {key: shlex.quote(name) for key, name in names.items()}
        kwargs["postprocess_steps"] = (
            [step.format(**quoted) for step in self.postprocess_steps]
            if applies
            else []
        )

        if kwargs["tux_prompt"]:
            kwargs["tux_prompt"] = [kwargs["tux_prompt"]]
        else:
            kwargs["tux_prompt"] = []

        kwargs["command_name"] = slugify(
            kwargs.get("parameters").get("command-name", "command")
        )

        tests = [
            t.render(
                arch=kwargs["arch"],
                commands=kwargs["commands"],
                command_name=kwargs["command_name"],
                device=kwargs["device"],
                overlays=kwargs["overlays"],
                parameters=kwargs["parameters"],
                test_definitions=kwargs["test_definitions"],
            )
            for t in kwargs["tests"]
        ]
        return templates.jobs().get_template(self.template).render(**kwargs) + "".join(
            tests
        )


class UsbgRpi4(UsbgDevice):
    name = "usbg-bcm2711-rpi-4-b"

    arch = "arm64"
    lava_arch = "arm64"

    required_downloads = ["firmware"]
    default_downloads = {
        "script": (
            "https://gitlab.com/Linaro/blueprints/ci/-/raw/"
            "630d54e45c42ae0ca2c2ec8c3c3ea07b0996ab58/"
            "support_files/ts-merge-images.sh",
            None,
        ),
    }
    boot_image = "firmware"

    # Merge only when a separate OS image is given. A complete disk
    # image boots as it is.
    postprocess_needs = ["os"]
    postprocess_docker = "debian"
    postprocess_steps = [
        "apt-get update",
        "apt-get install -qy fdisk gdisk coreutils",
        "fdisk -l {firmware}",
        "fdisk -l {os}",
        "bash {script} {firmware} {os}",
        "fdisk -l {firmware}",
    ]

    # -O because curl writes to stdout without it, and LAVA unpacks
    # that file name afterwards.
    transfer_overlay_download = (
        "sleep 5; ip addr; route -n; curl --fail --retry 20 --retry-connrefused -O"
    )
