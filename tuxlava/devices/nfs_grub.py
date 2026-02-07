# -*- coding: utf-8 -*-
#
# vim: set ts=4
#
# Copyright 2026-present Linaro Limited
#
# SPDX-License-Identifier: MIT

from tuxlava.devices.nfs import NfsDevice
from tuxlava.exceptions import InvalidArgument
from tuxlava.utils import compression


class NfsGrub(NfsDevice):
    name = "nfs-grub"

    arch = "arm64"
    lava_arch = "arm64"

    boot_method = "grub"
    context_overrides = {
        "arch": "arm64",
    }

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
        visibility,
        **kwargs,
    ):
        if boot_args and '"' in boot_args:
            raise InvalidArgument('argument --boot-args should not contain "')
        if prompt and '"' in prompt:
            raise InvalidArgument('argument --prompt should not contain "')
        if modules and compression(modules[0]) not in [("tar", "gz"), ("tar", "xz")]:
            raise InvalidArgument(
                "argument --modules should be a .tar.gz, tar.xz or .tgz"
            )

        for test in tests:
            test.validate(device=self, parameters=parameters, **kwargs)
