#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#
from xotl.crdt.base import CvRDT
from xotl.crdt.clocks import VClock


class GCounter(CvRDT):
    '''A increment-only counter.

    '''
    def __init__(self, *, actor: str) -> None:
        self.actor = actor
        self.vclock = VClock()

    def __repr__(self):
        return f"<GCounter of {self.value}; {self.actor}, {self.vclock.simplified}>"

    def incr(self):
        'Increases the counter by one.'
        self.vclock = self.vclock.bump(self.actor)

    @property
    def value(self) -> int:
        'The current value of the counter'
        return sum(d.counter for d in self.vclock.dots)

    def merge(self, other: 'GCounter') -> None:  # type: ignore
        'Merge this replica with another in-place'
        self.vclock += other.vclock

    def __le__(self, other):
        return self.vclock <= other.vclock


class PNCounter(CvRDT):
    '''A counter that allows increments and decrements.'''
    def __init__(self, *, actor: str) -> None:
        self.actor = actor
        self.pos = GCounter(actor=actor)
        self.neg = GCounter(actor=actor)

    def __repr__(self):
        return f"<PNCounter of {self.value}; with {self.pos} and {self.neg}>"

    def incr(self):
        'Increase the counter by one.'
        self.pos.incr()

    def decr(self):
        'Decreases the counter by one.'
        self.neg.incr()

    @property
    def value(self) -> int:
        'The current value of the counter.'
        return self.pos.value - self.neg.value

    def merge(self, other: 'PNCounter') -> None:  # type: ignore
        'Merge this replica with another in-place'
        self.pos.merge(other.pos)
        self.neg.merge(other.neg)

    def __le__(self, other):
        return self.pos <= other.pos and self.neg <= other.neg
