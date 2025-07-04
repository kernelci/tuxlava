# -*- coding: utf-8 -*-
#
# vim: set ts=4
#
# Copyright (c) 2025-present Qualcomm Technologies, Inc. and/or its subsidiaries.
#
# SPDX-License-Identifier: MIT

from tuxlava.tests import Test


class WiFiTest(Test):
    devices = [
        "fastboot-*",
        "flasher-*",
    ]
    need_test_definition = True

    def render(self, **kwargs):
        kwargs["name"] = self.name
        kwargs["timeout"] = self.timeout
        return self._render("wifi.yaml.jinja2", **kwargs)


class WiFiBasic(WiFiTest):
    name = "wifi"
    timeout = 10
