#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#
from xotl.crdt.base import CvRDT
from xotl.crdt.clocks import VClock, Dot


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
    '''The USet.

    .. warning:: You must be careful using this directly.  You MUST never add
       the same item twice.  This as way to implement the `ORSet`:class:.

    '''
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
        '''Add `item` to the set.'''
        self.vclock = self.vclock.bump(self.actor)
        self.items.add(item)

    def remove(self, item) -> None:
        '''Remove `item` to the set.

        If `item` is not in the (at this replica) nothing happens.

        '''
        if item in self.items:
            self.vclock = self.vclock.bump(self.actor)
            self.items.remove(item)

    def __repr__(self):
        return f"<USet: {self.value}; {self.actor}, {self.vclock.simplified}>"


class ORSet(CvRDT):
    '''The Observed-Remove Set.

    '''
    def __init__(self, *, actor) -> None:
        self.actor = actor
        self.items = USet(actor=actor)
        self.ticks = 0

    def __le__(self, other: 'ORSet') -> bool:
        return self.items <= other.items

    def merge(self, other: 'ORSet') -> None:  # type: ignore
        self.items.merge(other.items)

    @property
    def value(self):
        return frozenset(item for item, _, _ in self.items.value)

    @property
    def dot(self) -> Dot:
        return self.items.vclock.find(self.actor)

    @property
    def dot_counter(self) -> int:
        try:
            return self.dot.counter
        except ValueError:
            return 0

    def add(self, item):
        '''Add `item` to the set.

        '''
        # USet requires unique items, we expect the actors are unique in the
        # cluster and each have an ever increasing tick.
        self.ticks += 1
        x = (item, self.actor, self.ticks)
        self.items.add(x)

    def remove(self, item):
        '''Remove `item` from the set.

        We remove the observed instances of `item` in this replica.  This
        means that an ``add(x)`` at one replica concurrent with a
        ``remove(x)`` at another, will result in the item being kept.

        '''
        xs = [x for x in self.items.value if x[0] == item]
        if xs:
            # I have to hack the internal VClock of 'self.items' to ensure
            # just a single bump.
            counter = self.dot_counter
            for x in xs:
                self.items.remove(x)
            object.__setattr__(self.dot, 'counter', counter + 1)

    def __repr__(self):
        return f"<ORSet: {self.value}; {self.actor}, {self.items}>"
