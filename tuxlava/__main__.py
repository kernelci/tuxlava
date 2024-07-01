#!/usr/bin/python3
# vim: set ts=4
#
# Copyright 2024-present Linaro Limited
#
# SPDX-License-Identifier: MIT

import logging
import sys

from tuxlava.jobs import Job
from tuxlava.argparse import filter_artefacts, setup_parser


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

    if options.tuxbuild or options.tuxmake:
        tux = options.tuxbuild or options.tuxmake
        options.kernel = options.kernel or tux.kernel
        options.modules = options.modules or tux.modules
        options.device = options.device or f"qemu-{tux.target_arch}"
        if options.device == "qemu-armv5":
            options.dtb = tux.url + "/dtbs/versatile-pb.dtb"
        if options.parameters:
            if options.modules:
                module, path = options.modules
                modules_path = options.parameters.get("MODULES_PATH", path)
                options.modules = [module, modules_path]

            for k in options.parameters:
                if isinstance(options.parameters[k], str):
                    options.parameters[k] = options.parameters[k].replace(
                        "$BUILD/", tux.url + "/"
                    )

    if not options.device:
        parser.error("argument --device is required")

    if "hacking-session" in options.tests:
        options.enable_network = True
        if not options.parameters.get("PUB_KEY"):
            parser.error("argument missing --parameters PUB_KEY='...'")

    artefacts = filter_artefacts(options)

    try:
        job = Job(
            device=options.device,
            bios=options.bios,
            bl1=options.bl1,
            commands=options.commands,
            dtb=options.dtb,
            kernel=options.kernel,
            ap_romfw=options.ap_romfw,
            mcp_fw=options.mcp_fw,
            mcp_romfw=options.mcp_romfw,
            fip=options.fip,
            enable_kvm=options.enable_kvm,
            enable_network=options.enable_network,
            prompt=options.prompt,
            rootfs=options.rootfs,
            rootfs_partition=options.partition,
            scp_fw=options.scp_fw,
            scp_romfw=options.scp_romfw,
            tests=[t.name for t in options.tests],
            timeouts=options.timeouts,
            uefi=options.uefi,
            boot_args=options.boot_args,
            secrets=options.secrets,
            modules=options.modules[0] if options.modules else None,
            overlays=options.overlays,
            parameters=options.parameters,
        )
        sys.stdout.write(job.render())
    except Exception as exc:
        LOG.error("Raised an exception %s", exc)
        raise


def start():
    if __name__ == "__main__":
        sys.exit(main())


start()
