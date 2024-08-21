# -*- coding: utf-8 -*-
#
# vim: set ts=4
#
# Copyright 2024-present Linaro Limited
#
# SPDX-License-Identifier: MIT


class TuxLavaException(Exception):
    def __str__(self):
        name = super().__str__()
        if hasattr(self, "msg"):
            return self.msg.format(name=name)
        else:
            return name


class InvalidArgument(TuxLavaException):
    pass


class MissingArgument(TuxLavaException):
    pass


class TuxLavaError(TuxLavaException):
    pass
