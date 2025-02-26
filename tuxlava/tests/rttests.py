# vim: set ts=4
#
# Copyright 2025-present Linaro Limited
#
# SPDX-License-Identifier: MIT

from tuxlava.tests import Test


class RTTests(Test):
    devices = [
        "qemu-*",
        "fvp-aemva",
        "avh-imx93",
        "avh-rpi4b",
        "nfs-*",
        "fastboot-*",
    ]
    bgcmd: str = ""
    duration: str = ""
    iterations:int = 2
    subtest: str = ""
    timeout:int = 10
    need_test_definition = True

    def render(self, **kwargs):
        kwargs["name"] = self.name
        kwargs["bgcmd"] = self.bgcmd
        kwargs["duration"] = self.duration
        kwargs["iterations"] = self.iterations
        kwargs["subtest"] = self.subtest
        kwargs["timeout"] = self.timeout
        return self._render("rt-tests.yaml.jinja2", **kwargs)

class RTTestsPmqtest(RTTests):
    name = "rt-tests-pmqtest"
    duration = "2m"
    subtest = name.replace("rt-tests-", "")

