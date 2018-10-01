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
        return f"<GCounter of {self.value}; in {self.actor} with {self.vclock}>"

    def incr(self):
        self.vclock = self.vclock.bump(self.actor)

    @property
    def value(self):
        return sum(d.counter for d in self.vclock.dots)

    def merge(self, other: 'GCounter'):
        'Merge this replica with another in-place'
        self.vclock = self.vclock.merge(other.vclock)

    @property
    def state(self):
        return self

    def __le__(self, other):
        return self.vclock <= other.vclock


class PNCounter(CvRDT):
    def __init__(self, *, actor: str):
        self.actor = actor
        self.pos = GCounter(actor=actor)
        self.neg = GCounter(actor=actor)

    def __repr__(self):
        return f"<PNCounter of {self.value}; with {self.pos} and {self.neg}>"

    def incr(self):
        self.pos.incr()

    def decr(self):
        self.neg.incr()

    @property
    def value(self):
        return self.pos.value - self.neg.value

    def merge(self, other: 'PNCounter'):
        'Merge this replica with another in-place'
        self.pos.merge(other.pos)
        self.neg.merge(other.neg)

    @property
    def state(self):
        return self

    def __le__(self, other):
        return self.pos <= other.pos and self.neg <= other.neg
