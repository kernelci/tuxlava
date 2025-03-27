#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# vim: set ts=4
#
# Copyright 2024-present Linaro Limited
#
# SPDX-License-Identifier: MIT

import re
import shlex
import tempfile

from pathlib import Path
from typing import Dict, List
from tuxlava.argparse import filter_options
from tuxlava.exceptions import InvalidArgument, MissingArgument, TuxLavaError
from tuxlava.devices import Device
from tuxlava.tests import Test
from tuxlava.tuxmake import TuxBuildBuild, TuxMakeBuild
from tuxlava.utils import pathurlnone

TEST_DEFINITIONS = "https://storage.tuxboot.com/test-definitions/2025.03.tar.zst"


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
        commands: List[str] = [],
        qemu_image: str = None,
        qemu_binary: str = None,
        dtb: str = None,
        kernel: str = None,
        boot: str = None,
        ap_romfw: str = None,
        mcp_fw: str = None,
        mcp_romfw: str = None,
        fip: str = None,
        enable_kvm: bool = False,
        enable_trustzone: bool = False,
        enable_network: bool = False,
        prompt: str = None,
        ramdisk: str = None,
        rootfs: str = None,
        rootfs_partition: int = None,
        shared: str = None,
        scp_fw: str = None,
        scp_romfw: str = None,
        shell: bool = False,
        ssh_host: str = None,
        ssh_prompt: str = None,
        ssh_port: int = 0,
        ssh_user: str = None,
        ssh_identity_file: str = None,
        tests: List[str] = [],
        timeouts: Dict[str, int] = {},
        tux_prompt: str = None,
        uefi: str = None,
        boot_args: str = None,
        secrets: str = None,
        modules: str = None,
        overlays: List[str] = [],
        parameters: Dict[str, str] = {},
        deploy_os: str = None,
        tuxbuild: str = None,
        tuxmake: str = None,
        job_definition: str = None,
        tmpdir: Path = None,
        cache_dir: Path = None,
    ) -> None:
        self.device = device
        self.bios = bios
        self.bl1 = bl1
        self.commands = commands
        self.qemu_image = qemu_image
        self.qemu_binary = qemu_binary
        self.dtb = dtb
        self.kernel = kernel
        self.boot = boot
        self.ap_romfw = ap_romfw
        self.mcp_fw = mcp_fw
        self.mcp_romfw = mcp_romfw
        self.fip = fip
        self.enable_kvm = enable_kvm
        self.enable_trustzone = enable_trustzone
        self.enable_network = enable_network
        self.prompt = prompt
        self.ramdisk = ramdisk
        self.rootfs = rootfs
        self.rootfs_partition = rootfs_partition
        self.shared = shared
        self.scp_fw = scp_fw
        self.scp_romfw = scp_romfw
        self.shell = shell
        self.ssh_host = ssh_host
        self.ssh_prompt = ssh_prompt
        self.ssh_port = ssh_port
        self.ssh_user = ssh_user
        self.ssh_identity_file = ssh_identity_file
        self.tests = tests
        self.timeouts = timeouts
        self.tux_prompt = tux_prompt
        self.uefi = uefi
        self.boot_args = boot_args
        self.secrets = secrets
        self.modules = modules
        self.overlays = overlays
        self.parameters = parameters
        self.deploy_os = deploy_os
        self.tuxbuild = tuxbuild
        self.tuxmake = tuxmake
        self.job_definition = job_definition
        self.tmpdir = tmpdir
        self.cache_dir = cache_dir
        self.test_definitions = None
        self.extra_assets = []
        self.tux_boot_args = None

    def __str__(self) -> str:
        tests = "_".join(self.tests) if self.tests else "boot"
        return f"Job {self.device}/{tests}"

    @property
    def lava_job_tags(self):
        tags = self.parameters.get("TAGS") if self.parameters else ""
        return tags.split(",") if tags else ""

    @property
    def lava_job_priority(self):
        priority = (
            self.parameters.get("LAVA_JOB_PRIORITY", "low")
            if self.parameters
            else "low"
        )
        if not re.match("^(100|[1-9][0-9]?|low|medium|high)$", str(priority)):
            raise InvalidArgument(
                "argument --parameters LAVA_JOB_PRIORITY must be a value between 1-100 or one of 'low', 'medium' or 'high'"
            )
        return priority

    def initialize(self) -> str:
        # Initialize Job class
        overlays = []

        # Grab the modules path from parameters if available, else set it
        # as "/" by default
        if isinstance(self.modules, str):
            self.modules = [
                self.modules,
                self.parameters.get("MODULES_PATH", "/") if self.parameters else "/",
            ]

        if self.tuxbuild or self.tuxmake:
            tux = (
                tuxbuild_url(self.tuxbuild)
                if self.tuxbuild
                else tuxmake_directory(self.tuxmake)
            )
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
        else:
            for k, v in self.parameters.items():
                if isinstance(v, str) and "$BUILD/" in v:
                    raise InvalidArgument(
                        "parameter with '$BUILD/' substitution requires --tuxbuild or --tuxmake"
                    )

        if self.shell:
            if "hacking-session" not in self.tests:
                self.tests.append("hacking-session")
            if not self.parameters.get("PUB_KEY"):
                keys = list(Path("~/.ssh/").expanduser().glob("id_*.pub"))
                if len(keys) == 0:
                    raise TuxLavaError("no ssh public key in ~/.ssh/")
                self.parameters["PUB_KEY"] = "\n\n".join(
                    k.read_text(encoding="utf-8").rstrip() for k in keys
                )

        if self.commands:
            self.tests.append("commands")
            self.commands = " ".join([shlex.quote(s) for s in self.commands])

        if "hacking-session" in self.tests:
            self.enable_network = True
            if not self.parameters.get("PUB_KEY"):
                raise MissingArgument("argument missing --parameters PUB_KEY='...'")

        self.device = Device.select(self.device)()
        self.tests = [Test.select(t)(self.timeouts.get(t)) for t in self.tests]
        self.device.validate(**filter_options(self))
        self.device.default(self)

        if self.shared is not None and not self.device.name.startswith("qemu-"):
            raise InvalidArgument("--shared options is only available for qemu devices")

        if self.tests:
            tests = [t.name for t in self.tests]
            if sorted(list(set(tests))) != sorted(tests):
                raise InvalidArgument("each test should appear only once")

        if self.device.flag_cache_rootfs:
            self.rootfs = pathurlnone(self.rootfs)

        if self.modules and not self.device.name.startswith("fastboot-"):
            overlays.append(("modules", self.modules[0], self.modules[1]))
            self.extra_assets.append(self.modules[0])

        # When using --shared without any arguments, point to cache_dir
        if self.shared is not None:
            if not self.shared:
                assert self.cache_dir
                self.shared = [str(self.cache_dir), "/mnt/tuxrun"]
            self.extra_assets.append(("file://" + self.shared[0], False))

        for index, item in enumerate(self.overlays):
            overlays.append((f"overlay-{index:02}", item[0], item[1]))
            self.extra_assets.append(item[0])

        # get test definitions url, when required
        if any(t.need_test_definition for t in self.tests):
            self.test_definitions = pathurlnone(TEST_DEFINITIONS)

        for _, v in self.parameters.items():
            if isinstance(v, str) and v.startswith("file://"):
                self.extra_assets.append(v)

        # Create the temp directory
        if self.tmpdir is None:
            self.tmpdir = Path(tempfile.mkdtemp(prefix="tuxlava-"))

        self.tux_boot_args = (
            " ".join(shlex.split(self.boot_args)) if self.boot_args else None
        )

        self.overlays = overlays
        # Add extra assets from device
        self.extra_assets.extend(self.device.extra_assets(**vars(self)))

    def render(self):
        def_arguments = {
            "bios": self.bios,
            "bl1": self.bl1,
            "commands": self.commands,
            "device": self.device,
            "qemu_image": self.qemu_image,
            "qemu_binary": self.qemu_binary,
            "dtb": self.dtb,
            "kernel": self.kernel,
            "boot": self.boot,
            "ap_romfw": self.ap_romfw,
            "mcp_fw": self.mcp_fw,
            "mcp_romfw": self.mcp_romfw,
            "fip": self.fip,
            "enable_kvm": self.enable_kvm,
            "enable_trustzone": self.enable_trustzone,
            "enable_network": self.enable_network,
            "modules": self.modules,
            "overlays": self.overlays,
            "prompt": self.prompt,
            "ramdisk": self.ramdisk,
            "rootfs": self.rootfs,
            "rootfs_partition": self.rootfs_partition,
            "shared": self.shared,
            "scp_fw": self.scp_fw,
            "scp_romfw": self.scp_romfw,
            "ssh_host": self.ssh_host,
            "ssh_prompt": self.ssh_prompt,
            "ssh_port": self.ssh_port,
            "ssh_user": self.ssh_user,
            "ssh_identity_file": self.ssh_identity_file,
            "tests": self.tests,
            "test_definitions": self.test_definitions,
            "tests_timeout": sum(t.timeout for t in self.tests),
            "timeouts": self.timeouts,
            "tmpdir": self.tmpdir,
            "tux_boot_args": self.tux_boot_args,
            "tux_prompt": self.prompt,
            "parameters": self.parameters,
            "uefi": self.uefi,
            "boot_args": self.boot_args,
            "secrets": self.secrets,
            "deploy_os": self.deploy_os,
            "LAVA_JOB_PRIORITY": self.lava_job_priority,
            "tags": self.lava_job_tags,
        }
        definition = self.device.definition(**def_arguments)
        return definition
