#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#
from xotl.crdt.vclock import VectorClock


class Counter:
    def __init__(self, actor):
        self.actor = actor
        self.vc = VectorClock()

    def __repr__(self):
        return f"<Counter of {self.value}; in {self.actor} with {self.vc}>"

    def incr(self):
        self.vc = self.vc.bump(self.actor)

    @property
    def value(self):
        return sum(d.counter for d in self.vc.dots)

    def merge(self, other: 'Counter'):
        'Merge this replica with another in-place'
        self.vc = self.vc.merge(other.vc)

    @property
    def state(self):
        return self
