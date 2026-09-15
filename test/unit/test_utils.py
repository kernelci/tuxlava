# -*- coding: utf-8 -*-

from argparse import ArgumentTypeError
from pathlib import Path

import pytest
import yaml

from tuxlava.utils import (
    downloaded_name,
    url_name,
    is_cpio_rootfs,
    kernel_type,
    is_plain_file_name,
    notnone,
    pathurlnone,
    yaml_quote,
)


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


def test_url_name_takes_the_last_part_of_the_path():
    assert url_name("https://e.com/a/b/rootfs.img.xz") == "rootfs.img.xz"


def test_url_name_ignores_the_query():
    # A redirect endpoint. Every image comes back as "download".
    url = "https://drive.usercontent.google.com/download?id=A&confirm=xxx"
    assert url_name(url) == "download"


def test_downloaded_name_drops_the_suffix_we_decompress():
    assert downloaded_name("rootfs.img.xz", "xz") == "rootfs.img"


def test_downloaded_name_keeps_the_suffix_without_compression():
    # No compression key means LAVA saves the file as it is.
    assert downloaded_name("rootfs.img.xz") == "rootfs.img.xz"


def test_downloaded_name_of_a_file_without_a_suffix():
    assert downloaded_name("Image") == "Image"


def test_is_plain_file_name_takes_a_normal_name():
    assert is_plain_file_name("rootfs.img.xz") is True


def test_is_plain_file_name_rejects_a_path():
    assert is_plain_file_name("a/b.img") is False
    assert is_plain_file_name("..") is False


def test_is_plain_file_name_rejects_what_breaks_the_url():
    # LAVA points at the file with downloads://<name>.
    for name in ("fw#1.wic", "fw?1.wic", "fw[1].wic"):
        assert is_plain_file_name(name) is False


def test_yaml_quote_wraps_the_value():
    assert yaml_quote("rootfs.img.xz") == '"rootfs.img.xz"'


def test_yaml_quote_keeps_a_colon_in_the_string():
    assert yaml.safe_load(f"key: {yaml_quote('a: b')}") == {"key": "a: b"}


def test_yaml_quote_keeps_a_hash_in_the_string():
    assert yaml.safe_load(f"key: {yaml_quote('a #1')}") == {"key": "a #1"}


def test_yaml_quote_escapes_a_quote():
    quoted = yaml_quote('a"b')
    assert yaml.safe_load(f"key: {quoted}") == {"key": 'a"b'}
