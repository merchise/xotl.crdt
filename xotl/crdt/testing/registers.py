#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#
from typing import Any
from dataclasses import dataclass, field

from xotl.crdt.register import LWWRegister
from xotl.crdt.testing.base import BaseCRDTMachine
from xotl.crdt.clocks import monotonic

from hypothesis import strategies as st, assume
from hypothesis.stateful import rule


atoms = (
    st.integers() |
    st.booleans() |
    st.text() |
    # float('nan') == float('nan') is False
    st.floats(allow_nan=False)
)


# I'm splitting the concurrent from the non-concurrent machinery.  Because
# using a strictly monotonic time function allows for this simple test-model:
#
#     Time     Replica 1      Replica 2  ...     Model
#     1        set to x                          x
#     2                       set to y           y
#
# There's no problem to update the Model to y, because Time is total, even
# though the vector clocks of the replicas are concurrent ([1, 0] and [0, 1])
# their timestamp makes Replica 2 a winner.
#
# The problem happens with:
#
#     Time     Replica 1      Replica 2  ...     Model
#     1        set to x       set to y           ?
#
# What is the right value for Model?  Worst yet with three replicas:
#
#     Time     Replica 1      Replica 2   Replica 3     Model
#     1        set to x       set to y                  ?
#     2                       set to z    set to a      ?
#


@dataclass
class Register:
    value: Any = field(default=None)  # type: ignore
    timestamp: float = field(default=0)  # type: ignore
    actor: str = field(default=None)     # type: ignore

    def set(self, value, timestamp=None, actor=None):
        '''Set the register's value.

        If `timestamp` is none defaults the result of
        `~xotl.crdt.clocks.monotonic`:func:.

        The value is only updated if `timestamp` is greater than the last
        recorded timestamp; or the timestamp is the same but the actor is
        greater.

        Return True if the value was updated.

        '''
        if timestamp is None:
            timestamp = monotonic()
        if timestamp > self.timestamp:
            self.value = value
            self.timestamp = timestamp
            self.actor = actor
            return True
        elif timestamp == self.timestamp:
            if self.actor is None or actor > self.actor:
                self.value = value
                self.timestamp = timestamp
                self.actor = actor
                return True
        return False


class BaseLWWRegisterMachine(BaseCRDTMachine):
    def __init__(self):
        super().__init__()
        # The 'subject' is the thing we're testing, the model keeps track of
        # what the subject state should be.
        self.model = Register()
        self.subjects = self.create_subjects(LWWRegister)


class LWWRegisterMachine(BaseLWWRegisterMachine):
    '''A simple LWWRegister stateful test machine.

    Since we run tests in a single process, each call to `run_set`:meth:
    happens after the previous, so we're allow to update the test-model with
    our value.

    See `LWWRegisterConcurrentMachine`:class: for a machine that simulate
    concurrent and conflicting updates.

    '''
    @rule(replica=BaseCRDTMachine.replicas, value=atoms)
    def run_set(self, replica, value):
        '''Set `value` in a single replica.'''
        replica.set(value)
        assert value == replica.value
        self.model.set(value)


class LWWRegisterConcurrentMachine(BaseLWWRegisterMachine):
    '''A concurrent LWWRegister stateful test machine.

    '''
    def __init__(self):
        super().__init__()
        self.time = 0

    @rule(replica=BaseCRDTMachine.replicas, value=atoms)
    def run_possibly_concurrent_set(self, replica, value):
        '''Set two different values in two replicas at the same time.

        In order to ensure that the replicas truly diverge at `set`, we call
        `run_synchronize`:meth: on both replicas before setting the new value.

        '''
        if self.model.set(value, timestamp=self.time, actor=replica.actor):
            replica.set(value, _timestamp=self.time)

    @rule()
    def tick(self):
        self.time += 1
