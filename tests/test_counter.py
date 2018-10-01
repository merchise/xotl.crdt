#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#
import pickle
from hypothesis import strategies as st
from hypothesis.stateful import Bundle, RuleBasedStateMachine, rule

from xotl.crdt.base import reconstruct
from xotl.crdt.counter import GCounter, PNCounter


class ModelCounter:
    def __init__(self):
        self.value = 0

    def incr(self):
        self.value += 1
        return self.value

    def decr(self):
        self.value -= 1

    def __repr__(self):
        return "<ModelCounter: {value}>".format(value=self.value)


REPLICA_NODES = list(range(5))


class GCounterComparison(RuleBasedStateMachine):
    def __init__(self):
        super().__init__()
        # The 'subject' is the thing we're testing, the model keeps track of
        # what the subject state should be.
        self.model = ModelCounter()
        # TODO: Replace all subjects for replicas of a distributed counter.
        self.subjects = tuple(
            GCounter(actor=f'R{i}') for i in REPLICA_NODES
        )
        self.save_state()

    # @rule()
    def save_state(self):
        self.data = pickle.dumps((self.model, self.subjects),
                                 pickle.HIGHEST_PROTOCOL)

    # @rule()
    def load_state(self):
        self.model, self.subjects = pickle.loads(self.data)

    replicas = Bundle('replicas')
    process_names = st.sampled_from(REPLICA_NODES)

    @rule(target=replicas, name=process_names)
    def replica(self, name):
        return self.subjects[name]

    @rule(replica=replicas)
    def run_incr(self, replica):
        value = replica.value
        replica.incr()
        assert value + 1 == replica.value
        self.model.incr()

    @rule(receiver=replicas)
    def run_synchronize(self, receiver):
        # Since any incr may have been done in any replica, we need to merge
        # from all other replicas to actually the get the model value.
        senders = [which for which in self.subjects if receiver is not which]
        for sender in senders:
            state = sender.state
            receiver.merge(reconstruct(state))
        assert receiver.value == self.model.value


TestGCounter = GCounterComparison.TestCase


class PNCounterComparison(RuleBasedStateMachine):
    def __init__(self):
        super().__init__()
        # The 'subject' is the thing we're testing, the model keeps track of
        # what the subject state should be.
        self.model = ModelCounter()
        # TODO: Replace all subjects for replicas of a distributed counter.
        self.subjects = tuple(
            PNCounter(actor=f'R{i}') for i in REPLICA_NODES
        )
        self.save_state()

    # @rule()
    def save_state(self):
        self.data = pickle.dumps((self.model, self.subjects),
                                 pickle.HIGHEST_PROTOCOL)

    # @rule()
    def load_state(self):
        self.model, self.subjects = pickle.loads(self.data)

    replicas = Bundle('replicas')
    process_names = st.sampled_from(REPLICA_NODES)

    @rule(target=replicas, name=process_names)
    def replica(self, name):
        return self.subjects[name]

    @rule(replica=replicas)
    def run_incr(self, replica):
        value = replica.value
        replica.incr()
        assert value + 1 == replica.value
        self.model.incr()

    @rule(replica=replicas)
    def run_decr(self, replica):
        value = replica.value
        replica.decr()
        assert value - 1 == replica.value
        self.model.decr()

    @rule(receiver=replicas)
    def run_synchronize(self, receiver):
        senders = [which for which in self.subjects if receiver is not which]
        for sender in senders:
            state = sender.state
            receiver.merge(reconstruct(state))
        assert receiver.value == self.model.value


TestPNCounter = PNCounterComparison.TestCase
