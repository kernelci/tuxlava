# -*- coding: utf-8 -*-
#
# vim: set ts=4
#
# Copyright 2024-present Linaro Limited
#
# SPDX-License-Identifier: MIT

import platform
from typing import List, Optional

from tuxlava import templates
from tuxlava.devices import Device
from tuxlava.exceptions import InvalidArgument
from tuxlava.utils import compression, notnone, slugify


class QemuDevice(Device):
    flag_cache_rootfs = True
    real_device = False

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

    dtb: Optional[str] = None
    bios: Optional[str] = None
    kernel: Optional[str] = None
    rootfs: Optional[str] = None
    enable_kvm: bool = False
    enable_network: bool = True

    test_character_delay: int = 0

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
        rootfs_partition,
        prompt,
        rootfs,
        enable_kvm,
        enable_trustzone,
        enable_network,
        tests,
        **kwargs,
    ):
        invalid_args = ["--" + k.replace("_", "-") for (k, v) in kwargs.items() if v]

        if len(invalid_args) > 0:
            raise InvalidArgument(
                f"Invalid option(s) for qemu devices: {', '.join(sorted(invalid_args))}"
            )

        if bios and self.name not in ["qemu-riscv32", "qemu-riscv64", "qemu-arm64"]:
            raise InvalidArgument(
                "argument --bios is only valid for qemu-riscv32, qemu-riscv64 and qemu-arm64 device"
            )
        if boot_args and '"' in boot_args:
            raise InvalidArgument('argument --boot-args should not contains "')
        if prompt and '"' in prompt:
            raise InvalidArgument('argument --prompt should not contains "')
        if dtb and self.name != "qemu-armv5":
            raise InvalidArgument("argument --dtb is only valid for qemu-armv5 device")
        if modules and compression(modules[0]) not in [("tar", "gz"), ("tar", "xz")]:
            raise InvalidArgument(
                "argument --modules should be a .tar.gz, tar.xz or .tgz"
            )

        for test in tests:
            test.validate(device=self, parameters=parameters, **kwargs)

    def default(self, options) -> None:
        options.bios = notnone(options.bios, self.bios)
        options.dtb = notnone(options.dtb, self.dtb)
        options.kernel = notnone(options.kernel, self.kernel)
        options.rootfs = notnone(options.rootfs, self.rootfs)

    def arch_customization(self, kwargs):
        pass

    def definition(self, **kwargs):
        kwargs = kwargs.copy()

        # Options that can *not* be updated
        kwargs["arch"] = self.arch
        kwargs["lava_arch"] = self.lava_arch
        kwargs["machine"] = self.machine
        kwargs["cpu"] = self.cpu
        kwargs["memory"] = self.memory
        kwargs["extra_options"] = self.extra_options.copy()
        kwargs["console"] = self.console
        kwargs["rootfs_dev"] = self.rootfs_dev
        kwargs["rootfs_arg"] = self.rootfs_arg
        kwargs["enable_trustzone"] = kwargs["enable_trustzone"]
        kwargs["no_kvm"] = not kwargs["enable_kvm"]
        kwargs["no_network"] = not kwargs["enable_network"]

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
        self.arch_customization(kwargs)

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
        return templates.jobs().get_template("qemu.yaml.jinja2").render(
            **kwargs
        ) + "".join(tests)

    def device_dict(self, context):
        if self.test_character_delay:
            context["test_character_delay"] = self.test_character_delay
        return templates.devices().get_template("qemu.yaml.jinja2").render(**context)


