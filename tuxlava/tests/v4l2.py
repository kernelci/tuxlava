# -*- coding: utf-8 -*-
#
# vim: set ts=4
#
# Copyright 2024-present Linaro Limited
#
# SPDX-License-Identifier: MIT

from tuxlava.tests import Test


class V4L2(Test):
    devices = [
        "qemu-*",
        "fvp-aemva",
        "avh-imx93",
        "avh-rpi4b",
        "nfs-*",
        "fastboot-*",
    ]
    name = "v4l2"
    timeout = 25
    need_test_definition = True

    def render(self, **kwargs):
        kwargs["name"] = self.name
        kwargs["timeout"] = self.timeout

        return self._render("v4l2.yaml.jinja2", **kwargs)
