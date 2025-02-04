<div align="center">
  <img src="tuxlava_full.svg" alt="TuxLAVA Logo" width="40%" />
</div>

[![Pipeline Status](https://gitlab.com/Linaro/tuxlava/badges/main/pipeline.svg)](https://gitlab.com/Linaro/tuxlava/pipelines)
[![coverage report](https://gitlab.com/Linaro/tuxlava/badges/main/coverage.svg)](https://gitlab.com/Linaro/tuxlava/commits/main)
[![PyPI version](https://badge.fury.io/py/tuxlava.svg)](https://pypi.org/project/tuxlava/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![PyPI - License](https://img.shields.io/pypi/l/tuxlava)](https://gitlab.com/Linaro/tuxlava/blob/main/LICENSE)

[Documentation](https://tuxlava.org/) - [Repository](https://gitlab.com/Linaro/tuxlava) - [Issues](https://gitlab.com/Linaro/tuxlava/-/issues)

TuxLAVA, by [Linaro](https://www.linaro.org/), is a python library and
a command line tool to generate Linaro Automated Validation
Architecture a.k.a [LAVA](https://www.lavasoftware.org/) jobs for
devices of the following type and has a standard list of devices that
are supported along with tests that could be run on these devices.

* AVH
* FASTBOOT
* FVP
* NFS
* QEMU
* SSH

TuxLAVA is a part of [TuxSuite](https://tuxsuite.com), a suite of
tools and services to help with Linux kernel development.


# Installing TuxLAVA

- [From PyPI](install-pypi.md)
- [Debian packages](install-deb.md)
- [RPM packages](install-rpm.md)
- [Run uninstalled](run-uninstalled.md)

# Using TuxLAVA as a library

TuxLAVA can be used as a python library as follows:

```shell
#!/usr/bin/env python

from tuxlava.jobs import Job

job = Job(
    device="nfs-x86_64",
    kernel="https://example.com/bzImage",
    rootfs="https://example.com/rootfs.tar.xz",
    tests=["ltp-smoke", "ltp-math"],
    modules="https://example.com/modules.tar.xz",
    parameters={"LAVA_JOB_PRIORITY": 50},
    timeouts={"deploy": 20},
)
job.initialize()
print(job.render())
```

# Using TuxLAVA as a command line

Call tuxlava as follows:

```shell
tuxlava --device nfs-x86_64 \
    --kernel /path/or/url/to/Image
    --modules /path/or/url/to/modules /usr/ \
    --rootfs /path/or/url/to/rootfs \
    --tests boot
```

TuxLAVA will output the LAVA job to the stdout with the provided
arguments for x86_64 device

The complete list of tuxlava options is available with the following
command:

```shell
tuxlava --help
```

# Examples

LAVA job to boot test a mipsel kernel at https://mykernel.org/vmlinux:

```shell
tuxlava --device qemu-mips32el \
    --kernel https://mykernel.org/vmlinux
```

Generate a LAVA job with *ltp-smoke* test:

```shell
tuxlava --device qemu-mips32el \
    --kernel https://mykernel.org/vmlinux \
    --test ltp-smoke
```