class QemuArm64(QemuDevice):
    name = "qemu-arm64"

    arch = "arm64"
    lava_arch = "arm64"
    machine = "virt,virtualization=on,gic-version=3,mte=on"
    cpu = "max,pauth-impdef=on"

    extra_options = ["-smp 2"]

    console = "ttyAMA0"
    rootfs_dev = "/dev/vda"
    rootfs_arg = "-drive file={rootfs},format=raw,id=hd0,if=virtio"

    kernel = "https://storage.tuxboot.com/buildroot/arm64/Image"
    rootfs = "https://storage.tuxboot.com/buildroot/arm64/rootfs.ext4.zst"

    def validate(self, enable_kvm, enable_trustzone, **kwargs):
        super().validate(
            enable_kvm=enable_kvm, enable_trustzone=enable_trustzone, **kwargs
        )

        if enable_kvm and platform.machine() == "aarch64":
            self.machine = "virt,gic-version=3"
            self.cpu = "max"

        if enable_trustzone:
            self.machine = f"{self.machine},secure=on"

    def arch_customization(self, kwargs):
        """
        cpu.lpa2 defaults to on in QEMU, for kernel version <= 5.4, cpu.lpa2
        needs to be set to off.
        """
        if "cpu.lpa2" not in kwargs.get("parameters").keys():
            return

        if kwargs["parameters"]["cpu.lpa2"] not in ["off", "on"]:
            return

        kwargs["cpu"] += f',lpa2={kwargs["parameters"]["cpu.lpa2"]}'


class QemuArm64BE(QemuArm64):
    name = "qemu-arm64be"

    arch = "arm64be"

    kernel = "https://storage.tuxboot.com/buildroot/arm64be/Image"
    rootfs = "https://storage.tuxboot.com/buildroot/arm64be/rootfs.ext4.zst"


class QemuArmv5(QemuDevice):
    name = "qemu-armv5"

    arch = "armv5"
    lava_arch = "arm"
    machine = "versatilepb"
    cpu = "arm926"
    memory = "256M"

    console = "ttyAMA0"
    rootfs_dev = "/dev/vda"
    rootfs_arg = "-drive file={rootfs},format=raw,id=hd0,if=virtio"

    dtb = "https://storage.tuxboot.com/buildroot/armv5/versatile-pb.dtb"
    kernel = "https://storage.tuxboot.com/buildroot/armv5/zImage"
    rootfs = "https://storage.tuxboot.com/buildroot/armv5/rootfs.ext4.zst"


class QemuArmv7(QemuDevice):
    name = "qemu-armv7"

    arch = "armv7"
    lava_arch = "arm"
    machine = "virt,gic-version=3"
    cpu = "cortex-a15"

    extra_options = ["-smp 2"]

    console = "ttyAMA0"
    rootfs_dev = "/dev/vda"
    rootfs_arg = "-drive file={rootfs},format=raw,id=hd0,if=virtio"

    kernel = "https://storage.tuxboot.com/buildroot/armv7/zImage"
    rootfs = "https://storage.tuxboot.com/buildroot/armv7/rootfs.ext4.zst"

    def arch_customization(self, kwargs):
        """
        We need to make sure that armv7 machines use up to <= 3G of RAM
        """
        if "machine.highmem" not in kwargs.get("parameters").keys():
            return

        if kwargs["parameters"]["machine.highmem"] not in ["off", "on"]:
            return

        kwargs["machine"] += f',highmem={kwargs["parameters"]["machine.highmem"]}'
        if "highmem=off" in kwargs["machine"]:
            self.memory = "3G"
            kwargs["memory"] = self.memory


class QemuArmv7BE(QemuArmv7):
    name = "qemu-armv7be"

    arch = "armv7be"

    kernel = "https://storage.tuxboot.com/buildroot/armv7be/zImage"
    rootfs = "https://storage.tuxboot.com/buildroot/armv7be/rootfs.ext4.zst"


class Qemui386(QemuDevice):
    name = "qemu-i386"

    arch = "i386"
    lava_arch = "i386"
    machine = "q35"
    cpu = "coreduo"

    extra_options = ["-smp 2"]

    console = "ttyS0"
    rootfs_dev = "/dev/sda"
    rootfs_arg = "-drive file={rootfs},if=ide,format=raw"

    kernel = "https://storage.tuxboot.com/buildroot/i386/bzImage"
    rootfs = "https://storage.tuxboot.com/buildroot/i386/rootfs.ext4.zst"


