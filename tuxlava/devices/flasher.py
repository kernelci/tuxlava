# Copyright (c) 2025-present Qualcomm Technologies, Inc. and/or its subsidiaries.
#
# SPDX-License-Identifier: MIT

from os.path import basename
from typing import List
from urllib.parse import urlparse

from tuxlava import templates
from tuxlava.devices import Device
from tuxlava.exceptions import InvalidArgument, MissingArgument
from tuxlava.utils import notnone


class FlasherDevice(Device):
    """
    Flasher device represents class of LAVA device types that use
    deploy-to-flasher method. This method can be used alongside other
    deployment methods. It uses a custom script that is called by
    lava-dispatcher during deploymen. It also requires a flasher_deploy_commands
    variable in the decvice dictionary.
    """

    arch: str = ""
    lava_arch: str = ""
    machine: str = ""
    cpu: str = ""
    memory: str = ""

    extra_options: List[str] = []
    extra_boot_args: str = ""

    console: str = ""

    template: str = "flasher.yaml.jinja2"
    test_character_delay: int = 0

    enable_network: bool = True

    def validate(
        self,
        parameters,
        prompt,
        rootfs,
        secrets,
        tests,
        visibility,
        **kwargs,
    ):
        invalid_args = ["--" + k.replace("_", "-") for (k, v) in kwargs.items() if v]

        if len(invalid_args) > 0:
            raise InvalidArgument(
                f"Invalid option(s) for flasher devices: {', '.join(sorted(invalid_args))}"
            )
        if prompt and '"' in prompt:
            raise InvalidArgument('argument --prompt should not contain "')
        for test in tests:
            test.validate(device=self, parameters=parameters, **kwargs)

    def default(self, options) -> None:
        options.rootfs = notnone(options.rootfs, self.rootfs)

    def definition(self, **kwargs):
        kwargs = kwargs.copy()

        kwargs["rootfs"] = notnone(kwargs.get("rootfs"), self.rootfs)
        if not kwargs["rootfs"]:
            raise MissingArgument(
                "Missing --rootfs argument. Can't render the template"
            )
        # extract file name from URL
        kwargs["rootfs_filename"] = basename(urlparse(kwargs["rootfs"]).path)
        # render the template
        tests = [
            t.render(
                arch=kwargs.get("arch"),
                commands=kwargs.get("commands"),
                command_name=kwargs.get("command_name"),
                device=kwargs.get("device"),
                overlays=kwargs.get("overlays"),
                parameters=kwargs.get("parameters"),
                test_definitions=kwargs.get("test_definitions"),
            )
            for t in kwargs["tests"]
        ]
        return templates.jobs().get_template(self.template).render(**kwargs) + "".join(
            tests
        )


class FlasherQCS6490(FlasherDevice):
    name = "flasher-qcs6490-rb3gen2-core-kit"

    arch = "arm64"
    lava_arch = "arm64"

    rootfs = None


class FlasherDebianQCS6490(FlasherQCS6490):
    name = "flasher-debian-qcs6490-rb3gen2-core-kit"

    template = "flasher-debian.yaml.jinja2"


class FlasherQcomQCS6490(FlasherQCS6490):
    name = "flasher-qcom-qcs6490-rb3gen2-core-kit"

    template = "flasher-qcom.yaml.jinja2"


class FlasherPokyAltcfgQCS6490(FlasherQCS6490):
    name = "flasher-poky-altcfg-qcs6490-rb3gen2-core-kit"

    template = "flasher-poky-altcfg.yaml.jinja2"


class FlasherQRB2210(FlasherDevice):
    name = "flasher-qrb2210-rb1"

    arch = "arm64"
    lava_arch = "arm64"

    rootfs = None


class FlasherDebianQRB2210(FlasherQRB2210):
    name = "flasher-debian-qrb2210-rb1"

    template = "flasher-debian.yaml.jinja2"


class FlasherQcomQRB2210(FlasherQRB2210):
    name = "flasher-qcom-qrb2210-rb1"

    template = "flasher-qcom.yaml.jinja2"


class FlasherPokyAltcfgQRB2210(FlasherQRB2210):
    name = "flasher-poky-altcfg-qrb2210-rb1"

    template = "flasher-poky-altcfg.yaml.jinja2"


class FlasherQCS9075IqRvk(FlasherDevice):
    name = "flasher-qcs9075-iq-9075-evk"

    arch = "arm64"
    lava_arch = "arm64"

    rootfs = None


class FlasherDebianQCS9075IqRvk(FlasherQCS9075IqRvk):
    name = "flasher-debian-qcs9075-iq-9075-evk"

    template = "flasher-debian.yaml.jinja2"


class FlasherQcomQCS9075IqRvk(FlasherQCS9075IqRvk):
    name = "flasher-qcom-qcs9075-iq-9075-evk"

    template = "flasher-qcom.yaml.jinja2"


class FlasherPokyAltcfgQCS9075IqRvk(FlasherQCS9075IqRvk):
    name = "flasher-poky-altcfg-qcs9075-iq-9075-evk"

    template = "flasher-poky-altcfg.yaml.jinja2"


class FlasherQCS9100Ride(FlasherDevice):
    name = "flasher-qcs9100-ride-sx"

    arch = "arm64"
    lava_arch = "arm64"

    rootfs = None


class FlasherDebianQCS9100Ride(FlasherQCS9100Ride):
    name = "flasher-debian-qcs9100-ride-sx"

    template = "flasher-debian.yaml.jinja2"


class FlasherQcomQCS9100Ride(FlasherQCS9100Ride):
    name = "flasher-qcom-qcs9100-ride-sx"

    template = "flasher-qcom.yaml.jinja2"


class FlasherPokyAltcfgQCS9100Ride(FlasherQCS9100Ride):
    name = "flasher-poky-altcfg-qcs9100-ride-sx"

    template = "flasher-poky-altcfg.yaml.jinja2"
