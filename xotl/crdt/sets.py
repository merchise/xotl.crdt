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


class GSet(CvRDT):
    def __init__(self, *, actor):
        self.actor = actor
        self.items = set()

    @property
    def value(self):
        return frozenset(self.items)

    def __le__(self, other: 'GSet') -> bool:
        return self.value <= other.value

    def merge(self, other: 'GSet') -> None:  # type: ignore
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

    def merge(self, other: 'TwoPhaseSet') -> None:  # type: ignore
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


class USet(CvRDT):
    # You must be careful using this directly.  You MUST never add the same
    # item twice.  I'm implementing this as way to implement the ORSet.
    def __init__(self, *, actor):
        self.actor = actor
        self.vclock = VClock()
        self.items = set()

    @property
    def value(self):
        return frozenset(self.items)

    def __le__(self, other: 'USet') -> bool:
        return self.vclock <= other.vclock

    def merge(self, other: 'USet') -> None:  # type: ignore
        if self.vclock >= other.vclock:
            # Our history contains all of others so we can stay the same.
            pass
        elif self.vclock < other.vclock:
            # other has seen events we haven't and all our events have been
            # witnessed by other; so we must simply take the state of other.
            self.items = set(other.items)
            self.vclock += other.vclock
        elif self.vclock // other.vclock:
            # We have diverging items; our assumption about unique items and
            # the precondition on 'remove' ensures that a replica cannot
            # remove an item unless its addition was in the history.
            self.items |= other.items
            self.vclock += other.vclock
        else:
            assert False

    def add(self, item) -> None:
        self.vclock = self.vclock.bump(self.actor)
        self.items.add(item)

    def remove(self, item) -> None:
        if item in self.items:
            self.vclock = self.vclock.bump(self.actor)
            self.items.remove(item)

    def __repr__(self):
        return f"<USet: {self.value}; {self.actor}, {self.vclock.simplified}>"


class ORSet(CvRDT):  # TODO: Do ORSet
    '''The Observed-Remove Set.

    '''
