#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#
'''Implements the Vector Clocks and monotonicity.

'''
from typing import Tuple, Sequence

from collections import deque
from dataclasses import dataclass
from itertools import groupby
from operator import attrgetter
from time import monotonic


@dataclass(frozen=True)
class Dot:
    # actor names should be unique across all actors
    actor: str
    counter: int
    timestamp: int  # this will be the result of monotonic.

    @property
    def core(self):
        return (self.actor, self.counter)

    def __eq__(self, other):
        if isinstance(other, Dot):
            return self.core == other.core
        else:
            return NotImplemented

    def __lt__(self, other):
        if isinstance(other, Dot) and self.actor == other.actor:
            return self.counter < other.counter
        else:
            return NotImplemented

    def __le__(self, other):
        if isinstance(other, Dot) and self.actor == other.actor:
            return self.counter <= other.counter
        else:
            return NotImplemented

    def __gt__(self, other):
        if isinstance(other, Dot) and self.actor == other.actor:
            return self.counter > other.counter
        else:
            return NotImplemented

    def __ge__(self, other):
        if isinstance(other, Dot) and self.actor == other.actor:
            return self.counter >= other.counter
        else:
            return NotImplemented

    def __repr__(self):
        return f'<dot: {self.actor}, {self.counter}, {self.timestamp}>'


@dataclass(frozen=True, init=False)
class VClock:
    dots: Tuple[Dot, ...]

    def __init__(self, dots: Sequence[Dot] = None) -> None:
        if dots:
            assert len([d.actor for d in dots]) == len({d.actor for d in dots}), \
                f'Repeated actors in {dots!r}'
        object.__setattr__(
            self,
            'dots',
            tuple(sorted(dots or [], key=attrgetter('actor')))
        )

    def descends(self, other: 'VClock') -> bool:
        '''True if self descends from other.

        Timestamps in dots are irrelevant, the only things that matter are
        actors and counters.

        '''
        if isinstance(other, VClock):
            if not other.dots:
                return True  # Every VC decends from the empty one.
            elif not self.dots:
                return False  # Empty VC doesnt descent from non-empty ones.
            # Remember, that '.dots' are ordered by 'actor'; with this in mind
            # the algorithm is easy to follow.
            theirs = deque(other.dots)
            ours = deque(self.dots)
            result = True
            while theirs and ours and result:
                their_dot = theirs.pop()
                our_dot = ours.pop()
                while ours and their_dot.actor != our_dot.actor:
                    our_dot = ours.pop()
                if our_dot.actor == their_dot.actor:
                    result = our_dot.counter >= their_dot.counter
                else:
                    assert not ours
                    result = False
            return result and not theirs and not ours
        else:
            raise TypeError(f"Invalid type for {other}")

    def __bool__(self):
        return bool(self.dots)

    def dominates(self, other: 'VClock') -> bool:
        '''True if self descends from other, but not viceversa.'''
        if isinstance(other, VClock):
            return self >= other and not (other >= self)
        else:
            raise TypeError(f"Invalid type for {other}")

    def __le__(self, other):
        return other >= self

    def __ge__(self, other):
        try:
            return self.descends(other)
        except TypeError:
            return NotImplemented

    def __lt__(self, other):
        return other >= self and not (self == other)

    def __eq__(self, other):
        if isinstance(other, VClock):
            return self.dots == other.dots
        else:
            return NotImplemented

    def merge(self, *others: 'VClock') -> 'VClock':
        '''Return the least possible common descendant.'''
        from heapq import merge
        get_actor = attrgetter('actor')
        groups = groupby(
            merge(self.dots, *(o.dots for o in others), key=get_actor),
            key=get_actor
        )
        dots = [
            Dot(actor,
                max(d.counter for d in lgroup),
                max(d.timestamp for d in lgroup))
            for actor, group in groups
            # convert group to a list so that we can do the double max above
            for lgroup in (list(group), )
        ]
        # Silly little trick to avoid sorting what is sorted already
        result = VClock()
        object.__setattr__(result, 'dots', tuple(dots))
        return result

    def __add__(self, other):
        'Return the merge with other.'
        return self.merge(other)

    def bump(self, actor, *, _timestamp=None):
        'Return a new VC with the actor increased'
        ts = _timestamp or monotonic()
        try:
            i = index(self.dots, actor, key=attrgetter('actor'))
            dots = list(self.dots)
            if _timestamp is None:
                # We should never go back in time, unless we're told to do so
                # (but there be dragons).
                ts = max(ts, dots[i].timestamp)
            dots[i] = Dot(actor, dots[i].counter + 1, ts)
        except ValueError:
            from heapq import merge
            new = Dot(actor, 1, ts)
            dots = merge(self.dots, [new], key=attrgetter('actor'))
        result = VClock()
        object.__setattr__(result, 'dots', tuple(dots))
        return result

    def find(self, actor) -> Dot:
        i = index(self.dots, actor, key=attrgetter('actor'))
        return self.dots[i]


def index(a, x, key=None):
    'Locate the leftmost value exactly equal to x'
    from bisect import bisect_left
    if not key:
        i = bisect_left(a, x)
        if i != len(a) and a[i] == x:
            return i
    else:
        i = bisect_left([key(y) for y in a], x)
        if i != len(a) and key(a[i]) == x:
            return i
    raise ValueError
