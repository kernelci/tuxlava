# -*- coding: utf-8 -*-
#
# vim: set ts=4
#
# Copyright 2024-present Linaro Limited
#
# SPDX-License-Identifier: MIT

from typing import List

from tuxlava import templates
from tuxlava.devices import Device
from tuxlava.exceptions import InvalidArgument
from tuxlava.utils import compression, notnone, slugify


class NfsDevice(Device):
    arch: str = ""
    lava_arch: str = ""
    machine: str = ""
    cpu: str = ""
    memory: str = "4G"

    extra_options: List[str] = []
    extra_boot_args: str = ""

    console: str = ""
    rootfs_dev: str = ""
    rootfs_arg: str = ""

    dtb: str = ""
    bios: str = ""
    kernel: str = ""
    rootfs: str = ""
    test_character_delay: int = 0

    enable_network: bool = True

    def validate(
        self,
        bios,
        boot_args,
        commands,
        dtb,
        kernel,
        modules,
        overlays,
        parameters,
        prompt,
        rootfs,
        enable_network,
        tests,
        **kwargs,
    ):
        invalid_args = ["--" + k.replace("_", "-") for (k, v) in kwargs.items() if v]

        if len(invalid_args) > 0:
            raise InvalidArgument(
                f"Invalid option(s) for nfs devices: {', '.join(sorted(invalid_args))}"
            )

        if boot_args and '"' in boot_args:
            raise InvalidArgument('argument --boot-args should not contain "')
        if prompt and '"' in prompt:
            raise InvalidArgument('argument --prompt should not contain "')
        if dtb and self.name not in [
            "nfs-bcm2711-rpi-4-b",
            "nfs-juno-r2",
            "nfs-rk3399-rock-pi-4b",
        ]:
            raise InvalidArgument(
                "argument --dtb is only valid for 'nfs-bcm2711-rpi-4-b', 'nfs-juno-r2' and 'nfs-rk3399-rock-pi-4b' devices"
            )
        if modules and compression(modules[0]) not in [("tar", "gz"), ("tar", "xz")]:
            raise InvalidArgument(
                "argument --modules should be a .tar.gz, tar.xz or .tgz"
            )

        for test in tests:
            test.validate(device=self, parameters=parameters, **kwargs)

    def default(self, options) -> None:
        options.kernel = notnone(options.kernel, self.kernel)
        options.rootfs = notnone(options.rootfs, self.rootfs)

    def definition(self, **kwargs):
        kwargs = kwargs.copy()

        # Options that can *not* be updated
        kwargs["arch"] = self.arch
        kwargs["lava_arch"] = self.lava_arch
        kwargs["extra_options"] = self.extra_options.copy()

        # Options that can be updated
        kwargs["dtb"] = notnone(kwargs.get("dtb"), self.dtb)
        kwargs["kernel"] = notnone(kwargs.get("kernel"), self.kernel)
        kwargs["rootfs"] = notnone(kwargs.get("rootfs"), self.rootfs)
        if self.extra_boot_args:
            if kwargs["tux_boot_args"]:
                kwargs["tux_boot_args"] = kwargs.get("tux_boot_args") + " "
            else:
                kwargs["tux_boot_args"] = ""
            kwargs["tux_boot_args"] += self.extra_boot_args

        if kwargs["tux_prompt"]:
            kwargs["tux_prompt"] = [kwargs["tux_prompt"]]
        else:
            kwargs["tux_prompt"] = []

        kwargs["command_name"] = slugify(
            kwargs.get("parameters").get("command-name", "command")
        )
        kwargs["redirect_to_kmsg"] = self.redirect_to_kmsg

        for key in kwargs.get("parameters").keys():
            kwargs[key] = kwargs.get("parameters").get(key)

        # render the template
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
        return templates.jobs().get_template("nfs.yaml.jinja2").render(
            **kwargs
        ) + "".join(tests)

    def device_dict(self, context):
        if self.test_character_delay:
            context["test_character_delay"] = self.test_character_delay
        return templates.devices().get_template("nfs.yaml.jinja2").render(**context)


class NfsJunoR2(NfsDevice):
    name = "nfs-juno-r2"

    arch = "arm64"
    lava_arch = "arm64"

    kernel = "https://storage.tuxboot.com/buildroot/arm64/Image"
    rootfs = "https://storage.tuxboot.com/buildroot/arm64/rootfs.tar.zst"


class NfsRpi4(NfsDevice):
    name = "nfs-bcm2711-rpi-4-b"

    arch = "arm64"
    lava_arch = "arm64"

    kernel = "https://storage.tuxboot.com/buildroot/arm64/Image"
    rootfs = "https://storage.tuxboot.com/buildroot/arm64/rootfs.tar.zst"


class NfsRockPi4(NfsDevice):
    name = "nfs-rk3399-rock-pi-4b"

    arch = "arm64"
    lava_arch = "arm64"

    kernel = "https://storage.tuxboot.com/buildroot/arm64/Image"
    rootfs = "https://storage.tuxboot.com/buildroot/arm64/rootfs.tar.zst"


class NfsI386(NfsDevice):
    name = "nfs-i386"

    arch = "i386"
    lava_arch = "i386"

    kernel = "https://storage.tuxboot.com/buildroot/x86_64/bzImage"
    rootfs = "https://storage.tuxboot.com/buildroot/x86_64/rootfs.tar.zst"


class NfsX86_64(NfsDevice):
    name = "nfs-x86_64"

    arch = "x86_64"
    lava_arch = "x86_64"

    kernel = "https://storage.tuxboot.com/buildroot/x86_64/bzImage"
    rootfs = "https://storage.tuxboot.com/buildroot/x86_64/rootfs.tar.zst"
