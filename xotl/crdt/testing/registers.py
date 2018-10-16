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
from xotl.crdt.testing.base import (
    ModelBasedCRDTMachine,
    SyncBasedCRDTMachine
)
from time import monotonic

from hypothesis import strategies as st
from hypothesis.stateful import rule


atoms = (
    st.integers() |
    st.booleans() |
    # float('nan') == float('nan') is False
    st.floats(allow_nan=False)
)

molecules = st.tuples(atoms)
values = atoms | molecules


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
# The problem happens with the following:
#
#    Time   R0           R1           R2           Model
#    0      set to 1                               1
#    0                   set to 2                  2
#
# At this moment synchronize R2 merging R0 first: 'R2 << R1' is True because
# R2's vclock is empty.  But after the merge, R2's is concurrent with R1 and
# 'R1 << R2' so the value of R1 is discarded; R2 keeps the value 1 (doesn't
# agree with Model) but R2 is now a descedant of R1 and R0.
#
# If we now merge R1 with R2 it will adjust it's value to 1.
#
# So I think, the way to test LWWRegister is to perform a full-synchronization
# and test that all replicas reached the same value.


@dataclass
class Register:
    value: Any = field(default=None)  # type: ignore
    timestamp: float = field(default=0)  # type: ignore
    process: str = field(default=None)     # type: ignore

    def set(self, value, timestamp=None, process=None):
        '''Set the register's value.

        If `timestamp` is none defaults the result of
        `~xotl.crdt.clocks.monotonic`:func:.

        The value is only updated if `timestamp` is greater than the last
        recorded timestamp; or the timestamp is the same but the process is
        greater.

        Return True if the value was updated.

        '''
        if timestamp is None:
            timestamp = monotonic()
        if timestamp > self.timestamp:
            self.value = value
            self.timestamp = timestamp
            self.process = process
            return True
        elif timestamp == self.timestamp:
            if self.process is None or process > self.process:
                self.value = value
                self.timestamp = timestamp
                self.process = process
                return True
        return False


class LWWRegisterMachine(ModelBasedCRDTMachine):
    '''A simple LWWRegister stateful test machine.

    Since we run tests in a single process, each call to `run_set`:meth:
    happens after the previous, so we're allowed to update the test-model with
    our value.

    See `LWWRegisterConcurrentMachine`:class: for a machine that simulate
    concurrent and conflicting updates.

    '''
    def __init__(self):
        super().__init__()
        self.model = Register()
        self.subjects = self.create_subjects(LWWRegister)

    @rule(replica=ModelBasedCRDTMachine.replicas, value=values)
    def run_set(self, replica, value):
        '''Set `value` in a single replica.'''
        ts = monotonic()
        replica.set(value, _timestamp=ts)
        assert value == replica.value
        self.model.set(value, timestamp=replica.timestamp,
                       process=replica.process)


class LWWRegisterConcurrentMachine(SyncBasedCRDTMachine):
    '''A concurrent LWWRegister stateful test machine.

    '''
    def __init__(self):
        super().__init__()
        self.time = 0
        self.subjects = self.create_subjects(LWWRegister)
        print('**************** New case ********************')

    @rule(replica=SyncBasedCRDTMachine.replicas, value=values)
    def run_possibly_concurrent_set(self, replica, value):
        '''Set value at a replica at the current time.

        Current time is only increased by calling `tick`:meth:.

        Notice that two consecutive calls with different replicas and values
        result in a (temporary) divergence of the replicas.

        '''
        print(f'Set value {value} at replica {replica.process} at {self.time}')
        replica.set(value, _timestamp=self.time)

    @rule()
    def tick(self):
        'Increase the current timer by 1.'
        self.time += 1
        print(f'Tick {self.time - 1} -> {self.time}')

    def teardown(self):
        print('---------------- End case --------------------')
        super().teardown()
