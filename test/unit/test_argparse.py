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