class QemuM68k(QemuDevice):
    name = "qemu-m68k"

    arch = "m68k"
    lava_arch = "m68k"
    machine = "virt"
    cpu = "m68040"
    memory = "3G"

    console = "ttyGF0"
    rootfs_dev = "/dev/vda"
    rootfs_arg = "-drive file={rootfs},format=raw,id=hd0,if=virtio -chardev stdio,signal=off,id=char0 -serial chardev:char0"

    kernel = "https://storage.tuxboot.com/buildroot/m68k/vmlinux"
    rootfs = "https://storage.tuxboot.com/buildroot/m68k/rootfs.ext4.zst"


class QemuMips32(QemuDevice):
    name = "qemu-mips32"

    arch = "mips32"
    lava_arch = "mips"
    machine = "malta"
    cpu = "mips32r6-generic"
    memory = "2G"

    console = "ttyS0"
    rootfs_dev = "/dev/sda"
    rootfs_arg = "-drive file={rootfs},if=ide,format=raw"

    kernel = "https://storage.tuxboot.com/buildroot/mips32/vmlinux"
    rootfs = "https://storage.tuxboot.com/buildroot/mips32/rootfs.ext4.zst"


class QemuMips32EL(QemuDevice):
    name = "qemu-mips32el"

    arch = "mips32el"
    lava_arch = "mipsel"
    machine = "malta"
    cpu = "mips32r6-generic"
    memory = "2G"

    console = "ttyS0"
    rootfs_dev = "/dev/sda"
    rootfs_arg = "-drive file={rootfs},if=ide,format=raw"

    kernel = "https://storage.tuxboot.com/buildroot/mips32el/vmlinux"
    rootfs = "https://storage.tuxboot.com/buildroot/mips32el/rootfs.ext4.zst"


class QemuMips64(QemuDevice):
    name = "qemu-mips64"

    arch = "mips64"
    lava_arch = "mips64"
    machine = "malta"
    memory = "2G"

    console = "ttyS0"
    rootfs_dev = "/dev/sda"
    rootfs_arg = "-drive file={rootfs},if=ide,format=raw"

    kernel = "https://storage.tuxboot.com/buildroot/mips64/vmlinux"
    rootfs = "https://storage.tuxboot.com/buildroot/mips64/rootfs.ext4.zst"


class QemuMips64EL(QemuDevice):
    name = "qemu-mips64el"

    arch = "mips64el"
    lava_arch = "mips64el"
    machine = "malta"
    memory = "2G"

    console = "ttyS0"
    rootfs_dev = "/dev/sda"
    rootfs_arg = "-drive file={rootfs},if=ide,format=raw"

    kernel = "https://storage.tuxboot.com/buildroot/mips64el/vmlinux"
    rootfs = "https://storage.tuxboot.com/buildroot/mips64el/rootfs.ext4.zst"


class QemuPPC32(QemuDevice):
    name = "qemu-ppc32"

    arch = "ppc32"
    lava_arch = "ppc"
    machine = "ppce500"
    cpu = "e500mc"

    console = "ttyS0"
    rootfs_dev = "/dev/vda"
    rootfs_arg = "-drive file={rootfs},format=raw,if=virtio"

    kernel = "https://storage.tuxboot.com/buildroot/ppc32/uImage"
    rootfs = "https://storage.tuxboot.com/buildroot/ppc32/rootfs.ext4.zst"


class QemuPPC64(QemuDevice):
    name = "qemu-ppc64"

    arch = "ppc64"
    lava_arch = "ppc64"
    machine = "pseries"
    cpu = "POWER8"

    extra_options = ["-smp 2"]

    console = "hvc0"
    rootfs_dev = "/dev/sda"
    rootfs_arg = "-drive file={rootfs},format=raw,if=scsi,index=0"

    kernel = "https://storage.tuxboot.com/buildroot/ppc64/vmlinux"
    rootfs = "https://storage.tuxboot.com/buildroot/ppc64/rootfs.ext4.zst"


