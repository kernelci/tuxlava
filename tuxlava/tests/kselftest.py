# -*- coding: utf-8 -*-
#
# vim: set ts=4
#
# Copyright 2024-present Linaro Limited
#
# SPDX-License-Identifier: MIT

from tuxlava.tests import Test


class KSelfTest(Test):
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
            self.cmdfile if self.cmdfile else self.name.replace("kselftest-", "")
        )

        if "CPUPOWER" in kwargs["parameters"]:
            kwargs["overlays"].insert(
                0, ("cpupower", kwargs["parameters"]["CPUPOWER"], "/")
            )
        if "KSELFTEST" in kwargs["parameters"]:
            kwargs["overlays"].insert(
                0,
                (
                    "kselftest",
                    kwargs["parameters"]["KSELFTEST"],
                    "/opt/kselftests/default-in-kernel/",
                ),
            )

        return self._render("kselftest.yaml.jinja2", **kwargs)


class KSelftestArm64(KSelfTest):
    devices = [
        "qemu-arm64",
        "fvp-aemva",
        "avh-imx93",
        "avh-rpi4b",
        "nfs-juno-r2",
        "nfs-bcm2711-rpi-4-b",
        "fastboot-dragonboard-410c",
        "fastboot-dragonboard-845c",
        "fastboot-e850-96",
    ]
    name = "kselftest-arm64"
    timeout = 45


class KSelftestBreakpoints(KSelfTest):
    devices = [
        "qemu-arm64",
        "fvp-aemva",
        "*-x86_64",
        "avh-imx93",
        "avh-rpi4b",
        "nfs-juno-r2",
        "nfs-bcm2711-rpi-4-b",
        "nfs-rk3399-rock-pi-4b",
        "fastboot-dragonboard-410c",
        "fastboot-dragonboard-845c",
        "fastboot-e850-96",
    ]
    name = "kselftest-breakpoints"
    timeout = 5


class KSelftestBPF(KSelfTest):
    name = "kselftest-bpf"
    timeout = 45


class KSelftestCapabilities(KSelfTest):
    name = "kselftest-capabilities"
    timeout = 5


class KSelftestCgroup(KSelfTest):
    name = "kselftest-cgroup"
    timeout = 5


class KSelftestClone3(KSelfTest):
    name = "kselftest-clone3"
    timeout = 5


class KSelftestCore(KSelfTest):
    name = "kselftest-core"
    timeout = 5


class KSelftestCpufreq(KSelfTest):
    name = "kselftest-cpufreq"
    timeout = 5


class KSelftestCpuHotplug(KSelfTest):
    name = "kselftest-cpu-hotplug"
    timeout = 5


class KSelftestDamon(KSelfTest):
    name = "kselftest-damon"
    timeout = 5


class KSelftestDma(KSelfTest):
    name = "kselftest-dma"
    timeout = 5


class KSelftestDmabufHeaps(KSelfTest):
    name = "kselftest-dmabuf-heaps"
    timeout = 5


class KSelftestDrivers(KSelfTest):
    name = "kselftest-drivers"
    timeout = 5


class KSelftestEfivarfs(KSelfTest):
    name = "kselftest-efivarfs"
    timeout = 5


class KSelftestExec(KSelfTest):
    name = "kselftest-exec"
    timeout = 5


class KSelftestFilesystems(KSelfTest):
    name = "kselftest-filesystems"
    timeout = 5


class KSelftestFirmware(KSelfTest):
    name = "kselftest-firmware"
    timeout = 5


class KSelftestFpu(KSelfTest):
    name = "kselftest-fpu"
    timeout = 5


class KSelftestFtrace(KSelfTest):
    name = "kselftest-ftrace"
    timeout = 5


class KSelftestFutex(KSelfTest):
    name = "kselftest-futex"
    timeout = 5


class KSelftestGpio(KSelfTest):
    name = "kselftest-gpio"
    timeout = 5


class KSelftestIa64(KSelfTest):
    name = "kselftest-ia64"
    timeout = 5


