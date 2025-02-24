#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# vim: set ts=4
#
# Copyright 2024-present Linaro Limited
#
# SPDX-License-Identifier: MIT

import argparse
import sys

from pathlib import Path
from tuxlava import __version__
from tuxlava.devices import Device
from tuxlava.tests import Test
from tuxlava.utils import pathurlnone


###########
# Helpers #
###########
def filter_options(options):
    keys = [
        "cache_dir",
        "debug",
        "deploy_os",
        "device",
        "extra_assets",
        "lava_definition",
        "qemu_binary",
        "qemu_image",
        "shell",
        "shared",
        "test_definitions",
        "timeouts",
        "tmpdir",
        "tux_boot_args",
        "tuxbuild",
        "tuxmake",
    ]
    return {k: getattr(options, k) for k in vars(options) if k not in keys}


###########
# Actions #
###########
class ListDevicesAction(argparse.Action):
    def __init__(
        self, option_strings, help, dest=argparse.SUPPRESS, default=argparse.SUPPRESS
    ):
        super().__init__(option_strings, dest=dest, default=default, nargs=0, help=help)

    def __call__(self, parser, namespace, values, option_string=None):
        parser._print_message(
            "\n".join([d.name for d in Device.list()]) + "\n", sys.stdout
        )
        parser.exit()


class ListTestsAction(argparse.Action):
    def __init__(
        self, option_strings, help, dest=argparse.SUPPRESS, default=argparse.SUPPRESS
    ):
        super().__init__(option_strings, dest=dest, default=default, nargs=0, help=help)

    def __call__(self, parser, namespace, values, option_string=None):
        parser._print_message("\n".join(Test.list()) + "\n", sys.stdout)
        parser.exit()


