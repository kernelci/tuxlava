# -*- coding: utf-8 -*-
#
# vim: set ts=4
#
# Copyright 2024-present Linaro Limited
#
# SPDX-License-Identifier: MIT

from tuxlava.tests import Test


class LTPTest(Test):
    devices = [
        "qemu-*",
        "fvp-aemva",
        "avh-imx93",
        "avh-rpi4b",
        "nfs-*",
        "fastboot-*",
    ]
    cmdfile: str = ""
    need_test_definition = True

    def render(self, **kwargs):
        kwargs["name"] = self.name
        kwargs["timeout"] = self.timeout
        kwargs["cmdfile"] = (
            self.cmdfile if self.cmdfile else self.name.replace("ltp-", "")
        )

        return self._render("ltp.yaml.jinja2", **kwargs)


class LTPCapBounds(LTPTest):
    name = "ltp-cap_bounds"
    timeout = 2


class LTPCapability(LTPTest):
    name = "ltp-capability"
    timeout = 2


class LTPCommands(LTPTest):
    name = "ltp-commands"
    timeout = 10


class LTPContainers(LTPTest):
    name = "ltp-containers"
    timeout = 5


class LTPController(LTPTest):
    name = "ltp-controllers"
    timeout = 90


class LTPCPUHotPlug(LTPTest):
    name = "ltp-cpuhotplug"
    timeout = 15


class LTPCrypto(LTPTest):
    name = "ltp-crypto"
    timeout = 10


class LTPCVE(LTPTest):
    name = "ltp-cve"
    timeout = 60


class LTPDIO(LTPTest):
    name = "ltp-dio"
    timeout = 2


class LTPFcntlLockTests(LTPTest):
    name = "ltp-fcntl-locktests"
    timeout = 5


class LTPFileCaps(LTPTest):
    name = "ltp-filecaps"
    timeout = 5


class LTPFSBind(LTPTest):
    name = "ltp-fs_bind"
    timeout = 25


class LTPFSPermsSimple(LTPTest):
    name = "ltp-fs_perms_simple"
    timeout = 5


class LTPFSX(LTPTest):
    name = "ltp-fsx"
    timeout = 1


class LTPFS(LTPTest):
    name = "ltp-fs"
    timeout = 45


class LTPHugetlb(LTPTest):
    name = "ltp-hugetlb"
    timeout = 2


class LTPIO(LTPTest):
    name = "ltp-io"
    timeout = 2


class LTPIPC(LTPTest):
    name = "ltp-ipc"
    timeout = 5


class LTPMath(LTPTest):
    name = "ltp-math"
    timeout = 2


class LTPMM(LTPTest):
    name = "ltp-mm"
    timeout = 20


class LTPNPTL(LTPTest):
    name = "ltp-nptl"
    timeout = 15


class LTPPTY(LTPTest):
    name = "ltp-pty"
    timeout = 10


class LTPSched(LTPTest):
    name = "ltp-sched"
    timeout = 10


class LTPSecurebits(LTPTest):
    name = "ltp-securebits"
    timeout = 2


class LTPSmoke(LTPTest):
    name = "ltp-smoke"
    cmdfile = "smoketest"
    timeout = 2


class LTPSyscalls(LTPTest):
    name = "ltp-syscalls"
    timeout = 60


class LTPTracing(LTPTest):
    name = "ltp-tracing"
    timeout = 2
