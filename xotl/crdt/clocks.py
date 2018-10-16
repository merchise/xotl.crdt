#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#
'''Implements the Vector Clocks.

'''
from typing import Tuple, Sequence

from collections import deque
from dataclasses import dataclass
from itertools import groupby
from operator import attrgetter

from xotl.crdt.base import Process


@dataclass(frozen=True, order=False, eq=True)
class Dot:
    '''A component on the vector clock.

    '''
    # process names should be unique across all processes
    process: Process
    counter: int


@dataclass(frozen=True, init=False)
class VClock:
    dots: Tuple[Dot, ...]

    def __init__(self, dots: Sequence[Dot] = None) -> None:
        if dots:
            assert len([d.process for d in dots]) == len({d.process for d in dots}), \
                f'Repeated processes in {dots!r}'
        # Avoid silly counters.
        dots = [d for d in (dots or []) if d.counter >= 0]
        dots.sort(key=attrgetter('process'))
        object.__setattr__(self, 'dots', tuple(dots))

    def __ge__(self, other: 'VClock') -> bool:
        '''True if this vclock descends (happens after) from other.'''
        if isinstance(other, VClock):
            # Remember, that '.dots' are ordered by 'process'; with this in
            # mind the algorithm is easy to follow.
            #
            # This algorithm consider missing processes as if they were there
            # with counter 0.  But, then if any process is present with
            # counter 0, we should remove it from the dots.
            theirs = deque(d for d in other.dots if d.counter)
            ours = deque(d for d in self.dots if d.counter)
            if not theirs:
                return True  # Every VC decends from the empty one.
            elif not ours:
                return False  # Empty VC doesnt descent from non-empty ones.
            result = True
            while theirs and ours and result:
                their_dot = theirs.popleft()
                our_dot = ours.popleft()
                while ours and their_dot.process != our_dot.process:
                    our_dot = ours.popleft()
                if our_dot.process == their_dot.process:
                    result = our_dot.counter >= their_dot.counter
                else:
                    assert not ours
                    result = False
            return result and not theirs
        else:
            return NotImplemented

    def __eq__(self, other: 'VClock') -> bool:  # type: ignore
        '''True if this vclock is the same as other.'''
        if isinstance(other, VClock):
            # The looping structure is similar to __ge__; however, we must
            # ensure every process present in `self` is also present in
            # `other` with the same counter, thus the stronger conditional in
            # the 'return'.  This is faster than ``self >= other >= self``.
            theirs = deque(d for d in other.dots if d.counter)
            ours = deque(d for d in self.dots if d.counter)
            result = True
            while theirs and ours and result:
                their_dot = theirs.popleft()
                our_dot = ours.popleft()
                while ours and their_dot.process != our_dot.process:
                    our_dot = ours.popleft()
                if our_dot.process == their_dot.process:
                    result = our_dot.counter == their_dot.counter
                else:
                    assert not ours
                    result = False
            return result and not ours and not theirs
        else:
            return NotImplemented

    def __floordiv__(self, other: 'VClock') -> bool:
        '''True if neither self descends from other nor other from self.

        This means that self and other represent concurrent events in
        different replicas.  In some texts this is represented as ``a || b``,
        here we have ``a // b``.

        '''
        return not (self <= other) and not (other <= self)

    def __le__(self, other: 'VClock') -> bool:
        return other >= self

    def __gt__(self, other):
        '''True if ``self >= other`` but not viceversa.'''
        if isinstance(other, VClock):
            # Is this the same as 'self != other and self >= other'?
            return not (other >= self) and self >= other
        else:
            return NotImplemented

    def __lt__(self, other):
        '''True if ``self <= other`` but not viceversa.'''
        if isinstance(other, VClock):
            # Is this the same as 'self != other and self <= other'?
            return not (other <= self) and self <= other
        else:
            return NotImplemented

    def __bool__(self):
        return bool(self.dots)

    def merge(self, *others: 'VClock') -> 'VClock':
        '''Return the least possible common descendant.'''
        from heapq import merge
        get_process = attrgetter('process')
        groups = groupby(
            merge(self.dots, *(o.dots for o in others), key=get_process),
            key=get_process
        )
        dots = [
            Dot(process, max(d.counter for d in lgroup))
            for process, group in groups
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

    def bump(self, process):
        '''Return a new VC with the process's counter increased.'''
        try:
            i = index(self.dots, process, key=attrgetter('process'))
            dots = list(self.dots)
            dots[i] = Dot(process, dots[i].counter + 1)
        except ValueError:
            from heapq import merge
            new = Dot(process, 1)
            dots = merge(self.dots, [new], key=attrgetter('process'))
        result = VClock()
        object.__setattr__(result, 'dots', tuple(dots))
        return result

    def find(self, process: Process) -> Dot:
        i = index(self.dots, process, key=attrgetter('process'))
        return self.dots[i]

    @property
    def simplified(self):
        return VClock([d for d in self.dots if d.counter])

    def reset(self):
        '''Reset the clock.

        Basically forget about all the clock state.

        '''
        self.dots = ()


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
