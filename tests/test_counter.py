#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#
from hypothesis import strategies as st
from hypothesis.stateful import Bundle, RuleBasedStateMachine, rule

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
        # The merge is a "local" operation.  The receiver may alter its the
        # state, the sender state is unaltered.  But we have only two
        # replicas, and the rule command always updates the model counter,
        # which means that after merging, the receiver must have the same
        # value as the model.
        senders = [which for which in self.subjects if receiver is not which]
        for sender in senders:
            state = sender.state
            receiver.merge(state)
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
            receiver.merge(state)
        assert receiver.value == self.model.value


TestPNCounter = PNCounterComparison.TestCase
