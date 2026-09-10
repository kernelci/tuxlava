# -*- coding: utf-8 -*-

from argparse import Namespace
from pathlib import Path

import pytest

from tuxlava.argparse import filter_options, setup_parser


def test_filter_options():
    assert filter_options(Namespace()) == {}
    assert filter_options(Namespace(hello="world")) == {"hello": "world"}
    assert filter_options(Namespace(hello="world", debug=True)) == {"hello": "world"}


def test_timeouts_parser():
    assert setup_parser().parse_args(["--timeouts", "boot=1"]).timeouts == {"boot": 1}
    assert setup_parser().parse_args(
        ["--timeouts", "boot=1", "deploy=42"]
    ).timeouts == {"boot": 1, "deploy": 42}

    with pytest.raises(SystemExit):
        setup_parser().parse_args(["--timeouts", "boot=a"])

    with pytest.raises(SystemExit):
        setup_parser().parse_args(["--timeouts", "booting=1"])


def test_test_definitions_parser():
    assert setup_parser().parse_args([]).test_definitions is None

    url = "https://example.com/2025.01.tar.zst"
    assert (
        setup_parser().parse_args(["--test-definitions", url]).test_definitions == url
    )

    options = setup_parser().parse_args(["--test-definitions", __file__])
    assert options.test_definitions == f"file://{Path(__file__).resolve()}"


def test_test_definitions_parser_invalid(capsys):
    with pytest.raises(SystemExit):
        setup_parser().parse_args(["--test-definitions", "ftp://example.com/x.tar.zst"])
    assert "Invalid scheme 'ftp'" in capsys.readouterr().err

    with pytest.raises(SystemExit):
        setup_parser().parse_args(["--test-definitions", "/nope/2025.01.tar.zst"])
    assert "/nope/2025.01.tar.zst no such file or directory" in capsys.readouterr().err


def test_firmware_takes_a_url():
    options = setup_parser().parse_args(
        ["--device", "qemu-arm64", "--firmware", "https://e.com/fw.wic.xz"]
    )
    assert options.downloads == {
        "firmware": "https://e.com/fw.wic.xz",
    }


def test_os_and_firmware_keep_their_own_names():
    options = setup_parser().parse_args(
        [
            "--device",
            "qemu-arm64",
            "--firmware",
            "https://e.com/a",
            "--os",
            "https://e.com/b",
        ]
    )
    assert list(options.downloads) == ["firmware", "os"]


def test_downloads_takes_the_name_from_the_url():
    options = setup_parser().parse_args(
        [
            "--device",
            "qemu-arm64",
            "--downloads",
            "https://e.com/packages.tar.gz",
        ]
    )
    assert options.downloads == {
        "packages": "https://e.com/packages.tar.gz",
    }


def test_downloads_can_be_given_several_times():
    options = setup_parser().parse_args(
        [
            "--device",
            "qemu-arm64",
            "--downloads",
            "https://e.com/testexport.tar.gz",
            "--downloads",
            "https://e.com/packages.tar.gz",
        ]
    )
    assert list(options.downloads) == ["testexport", "packages"]


def test_downloads_rejects_the_same_name_twice(capsys):
    # Two nameless URLs from a redirect endpoint both come out as
    # "download". One would quietly overwrite the other.
    with pytest.raises(SystemExit):
        setup_parser().parse_args(
            [
                "--device",
                "qemu-arm64",
                "--downloads",
                "https://e.com/download?id=A",
                "--downloads",
                "https://e.com/download?id=B",
            ]
        )
    assert "download" in capsys.readouterr().err


def test_downloads_clashing_with_firmware_is_an_error(capsys):
    with pytest.raises(SystemExit):
        setup_parser().parse_args(
            [
                "--device",
                "qemu-arm64",
                "--firmware",
                "https://e.com/a",
                "--downloads",
                "https://e.com/b",
                "firmware.wic.xz",
            ]
        )
    assert "firmware" in capsys.readouterr().err


def test_downloads_with_a_missing_file_is_an_error(capsys):
    # A bad path used to come out as a traceback.
    with pytest.raises(SystemExit):
        setup_parser().parse_args(
            ["--device", "qemu-arm64", "--downloads", "/nope/x.wic"]
        )
    assert "no such file or directory" in capsys.readouterr().err


def test_downloads_with_a_bad_scheme_is_an_error(capsys):
    with pytest.raises(SystemExit):
        setup_parser().parse_args(
            ["--device", "qemu-arm64", "--downloads", "ftp://e.com/a"]
        )
    assert "Invalid scheme 'ftp'" in capsys.readouterr().err
