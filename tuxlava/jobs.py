#!/usr/bin/python3
# vim: set ts=4
#
# Copyright 2024-present Linaro Limited
#
# SPDX-License-Identifier: MIT


from typing import Dict, List
from tuxlava.devices import Device
from tuxlava.tests import Test
from tuxlava.yaml import yaml_load
from tuxlava.utils import pathurlnone


TEST_DEFINITIONS = "https://storage.tuxboot.com/test-definitions/2024.06.tar.zst"


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
        prompt: str = None,
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
        self.prompt = prompt
        self.rootfs = rootfs
        self.rootfs_partition = rootfs_partition
        self.shared = shared
        self.scp_fw = scp_fw
        self.scp_romfw = scp_romfw
        self.tests = tests
        self.timeouts = timeouts
        self.tux_boot_args = (
            " ".join(shlex.split(boot_args)) if boot_args else None
        )
        self.tux_prompt = tux_prompt
        self.uefi = uefi
        self.boot_args = boot_args
        self.secrets = secrets
        self.modules = modules
        self.overlays = overlays if overlays else []
        self.parameters = parameters

    def __str__(self) -> str:
        tests = "_".join(self.tests) if tests else "boot"
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

        if self.parameters:
            if self.modules:
                modules_path = self.parameters.get("MODULES_PATH", "/")
                self.modules = [module, modules_path]

        if self.modules:
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
            "overlays": overlays,
            "prompt": self.prompt,
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
        }
        definition = self.device.definition(**def_arguments)

        job_definition = yaml_load(definition)
        job_timeout = (job_definition["timeouts"]["job"]["minutes"] + 1) * 60
        context = job_definition.get("context", {})
        return definition
