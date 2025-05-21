<div align="center">
  <img src="https://gitlab.com/Linaro/tuxlava/raw/main/tuxlava_logo.png" alt="TuxLAVA Logo" width="40%" />
</div>

[![Pipeline Status](https://gitlab.com/Linaro/tuxlava/badges/main/pipeline.svg)](https://gitlab.com/Linaro/tuxlava/pipelines)
[![coverage report](https://gitlab.com/Linaro/tuxlava/badges/main/coverage.svg)](https://gitlab.com/Linaro/tuxlava/commits/main)
[![PyPI version](https://badge.fury.io/py/tuxlava.svg)](https://pypi.org/project/tuxlava/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![PyPI - License](https://img.shields.io/pypi/l/tuxlava)](https://gitlab.com/Linaro/tuxlava/blob/main/LICENSE)

[Documentation](https://tuxlava.org/) - [Repository](https://gitlab.com/Linaro/tuxlava) - [Issues](https://gitlab.com/Linaro/tuxlava/-/issues)

TuxLAVA is a command-line tool and Python library that simplifies
creating LAVA job definitions for various device types. Developed by
Linaro, it's part of TuxSuite and streamlines Linux kernel test
automation.

* AVH
* FASTBOOT
* FVP
* NFS
* QEMU
* SSH

TuxLAVA is a part of [TuxSuite](https://tuxsuite.com), a suite of
tools and services to help with Linux kernel development.

[[_TOC_]]

# Installing TuxLAVA

- [From PyPI](docs/install-pypi.md)
- [Debian packages](docs/install-deb.md)
- [RPM packages](docs/install-rpm.md)
- [Run uninstalled](docs/run-uninstalled.md)

# Examples

LAVA job to boot test a mipsel kernel at https://url/to/vmlinux:

```shell
tuxlava --device qemu-mips32el \
    --kernel https://url/to/vmlinux
```

Generate a LAVA job with *ltp-smoke* test:

```shell
tuxlava --device qemu-mips32el \
    --kernel https://url/to/vmlinux \
    --test ltp-smoke
```

# Using TuxLAVA as a command line

Call tuxlava as follows:

```shell
tuxlava --device nfs-x86_64 \
    --kernel https://url/to/Image \
    --modules https://url/to/modules /usr/ \
    --rootfs https://url/to/rootfs \
    --tests boot
```

> The `--kernel`, `--modules`, and `--rootfs` arguments can be URLs
(e.g. `https://...`), file URLs (e.g. `file:///...`), or absolute
file paths (e.g. `/path/to/Image`).

TuxLAVA will output the LAVA job to the stdout with the provided
arguments for x86_64 device

The complete list of tuxlava options is available with the following
command:

```shell
tuxlava --help
```

# Using TuxLAVA as a library

TuxLAVA can be used as a python library as follows:

```shell
#!/usr/bin/env python

from tuxlava.jobs import Job

job = Job(
    device="nfs-x86_64",
    kernel="https://url/to/bzImage",
    rootfs="https://url/to/rootfs.tar.xz",
    tests=["ltp-smoke", "ltp-math"],
    modules="https://url/to/modules.tar.xz",
    parameters={"LAVA_JOB_PRIORITY": 50},
    timeouts={"deploy": 20},
)
job.initialize()
print(job.render())
```

## Contributing

Contributions, bug reports and feature requests are welcome!
Please see the [issues](https://gitlab.com/Linaro/tuxlava/-/issues)
or open a [merge request](https://gitlab.com/Linaro/tuxlava/-/merge_requests).
