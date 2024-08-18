# -*- coding: utf-8 -*-
#
# vim: set ts=4
#
# Copyright 2024-present Linaro Limited
#
# SPDX-License-Identifier: MIT

from tuxlava.tests import Test


class TFATests(Test):
    devices = ["qemu-arm64"]
    name = "tfa-tests"
    timeout = 30

    def render(self, **kwargs):
        kwargs["name"] = self.name
        kwargs["timeout"] = self.timeout

        return self._render("tfa-tests.yaml.jinja2", **kwargs)
