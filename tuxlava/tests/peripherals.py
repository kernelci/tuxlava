# -*- coding: utf-8 -*-
#
# vim: set ts=4
#
# Copyright 2024-present Linaro Limited
#
# SPDX-License-Identifier: MIT

from tuxlava.tests import Test


class Peripherals(Test):
    devices = ["qemu-*", "fvp-aemva", "avh-imx93", "avh-rpi4b"]
    need_test_definition = True

    def render(self, **kwargs):
        kwargs["name"] = self.name
        kwargs["timeout"] = self.timeout
        return self._render("peripherals.yaml.jinja2", **kwargs)


class PeripheralsUSBGadgetFramwork(Peripherals):
    name = "usb-gadget-framwork"
    timeout = 10
