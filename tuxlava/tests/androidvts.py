# -*- coding: utf-8 -*-
#
# vim: set ts=4
#
# Copyright 2024-present Linaro Limited
#
# SPDX-License-Identifier: MIT

from tuxlava.exceptions import MissingArgument
from tuxlava.tests import Test


class AndroidVTS(Test):
    devices = [
        "fastboot-aosp-*",
    ]
    name: str = "android-vts"
    timeout = 480
    test_params: str = "vts"
    expects_reboot = "true"
    pkg_name: str = "android-vts.zip"
    test_path: str = "android-vts"

    def render(self, **kwargs):
        kwargs["name"] = self.name
        kwargs["timeout"] = self.timeout

        params = kwargs.get("parameters", {})
        if not params.get("TEST_VTS_URL"):
            raise MissingArgument("argument missing --parameters 'TEST_VTS_URL='...'")
        kwargs["test_url"] = params["TEST_VTS_URL"]
        kwargs["test_params"] = params.get("vts_test_params", self.test_params)
        kwargs["pkg_name"] = params.get("vts_pkg_name", self.pkg_name)
        kwargs["test_path"] = params.get("vts_test_path", self.test_path)
        kwargs["expect_reboot"] = params.get("vts_expects_reboot", self.expects_reboot)
        if params.get("SQUAD_URL"):
            kwargs["SQUAD_URL"] = params["SQUAD_URL"]
        kwargs["ANDROID_VERSION"] = params.get("ANDROID_VERSION", "master")

        return self._render("android-xts.yaml.jinja2", **kwargs)


class AndroidVTSKernelV7a(AndroidVTS):
    name = "android-vts-kernel-v7a"
    test_params = "vts-kernel --abi armeabi-v7a"


class AndroidVTSKernelV8a(AndroidVTS):
    name = "android-vts-kernel-v8a"
    test_params = "vts-kernel --abi arm64-v8a"
