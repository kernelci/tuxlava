# -*- coding: utf-8 -*-

from pathlib import Path

import pytest

from tuxlava.jobs import TEST_DEFINITIONS, Job


def job(**kwargs):
    return Job(
        device="qemu-arm64",
        kernel="https://example.com/Image",
        tests=["ltp-smoke"],
        **kwargs,
    )


def test_test_definitions_default():
    j = job()
    j.initialize()
    assert j.test_definitions == TEST_DEFINITIONS


def test_test_definitions_override():
    url = "https://example.com/2025.01.tar.zst"
    j = job(test_definitions=url)
    j.initialize()
    assert j.test_definitions == url
    assert url in j.render()


def test_test_definitions_local_path():
    j = job(test_definitions=__file__)
    j.initialize()
    assert j.test_definitions == f"file://{Path(__file__).resolve()}"


def test_test_definitions_unused_without_tests():
    j = Job(device="qemu-arm64", kernel="https://example.com/Image")
    j.initialize()
    assert j.test_definitions is None


def test_str_before_initialize():
    assert str(job()) == "Job qemu-arm64/ltp-smoke"


def test_str_after_initialize():
    j = job()
    j.initialize()
    assert str(j) == "Job qemu-arm64/ltp-smoke"


def test_initialize_does_not_change_the_default_tests():
    Job(
        device="qemu-arm64", kernel="https://example.com/Image", commands=["ls"]
    ).initialize()
    j = Job(device="qemu-arm64", kernel="https://example.com/Image")
    assert j.tests == []


@pytest.mark.parametrize(
    "name, value",
    [
        ("commands", ["ls"]),
        ("tests", ["ltp-smoke"]),
        ("timeouts", {"boot": 5}),
        ("secrets", {"k": "v"}),
        ("overlays", [["https://e.com/o.tar.xz", "/"]]),
        ("downloads", {"os": ("https://e.com/os.wic.xz", None)}),
        ("pflash", ["https://e.com/flash0.img"]),
        ("parameters", {"K": "V"}),
    ],
)
def test_job_copies_mutable_arguments(name, value):
    j = Job(device="qemu-arm64", **{name: value})
    assert getattr(j, name) == value
    assert getattr(j, name) is not value


@pytest.mark.parametrize(
    "name, empty",
    [
        ("commands", []),
        ("tests", []),
        ("timeouts", {}),
        ("secrets", {}),
        ("overlays", []),
        ("downloads", {}),
        ("pflash", []),
        ("parameters", {}),
    ],
)
def test_job_takes_none_for_list_and_dict_arguments(name, empty):
    j = Job(device="qemu-arm64", **{name: None})
    assert getattr(j, name) == empty
