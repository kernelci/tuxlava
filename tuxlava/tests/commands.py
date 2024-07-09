# -*- coding: utf-8 -*-
#
# vim: set ts=4
#
# Copyright 2024-present Linaro Limited
#
# SPDX-License-Identifier: MIT

from tuxlava.tests import Test


class Commands(Test):
    devices = [
        "qemu-*",
        "fvp-aemva",
        "avh-imx93",
        "avh-rpi4b",
        "nfs-*",
        "fastboot-*",
    ]
    name = "commands"
    timeout = 2

    def render(self, **kwargs):
        kwargs["name"] = self.name
        kwargs["timeout"] = self.timeout

        return self._render("commands.yaml.jinja2", **kwargs)