class KeyValueAction(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        for value in values:
            key, *value = value.split("=")
            getattr(namespace, self.dest)[key] = "=".join(value)


class KeyValueParameterAction(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        for value in values:
            key, value = value.split("=", maxsplit=1)
            if key in ["KSELFTEST"]:
                if "$BUILD/" not in value:
                    value = pathurlnone(value)
            getattr(namespace, self.dest)[key] = value


class KeyValueIntAction(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        KEYS = ["deploy", "boot"] + Test.list()
        for value in values:
            try:
                key, value = value.split("=")
            except ValueError:
                raise argparse.ArgumentError(
                    self, f"Invalid format for '{value}' timeout"
                )
            if key not in KEYS:
                raise argparse.ArgumentError(self, f"Invalid timeout '{key}'")
            try:
                getattr(namespace, self.dest)[key] = int(value)
            except ValueError:
                raise argparse.ArgumentError(
                    self, f"Invalid value for {key} timeout: '{value}'"
                )


class OneTwoPathAction(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        if len(values) == 1:
            values = [values[0], "/"]
        elif len(values) > 2:
            raise argparse.ArgumentError(
                self,
                "takes one or two arguments, first should be a URL and second the destination.",
            )
        try:
            values[0] = pathurlnone(values[0])
        except argparse.ArgumentTypeError as exc:
            raise argparse.ArgumentError(self, str(exc))
        if isinstance(getattr(namespace, self.dest), list):
            getattr(namespace, self.dest).append(values)
        else:
            setattr(namespace, self.dest, values)


class SharedAction(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        if values is None:
            return
        if len(values) == 1:
            values = [values[0], "/mnt/tuxrun"]
        if len(values) > 2:
            raise argparse.ArgumentError(
                self,
                "takes zero, one or two arguments, first is the source and the second the destination. The later is optional.",
            )
        setattr(namespace, self.dest, values)


##########
# Setups #
##########
def setup_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="tuxlava", description="TuxLava")

    parser.add_argument(
        "--version", action="version", version=f"%(prog)s, {__version__}"
    )

    group = parser.add_argument_group("listing")
    group.add_argument(
        "--list-devices", action=ListDevicesAction, help="List available devices"
    )
    group.add_argument(
        "--list-tests", action=ListTestsAction, help="List available tests"
    )

    group = parser.add_argument_group("artefacts")

    def artefact(name):
        group.add_argument(
            f"--{name}",
            default=None,
            metavar="URL",
            type=pathurlnone,
            help=f"{name} URL",
        )

    artefact("ap-romfw")
    artefact("bios")
    artefact("bl1")
    artefact("ssh-identity-file")
    artefact("dtb")
    artefact("fip")
    artefact("job-definition")
    artefact("kernel")
    artefact("mcp-fw")
    artefact("mcp-romfw")
    artefact("ramdisk")
    group.add_argument(
        "--modules",
        default=None,
        type=str,
        help="modules URL and optionally PATH to extract the modules, default PATH '/'",
        action=OneTwoPathAction,
        nargs="+",
    )
    group.add_argument(
        "--overlay",
        default=[],
        type=str,
        help="Tarball with overlay and optionally PATH to extract the tarball, default PATH '/'. Overlay can be specified multiple times",
        action=OneTwoPathAction,
        nargs="+",
        dest="overlays",
    )
    group.add_argument(
        "--partition",
        default=None,
        metavar="NUMBER",
        type=int,
        help="rootfs partition number",
    )
    artefact("rootfs")
    artefact("scp-fw")
    artefact("scp-romfw")
    group.add_argument(
        "--ssh-host",
        default=None,
        metavar="HOST ADDR",
        type=str,
        help="ssh host address, applicable to ssh-device",
    )
    group.add_argument(
        "--ssh-port",
        default=None,
        metavar="NUMBER",
        type=int,
        help="ssh port number. Defaults to 22, applicable to ssh-device",
    )
    group.add_argument(
        "--ssh-prompt",
        default=None,
        metavar="STRING",
        type=str,
        help="ssh prompt to expect, applicable to ssh-device",
    )
    group.add_argument(
        "--ssh-user",
        default=None,
        metavar="USERNAME",
        type=str,
        help="ssh username, applicable to ssh-device",
    )
    group.add_argument(
        "--tuxbuild",
        metavar="URL",
        default=None,
        type=str,
        help="URL of a TuxBuild build",
    )
    group.add_argument(
        "--tuxmake",
        metavar="DIRECTORY",
        default=None,
        type=str,
        help="directory containing a TuxMake build",
    )
    artefact("uefi")
    group.add_argument(
        "--fvp-ubl-license",
        default=None,
        metavar="FVP UBL License",
        type=str,
        help="UBL License to be passed to FVP that need User Based License. Applicable to FVP device type only",
    )

    group = parser.add_argument_group("secrets")
    group.add_argument(
        "--secrets",
        metavar="K=V",
        default={},
        type=str,
        help="job secrets as key=value",
        action=KeyValueAction,
        nargs="+",
    )

    group = parser.add_argument_group("test parameters")
    group.add_argument(
        "--parameters",
        metavar="K=V",
        default={},
        type=str,
        help="test parameters as key=value",
        action=KeyValueParameterAction,
        nargs="+",
    )
    group.add_argument(
        "--tests",
        nargs="+",
        default=[],
        metavar="T",
        help="test suites",
        choices=Test.list(),
        action="extend",
    )
    group.add_argument(
        "--shell",
        action="store_true",
        help="Start a shell in the VM",
    )
    group.add_argument(
        "commands",
        nargs="*",
        help="Space separated list of commands to run inside the VM",
    )

    group = parser.add_argument_group("run options")
    group.add_argument(
        "--device",
        default=None,
        metavar="NAME",
        help="Device type",
        choices=[d.name for d in Device.list()],
    )
    group.add_argument(
        "--boot-args", default=None, metavar="ARGS", help="extend boot arguments"
    )
    group.add_argument(
        "--boot", default=None, metavar="NAME", help="Boot Image URL/Path"
    )
    group.add_argument(
        "--prompt", default=None, metavar="PROMPT", help="extra console prompt"
    )
    group.add_argument(
        "--timeouts",
        metavar="K=V",
        default={},
        type=str,
        help="timeouts in minutes as action=duration",
        action=KeyValueIntAction,
        nargs="+",
    )
    group.add_argument(
        "--deploy-os",
        default="debian",
        metavar="DEPLOY_OS",
        help="Deployment operating system name. Default is 'debian'",
    )
    group.add_argument(
        "--enable-kvm",
        default=False,
        action="store_true",
        help="Enable kvm, only possible if host and QEMU system are the same",
    )
    group.add_argument(
        "--enable-trustzone",
        default=False,
        action="store_true",
        help="Enable trustzone, applicable to QEMU arm64 device only",
    )

    group.add_argument(
        "--enable-network",
        default=False,
        action="store_true",
        help="Enable network",
    )

    group = parser.add_argument_group("runtime")
    group.add_argument(
        "--qemu-image",
        default=None,
        help="Use qemu from the given container image",
    )

    group.add_argument(
        "--qemu-binary",
        default=None,
        type=Path,
        help="Use qemu from the given path",
    )

    group = parser.add_argument_group("output")
    group.add_argument(
        "--lava-definition",
        default=False,
        action="store_true",
        help="Save the LAVA definition.yaml file",
    )
    group.add_argument(
        "--shared",
        default=None,
        type=str,
        help="Directory to share with the device",
        action=SharedAction,
        nargs="*",
    )

    group = parser.add_argument_group("debugging")
    group.add_argument(
        "--debug",
        default=False,
        action="store_true",
        help="Print more debug information about tuxlava",
    )

    return parser
