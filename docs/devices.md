# Devices

TuxLAVA supports the following virtual devices.

* AVH
* Fastboot
* FVP
* NFS
* QEMU
* SSH

!!! tip "Listing devices"
    You can list the supported devices with:
    ```shell
    tuxlava --list-devices
    ```

## AVH devices

Device        | AVH Model      |
--------------|----------------|
avh-imx93     | i.MX93         |
avh-rpi4b     | Raspberry Pi 4 |

## Fastboot devices

Device                          |
--------------------------------|
fastboot-aosp-dragonboard-845c  |
fastboot-aosp-qrb5165-rb5       |
fastboot-dragonboard-410c       |
fastboot-dragonboard-845c       |
fastboot-exynos850-e850-96      |
fastboot-oe-dragonboard-845c    |
fastboot-x15                    |

## FVP devices

Device                |
----------------------|
fvp-aemva             |
fvp-lava              |
fvp-morello-android   |
fvp-morello-baremetal |
fvp-morello-busybox   |
fvp-morello-debian    |
fvp-morello-grub      |
fvp-morello-oe        |
fvp-morello-ubuntu    |

!!! tip "Arm architecture version on fvp-aemva"
    By default `fvp-aemva` runs the FVP model at Armv9.7, exposing
    SVE2 v3, SME2 v3, LSFE and the FP16 matrix instructions. Armv9.6
    made `HCR_EL2.E2H` read-as-one, so nVHE is no longer
    architecturally possible. Stable kernels that always run the
    nVHE-flavoured SVE EL2 init (between the refactor in v5.15 and
    the v6.5 hVHE rework) hang when writing `ZCR_EL2`. In practice
    that affects **linux-5.15.y** and **linux-6.1.y**. Older kernels
    (linux-5.10.y) kept a VHE guard around the nVHE setup and still
    boot at Armv9.7; newer kernels (linux-6.6.y and later) inherit
    the v6.5 hVHE rework and also boot unchanged. Pass
    `--parameters FVP_ARM_ARCH_VERSION=9.5` to clamp the model to
    Armv9.5 for the affected branches. The same knob can be used to
    target older architecture versions when newer ones cause issues.

# NFS devices

Device                 |
-----------------------|
nfs-bcm2711-rpi-4-b    |
nfs-i386               |
nfs-juno-r2            |
nfs-rk3399-rock-pi-4b  |
nfs-x86_64             |

## QEMU devices

Device        | Description         |
--------------|---------------------|
qemu-arm64    | 64-bit ARMv8        |
qemu-arm64be  | 64-bit ARMv8 (BE)   |
qemu-armv5    | 32-bit ARM          |
qemu-armv7    | 32-bit ARM          |
qemu-armv7be  | 32-bit ARM (BE)     |
qemu-i386     | 32-bit X86          |
qemu-m68k     | 32-bit m68k (BE)    |
qemu-mips32   | 32-bit MIPS         |
qemu-mips32el | 32-bit MIPS (EL)    |
qemu-mips64   | 64-bit MIPS         |
qemu-mips64el | 64-bit MIPS (EL)    |
qemu-ppc32    | 32-bit PowerPC      |
qemu-ppc64    | 64-bit PowerPC      |
qemu-ppc64le  | 64-bit PowerPC (EL) |
qemu-riscv32  | 32-bit RISC-V       |
qemu-riscv64  | 64-bit RISC-V       |
qemu-s390     | 64-bit s390         |
qemu-sh4      | 32-bit SH           |
qemu-sparc64  | 64-bit Sparc        |
qemu-x86_64   | 64-bit X86          |

## Using Secrets to Authorize URIs downloads in QEMU

QEMU devices support to allow downloading images from URLs
that require Authorization headers. Secrets can now be injected into
the job definition and used to authenticate downloads securely.

## SSH device

Device        | Description            | Machine     | CPU              |
--------------|------------------------|-------------|------------------|
ssh-device    | Device with ssh access | Any         | Any	        |
