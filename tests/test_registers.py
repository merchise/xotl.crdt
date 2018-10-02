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

from hypothesis import strategies as st, assume
from hypothesis.stateful import Bundle, RuleBasedStateMachine, rule

from xotl.crdt.base import reconstruct
from xotl.crdt.register import LWWRegister


@dataclass
class Register:
    value: Any = field(default=None)

    def set(self, value):
        self.value = value


REPLICA_NODES = list(range(5))

atoms = (
    st.integers() |
    st.booleans() |
    st.text() |
    # float('nan') == float('nan') is False
    st.floats(allow_nan=False)
)

small_integers = st.integers(min_value=0, max_value=100)


class LWWRegisterMachine(RuleBasedStateMachine):
    def __init__(self):
        super().__init__()
        # The 'subject' is the thing we're testing, the model keeps track of
        # what the subject state should be.
        self.model = Register()
        # TODO: Replace all subjects for replicas of a distributed counter.
        self.subjects = tuple(
            LWWRegister(actor=f'R{i}') for i in REPLICA_NODES
        )

    replicas = Bundle('replicas')
    process_names = st.sampled_from(REPLICA_NODES)

    @rule(target=replicas, name=process_names)
    def replica(self, name):
        return self.subjects[name]

    @rule(replica=replicas, value=atoms)
    def run_set(self, replica, value):
        replica.set(value)
        assert value == replica.value
        self.model.set(value)

    @rule(replica1=replicas, replica2=replicas,
          value1=atoms, value2=atoms)
    def run_set_concurrently(self, replica1, replica2, value1, value2):
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

    @rule(receiver=replicas)
    def run_synchronize(self, receiver):
        # Since any incr may have been done in any replica, we need to merge
        # from all other replicas to actually the get the model value.
        senders = [which for which in self.subjects if receiver is not which]
        for sender in senders:
            state = sender.state
            receiver.merge(reconstruct(state))
        assert receiver.value == self.model.value


TestLWWRegister = LWWRegisterMachine.TestCase
