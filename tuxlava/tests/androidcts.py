# -*- coding: utf-8 -*-
#
# vim: set ts=4
#
# Copyright 2024-present Linaro Limited
#
# SPDX-License-Identifier: MIT

from tuxlava.exceptions import MissingArgument
from tuxlava.tests import Test


class AndroidCTS(Test):
    devices = [
        "fastboot-aosp-*",
    ]
    name: str = "android-cts"
    timeout = 480
    test_params: str = "cts"
    expects_reboot = "false"
    pkg_name: str = "android-cts.zip"
    test_path: str = "android-cts"

    def render(self, **kwargs):
        kwargs["name"] = self.name
        kwargs["timeout"] = self.timeout

        params = kwargs.get("parameters", {})
        if not params.get("TEST_CTS_URL"):
            raise MissingArgument("argument missing --parameters 'TEST_CTS_URL='...'")
        kwargs["test_url"] = params["TEST_CTS_URL"]
        kwargs["test_params"] = params.get("cts_test_params", self.test_params)
        kwargs["pkg_name"] = params.get("cts_pkg_name", self.pkg_name)
        kwargs["test_path"] = params.get("cts_test_path", self.test_path)
        kwargs["expect_reboot"] = params.get("cts_expects_reboot", self.expects_reboot)
        if params.get("SQUAD_URL"):
            kwargs["SQUAD_URL"] = params["SQUAD_URL"]
        kwargs["ANDROID_VERSION"] = params.get("ANDROID_VERSION", "master")

        return self._render("android-xts.yaml.jinja2", **kwargs)
