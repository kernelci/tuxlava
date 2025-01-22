# -*- coding: utf-8 -*-
#
# vim: set ts=4
#
# Copyright 2024-present Linaro Limited
#
# SPDX-License-Identifier: MIT

from typing import Optional

from tuxlava import templates
from tuxlava.devices import Device
from tuxlava.exceptions import InvalidArgument
from tuxlava.utils import compression, notnone, slugify


class AvhDevice(Device):
    flag_use_pre_run_cmd = True
    flag_cache_rootfs = True
    real_device = False

    api_endpoint: str = "https://app.avh.arm.com/api"
    api_token: str = ""
    project_name: str = "Default Project"
    model: str = ""
    boot_args: Optional[str] = None

    arch: str = ""
    dtb: Optional[str] = None
    kernel: Optional[str] = None
    rootfs: Optional[str] = None
    rootfs_partition: int = 1

    test_character_delay: int = 0

    def validate(
        self,
        secrets,
        dtb,
        kernel,
        rootfs,
        boot_args,
        modules,
        overlays,
        parameters,
        rootfs_partition,
        prompt,
        tests,
        commands,
        **kwargs,
    ):
        invalid_args = ["--" + k.replace("_", "-") for (k, v) in kwargs.items() if v]
        if len(invalid_args) > 0:
            raise InvalidArgument(
                f"Invalid option(s) for avh devices: {', '.join(sorted(invalid_args))}"
            )

        if not secrets:
            raise InvalidArgument("argument '--secrets' is required by AVH device")
        if secrets.get("avh_api_token") is None:
            raise InvalidArgument(
                "argument '--secrets' key 'avh_api_token' value is required by AVH device"
            )

        if boot_args and '"' in boot_args:
            raise InvalidArgument('argument --boot-args should not contains "')

        if prompt and '"' in prompt:
            raise InvalidArgument('argument --prompt should not contains "')

        if modules and compression(modules[0]) not in [("tar", "gz"), ("tar", "xz")]:
            raise InvalidArgument(
                "argument --modules should be a .tar.gz, tar.xz or .tgz"
            )

        for test in tests:
            test.validate(device=self, parameters=parameters, **kwargs)

    def default(self, options) -> None:
        options.dtb = notnone(options.dtb, self.dtb)
        options.kernel = notnone(options.kernel, self.kernel)
        options.rootfs = notnone(options.rootfs, self.rootfs)

    def definition(self, **kwargs):
        kwargs = kwargs.copy()

        # Options that can *not* be updated
        kwargs["model"] = self.model
        kwargs["arch"] = self.arch

        # Options that can be updated
        kwargs["api_endpoint"] = self.api_endpoint
        kwargs["model"] = self.model
        kwargs["project_name"] = self.project_name
        if kwargs["rootfs_partition"] is None:
            kwargs["rootfs_partition"] = self.rootfs_partition
        if kwargs["boot_args"] is None:
            kwargs["boot_args"] = self.boot_args
        if kwargs["tux_prompt"]:
            kwargs["tux_prompt"] = [kwargs["tux_prompt"]]
        else:
            kwargs["tux_prompt"] = []

        kwargs["command_name"] = slugify(
            kwargs.get("parameters").get("command-name", "command")
        )

        kwargs["redirect_to_kmsg"] = self.redirect_to_kmsg

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
        return templates.jobs().get_template("avh.yaml.jinja2").render(
            **kwargs
        ) + "".join(tests)

    def device_dict(self, context):
        if self.test_character_delay:
            context["test_character_delay"] = self.test_character_delay
        return templates.devices().get_template("avh.yaml.jinja2").render(**context)


class AvhImx93(AvhDevice):
    name = "avh-imx93"

    model = "imx93"
    arch = "arm64"


class AvhRpi4b(AvhDevice):
    name = "avh-rpi4b"

    model = "rpi4b"
    arch = "arm64"
