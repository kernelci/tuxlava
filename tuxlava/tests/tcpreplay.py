# -*- coding: utf-8 -*-
#
# vim: set ts=4
#
# Copyright 2025-present Linaro Limited
#
# SPDX-License-Identifier: MIT

from tuxlava.tests import Test


class TCPReplay(Test):
    devices = [
        "qemu-*",
        "fvp-aemva",
        "avh-imx93",
        "avh-rpi4b",
        "nfs-*",
        "fastboot-*",
    ]
    name = "tcpreplay"
    timeout: int = 7

    def render(self, **kwargs):
        kwargs["name"] = self.name
        kwargs["timeout"] = self.timeout

        return self._render("tcpreplay.yaml.jinja2", **kwargs)
