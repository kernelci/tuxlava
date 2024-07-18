#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# vim: set ts=4
#
# Copyright 2024-present Linaro Limited
#
# SPDX-License-Identifier: MIT

import shlex

from typing import Dict, List
from tuxlava.exceptions import InvalidArgument
from tuxlava.devices import Device
from tuxlava.tests import Test
from tuxlava.tuxmake import TuxBuildBuild, TuxMakeBuild
from tuxlava.utils import pathurlnone


TEST_DEFINITIONS = "https://storage.tuxboot.com/test-definitions/2024.06.tar.zst"


def tuxbuild_url(s):
    try:
        return TuxBuildBuild(s.rstrip("/"))
    except TuxBuildBuild.Invalid as e:
        raise InvalidArgument(str(e))


def tuxmake_directory(s):
    try:
        return TuxMakeBuild(s)
    except TuxMakeBuild.Invalid as e:
        raise InvalidArgument(str(e))


class Job:
    def __init__(
        self,
        *,
        device: str,
        bios: str = None,
        bl1: str = None,
        commands: List[str] = None,
        qemu_image: str = None,
        dtb: str = None,
        kernel: str = None,
        ap_romfw: str = None,
        mcp_fw: str = None,
        mcp_romfw: str = None,
        fip: str = None,
        enable_kvm: bool = False,
        enable_network: bool = False,
        prompt: str = None,
        ramdisk: str = None,
        rootfs: str = None,
        rootfs_partition: int = None,
        shared: bool = False,
        scp_fw: str = None,
        scp_romfw: str = None,
        tests: List[str] = None,
        timeouts: Dict[str, int] = None,
        tux_boot_args: str = None,
        tux_prompt: str = None,
        uefi: str = None,
        boot_args: str = None,
        secrets: str = None,
        modules: str = None,
        overlays: List[str] = None,
        parameters: Dict[str, str] = None,
        deploy_os: str = None,
        tuxbuild: str = None,
        tuxmake: str = None,
    ) -> None:
        self.device = device
        self.bios = bios
        self.bl1 = bl1
        self.commands = commands
        self.qemu_image = qemu_image
        self.dtb = dtb
        self.kernel = kernel
        self.ap_romfw = ap_romfw
        self.mcp_fw = mcp_fw
        self.mcp_romfw = mcp_romfw
        self.fip = fip
        self.enable_kvm = enable_kvm
        self.enable_network = enable_network
        self.prompt = prompt
        self.ramdisk = ramdisk
        self.rootfs = rootfs
        self.rootfs_partition = rootfs_partition
        self.shared = shared
        self.scp_fw = scp_fw
        self.scp_romfw = scp_romfw
        self.tests = tests
        self.timeouts = timeouts
        self.tux_boot_args = " ".join(shlex.split(boot_args)) if boot_args else None
        self.tux_prompt = tux_prompt
        self.uefi = uefi
        self.boot_args = boot_args
        self.secrets = secrets
        self.modules = modules
        self.overlays = overlays if overlays else []
        self.parameters = parameters
        self.deploy_os = deploy_os
        self.tuxbuild = tuxbuild
        self.tuxmake = tuxmake

    def __str__(self) -> str:
        tests = "_".join(self.tests) if self.tests else "boot"
        return f"Job {self.device}/{tests}"

    def render(self) -> str:
        # Render the job definition
        overlays = []

        self.device = Device.select(self.device)()
        self.tests = [Test.select(t)(self.timeouts.get(t)) for t in self.tests]
        self.device.default(self)

        # get test definitions url, when required
        test_definitions = None
        if any(t.need_test_definition for t in self.tests):
            test_definitions = pathurlnone(TEST_DEFINITIONS)

        if self.tuxbuild or self.tuxmake:
            tux = tuxbuild_url(self.tuxbuild) or tuxmake_directory(self.tuxmake)
            self.kernel = self.kernel or tux.kernel
            self.modules = self.modules or tux.modules
            self.device = self.device or f"qemu-{tux.target_arch}"
            if self.device == "qemu-armv5":
                self.dtb = tux.url + "/dtbs/versatile-pb.dtb"
            if self.parameters:
                if self.modules:
                    module, path = self.modules
                    modules_path = self.parameters.get("MODULES_PATH", path)
                    self.modules = [module, modules_path]

                for k in self.parameters:
                    if isinstance(self.parameters[k], str):
                        self.parameters[k] = self.parameters[k].replace(
                            "$BUILD/", tux.url + "/"
                        )

        if self.modules and not hasattr(self.device, "real_device"):
            overlays.append(("modules", self.modules[0], self.modules[1]))

        for index, item in enumerate(self.overlays):
            overlays.append((f"overlay-{index:02}", item[0], item[1]))

        commands = " ".join([shlex.quote(s) for s in self.commands])

        def_arguments = {
            "bios": self.bios,
            "bl1": self.bl1,
            "commands": commands,
            "device": self.device,
            "qemu_image": False,
            "dtb": self.dtb,
            "kernel": self.kernel,
            "ap_romfw": self.ap_romfw,
            "mcp_fw": self.mcp_fw,
            "mcp_romfw": self.mcp_romfw,
            "fip": self.fip,
            "enable_kvm": self.enable_kvm,
            "enable_network": self.enable_network,
            "modules": self.modules,
            "overlays": overlays,
            "prompt": self.prompt,
            "ramdisk": self.ramdisk,
            "rootfs": self.rootfs,
            "rootfs_partition": self.rootfs_partition,
            "shared": False,
            "scp_fw": self.scp_fw,
            "scp_romfw": self.scp_romfw,
            "tests": self.tests,
            "test_definitions": test_definitions,
            "tests_timeout": sum(t.timeout for t in self.tests),
            "timeouts": self.timeouts,
            "tux_boot_args": (
                " ".join(shlex.split(self.boot_args)) if self.boot_args else None
            ),
            "tux_prompt": self.prompt,
            "parameters": self.parameters,
            "uefi": self.uefi,
            "boot_args": self.boot_args,
            "secrets": self.secrets,
            "deploy_os": self.deploy_os,
        }
        definition = self.device.definition(**def_arguments)
        return definition