class KSelftestIntelPstate(KSelfTest):
    devices = ["*-x86_64", "*-i386"]
    name = "kselftest-intel_pstate"
    timeout = 5


class KSelftestIommu(KSelfTest):
    name = "kselftest-iommu"
    timeout = 5


class KSelftestIPC(KSelfTest):
    name = "kselftest-ipc"
    timeout = 5


class KSelftestIR(KSelfTest):
    name = "kselftest-ir"
    timeout = 5


class KSelftestKcmp(KSelfTest):
    name = "kselftest-kcmp"
    timeout = 5


class KSelftestKexec(KSelfTest):
    devices = ["*-x86_64", "*-i386", "qemu-ppc64le"]
    name = "kselftest-kexec"
    timeout = 5


class KSelftestKmod(KSelfTest):
    name = "kselftest-kmod"
    timeout = 5


class KSelftestKvm(KSelfTest):
    name = "kselftest-kvm"
    timeout = 15


class KSelftestLandlock(KSelfTest):
    name = "kselftest-landlock"
    timeout = 5


class KSelftestLib(KSelfTest):
    name = "kselftest-lib"
    timeout = 5


class KSelftestLivepatch(KSelfTest):
    devices = ["*-x86_64", "*-i386"]
    name = "kselftest-livepatch"
    timeout = 5


# Can't run this in LAVA since the intention is to trigger crashes.
# That will mean that LAVA will always end with a failure.
# class KSelftestLkdtm(KSelfTest):
#    name = "kselftest-lkdtm"
#    timeout = 5


class KSelftestLocking(KSelfTest):
    name = "kselftest-locking"
    timeout = 5


class KSelftestMembarrier(KSelfTest):
    name = "kselftest-membarrier"
    timeout = 5


class KSelftestMemfd(KSelfTest):
    name = "kselftest-memfd"
    timeout = 5


class KSelftestMm(KSelfTest):
    name = "kselftest-mm"
    timeout = 5


class KSelftestMemoryHotplug(KSelfTest):
    name = "kselftest-memory-hotplug"
    timeout = 5


class KSelftestMincore(KSelfTest):
    name = "kselftest-mincore"
    timeout = 5


class KSelftestMount(KSelfTest):
    name = "kselftest-mount"
    timeout = 5


class KSelftestMount_setattr(KSelfTest):
    name = "kselftest-mount_setattr"
    timeout = 5


class KSelftestMoveMountSetGroup(KSelfTest):
    name = "kselftest-move_mount_set_group"
    timeout = 5


class KSelftestMqueue(KSelfTest):
    name = "kselftest-mqueue"
    timeout = 5


class KSelftestNci(KSelfTest):
    name = "kselftest-nci"
    timeout = 5


class KSelftestNet(KSelfTest):
    name = "kselftest-net"
    timeout = 5


class KSelftestNetAf_unix(KSelfTest):
    name = "kselftest-net-af_unix"
    cmdfile = "net.af_unix"
    timeout = 5


class KSelftestNetForwarding(KSelfTest):
    name = "kselftest-net-forwarding"
    cmdfile = "net.forwarding"
    timeout = 10


class KSelftestNetHsr(KSelfTest):
    name = "kselftest-net-hsr"
    cmdfile = "net.hsr"
    timeout = 5


class KSelftestNetMptcp(KSelfTest):
    name = "kselftest-net-mptcp"
    cmdfile = "net.mptcp"
    timeout = 5


class KSelftestNetfilter(KSelfTest):
    name = "kselftest-netfilter"
    timeout = 5


class KSelftestNolibc(KSelfTest):
    name = "kselftest-nolibc"
    timeout = 5


class KSelftestNsfs(KSelfTest):
    name = "kselftest-nsfs"
    timeout = 5


class KSelftestNtb(KSelfTest):
    name = "kselftest-ntb"
    timeout = 5


class KSelftestOpenat2(KSelfTest):
    name = "kselftest-openat2"
    timeout = 5


