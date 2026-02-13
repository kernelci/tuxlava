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


class NfsBootloader(NfsDevice):

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
        invalid_args = ["--" + k.replace("_", "-") for (k, v) in kwargs.items() if v]
        if len(invalid_args) > 0:
            raise InvalidArgument(
                f"Invalid option(s) for nfs-bootloader devices: {', '.join(sorted(invalid_args))}"
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


class NfsGrub(NfsBootloader):
    boot_method = "grub"


class NfsGrubArm64(NfsGrub):
    name = "nfs-grub-arm64"
    arch = "arm64"
    lava_arch = "arm64"
    context_overrides = {"arch": "arm64"}


class NfsGrubRiscv64(NfsGrub):
    name = "nfs-grub-riscv64"
    arch = "riscv64"
    lava_arch = "riscv64"
    context_overrides = {"arch": "riscv64"}


class NfsGrubPpc64le(NfsGrub):
    name = "nfs-grub-ppc64le"
    arch = "ppc64le"
    lava_arch = "ppc64le"
    context_overrides = {"arch": "ppc64le"}


class NfsGrubI386(NfsGrub):
    name = "nfs-grub-i386"
    arch = "i386"
    lava_arch = "i386"
    context_overrides = {"arch": "i386"}


class NfsGrubX86_64(NfsGrub):
    name = "nfs-grub-x86-64"
    arch = "x86_64"
    lava_arch = "x86_64"
    context_overrides = {"arch": "x86_64"}


class NfsUboot(NfsBootloader):
    boot_method = "u-boot"


class NfsUbootArm64(NfsUboot):
    name = "nfs-uboot-arm64"
    arch = "arm64"
    lava_arch = "arm64"
    context_overrides = {"arch": "arm64"}


class NfsUbootRiscv64(NfsUboot):
    name = "nfs-uboot-riscv64"
    arch = "riscv64"
    lava_arch = "riscv64"
    context_overrides = {"arch": "riscv64"}


class NfsUbootPpc64le(NfsUboot):
    name = "nfs-uboot-ppc64le"
    arch = "ppc64le"
    lava_arch = "ppc64le"
    context_overrides = {"arch": "ppc64le"}


class NfsUbootI386(NfsUboot):
    name = "nfs-uboot-i386"
    arch = "i386"
    lava_arch = "i386"
    context_overrides = {"arch": "i386"}


class NfsUbootX86_64(NfsUboot):
    name = "nfs-uboot-x86-64"
    arch = "x86_64"
    lava_arch = "x86_64"
    context_overrides = {"arch": "x86_64"}
