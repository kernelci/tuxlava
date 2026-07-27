# -*- coding: utf-8 -*-

from pathlib import Path

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
