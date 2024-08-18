# -*- coding: utf-8 -*-
#
# vim: set ts=4
#
# Copyright 2024-present Linaro Limited
#
# SPDX-License-Identifier: MIT

from tuxlava.tests import Test


class HackingSession(Test):
    devices = [
        "qemu-armv6",
        "qemu-armv7",
        "qemu-arm64",
        "qemu-i386",
        "qemu-x86_64",
        "fvp-aemva",
        "nfs-*",
        "fastboot-*",
    ]
    name = "hacking-session"
    timeout = 20
    need_test_definition = True

    def render(self, **kwargs):
        kwargs["name"] = self.name
        kwargs["timeout"] = self.timeout

        return self._render("hackingsession.yaml.jinja2", **kwargs)
