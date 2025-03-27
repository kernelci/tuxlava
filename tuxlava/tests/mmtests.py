# -*- coding: utf-8 -*-
#
# vim: set ts=4
#
# Copyright 2024-present Linaro Limited
#
# SPDX-License-Identifier: MIT

from tuxlava.tests import Test


class MMTests(Test):
    devices = [
        "qemu-arm64",
        "qemu-x86_64",
        "avh-imx93",
        "avh-rpi4b",
        "nfs-*",
        "fastboot-*",
    ]
    configfile: str = ""
    full_archive: bool = False
    iterations: int = 10
    timeout = 90
    need_test_definition = True

    def render(self, **kwargs):
        kwargs["name"] = self.name
        kwargs["configfile"] = self.configfile
        kwargs["full_archive"] = self.full_archive
        kwargs["iterations"] = self.iterations
        kwargs["timeout"] = self.timeout
        return self._render("mmtests.yaml.jinja2", **kwargs)


class MMTestsDbSqliteInsertSmall(MMTests):
    configfile = "configs/config-db-sqlite-insert-small"
    name = "mmtests-db-sqlite-insert-small"


class MMTestsHpcScimarkcSmall(MMTests):
    configfile = "configs/config-hpc-scimarkc-small"
    name = "mmtests-hpc-scimarkc-small"
    iterations = 20


class MMTestsBlogbench(MMTests):
    configfile = "configs/config-io-blogbench"
    name = "mmtests-io-blogbench"
    iterations = 30


class MMTestsFioRandreadAsyncRandwrite(MMTests):
    configfile = "configs/config-io-fio-randread-async-randwrite"
    name = "mmtests-io-fio-randread-async-randwrite"


class MMTestsFioRandreadAsyncSeqwrite(MMTests):
    configfile = "configs/config-io-fio-randread-async-seqwrite"
    name = "mmtests-io-fio-randread-async-seqwrite"


class MMTestsFioRandreadSyncHeavywrite(MMTests):
    configfile = "configs/config-io-fio-randread-sync-heavywrite"
    name = "mmtests-io-fio-randread-sync-heavywrite"


class MMTestsFioRandreadSyncRandwrite(MMTests):
    configfile = "configs/config-io-fio-randread-sync-randwrite"
    name = "mmtests-io-fio-randread-sync-randwrite"


class MMTestsFsmarkSmallFileStream(MMTests):
    configfile = "configs/config-io-fsmark-small-file-stream"
    name = "mmtests-io-fsmark-small-file-stream"


class MMTestsRedisBenchmarkSmall(MMTests):
    configfile = "configs/config-memdb-redis-benchmark-small"
    name = "mmtests-memdb-redis-benchmark-small"
    iterations = 20


class MMTestsRedisMemtierSmall(MMTests):
    configfile = "configs/config-memdb-redis-memtier-small"
    name = "mmtests-memdb-redis-memtier-small"
    iterations = 20


class MMTestsSchbench(MMTests):
    configfile = "configs/config-scheduler-schbench"
    name = "mmtests-scheduler-schbench"


class MMTestsSysbenchCpu(MMTests):
    configfile = "configs/config-scheduler-sysbench-cpu"
    name = "mmtests-scheduler-sysbench-cpu"


class MMTestsSysbenchThread(MMTests):
    configfile = "configs/config-scheduler-sysbench-thread"
    name = "mmtests-scheduler-sysbench-thread"


class MMTestsAim9Disk(MMTests):
    configfile = "configs/config-workload-aim9-disk"
    name = "mmtests-workload-aim9-disk"


class MMTestsCoremark(MMTests):
    configfile = "configs/config-workload-coremark"
    name = "mmtests-workload-coremark"
    iterations = 20


class MMTestsCyclictestFineHackbench(MMTests):
    configfile = "configs/config-workload-cyclictest-fine-hackbench"
    name = "mmtests-workload-cyclictest-fine-hackbench"
    iterations = 15


class MMTestsCyclictestHackbench(MMTests):
    configfile = "configs/config-workload-cyclictest-hackbench"
    name = "mmtests-workload-cyclictest-hackbench"
    iterations = 20


class MMTestsEbizzy(MMTests):
    configfile = "configs/config-workload-ebizzy"
    name = "mmtests-workload-ebizzy"


class MMTestsPmqtestHackbench(MMTests):
    configfile = "configs/config-workload-pmqtest-hackbench"
    name = "mmtests-workload-pmqtest-hackbench"


class MMTestsStressngAfAlg(MMTests):
    configfile = "configs/config-workload-stressng-af-alg"
    name = "mmtests-workload-stressng-af-alg"


class MMTestsStressngBadAltstack(MMTests):
    configfile = "configs/config-workload-stressng-bad-altstack"
    name = "mmtests-workload-stressng-bad-altstack"


class MMTestsStressngClassIoParallel(MMTests):
    configfile = "configs/config-workload-stressng-class-io-parallel"
    name = "mmtests-workload-stressng-class-io-parallel"


class MMTestsStressngContext(MMTests):
    configfile = "configs/config-workload-stressng-context"
    name = "mmtests-workload-stressng-context"


class MMTestsStressngFork(MMTests):
    configfile = "configs/config-workload-stressng-fork"
    name = "mmtests-workload-stressng-fork"


class MMTestsStressngGet(MMTests):
    configfile = "configs/config-workload-stressng-get"
    name = "mmtests-workload-stressng-get"


class MMTestsStressngGetdent(MMTests):
    configfile = "configs/config-workload-stressng-getdent"
    name = "mmtests-workload-stressng-getdent"


class MMTestsStressngMadvise(MMTests):
    configfile = "configs/config-workload-stressng-madvise"
    name = "mmtests-workload-stressng-madvise"


class MMTestsStressngMmap(MMTests):
    configfile = "configs/config-workload-stressng-mmap"
    name = "mmtests-workload-stressng-mmap"


class MMTestsStressngVmSplice(MMTests):
    configfile = "configs/config-workload-stressng-vm-splice"
    name = "mmtests-workload-stressng-vm-splice"


class MMTestsStressngZombie(MMTests):
    configfile = "configs/config-workload-stressng-zombie"
    name = "mmtests-workload-stressng-zombie"


class MMTestsUnixBench(MMTests):
    configfile = "configs/config-workload-unixbench"
    name = "mmtests-workload-unixbench"


class MMTestsUsemem(MMTests):
    configfile = "configs/config-workload-usemem"
    name = "mmtests-workload-usemem"


class MMTestsScaleIoProcesses(MMTests):
    configfile = "configs/config-workload-will-it-scale-io-processes"
    name = "mmtests-workload-will-it-scale-io-processes"


class MMTestsScaleIoThreads(MMTests):
    configfile = "configs/config-workload-will-it-scale-io-threads"
    name = "mmtests-workload-will-it-scale-io-threads"


class MMTestsScalePfProcesses(MMTests):
    configfile = "configs/config-workload-will-it-scale-pf-processes"
    name = "mmtests-workload-will-it-scale-pf-processes"


class MMTestsScalePfThreads(MMTests):
    configfile = "configs/config-workload-will-it-scale-pf-threads"
    name = "mmtests-workload-will-it-scale-pf-threads"


class MMTestsScaleSysProcesses(MMTests):
    configfile = "configs/config-workload-will-it-scale-sys-processes"
    name = "mmtests-workload-will-it-scale-sys-processes"


class MMTestsScaleSysThreads(MMTests):
    configfile = "configs/config-workload-will-it-scale-sys-threads"
    name = "mmtests-workload-will-it-scale-sys-threads"
