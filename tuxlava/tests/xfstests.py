# -*- coding: utf-8 -*-
#
# vim: set ts=4
#
# Copyright 2024-present Linaro Limited
#
# SPDX-License-Identifier: MIT

from tuxlava.tests import Test


class XfsTests(Test):
    devices = [
        "qemu-arm64",
        "qemu-x86_64",
        "fvp-aemva",
        "nfs-*",
        "fastboot-*",
    ]
    configfile: str = ""
    timeout = 90
    need_test_definition = True

    def render(self, **kwargs):
        kwargs["name"] = self.name
        kwargs["test_filesystem"] = self.test_filesystem
        kwargs["timeout"] = self.timeout
        return self._render("xfstests.yaml.jinja2", **kwargs)


class XfsTestsBtrfs(XfsTests):
    name = "xfstests-btrfs"
    test_filesystem = "btrfs"


class XfsTestsExt4(XfsTests):
    name = "xfstests-ext4"
    test_filesystem = "ext4"


class XfsTestsF2fs(XfsTests):
    name = "xfstests-f2fs"
    test_filesystem = "f2fs"


class XfsTestsNilfs2(XfsTests):
    name = "xfstests-nilfs2"
    test_filesystem = "nilfs2"


class XfsTestsXfs(XfsTests):
    name = "xfstests-xfs"
    test_filesystem = "xfs"
