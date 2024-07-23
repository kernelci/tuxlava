# -*- coding: utf-8 -*-

from argparse import Namespace

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
