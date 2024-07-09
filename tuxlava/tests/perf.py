# -*- coding: utf-8 -*-
#
# vim: set ts=4
#
# Copyright 2024-present Linaro Limited
#
# SPDX-License-Identifier: MIT

from tuxlava.tests import Test


class Perf(Test):
    devices = [
        "qemu-*",
        "fvp-aemva",
        "avh-imx93",
        "avh-rpi4b",
        "nfs-*",
        "fastboot-*",
    ]
    name = "perf"
    timeout = 30
    need_test_definition = True

    def render(self, **kwargs):
        kwargs["name"] = self.name
        kwargs["timeout"] = self.timeout

        if "PERF" in kwargs["parameters"]:
            kwargs["overlays"].insert(
                0,
                (
                    "perf",
                    kwargs["parameters"]["PERF"],
                    "/",
                ),
            )

        return self._render("perf.yaml.jinja2", **kwargs)
