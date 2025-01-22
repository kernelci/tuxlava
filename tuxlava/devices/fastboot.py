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


class FastbootDevice(Device):
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
    boot: str = ""
    rootfs: str = ""
    ramdisk: str = ""
    template: str = "fastboot.yaml.jinja2"
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
        ramdisk,
        rootfs,
        enable_network,
        tests,
        boot,
        **kwargs,
    ):
        invalid_args = ["--" + k.replace("_", "-") for (k, v) in kwargs.items() if v]

        if len(invalid_args) > 0:
            raise InvalidArgument(
                f"Invalid option(s) for fastboot devices: {', '.join(sorted(invalid_args))}"
            )

        if bios and self.name not in [
            "fastboot-dragonboard-845c",
            "fastboot-qrb5165-rb5",
        ]:
            raise InvalidArgument(
                "argument --bios is only valid for 'fastboot-dragonboard-845c' and 'fastboot-qrb5165-rb5' device"
            )
        if ramdisk and self.name not in [
            "fastboot-dragonboard-845c",
            "fastboot-qrb5165-rb5",
        ]:
            raise InvalidArgument(
                "argument --ramdisk is only valid for 'fastboot-dragonboard-845c' and 'fastboot-qrb5165-rb5' device"
            )
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

    def default(self, options) -> None:
        options.kernel = notnone(options.kernel, self.kernel)
        options.boot = notnone(options.boot, self.boot)
        options.rootfs = notnone(options.rootfs, self.rootfs)

    def definition(self, **kwargs):
        kwargs = kwargs.copy()

        # Options that can *not* be updated
        kwargs["arch"] = self.arch
        kwargs["lava_arch"] = self.lava_arch
        kwargs["extra_options"] = self.extra_options.copy()

        # Options that can be updated
        kwargs["bios"] = notnone(kwargs.get("bios"), self.bios)
        kwargs["dtb"] = notnone(kwargs.get("dtb"), self.dtb)
        kwargs["kernel"] = notnone(kwargs.get("kernel"), self.kernel)
        kwargs["boot"] = notnone(kwargs.get("boot"), self.boot)
        kwargs["ramdisk"] = notnone(kwargs.get("ramdisk"), self.ramdisk)
        kwargs["rootfs"] = notnone(kwargs.get("rootfs"), self.rootfs)
        kwargs["reboot_to_fastboot"] = self.reboot_to_fastboot
        kwargs["redirect_to_kmsg"] = self.redirect_to_kmsg
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

        # populate all other parameters supplied
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
        return templates.jobs().get_template(self.template).render(**kwargs) + "".join(
            tests
        )

    def device_dict(self, context):
        if self.test_character_delay:
            context["test_character_delay"] = self.test_character_delay
        return (
            templates.devices().get_template("fastboot.yaml.jinja2").render(**context)
        )


class FastbootE850_96(FastbootDevice):
    name = "fastboot-e850-96"

    arch = "arm64"
    lava_arch = "arm64"

    kernel = "https://storage.tuxboot.com/buildroot/arm64/Image"
    rootfs = "https://storage.tuxboot.com/buildroot/arm64/rootfs.tar.zst"


class FastbootDragonboard_410c(FastbootDevice):
    name = "fastboot-dragonboard-410c"

    arch = "arm64"
    lava_arch = "arm64"

    kernel = "https://storage.tuxboot.com/buildroot/arm64/Image"
    rootfs = "https://storage.tuxboot.com/buildroot/arm64/rootfs.tar.zst"


class FastbootDragonboard_845c(FastbootDevice):
    name = "fastboot-dragonboard-845c"
    arch = "arm64"
    lava_arch = "arm64"
    redirect_to_kmsg = False

    kernel = "https://storage.tuxboot.com/buildroot/arm64/Image"
    rootfs = "https://storage.tuxboot.com/buildroot/arm64/rootfs.tar.zst"
    bios = "https://images.validation.linaro.org/snapshots.linaro.org/96boards/dragonboard845c/linaro/rescue/28/dragonboard-845c-bootloader-ufs-linux-28/gpt_both0.bin"
    ramdisk = "https://snapshots.linaro.org/member-builds/qcomlt/boards/qcom-armv8a/openembedded/master/56008/rpb/initramfs-rootfs-image-qcom-armv8a.rootfs-20240118001247-92260.cpio.gz"


class FastbootOEDragonboard_845c(FastbootDevice):
    name = "fastboot-oe-dragonboard-845c"
    arch = "arm64"
    lava_arch = "arm64"
    redirect_to_kmsg = False

    boot = "https://storage.tuxboot.com/buildroot/arm64/boot.img"
    rootfs = "https://storage.tuxboot.com/buildroot/arm64/rootfs.tar.zst"
    bios = "https://images.validation.linaro.org/snapshots.linaro.org/96boards/dragonboard845c/linaro/rescue/28/dragonboard-845c-bootloader-ufs-linux-28/gpt_both0.bin"
    template = "fastboot-oe.yaml.jinja2"


