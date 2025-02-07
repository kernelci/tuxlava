#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# vim: set ts=4
#
# Copyright 2024-present Linaro Limited
#
# SPDX-License-Identifier: MIT

import logging
import sys

from tuxlava.jobs import Job
from tuxlava.exceptions import TuxLavaException
from tuxlava.argparse import setup_parser


LOG = logging.getLogger("tuxlava")


def main() -> int:
    # Parse command line
    parser = setup_parser()
    options = parser.parse_args()

    # Setup logging
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter("%(message)s"))
    LOG.addHandler(handler)
    LOG.setLevel(logging.DEBUG if options.debug else logging.INFO)

    if not options.device:
        if not (options.tuxmake or options.tuxbuild):
            parser.error("argument --device is required")

    if "hacking-session" in options.tests:
        options.enable_network = True
        if not options.parameters.get("PUB_KEY"):
            parser.error("argument missing --parameters PUB_KEY='...'")

    try:
        job = Job(
            device=options.device,
            bios=options.bios,
            bl1=options.bl1,
            commands=options.commands,
            dtb=options.dtb,
            kernel=options.kernel,
            boot=options.boot,
            ap_romfw=options.ap_romfw,
            mcp_fw=options.mcp_fw,
            mcp_romfw=options.mcp_romfw,
            fip=options.fip,
            enable_kvm=options.enable_kvm,
            enable_trustzone=options.enable_trustzone,
            enable_network=options.enable_network,
            qemu_image=options.qemu_image,
            qemu_binary=options.qemu_binary,
            prompt=options.prompt,
            ramdisk=options.ramdisk,
            rootfs=options.rootfs,
            rootfs_partition=options.partition,
            scp_fw=options.scp_fw,
            scp_romfw=options.scp_romfw,
            shell=options.shell,
            ssh_host=options.ssh_host,
            ssh_prompt=options.ssh_prompt,
            ssh_port=options.ssh_port,
            ssh_user=options.ssh_user,
            ssh_identity_file=options.ssh_identity_file,
            tests=options.tests,
            timeouts=options.timeouts,
            uefi=options.uefi,
            boot_args=options.boot_args,
            secrets=options.secrets,
            modules=options.modules,
            overlays=options.overlays,
            parameters=options.parameters,
            deploy_os=options.deploy_os,
            tuxbuild=options.tuxbuild,
            tuxmake=options.tuxmake,
            job_definition=options.job_definition,
            shared=options.shared,
        )
        job.initialize()
        sys.stdout.write(job.render())
    except TuxLavaException as exc:
        parser.error(str(exc))
    except Exception as exc:
        LOG.error("Raised an exception %s", exc)
        raise


def start():
    if __name__ == "__main__":
        sys.exit(main())


start()
