# -*- coding: utf-8 -*-

import os
import yaml
import pytest
from pathlib import Path

from tuxlava.jobs import Job, DEVICE_DICT_VARS
from tuxlava.devices import Device
from tuxlava.exceptions import InvalidArgument

BASE = (Path(__file__) / "..").resolve()
DEVICE_DICTS = BASE / ".." / "device_dicts"
DEVICE_DICT_REFS = BASE / "refs" / "device_dicts"


class TestDeviceDictVars:

    def test_device_dict_vars_is_set(self):
        assert DEVICE_DICT_VARS
        assert isinstance(DEVICE_DICT_VARS, set)

    def test_device_dict_vars_contains_expected(self):
        expected = {
            "boot_method",
            "connection_command",
            "docker_shell_extra_arguments",
            "hard_reset_command",
            "power_off_command",
            "power_on_command",
        }
        assert expected.issubset(DEVICE_DICT_VARS)


class TestDeviceDictLoading:

    def test_device_dict_file_not_found(self):
        job = Job(
            device="nfs-cd8180-orion-o6",
            kernel="https://example.com/Image.gz",
            rootfs="https://example.com/rootfs.tar.xz",
            device_dict=Path("/nonexistent/path.jinja2"),
        )
        with pytest.raises(InvalidArgument, match="Device dict file not found"):
            job.initialize()

    def test_device_dict_loads_config(self):
        device_dict_path = DEVICE_DICTS / "cd8180-orion-o6.jinja2"
        job = Job(
            device="nfs-cd8180-orion-o6",
            kernel="https://example.com/Image.gz",
            rootfs="https://example.com/rootfs.tar.xz",
            device_dict=device_dict_path,
        )
        job.initialize()

        assert job.d_dict_config is not None
        assert "boot_method" in job.d_dict_config
        assert job.d_dict_config["boot_method"] == "grub"
        assert "connection_command" in job.d_dict_config
        assert "docker_shell_extra_arguments" in job.d_dict_config

    def test_device_dict_loads_fastboot_config(self):
        device_dict_path = DEVICE_DICTS / "dragonboard-845c.jinja2"
        job = Job(
            device="fastboot-dragonboard-845c",
            kernel="https://example.com/Image.gz",
            rootfs="https://example.com/rootfs.tar.xz",
            device_dict=device_dict_path,
        )
        job.initialize()

        assert job.d_dict_config is not None
        assert "boot_method" in job.d_dict_config
        assert job.d_dict_config["boot_method"] == "fastboot"

    def test_device_dict_unknown_variable_raises_error(self, tmp_path):
        bad_config = tmp_path / "bad-config.jinja2"
        bad_config.write_text("""{# Bad config with unknown variable #}
{% set boot_method = 'grub' %}
{% set unknown_variable = 'should fail' %}
{% set connection_command = 'telnet localhost 2000' %}
""")

        job = Job(
            device="nfs-cd8180-orion-o6",
            kernel="https://example.com/Image.gz",
            rootfs="https://example.com/rootfs.tar.xz",
            device_dict=bad_config,
        )
        with pytest.raises(InvalidArgument, match="Unknown variable.*unknown_variable"):
            job.initialize()

    def test_device_dict_none_when_not_provided(self):
        job = Job(
            device="nfs-juno-r2",
            kernel="https://example.com/Image.gz",
            rootfs="https://example.com/rootfs.tar.xz",
        )
        job.initialize()

        assert job.d_dict_config is None


class TestDeviceDictConfigs:

    @pytest.mark.parametrize(
        "config_file,device,boot_method",
        [
            ("cd8180-orion-o6.jinja2", "nfs-cd8180-orion-o6", "grub"),
            ("ampereone.jinja2", "nfs-ampereone", "grub"),
            ("ampereone-ac04.jinja2", "nfs-ampereone", "grub"),
            ("bcm2711-rpi-4-b.jinja2", "nfs-bcm2711-rpi-4-b", "u-boot"),
            ("juno-r2.jinja2", "nfs-juno-r2", "u-boot"),
            ("s32g399a-rdb3.jinja2", "nfs-s32g399a-rdb3", "u-boot"),
            ("dragonboard-410c.jinja2", "fastboot-dragonboard-410c", "fastboot"),
            ("dragonboard-845c.jinja2", "fastboot-dragonboard-845c", "fastboot"),
            ("gs101-oriole.jinja2", "fastboot-gs101-oriole", "fastboot"),
            ("qrb5165-rb5.jinja2", "fastboot-qrb5165-rb5", "fastboot"),
        ],
    )
    def test_device_dict_config_loads(self, config_file, device, boot_method):
        device_dict_path = DEVICE_DICTS / config_file
        if not device_dict_path.exists():
            pytest.skip(f"Config file {config_file} not found")

        job = Job(
            device=device,
            kernel="https://example.com/Image.gz",
            rootfs="https://example.com/rootfs.tar.xz",
            device_dict=device_dict_path,
        )
        job.initialize()

        assert job.d_dict_config is not None
        assert job.d_dict_config.get("boot_method") == boot_method
        assert "docker_shell_extra_arguments" in job.d_dict_config


