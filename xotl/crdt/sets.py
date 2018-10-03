#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#
from xotl.crdt.base import CvRDT


class GSet(CvRDT):
    def __init__(self, *, actor):
        self.actor = actor
        self.items = ()  # as a tuple

    @property
    def value(self):
        return set(self.items)

    def __le__(self, other: 'GSet') -> bool:
        return self.value <= other.value

    def merge(self, other: 'GSet') -> None:
        self.items = tuple(self.value | other.value)

    def add(self, item):
        self.items += (item, )
