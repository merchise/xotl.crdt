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


@dataclass
class Register:
    value: Any = field(default=None)  # type: ignore
    timestamp: float = field(default=0)  # type: ignore

    def set(self, value, timestamp=None):
        '''Set the register's value.

        If `timestamp` is none defaults the result of
        `~xotl.crdt.clocks.monotonic`:func:.

        The value is only updated if `timestamp` is greater than the last
        recorded timestamp.

        '''
        if timestamp is None:
            timestamp = monotonic()
        if timestamp > self.timestamp:
            self.value = value
            self.timestamp = timestamp


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

    @rule(replica1=BaseCRDTMachine.replicas, replica2=BaseCRDTMachine.replicas,
          value1=atoms, value2=atoms)
    def run_set_concurrently(self, replica1, replica2, value1, value2):
        '''Set two different values in two replicas at the same time.

        In order to ensure that the replicas truly diverge at `set`, we call
        `run_synchronize`:meth: on both replicas before setting the new value.

        '''
        assume(replica1 is not replica2 and value1 != value2)
        self.run_synchronize(replica1)
        self.run_synchronize(replica2)
        assert replica1.vclock <= replica2.vclock <= replica1.vclock

        ts = self.tick()

        replica1.set(value1, _timestamp=ts)
        assert replica1.timestamp == ts,\
            f"replica.timestamp {replica1.timestamp} != {ts}"

        replica2.set(value2, _timestamp=ts)
        assert replica2.timestamp == ts,\
            f"replica.timestamp {replica2.timestamp} != {ts}"

        assert replica1.vclock // replica2.vclock

        assert (replica1 << replica2) == (replica1.actor < replica2.actor)
        if replica1.actor < replica2.actor:
            self.model.set(value2, timestamp=ts)
        else:
            self.model.set(value1, timestamp=ts)

    def tick(self):
        result = self.time
        self.time += 1
        return result
