# -*- coding: utf-8 -*-
#
# vim: set ts=4
#
# Copyright 2024-present Linaro Limited
#
# SPDX-License-Identifier: MIT

from typing import Dict, List, Optional

from tuxlava.exceptions import InvalidArgument
from tuxlava.tests import Test


class MorelloTest(Test):
    template = "morello.yaml.jinja2"
    test_def_name: Optional[str] = None
    parameters: List[str] = []
    optional_parameters: Dict[str, str] = {}

    def validate(self, device, parameters, **kwargs):
        for key, value in self.optional_parameters.items():
            if key not in parameters:
                parameters[key] = value

        super().validate(device=device, parameters=parameters, **kwargs)
        missing = set(self.parameters) - set(parameters.keys())
        if missing:
            raise InvalidArgument(f"Missing --parameters {', '.join(sorted(missing))}")

    def render(self, **kwargs):
        kwargs["name"] = self.name
        kwargs["timeout"] = self.timeout
        kwargs["test_def_name"] = (
            self.test_def_name if self.test_def_name else self.name
        )

        # remap some parameters
        MAPPINGS = {
            "BIONIC_TEST_TYPE": "TEST_TYPE",
            "LLDB_URL": "LLDB_TESTS_URL",
            "USERDATA": "USERDATA_URL",
        }
        for key, value in MAPPINGS.items():
            if key in kwargs["parameters"]:
                kwargs["parameters"][value] = kwargs["parameters"].pop(key)

        return self._render(self.template, **kwargs)


class MorelloAndroidTest(MorelloTest):
    devices = ["fvp-morello-android"]


class MorelloDebianPureCap(MorelloTest):
    devices = ["fvp-morello-debian"]
    template = "morello-debian-purecap.yaml.jinja2"
    name = "debian-purecap"
    timeout = 5


class MorelloGrubBusyBoxBootDT(MorelloTest):
    devices = ["fvp-morello-grub"]
    template = "morello-busybox-dt.yaml.jinja2"
    name = "boot-busybox-dt"
    timeout = 5


class MorelloGrubDebianBootDT(MorelloTest):
    devices = ["fvp-morello-grub"]
    template = "morello-debian-dt.yaml.jinja2"
    name = "boot-debian-dt"
    timeout = 5


class MorelloGrubBusyBoxBootACPI(MorelloTest):
    devices = ["fvp-morello-grub"]
    template = "morello-busybox-acpi.yaml.jinja2"
    name = "boot-busybox-acpi"
    timeout = 5


class MorelloGrubDebianBootACPI(MorelloTest):
    devices = ["fvp-morello-grub"]
    template = "morello-debian-acpi.yaml.jinja2"
    name = "boot-debian-acpi"
    timeout = 5


class MorelloBusyBoxPureCap(MorelloTest):
    devices = ["fvp-morello-busybox"]
    template = "morello-busybox-purecap.yaml.jinja2"
    name = "purecap"
    timeout = 5


class MorelloBusyBoxVirtioP9(MorelloTest):
    devices = ["fvp-morello-busybox"]
    template = "morello-busybox-virtio.yaml.jinja2"
    name = "virtiop9"
    timeout = 5


class MorelloSmc91x(MorelloTest):
    devices = ["fvp-morello-android", "fvp-morello-busybox"]
    name = "smc91x"
    template = "morello-smc91x.yaml.jinja2"
    timeout = 5


class MorelloVirtioNet(MorelloTest):
    devices = ["fvp-morello-android", "fvp-morello-busybox"]
    name = "virtio_net"
    template = "morello-virtio_net.yaml.jinja2"
    timeout = 5


class MorelloBinder(MorelloAndroidTest):
    name = "binder"
    timeout = 34


class MorelloBionic(MorelloAndroidTest):
    name = "bionic"
    timeout = 1000
    parameters = ["BIONIC_TEST_TYPE", "GTEST_FILTER"]
    optional_parameters = {
        "BIONIC_TEST_TYPE": "static",
        "GTEST_FILTER": "string_nofortify.*-string_nofortify.strlcat_overread:string_nofortify.bcopy:string_nofortify.memmove",
    }

    def validate(self, device, parameters, **kwargs):
        super().validate(device=device, parameters=parameters, **kwargs)

        if parameters.get("BIONIC_TEST_TYPE", "static") not in ["dynamic", "static"]:
            raise InvalidArgument("Invalid value for --parameters BIONIC_TEST_TYPE")

    def render(self, parameters, **kwargs):
        parameters["TEST_PATHS"] = "nativetest64 nativetestc64"
        return super().render(parameters=parameters, **kwargs)


class MorelloBoringSSL(MorelloAndroidTest):
    name = "boringssl"
    timeout = 240
    parameters = ["SYSTEM_URL"]


class MorelloCompartment(MorelloAndroidTest):
    name = "compartment"
    timeout = 15
    parameters = ["USERDATA"]
    test_def_name = "compartment-demo"


class MorelloDeviceTree(MorelloAndroidTest):
    name = "device-tree"
    timeout = 15


class MorelloDvfs(MorelloAndroidTest):
    name = "dvfs"
    timeout = 15


class MorelloLibPcre(MorelloAndroidTest):
    name = "libpcre"
    timeout = 60


class MorelloFWTS(MorelloTest):
    name = "fwts"
    timeout = 120
    devices = ["fvp-morello-oe"]
    template = "fwts.yaml.jinja2"
    need_test_definition = True


class MorelloLibJPEGTurbo(MorelloAndroidTest):
    name = "libjpeg-turbo"
    timeout = 30
    parameters = ["LIBJPEG_TURBO_URL", "SYSTEM_URL"]


class MorelloLibPNG(MorelloAndroidTest):
    name = "libpng"
    timeout = 30
    parameters = ["PNG_URL", "SYSTEM_URL"]


class MorelloLibPDFium(MorelloAndroidTest):
    name = "libpdfium"
    timeout = 30
    parameters = ["PDFIUM_URL", "SYSTEM_URL"]


class MorelloLLDB(MorelloAndroidTest):
    name = "lldb"
    timeout = 30
    parameters = ["LLDB_URL", "TC_URL"]


class MorelloAndroidBoot(MorelloAndroidTest):
    name = "boottest"
    timeout = 150


class MorelloLOGD(MorelloAndroidTest):
    name = "logd"
    timeout = 420
    parameters = ["USERDATA"]


class MorelloMulticore(MorelloAndroidTest):
    name = "multicore"
    timeout = 15
    test_def_name = "multicore-boot"


class Morellozlib(MorelloAndroidTest):
    name = "zlib"
    timeout = 30
    parameters = ["SYSTEM_URL"]