class QemuPPC64LE(QemuDevice):
    name = "qemu-ppc64le"

    arch = "ppc64le"
    lava_arch = "ppc64le"
    machine = "pseries"
    cpu = "POWER8"

    extra_options = ["-smp 2"]

    console = "hvc0"
    rootfs_dev = "/dev/sda"
    rootfs_arg = "-drive file={rootfs},format=raw,if=scsi,index=0"

    kernel = "https://storage.tuxboot.com/buildroot/ppc64le/vmlinux"
    rootfs = "https://storage.tuxboot.com/buildroot/ppc64le/rootfs.ext4.zst"


class QemuRiscV32(QemuDevice):
    name = "qemu-riscv32"

    arch = "riscv32"
    lava_arch = "riscv32"
    machine = "virt"
    cpu = "rv32"
    memory = "2G"

    extra_options = ["-smp 2"]

    console = "ttyS0"
    rootfs_dev = "/dev/vda"
    rootfs_arg = "-drive file={rootfs},format=raw,id=hd0,if=virtio"

    bios = "https://storage.tuxboot.com/buildroot/riscv32/fw_jump.elf"
    kernel = "https://storage.tuxboot.com/buildroot/riscv32/Image"
    rootfs = "https://storage.tuxboot.com/buildroot/riscv32/rootfs.ext4.zst"


class QemuRiscV64(QemuDevice):
    name = "qemu-riscv64"

    arch = "riscv64"
    lava_arch = "riscv64"
    machine = "virt"
    cpu = "rv64"

    extra_options = ["-smp 2"]

    console = "ttyS0"
    rootfs_dev = "/dev/vda"
    rootfs_arg = "-drive file={rootfs},format=raw,id=hd0,if=virtio"

    kernel = "https://storage.tuxboot.com/buildroot/riscv64/Image"
    rootfs = "https://storage.tuxboot.com/buildroot/riscv64/rootfs.ext4.zst"


class QemuS390(QemuDevice):
    name = "qemu-s390"

    arch = "s390"
    lava_arch = "s390x"
    machine = "s390-ccw-virtio"
    cpu = "max,zpci=on"

    extra_options = ["-smp 2"]

    console = "ttyS0"
    rootfs_dev = "/dev/vda net.ifnames=0"
    rootfs_arg = "-drive file={rootfs},format=raw,id=hd0,if=virtio"

    kernel = "https://storage.tuxboot.com/buildroot/s390/bzImage"
    rootfs = "https://storage.tuxboot.com/buildroot/s390/rootfs.ext4.zst"


class QemuSh4(QemuDevice):
    name = "qemu-sh4"

    arch = "sh4"
    lava_arch = "sh4"
    machine = "r2d"
    cpu = "sh7785"

    extra_boot_args = "noiotrap"

    console = "ttySC1"
    rootfs_dev = "/dev/sda"
    rootfs_arg = "-drive file={rootfs},if=ide,format=raw -serial null -serial stdio"

    kernel = "https://storage.tuxboot.com/buildroot/sh4/zImage"
    rootfs = "https://storage.tuxboot.com/buildroot/sh4/rootfs.ext4.zst"

    test_character_delay = 5


class QemuSPARC64(QemuDevice):
    name = "qemu-sparc64"

    arch = "sparc64"
    lava_arch = "sparc64"
    machine = "sun4u"

    console = "ttyS0"
    rootfs_dev = "/dev/sda"
    rootfs_arg = "-drive file={rootfs},if=ide,format=raw"

    kernel = "https://storage.tuxboot.com/buildroot/sparc64/vmlinux"
    rootfs = "https://storage.tuxboot.com/buildroot/sparc64/rootfs.ext4.zst"


class QemuX86_64(QemuDevice):
    name = "qemu-x86_64"

    arch = "x86_64"
    lava_arch = "x86_64"
    machine = "q35"
    cpu = "Nehalem"

    extra_options = ["-smp 2"]

    console = "ttyS0"
    rootfs_dev = "/dev/sda"
    rootfs_arg = "-drive file={rootfs},if=ide,format=raw"

    kernel = "https://storage.tuxboot.com/buildroot/x86_64/bzImage"
    rootfs = "https://storage.tuxboot.com/buildroot/x86_64/rootfs.ext4.zst"
