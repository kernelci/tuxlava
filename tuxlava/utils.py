# -*- coding: utf-8 -*-
#
# vim: set ts=4
#
# Copyright 2024-present Linaro Limited
#
# SPDX-License-Identifier: MIT

import argparse
import json
import re
from pathlib import Path
from urllib.parse import urlparse

AVH_API_TOKEN = "avh_api_token"

COMPRESSIONS = {
    ".tar.xz": ("tar", "xz"),
    ".tar.gz": ("tar", "gz"),
    ".tar": ("tar", None),
    ".tgz": ("tar", "gz"),
    ".tar.zst": ("tar", "zstd"),
    ".cpio.xz": ("cpio.newc", "xz"),
    ".cpio.gz": ("cpio.newc", "gz"),
    ".cpio.zst": ("cpio.newc", "zstd"),
    ".cpio": ("cpio.newc", None),
    ".ext4.xz": ("ext4", "xz"),
    ".ext4.gz": ("ext4", "gz"),
    ".ext4.zst": ("ext4", "zstd"),
    ".ext4": ("ext4", None),
    ".gz": (None, "gz"),
    ".xz": (None, "xz"),
    ".zst": (None, "zstd"),
    ".py": ("file", None),
    ".sh": ("file", None),
}


def compression(path):
    for ext, ret in COMPRESSIONS.items():
        if path.endswith(ext):
            return ret
    return (None, None)


def kernel_type(kernel):
    # LAVA picks the u-boot boot command from the type: bootz for a
    # zImage, bootm for a uImage and booti for an Image.
    name = (kernel or "").rsplit("/", 1)[-1].lower()
    if name.startswith("zimage"):
        return "zimage"
    if name.startswith("uimage"):
        return "uimage"
    return "image"


def is_cpio_rootfs(rootfs):
    # Some images do not have the cpio extension, so match "ramdisk" in
    # the name too.
    name = (rootfs or "").rsplit("/", 1)[-1].lower()
    return compression(name)[0] == "cpio.newc" or "ramdisk" in name


def secret_headers(secrets, given):
    """Headers per artefact.

    "kernel:Authorization=x" is only for the kernel. "Authorization=x" has
    no artefact and is used for the artefacts in 'given', the ones that
    come from the command line. A device default gets no header, the url
    can point to another host.
    """
    defaults = {}
    only = {}
    for key, value in secrets.items():
        artefact, sep, header = key.partition(":")
        if not sep:
            artefact, header = "", artefact
        if not value or not header or header.lower() == AVH_API_TOKEN:
            continue
        if artefact:
            only.setdefault(artefact, {})[header] = value
        else:
            defaults[header] = value

    headers = {name: dict(defaults) for name in given}
    for name, own in only.items():
        headers.setdefault(name, {}).update(own)
    return {name: h for name, h in headers.items() if h}


def secret_headers_yaml(headers, artefact, indent):
    own = headers.get(artefact)
    if not own:
        return ""
    pad = " " * indent
    lines = [f"{pad}headers:"]
    # json is a subset of yaml. Quote with it, a value with a '"' or a
    # newline would otherwise end the scalar and write its own yaml.
    lines += [
        f"{pad}  {json.dumps(name, ensure_ascii=False)}: "
        f"{json.dumps(value, ensure_ascii=False)}"
        for name, value in own.items()
    ]
    return "\n".join(lines) + "\n"


def pathurlnone(string):
    if string is None:
        return None
    url = urlparse(string)
    if url.scheme in ["http", "https"]:
        return string
    if url.scheme not in ["", "file"]:
        raise argparse.ArgumentTypeError(f"Invalid scheme '{url.scheme}'")

    path = Path(string if url.scheme == "" else url.path)
    if not path.exists():
        raise argparse.ArgumentTypeError(f"{path} no such file or directory")
    return f"file://{path.expanduser().resolve()}"


def notnone(value, fallback):
    if value is None:
        return fallback
    return value


def slugify(s):
    s = s.lower().strip()
    s = re.sub(r"[^\w\s-]", "", s)
    s = re.sub(r"[\s_-]+", "-", s)
    s = re.sub(r"^-+|-+$", "", s)
    return s
