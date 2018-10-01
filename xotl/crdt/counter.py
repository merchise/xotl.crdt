#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#
from xotl.crdt.base import CvRDT
from xotl.crdt.vclock import VClock


class GCounter(CvRDT):
    # The G-Counter is basically an actor-limited interface for the vclock.
    def __init__(self, *, actor: str):
        self.actor = actor
        self.vclock = VClock()

    def __repr__(self):
        return f"<Counter of {self.value}; in {self.actor} with {self.vclock}>"

    def incr(self):
        self.vclock = self.vclock.bump(self.actor)

    @property
    def value(self):
        return sum(d.counter for d in self.vclock.dots)

    def merge(self, other: 'Counter'):
        'Merge this replica with another in-place'
        self.vclock = self.vclock.merge(other.vc)

    @property
    def state(self):
        return self
