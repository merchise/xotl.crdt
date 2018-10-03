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
        self.items = set()

    @property
    def value(self):
        return frozenset(self.items)

    def __le__(self, other: 'GSet') -> bool:
        return self.value <= other.value

    def merge(self, other: 'GSet') -> None:
        self.items |= other.value

    def add(self, item):
        self.items.add(item)


class TwoPhaseSet(CvRDT):
    def __init__(self, *, actor):
        self.actor = actor
        self.living = GSet(actor=actor)
        self.dead = GSet(actor=actor)

    @property
    def value(self):
        return self.living.value - self.dead.value

    def __le__(self, other: 'TwoPhaseSet') -> bool:
        return (self.living.value <= other.living.value or
                self.dead.value <= other.dead.value)

    def merge(self, other: 'TwoPhaseSet') -> None:
        self.living.items |= other.living.items
        self.dead.items |= other.dead.items

    def add(self, item) -> None:
        self.living.add(item)

    def remove(self, item) -> bool:
        if item in self.value:
            self.dead.add(item)
            return True
        else:
            return False