class KSelftestPerfEvents(KSelfTest):
    name = "kselftest-perf_events"
    timeout = 5


class KSelftestPidfd(KSelfTest):
    name = "kselftest-pidfd"
    timeout = 5


class KSelftestPidNamespace(KSelfTest):
    name = "kselftest-pid_namespace"
    timeout = 5


class KSelftestPrctl(KSelfTest):
    name = "kselftest-prctl"
    timeout = 5


class KSelftestProc(KSelfTest):
    name = "kselftest-proc"
    timeout = 5


class KSelftestPstore(KSelfTest):
    name = "kselftest-pstore"
    timeout = 5


class KSelftestPtp(KSelfTest):
    name = "kselftest-ptp"
    timeout = 5


class KSelftestPtrace(KSelfTest):
    devices = ["*-x86_64", "*-i386"]
    name = "kselftest-ptrace"
    timeout = 5


class KSelftestRcutorture(KSelfTest):
    name = "kselftest-rcutorture"
    timeout = 5


class KSelftestResctrl(KSelfTest):
    name = "kselftest-resctrl"
    timeout = 5


class KSelftestRlimits(KSelfTest):
    name = "kselftest-rlimits"
    timeout = 5


class KSelftestRseq(KSelfTest):
    name = "kselftest-rseq"
    timeout = 5


class KSelftestRtc(KSelfTest):
    name = "kselftest-rtc"
    timeout = 5


class KSelftestRust(KSelfTest):
    name = "kselftest-rust"
    timeout = 5


class KSelftestSafesetid(KSelfTest):
    name = "kselftest-safesetid"
    timeout = 5


class KSelftestSched(KSelfTest):
    name = "kselftest-sched"
    timeout = 5


class KSelftestSeccomp(KSelfTest):
    name = "kselftest-seccomp"
    timeout = 5


class KSelftestSgx(KSelfTest):
    name = "kselftest-sgx"
    timeout = 5


class KSelftestSigaltstack(KSelfTest):
    name = "kselftest-sigaltstack"
    timeout = 5


class KSelftestSize(KSelfTest):
    name = "kselftest-size"
    timeout = 5


class KSelftestSplice(KSelfTest):
    name = "kselftest-splice"
    timeout = 5


class KSelftestStaticKeys(KSelfTest):
    name = "kselftest-static_keys"
    timeout = 5


class KSelftestSync(KSelfTest):
    name = "kselftest-sync"
    timeout = 5


class KSelftestSysctl(KSelfTest):
    name = "kselftest-sysctl"
    timeout = 5


class KSelftestTcTesting(KSelfTest):
    name = "kselftest-tc-testing"
    timeout = 5


class KSelftestTdx(KSelfTest):
    name = "kselftest-tdx"
    timeout = 5


class KSelftestTimens(KSelfTest):
    name = "kselftest-timens"
    timeout = 5


class KSelftestTimers(KSelfTest):
    name = "kselftest-timers"
    timeout = 5


class KSelftestTmpfs(KSelfTest):
    name = "kselftest-tmpfs"
    timeout = 5


class KSelftestTpm2(KSelfTest):
    name = "kselftest-tpm2"
    timeout = 5


class KSelftestUevent(KSelfTest):
    name = "kselftest-uevent"
    timeout = 5


class KSelftestUser(KSelfTest):
    name = "kselftest-user"
    timeout = 5


class KSelftestUserEvents(KSelfTest):
    name = "kselftest-user_events"
    timeout = 5


class KSelftestVDSO(KSelfTest):
    name = "kselftest-vDSO"
    timeout = 5


class KSelftestWatchdog(KSelfTest):
    name = "kselftest-watchdog"
    timeout = 5


class KSelftestX86(KSelfTest):
    devices = ["*-x86_64", "*-i386"]
    name = "kselftest-x86"
    timeout = 5


class KSelftestZram(KSelfTest):
    name = "kselftest-zram"
    timeout = 5
