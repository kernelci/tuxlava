# Devices

TuxLAVA supports the following virtual devices.

* AVH
* Fastboot
* FVP
* NFS
* QEMU
* SSH
* USBG

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
fastboot-gs101-oriole           |
fastboot-oe-dragonboard-845c    |
fastboot-qrb5165-rb5            |
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
nfs-am57xx-beagle-x15  |
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

## USBG devices

Device                 |
-----------------------|
usbg-bcm2711-rpi-4-b   |

The usbg devices boot a whole disk image that the dispatcher
exports as USB mass storage. The board boots from it as if a USB
disk was plugged in.

The board boots from `--firmware`, and `--os` is merged into it
by a default `script` download. For example:

```shell
tuxlava -d usbg-bcm2711-rpi-4-b \
  --firmware https://example.com/firmware.wic.xz \
  --os https://example.com/os.wic.xz
```

Anything else the job needs goes in with `--downloads`, once
per file. Use it for files a test reads on the dispatcher.

Every one of them takes an optional file name after the URL.
Some URLs have no file name in the path. A redirect endpoint
saves every file as `download`, so they overwrite each other
and we cannot see the compression either. Say the name and
both problems go away:

```shell
tuxlava -d usbg-bcm2711-rpi-4-b \
  --firmware "https://example.com/download?id=A" firmware.wic.xz \
  --os "https://example.com/download?id=B" os.wic.xz \
  --downloads "https://example.com/download?id=C" packages.tar.gz
```

The compression comes from that name, so LAVA unpacks the file
during the download and it lands as `packages.tar`. A name with
no known suffix is left as it is.

A `--downloads` file is named after its file name, so
`packages.tar.gz` becomes `packages` in the job. Everything
lands in one directory, so two files that end up with the same
name is an error.

These devices retry failed downloads three times. LAVA
divides the deploy timeout by the number of tries, so
`--timeouts deploy=45` gives 15 minutes per try, not 45. Keep
that in mind when you raise it.
