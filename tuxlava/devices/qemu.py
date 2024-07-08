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
        partition,
        prompt,
        rootfs,
        enable_kvm,
        tests,
        **kwargs,
    ):
        invalid_args = ["--" + k.replace("_", "-") for (k, v) in kwargs.items() if v]

        if len(invalid_args) > 0:
            raise InvalidArgument(
                f"Invalid option(s) for qemu devices: {', '.join(sorted(invalid_args))}"
            )

        if bios and self.name not in ["qemu-riscv32", "qemu-riscv64"]:
            raise InvalidArgument(
                "argument --bios is only valid for qemu-riscv32 and qemu-riscv64 device"
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
        kwargs["no_kvm"] = not kwargs["enable_kvm"]

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

        if "cpu.lpa2" in kwargs.get("parameters").keys() and kwargs["parameters"].get(
            "cpu.lpa2"
        ) in ["off", "on"]:
            if self.name not in ["qemu-arm64", "qemu-arm64be"]:
                raise InvalidArgument(
                    "argument '--parameters cpu.lpa2=on/off' is only valid for qemu-arm64 and qemu-arm64be device"
                )
            kwargs["cpu"] += f',lpa2={kwargs["parameters"]["cpu.lpa2"]}'

        kwargs["command_name"] = slugify(
            kwargs.get("parameters").get("command-name", "command")
        )

        tmp_ljp = kwargs.get("parameters").get("lava_job_priority") or 50
        if "lava_job_priority" in kwargs.get("parameters").keys():
            if int(tmp_ljp) > 100 or int(tmp_ljp) <= 0:
                raise InvalidArgument("argument --parameters lava_job_priority must be a value between 1-100")
        kwargs["lava_job_priority"] = tmp_ljp

        # render the template
        tests = [
            t.render(
                arch=kwargs["arch"],
                commands=kwargs["commands"],
                command_name=kwargs["command_name"],
                device=kwargs["device"],
                overlays=kwargs["overlays"],
                parameters=kwargs["parameters"],
                lava_job_priority=kwargs["lava_job_priority"],
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
    rootfs_arg = "-drive file={rootfs},if=none,format=raw,id=hd0 -device virtio-blk-device,drive=hd0"

    kernel = "https://storage.tuxboot.com/buildroot/arm64/Image"
    rootfs = "https://storage.tuxboot.com/buildroot/arm64/rootfs.ext4.zst"

    def validate(self, enable_kvm, **kwargs):
        super().validate(enable_kvm=enable_kvm, **kwargs)

        if enable_kvm and platform.machine() == "aarch64":
            self.machine = "virt,gic-version=3"
            self.cpu = "max"


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
    rootfs_arg = "-drive file={rootfs},if=none,format=raw,id=hd0 -device virtio-blk-pci,drive=hd0"

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
    rootfs_arg = "-drive file={rootfs},if=none,format=raw,id=hd0 -device virtio-blk-device,drive=hd0"

    kernel = "https://storage.tuxboot.com/buildroot/armv7/zImage"
    rootfs = "https://storage.tuxboot.com/buildroot/armv7/rootfs.ext4.zst"


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
    rootfs_arg = "-drive file={rootfs},format=raw,id=hd0 -device virtio-blk-device,drive=hd0 -chardev stdio,signal=off,id=char0 -serial chardev:char0"

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
    rootfs_arg = (
        "-drive file={rootfs},format=raw,id=hd0 -device virtio-blk-device,drive=hd0"
    )

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
    rootfs_arg = (
        "-drive file={rootfs},format=raw,id=hd0 -device virtio-blk-device,drive=hd0"
    )

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
    rootfs_arg = (
        "-drive file={rootfs},if=none,format=raw,id=hd0 -device virtio-blk,drive=hd0"
    )

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
