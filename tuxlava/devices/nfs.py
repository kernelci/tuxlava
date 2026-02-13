# -*- coding: utf-8 -*-
#
# vim: set ts=4
#
# Copyright 2024-present Linaro Limited
#
# SPDX-License-Identifier: MIT

from typing import Any, Dict, List, Optional

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

    boot_method: str = "u-boot"
    # Whether device needs storage preparation (mkfs/mount scratch)
    needs_storage_prep: bool = False
    # Storage device path for prep-tests (only used if needs_storage_prep=True)
    storage_device: str = "$(lava-target-storage SATA || lava-target-storage USB)"
    device_kernel_args: str = ""
    context_overrides: Dict[str, Any] = {}

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
            "nfs-s32g399a-rdb3",
        ]:
            raise InvalidArgument(
                "argument --dtb is only valid for 'nfs-bcm2711-rpi-4-b', 'nfs-juno-r2', 'nfs-rk3399-rock-pi-4b' and 'nfs-s32g399a-rdb3' devices"
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

    def device_dict(
        self, context: Dict[str, Any], d_dict_config: Optional[Dict[str, Any]] = None
    ) -> str:
        """Generate device dictionary.

        Args:
            context: LAVA context variables
            d_dict_config: Optional device dict config. When provided, generates
                           device dictionary with power/serial commands.

        Returns:
            Rendered device dictionary YAML string
        """
        template_name = (
            "nfs-device-dict.yaml.jinja2"
            if d_dict_config
            else "nfs-standard.yaml.jinja2"
        )

        return self._render_device_dict(
            template_name,
            context,
            d_dict_config,
            d_dict_defaults={
                "connection_command": "telnet localhost 2000",
                "boot_method": self.boot_method,
            },
        )


class NfsJunoR2(NfsDevice):
    name = "nfs-juno-r2"

    arch = "arm64"
    lava_arch = "arm64"

    kernel = "https://storage.tuxboot.com/buildroot/arm64/Image"
    rootfs = "https://storage.tuxboot.com/debian/20250326/trixie/arm64/rootfs.tar.xz"

    boot_method = "u-boot"
    needs_storage_prep = True
    device_kernel_args = (
        "default_hugepagesz=2M hugepages=256 earlycon rw pci=config_acs=000000@pci:0:0"
    )
    context_overrides = {
        "bootloader_prompt": "juno#",
        "booti_dtb_addr": "0x88000000",
        "extra_nfsroot_args": ",wsize=65536",
    }


class NfsRpi4(NfsDevice):
    name = "nfs-bcm2711-rpi-4-b"

    arch = "arm64"
    lava_arch = "arm64"

    kernel = "https://storage.tuxboot.com/buildroot/arm64/Image"
    rootfs = "https://storage.tuxboot.com/debian/20250326/trixie/arm64/rootfs.tar.xz"

    boot_method = "u-boot"
    device_kernel_args = (
        "8250.nr_uarts=1 cma=64M rootwait earlycon systemd.log_level=warning "
    )
    context_overrides = {
        "arch": "arm64",
        "booti_dtb_addr": "0x86000000",
        "console_device": "ttyS0",
        "extra_nfsroot_args": ",vers=3",
    }


class NfsNxpRdb3(NfsDevice):
    name = "nfs-s32g399a-rdb3"

    arch = "arm64"
    lava_arch = "arm64"

    kernel = "https://storage.tuxboot.com/buildroot/arm64/Image"
    rootfs = "https://storage.tuxboot.com/debian/20250326/trixie/arm64/rootfs.tar.xz"

    boot_method = "u-boot"
    device_kernel_args = "rootwait earlycon systemd.log_level=warning"
    context_overrides = {
        "arch": "arm64",
        "booti_dtb_addr": "0x86000000",
        "extra_nfsroot_args": ",vers=3",
    }


class NfsRockPi4(NfsDevice):
    name = "nfs-rk3399-rock-pi-4b"

    arch = "arm64"
    lava_arch = "arm64"

    kernel = "https://storage.tuxboot.com/buildroot/arm64/Image"
    rootfs = "https://storage.tuxboot.com/debian/20250326/trixie/arm64/rootfs.tar.xz"

    boot_method = "u-boot"
    device_kernel_args = "rootwait earlycon systemd.log_level=warning"
    context_overrides = {
        "arch": "arm64",
        "booti_dtb_addr": "0x86000000",
        "extra_nfsroot_args": ",vers=3",
    }


class NfsI386(NfsDevice):
    name = "nfs-i386"

    arch = "i386"
    lava_arch = "i386"

    kernel = "https://storage.tuxboot.com/buildroot/x86_64/bzImage"
    rootfs = "https://storage.tuxboot.com/debian/20250326/trixie/i386/rootfs.tar.xz"

    boot_method = "ipxe"
    needs_storage_prep = True
    device_kernel_args = "rootwait"
    context_overrides = {
        "test_character_delay": 10,
    }


class NfsX86_64(NfsDevice):
    name = "nfs-x86_64"

    arch = "x86_64"
    lava_arch = "x86_64"

    kernel = "https://storage.tuxboot.com/buildroot/x86_64/bzImage"
    rootfs = "https://storage.tuxboot.com/debian/20250326/trixie/amd64/rootfs.tar.xz"

    boot_method = "ipxe"
    needs_storage_prep = True
    device_kernel_args = "rootwait"
    context_overrides = {
        "test_character_delay": 10,
    }


class NfsAmpereOne(NfsDevice):
    name = "nfs-ampereone"

    arch = "arm64"
    lava_arch = "arm64"

    kernel = "https://storage.tuxboot.com/buildroot/arm64/Image"
    rootfs = "https://storage.tuxboot.com/debian/trixie/arm64/rootfs.tar.xz"

    boot_method = "grub"
    needs_storage_prep = True
    storage_device = "/dev/nvme0n1p2"
    context_overrides = {
        "arch": "arm64",
    }


class NfsAltraMaxAc02(NfsAmpereOne):
    name = "nfs-altra-max-ac02"


class NfsAmpereOneOc04(NfsAmpereOne):
    name = "nfs-ampereone-ac04"


class NfsCd8180OrionO6(NfsDevice):
    name = "nfs-cd8180-orion-o6"

    arch = "arm64"
    lava_arch = "arm64"

    kernel = "https://storage.tuxboot.com/buildroot/arm64/Image"
    rootfs = "https://storage.tuxboot.com/debian/trixie/arm64/rootfs.tar.xz"

    boot_method = "grub"
    needs_storage_prep = True
    storage_device = "/dev/nvme0n1p2"
    device_kernel_args = "rw console=ttyAMA2,115200 efi=noruntime earlycon=pl011,0x040d0000 arm-smmu-v3.disable_bypass=0 cma=640M acpi=force"
    context_overrides = {
        "arch": "arm64",
    }
