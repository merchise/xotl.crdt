#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#
from typing import Any
from time import monotonic
from dataclasses import dataclass, field

from xotl.crdt.register import LWWRegister
from xotl.crdt.testing.base import BaseCRDTMachine

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

    def set(self, value):
        self.value = value


class LWWRegisterMachine(BaseCRDTMachine):
    def __init__(self):
        super().__init__()
        # The 'subject' is the thing we're testing, the model keeps track of
        # what the subject state should be.
        self.model = Register()
        self.subjects = self.create_subjects(LWWRegister)

    @rule(replica=BaseCRDTMachine.replicas, value=atoms)
    def run_set(self, replica, value):
        '''Set `value` in a single replica.'''
        replica.set(value)
        assert value == replica.value
        self.model.set(value)

    @rule(replica1=BaseCRDTMachine.replicas, replica2=BaseCRDTMachine.replicas,
          value1=atoms, value2=atoms)
    def run_set_concurrently(self, replica1, replica2, value1, value2):
        '''Set two different values in two replicas at the same time.

        In order to ensure some consistency, we call `run_synchronize`:meth:
        on both replicas before setting the new value.

        '''
        assume(replica1 is not replica2 and value1 != value2)
        self.run_synchronize(replica1)
        self.run_synchronize(replica2)
        ts = monotonic()
        replica1.set(value1, _timestamp=ts)
        replica2.set(value2, _timestamp=ts)
        assert replica1.timestamp == replica2.timestamp == ts
        if replica1 <= replica2:
            self.model.set(value2)
        else:
            self.model.set(value1)
