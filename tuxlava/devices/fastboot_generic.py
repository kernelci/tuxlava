# -*- coding: utf-8 -*-
#
# vim: set ts=4
#
# Copyright 2026-present Linaro Limited
#
# SPDX-License-Identifier: MIT

from tuxlava.devices.fastboot import FastbootDevice
from tuxlava.exceptions import InvalidArgument
from tuxlava.utils import compression


class FastbootGeneric(FastbootDevice):
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
        ramdisk,
        rootfs,
        enable_network,
        tests,
        boot,
        visibility,
        **kwargs,
    ):
        invalid_args = ["--" + k.replace("_", "-") for (k, v) in kwargs.items() if v]
        if len(invalid_args) > 0:
            raise InvalidArgument(
                f"Invalid option(s) for fastboot-generic devices: {', '.join(sorted(invalid_args))}"
            )

        if boot_args and '"' in boot_args:
            raise InvalidArgument('argument --boot-args should not contain "')
        if prompt and '"' in prompt:
            raise InvalidArgument('argument --prompt should not contain "')
        if modules and compression(modules[0]) not in [("tar", "gz"), ("tar", "xz")]:
            raise InvalidArgument(
                "argument --modules should be a .tar.gz, .tar.xz or .tgz"
            )

        for test in tests:
            test.validate(device=self, parameters=parameters, **kwargs)


class FastbootGenericArm64(FastbootGeneric):
    name = "fastboot-arm64"
    arch = "arm64"
    lava_arch = "arm64"
