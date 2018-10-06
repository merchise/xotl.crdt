#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#
from xotl.crdt.base import CvRDT
from xotl.crdt.clocks import VClock, Dot, monotonic


class LWWRegister(CvRDT):
    '''The Last-Write-Wins Register.

    If two actors set a value concurrently (as per vector clock counter) and
    with the same time stamp.  The actor which is first in lexicographic order
    wins.

    '''
    def init(self):
        self.vclock = VClock([Dot(self.actor, 0, 0)])
        self.atom = None

    @property
    def value(self):
        return self.atom

    @property
    def dot(self) -> Dot:
        return self.vclock.find(self.actor)

    @property
    def timestamp(self) -> float:
        return self.dot.timestamp

    def set(self, value, *, _timestamp=None):
        '''Set the `value` of the register.

        `value` should be an immutable object.  Putting a mutable object may
        lead to unexpected behavior (specially if it implements an unsafe
        hash).

        '''
        hash(value)  # Check is immutable; mutable objs should raise an error
        if _timestamp is None:
            ts = max(self.dot.timestamp, monotonic())
        else:
            ts = _timestamp
        self.vclock = self.vclock.bump(self.actor, _timestamp=ts)
        self.atom = value

    def __le__(self, other: 'LWWRegister') -> bool:
        return self.vclock <= other.vclock

    def __lt__(self, other: 'LWWRegister') -> bool:
        return self.vclock < other.vclock

    def __gt__(self, other: 'LWWRegister') -> bool:
        return self.vclock > other.vclock

    def __ge__(self, other: 'LWWRegister') -> bool:
        return self.vclock >= other.vclock

    def __floordiv__(self, other: 'LWWRegister') -> bool:
        return self.vclock // other.vclock

    def __lshift__(self, other: 'LWWRegister') -> bool:
        '''True is `other` wins.

        `other` wins if:

        - its vector clock dominates ours (it descends from ours and knows
          even more than we do).

        - its vector clock is concurrent with ours but it's marked with a
          higher timestamp.

        '''
        if self.vclock < other.vclock:
            return True
        elif self.vclock > other.vclock:
            return False
        elif self.vclock // other.vclock or self.vclock == self.vclock:
            if self.timestamp < other.timestamp:
                return True
            elif self.timestamp > other.timestamp:
                return False
            else:
                return self.actor < other.actor
        else:
            assert False

    def merge(self, other: 'LWWRegister') -> None:  # type: ignore
        if self << other:
            assert not (other << self)
            self.atom = other.value
            # I need to trick the vclock to update the timestamp of the
            # winning node.
            self.vclock += other.vclock
            object.__setattr__(self.dot, 'timestamp', other.timestamp)
        else:
            ts = self.timestamp
            self.vclock += other.vclock
            object.__setattr__(self.dot, 'timestamp', ts)

    def __repr__(self):
        return f"<LWWRegister: {self.value}; {self.actor}, {self.vclock.simplified}>"

    def reset(self, value=None):
        '''Reset the internal state of value.

        This method should only be used within the boundaries of a
        coordination controlled layer.  Notice it may not be sufficient for a
        majority of the nodes to agree on the value, but the whole set of
        nodes.  You probably only need to call this when removing/adding an
        actor from the cluster.

        '''
        self.vclock = VClock()
        self.atom = value
