# -*- coding: utf-8 -*-
#
# vim: set ts=4
#
# Copyright 2026-present Linaro Limited
#
# SPDX-License-Identifier: MIT

import re
from pathlib import Path
from urllib.parse import urlparse

import requests
import yaml

from tuxlava.exceptions import InvalidArgument
from tuxlava.requests import requests_get
from tuxlava.tests import Test
from tuxlava.utils import url_name


def read_url(url):
    parsed = urlparse(url)
    if parsed.scheme not in ["http", "https"]:
        try:
            return Path(parsed.path).read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError) as e:
            raise InvalidArgument(f"{parsed.path}: can't read it: {e}")

    try:
        ret = requests_get(url)
    except requests.RequestException as e:
        raise InvalidArgument(f"{url}: download failed: {e}")
    if ret.status_code != 200:
        raise InvalidArgument(f"{url}: download failed with HTTP {ret.status_code}")
    try:
        return ret.content.decode("utf-8")
    except UnicodeDecodeError as e:
        raise InvalidArgument(f"{url}: can't read it: {e}")


def pasted_text(text):
    return text if text.endswith("\n") else text + "\n"


def yaml_test_minutes(source, text):
    try:
        items = yaml.safe_load(text)
    except yaml.YAMLError as e:
        raise InvalidArgument(f"{source}: invalid YAML: {e}")

    if not isinstance(items, list):
        raise InvalidArgument(f"{source}: must be a YAML list of test actions")

    # The text is pasted between the other actions of the job, as it is
    try:
        pasted = yaml.safe_load("- {}\n" + pasted_text(text) + "- {}\n")
    except yaml.YAMLError:
        pasted = None
    if pasted != [{}] + items + [{}]:
        raise InvalidArgument(
            f"{source}: must be one plain YAML list with the items at column 0, "
            "it is pasted into the job as it is"
        )

    minutes = 0
    for i, item in enumerate(items, start=1):
        if not isinstance(item, dict) or set(item.keys()) != {"test"}:
            raise InvalidArgument(
                f"{source}: item {i} must be a mapping with a single 'test' key"
            )
        test_action = item["test"]
        timeout = test_action.get("timeout") if isinstance(test_action, dict) else None
        item_minutes = None
        if isinstance(timeout, dict) and set(timeout.keys()) == {"minutes"}:
            item_minutes = timeout["minutes"]
        if type(item_minutes) is not int or item_minutes <= 0:
            raise InvalidArgument(
                f"{source}: item {i} must set timeout.minutes as a positive integer "
                "and no other unit, tuxlava adds it to the job timeout budget"
            )
        minutes += item_minutes

    return minutes


class YamlTest(Test):
    devices = ["*"]

    def __init__(self, url):
        self.name = Path(url_name(url)).stem
        if not re.fullmatch(r"[A-Za-z0-9._-]+", self.name):
            raise InvalidArgument(
                f"{url}: the file name can only have letters, digits, '.', '_' and '-'"
            )
        self.text = read_url(url)
        self.timeout = yaml_test_minutes(url, self.text)

    def render(self, **kwargs):
        return pasted_text(self.text)
