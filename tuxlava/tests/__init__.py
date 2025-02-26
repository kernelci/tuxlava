# -*- coding: utf-8 -*-
#
# vim: set ts=4
#
# Copyright 2024-present Linaro Limited
#
# SPDX-License-Identifier: MIT

import fnmatch
from typing import List

from tuxlava import templates
from tuxlava.devices import Device
from tuxlava.exceptions import InvalidArgument


def subclasses(cls):
    return set(cls.__subclasses__()).union(
        [s for c in cls.__subclasses__() for s in subclasses(c)]
    )


def is_test_supported(test, devices):
    # checks if the given test is available/supported for any device in devices list
    for d in devices:
        for pat in test.devices:
            if fnmatch.fnmatch(d.name, pat):
                return True

    return False


class Test:
    devices: List[str] = []
    name: str = ""
    timeout: int = 0
    need_test_definition: bool = False

    def __init__(self, timeout):
        if timeout:
            self.timeout = timeout

    @classmethod
    def select(cls, name):
        for subclass in subclasses(cls):
            if subclass.name == name:
                return subclass
        raise InvalidArgument(f"Unknown test {name}")

    @classmethod
    def list(cls, device=None, virtual_device=False):
        if virtual_device:
            virtual_devices = Device.list(virtual_device=True)
            return sorted(
                t.name
                for t in subclasses(cls)
                if t.name and is_test_supported(t, virtual_devices)
            )
        if device is None:
            return sorted(s.name for s in subclasses(cls) if s.name)
        return sorted(
            t.name
            for t in subclasses(cls)
            if t.name and any([fnmatch.fnmatch(device, pat) for pat in t.devices])
        )

    def validate(self, device, **kwargs):
        if not any([fnmatch.fnmatch(device.name, pat) for pat in self.devices]):
            raise InvalidArgument(
                f"Test '{self.name}' not supported on device '{device.name}'"
            )

    def _render(self, filename, **kwargs):
        return templates.tests().get_template(filename).render(**kwargs)


import tuxlava.tests.commands  # noqa: E402
import tuxlava.tests.hackingsession  # noqa: E402
import tuxlava.tests.kselftest  # noqa: E402
import tuxlava.tests.kunit  # noqa: E402
import tuxlava.tests.kvmunittests  # noqa: E402
import tuxlava.tests.libgpiod  # noqa: E402
import tuxlava.tests.libhugetlbfs  # noqa: E402
import tuxlava.tests.ltp  # noqa: E402
import tuxlava.tests.mmtests  # noqa: E402,F401
import tuxlava.tests.modules  # noqa: E402,F401
import tuxlava.tests.morello  # noqa: E402,F401
import tuxlava.tests.network  # noqa: E402,F401
import tuxlava.tests.perf  # noqa: E402,F401
import tuxlava.tests.peripherals  # noqa: E402,F401
import tuxlava.tests.rcutorture  # noqa: E402,F401
import tuxlava.tests.rttests  # noqa: E402,F401
import tuxlava.tests.systemdanalyze  # noqa: E402,F401
import tuxlava.tests.tfatests  # noqa: E402,F401
import tuxlava.tests.v4l2  # noqa: E402,F401
import tuxlava.tests.vdso  # noqa: E402,F401
import tuxlava.tests.xfstests  # noqa: E402,F401
import tuxlava.tests.androidcts  # noqa: E402,F401
import tuxlava.tests.androidvts  # noqa: E402,F401
