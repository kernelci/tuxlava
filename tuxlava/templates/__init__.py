# -*- coding: utf-8 -*-
#
# vim: set ts=4
#
# Copyright 2024-present Linaro Limited
#
# SPDX-License-Identifier: MIT

from functools import lru_cache
from pathlib import Path

import jinja2

from tuxlava.utils import compression

BASE = (Path(__file__) / "..").resolve()


@lru_cache(maxsize=None)
def jobs():
    env = jinja2.Environment(
        autoescape=False,
        trim_blocks=True,
        loader=jinja2.FileSystemLoader(str(BASE / "jobs")),
        undefined=jinja2.StrictUndefined,
    )
    env.globals["compression"] = compression
    return env


@lru_cache(maxsize=None)
def devices():
    return jinja2.Environment(
        autoescape=False,
        trim_blocks=True,
        loader=jinja2.FileSystemLoader(str(BASE / "devices")),
    )


@lru_cache(maxsize=None)
def tests():
    return jinja2.Environment(
        autoescape=False,
        trim_blocks=True,
        loader=jinja2.FileSystemLoader(str(BASE / "tests")),
        undefined=jinja2.StrictUndefined,
    )
