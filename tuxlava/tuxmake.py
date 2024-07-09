# -*- coding: utf-8 -*-
#
# vim: set ts=4
#
# Copyright 2024-present Linaro Limited
#
# SPDX-License-Identifier: MIT

import contextlib
import json
from pathlib import Path

from tuxlava.requests import requests_get


class InvalidTuxBuild(Exception):
    pass


class TuxBuild:
    Invalid = InvalidTuxBuild

    def __init__(self):
        self.kernel = None
        self.modules = []
        self.target_arch = None

    def parse(self, url, data):
        try:
            metadata = json.loads(data)
        except json.JSONDecodeError as e:
            raise self.Invalid(f"Invalid metadata.json: {e}")

        try:
            self.target_arch = metadata["build"]["target_arch"]
        except KeyError:
            raise self.Invalid("{url}/metadata.json is invalid")

        with contextlib.suppress(IndexError, KeyError):
            self.kernel = url + "/" + metadata["results"]["artifacts"]["kernel"][0]
        with contextlib.suppress(IndexError, KeyError):
            self.modules = [
                url + "/" + metadata["results"]["artifacts"]["modules"][0],
                "/",
            ]

        if self.kernel is None:
            raise self.Invalid("Missing kernel in directory")


class TuxBuildBuild(TuxBuild):
    def __init__(self, url):
        super().__init__()

        self.url = url
        ret = requests_get(f"{url}/metadata.json")
        if ret.status_code != 200:
            raise self.Invalid(f"{url}/metadata.json is missing")

        self.parse(url, ret.text)


class TuxMakeBuild(TuxBuild):
    def __init__(self, directory):
        super().__init__()

        self.location = Path(directory).resolve()
        self.url = f"file://{self.location}"
        metadata_file = self.location / "metadata.json"
        if not self.location.is_dir():
            raise self.Invalid(f"{directory} is not a directory")
        if not metadata_file.exists():
            raise self.Invalid(
                f"{directory} is not a valid TuxMake artifacts directory: missing metadata.json"
            )

        self.parse(f"file://{self.location}", metadata_file.read_text(encoding="utf-8"))