class FastbootX15(FastbootDevice):
    name = "fastboot-x15"

    arch = "arm64"
    lava_arch = "arm64"
    reboot_to_fastboot = "true"

    kernel = "https://storage.tuxboot.com/buildroot/arm64/Image"
    rootfs = "https://storage.tuxboot.com/buildroot/arm64/rootfs.tar.zst"


class FastbootQRB5165rb5(FastbootDevice):
    name = "fastboot-qrb5165-rb5"

    arch = "arm64"
    lava_arch = "arm64"

    kernel = "https://storage.tuxboot.com/buildroot/arm64/Image"
    rootfs = "https://storage.tuxboot.com/buildroot/arm64/rootfs.tar.zst"
    bios = "https://images.validation.linaro.org/snapshots.linaro.org/96boards/qrb5165-rb5/linaro/rescue/27/rb5-bootloader-ufs-linux-27/gpt_both0.bin"
    ramdisk = "https://snapshots.linaro.org/member-builds/qcomlt/boards/qcom-armv8a/openembedded/master/56008/rpb/initramfs-rootfs-image-qcom-armv8a.rootfs-20240118001247-92260.cpio.gz"


class FastbootAOSPDevice(Device):
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
    device_type: str = ""

    test_character_delay: int = 0

    def validate(
        self,
        boot_args,
        commands,
        overlays,
        parameters,
        prompt,
        tests,
        **kwargs,
    ):
        invalid_args = ["--" + k.replace("_", "-") for (k, v) in kwargs.items() if v]

        if len(invalid_args) > 0:
            raise InvalidArgument(
                f"Invalid option(s) for fastboot aosp devices: {', '.join(sorted(invalid_args))}"
            )

        if boot_args and '"' in boot_args:
            raise InvalidArgument('argument --boot-args should not contain "')
        if prompt and '"' in prompt:
            raise InvalidArgument('argument --prompt should not contain "')

        for test in tests:
            test.validate(device=self, parameters=parameters, **kwargs)

    def default(self, options) -> None:
        pass

    def definition(self, **kwargs):
        kwargs = kwargs.copy()

        # Options that can *not* be updated
        kwargs["arch"] = self.arch
        kwargs["lava_arch"] = self.lava_arch
        kwargs["extra_options"] = self.extra_options.copy()
        kwargs["ptable"] = self.ptable

        # Options that can be updated
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

        for v in [
            "TUXSUITE_BAKE_VENDOR_DOWNLOAD_URL",
            "BUILD_REFERENCE_IMAGE_GZ_URL",
            "LKFT_BUILD_CONFIG",
        ]:
            if v not in kwargs.get("parameters").keys():
                raise InvalidArgument(f"argument --parameters {v} must be provided")
            kwargs[v] = kwargs["parameters"][v]

        # populate all other parameters supplied
        for key in kwargs.get("parameters").keys():
            kwargs[key] = kwargs.get("parameters").get(key)

        # render the template
        tests = [
            t.render(
                arch=kwargs["arch"],
                commands=kwargs["commands"],
                command_name=kwargs["command_name"],
                device=kwargs["device"],
                device_type=self.device_type,
                overlays=kwargs["overlays"],
                parameters=kwargs["parameters"],
                test_definitions=kwargs["test_definitions"],
            )
            for t in kwargs["tests"]
        ]
        return templates.jobs().get_template("fastboot-aosp.yaml.jinja2").render(
            **kwargs
        ) + "".join(tests)


class FastbootAOSPDragonboard_845c(FastbootAOSPDevice):
    name = "fastboot-aosp-dragonboard-845c"

    arch = "arm64"
    lava_arch = "arm64"
    device_type = "dragonboard-845c"

    ptable = "https://images.validation.linaro.org/snapshots.linaro.org/96boards/dragonboard845c/linaro/rescue/101/dragonboard-845c-bootloader-ufs-aosp-101/gpt_both0.bin"


class FastbootAOSPQRB5165rb5(FastbootAOSPDevice):
    name = "fastboot-aosp-qrb5165-rb5"

    arch = "arm64"
    lava_arch = "arm64"
    device_type = "qrb5165-rb5"

    ptable = "https://images.validation.linaro.org/snapshots.linaro.org/96boards/qrb5165-rb5/linaro/rescue/27/rb5-bootloader-ufs-aosp-27/gpt_both0.bin"
    ramdisk = "https://snapshots.linaro.org/member-builds/qcomlt/boards/qcom-armv8a/openembedded/master/56008/rpb/initramfs-rootfs-image-qcom-armv8a.rootfs-20240118001247-92260.cpio.gz"
