# -*- coding: utf-8 -*-
#
# vim: set ts=4
#
# Copyright 2024-present Linaro Limited
#
# SPDX-License-Identifier: MIT

from tuxlava.tests import Test


class Peripherals(Test):
    devices = ["qemu-*", "fvp-aemva", "avh-imx93", "avh-rpi4b", "fastboot-*"]
    need_test_definition = True
    branch = "master"

    def render(self, **kwargs):
        kwargs["name"] = self.name
        kwargs["timeout"] = self.timeout
        kwargs["branch"] = self.branch
        return self._render("peripherals.yaml.jinja2", **kwargs)


class PeripheralsUSBGadgetFramework(Peripherals):
    name = "usb-gadget-framework"
    timeout = 10


class PeripheralsysfsFramework(Peripherals):
    name = "sysfs-interface-framework"
    timeout = 10
    branch = "interface"
