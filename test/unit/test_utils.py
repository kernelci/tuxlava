# -*- coding: utf-8 -*-

from argparse import ArgumentTypeError
from pathlib import Path

import pytest

from tuxlava.utils import is_cpio_rootfs, kernel_type, notnone, pathurlnone


def test_is_cpio_rootfs():
    assert is_cpio_rootfs(None) is False
    assert is_cpio_rootfs("") is False

    assert is_cpio_rootfs("https://example.com/rootfs.cpio.gz") is True
    assert is_cpio_rootfs("https://example.com/rootfs.cpio") is True
    assert is_cpio_rootfs("https://example.com/rootfs.ext4.zst") is False

    assert is_cpio_rootfs("https://example.com/ramdisk.img") is True
    assert is_cpio_rootfs("https://example.com/ramdisk/rootfs.ext4.zst") is False


def test_kernel_type():
    assert kernel_type("https://example.com/zImage") == "zimage"
    assert kernel_type("https://example.com/zImage.gz") == "zimage"
    assert kernel_type("https://example.com/zImage.zst") == "zimage"
    assert kernel_type("https://example.com/uImage") == "uimage"
    assert kernel_type("https://example.com/uImage.zst") == "uimage"

    # everything else is an "image", including a bzImage
    assert kernel_type("https://example.com/Image") == "image"
    assert kernel_type("https://example.com/Image.gz") == "image"
    assert kernel_type("https://example.com/bzImage") == "image"
    assert kernel_type("https://example.com/vmlinuz") == "image"

    assert kernel_type(None) == "image"
    assert kernel_type("") == "image"


def test_notnone():
    assert notnone(None, "fallback") == "fallback"
    assert notnone("", "fallback") == ""
    assert notnone("hello", "fallback") == "hello"


def test_pathurlnone():
    assert pathurlnone(None) is None
    assert pathurlnone("https://example.com/kernel") == "https://example.com/kernel"
    assert pathurlnone(__file__) == f"file://{Path(__file__).expanduser().resolve()}"

    with pytest.raises(ArgumentTypeError) as exc:
        pathurlnone("ftp://example.com/kernel")
    assert exc.match("Invalid scheme 'ftp'")

    with pytest.raises(ArgumentTypeError) as exc:
        pathurlnone("file:///should-not-exists")
    assert exc.match("/should-not-exists no such file or directory")
