# -*- coding: utf-8 -*-
#
# vim: set ts=4
#
# Copyright 2024-present Linaro Limited
#
# SPDX-License-Identifier: MIT

from typing import Dict, List

from tuxlava.exceptions import InvalidArgument


def subclasses(cls):
    return set(cls.__subclasses__()).union(
        [s for c in cls.__subclasses__() for s in subclasses(c)]
    )


class Device:
    name: str = ""
    flag_use_pre_run_cmd: bool = False
    flag_cache_rootfs: bool = False
    reboot_to_fastboot: str = "false"
    redirect_to_kmsg: bool = True
    real_device: bool = True

    @classmethod
    def select(cls, name):
        for subclass in subclasses(cls):
            if subclass.name == name:
                return subclass
        raise InvalidArgument(
            f"Unknown device {name}. Available: {', '.join([c.name for c in cls.list()])}"
        )

    @classmethod
    def list(cls, virtual_device=False) -> List["Device"]:
        if virtual_device:
            return sorted(
                [s for s in subclasses(cls) if s.name and not s.real_device],
                key=lambda d: d.name,
            )
        return sorted([s for s in subclasses(cls) if s.name], key=lambda d: d.name)

    def validate(self, **kwargs):
        raise NotImplementedError  # pragma: no cover

    def default(self, options) -> None:
        raise NotImplementedError  # pragma: no cover

    def definition(self, **kwargs) -> str:
        raise NotImplementedError  # pragma: no cover

    def device_dict(self, context: Dict) -> str:
        raise NotImplementedError  # pragma: no cover

    def extra_assets(self, tmpdir, **kwargs) -> List[str]:
        return []


import tuxlava.devices.avh  # noqa: E402
import tuxlava.devices.fastboot  # noqa: E402
import tuxlava.devices.fvp  # noqa: E402
import tuxlava.devices.nfs  # noqa: E402,F401
import tuxlava.devices.qemu  # noqa: E402,F401
import tuxlava.devices.ssh  # noqa: E402,F401
