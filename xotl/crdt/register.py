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


class LWWRegister(CvRDT):
    '''The Last-Write-Wins Register.

    If two actors set a value concurrently (as per vector clock counter) and
    with the same time stamp.  The actor which is first in lexicographic order
    wins.

    '''
    def __init__(self, *, actor: str) -> None:
        self.actor = actor
        self.vclock = VClock([Dot(actor, 0, 0)])
        self.atom = None

    @property
    def value(self):
        return self.atom

    @property
    def timestamp(self) -> float:
        dot = self.vclock.find(self.actor)
        return dot.timestamp

    def set(self, value, *, _timestamp=None):
        hash(value)  # Check is immutable; mutable objs should raise an error
        self.vclock = self.vclock.bump(self.actor, _timestamp=_timestamp)
        self.atom = value

    def __le__(self, other: 'LWWRegister') -> bool:
        return (self.vclock <= other.vclock or
                self.timestamp <= other.timestamp or
                self.actor <= other.actor)

    def merge(self, other: 'LWWRegister') -> None:  # type: ignore
        if self <= other:
            self.atom = other.value
        t1, t2 = self.timestamp, other.timestamp
        self.vclock = self.vclock.merge(other.vclock)
        # I need to trick the vclock to update the timestamp of the selected
        # winning node.
        dot = self.vclock.find(self.actor)
        object.__setattr__(dot, 'timestamp', max(t1, t2))

    def __repr__(self):
        return f"<LWWRegister: {self.value}; {self.vclock}>"