class TestDeviceDictRendering:

    def test_nfs_device_dict_rendering_with_config(self):
        device = Device.select("nfs-cd8180-orion-o6")()
        context = {"arch": "arm64"}
        d_dict_config = {
            "boot_method": "grub",
            "connection_command": "telnet localhost 2000",
            "hard_reset_command": "pduclient --command reboot",
            "power_off_command": "pduclient --command off",
            "power_on_command": "pduclient --command on",
            "docker_shell_extra_arguments": ["--add-host=test:127.0.0.1"],
        }

        result = device.device_dict(context, d_dict_config)

        assert "connect: telnet localhost 2000" in result
        assert "hard_reset: pduclient --command reboot" in result
        assert "power_off: pduclient --command off" in result
        assert "power_on: pduclient --command on" in result
        assert "--add-host=test:127.0.0.1" in result

    def test_nfs_device_dict_rendering_without_config(self):
        device = Device.select("nfs-juno-r2")()
        context = {"arch": "arm64"}

        result = device.device_dict(context, None)

        assert "hard_reset:" not in result
        assert "power_off:" not in result

    def test_fastboot_device_dict_rendering_with_config(self):
        device = Device.select("fastboot-dragonboard-845c")()
        context = {"arch": "arm64"}
        d_dict_config = {
            "boot_method": "fastboot",
            "connection_command": "telnet localhost 3000",
            "hard_reset_command": "pduclient --command reboot",
            "power_off_command": "pduclient --command off",
            "power_on_command": "pduclient --command on",
            "fastboot_serial_number": "abc123",
            "docker_shell_extra_arguments": ["--device=/dev/ttyUSB0"],
        }

        result = device.device_dict(context, d_dict_config)

        assert "connect: telnet localhost 3000" in result
        assert 'fastboot_serial_number: "abc123"' in result
        assert "--device=/dev/ttyUSB0" in result

    def test_device_dict_with_d_dict_defaults(self):
        device = Device.select("nfs-juno-r2")()
        context = {"arch": "arm64"}
        d_dict_config = {
            "boot_method": "u-boot",
            "connection_command": "telnet localhost 2000",
            "hard_reset_command": "pduclient --command reboot",
            "power_off_command": "pduclient --command off",
            "power_on_command": "pduclient --command on",
            "docker_shell_extra_arguments": [],
        }

        result = device.device_dict(context, d_dict_config)

        assert "connect: telnet localhost 2000" in result


@pytest.mark.parametrize(
    "device,config_file,ref_file",
    [
        (
            "fastboot-dragonboard-845c",
            "dragonboard-845c.jinja2",
            "dragonboard-845c.yaml",
        ),
        (
            "nfs-cd8180-orion-o6",
            "cd8180-orion-o6.jinja2",
            "cd8180-orion-o6.yaml",
        ),
    ],
)
def test_device_dict_rendering_with_config_file(device, config_file, ref_file):
    device_dict_path = DEVICE_DICTS / config_file
    job = Job(
        device=device,
        kernel="https://example.com/Image.gz",
        rootfs="https://example.com/rootfs.tar.xz",
    )
    job.device_dict = device_dict_path
    job.initialize()

    context = {"arch": "arm64"}
    result = job.device.device_dict(context, job.d_dict_config)

    ref_path = DEVICE_DICT_REFS / ref_file
    if os.environ.get("TUXLAVA_RENDER"):
        ref_path.write_text(result, encoding="utf-8")

    assert result == ref_path.read_text(encoding="utf-8")

    try:
        yaml.load(result, Loader=yaml.SafeLoader)
    except yaml.YAMLError as e:
        pytest.fail(f"Device dict YAML is invalid: {e}")
