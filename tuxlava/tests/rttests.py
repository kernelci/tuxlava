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
    duration: str = "5m"
    iterations: int = 1
    subtest: str = ""
    timeout: int = 7
    need_test_definition = True

    def render(self, **kwargs):
        kwargs["name"] = self.name
        kwargs["bgcmd"] = self.bgcmd
        kwargs["duration"] = self.duration
        kwargs["iterations"] = self.iterations
        kwargs["subtest"] = self.name.replace("rt-tests-", "")
        kwargs["timeout"] = self.timeout
        return self._render("rt-tests.yaml.jinja2", **kwargs)


class RTTestsCyclicDeadline(RTTests):
    name = "rt-tests-cyclicdeadline"


class RTTestsPiStress(RTTests):
    name = "rt-tests-pi-stress"


class RTTestsPmqtest(RTTests):
    name = "rt-tests-pmqtest"


class RTTestsRtMigrateTest(RTTests):
    name = "rt-tests-rt-migrate-test"


class RTTestsSignalTest(RTTests):
    name = "rt-tests-signaltest"
