#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#
from hypothesis import strategies as st, assume
from hypothesis.stateful import Bundle, RuleBasedStateMachine, rule

from xotl.crdt.vclock import VectorClock
from xotl.crdt.cv import dump_state, perform_merge, get_value


class ModelCounter:
    def __init__(self):
        self.value = 0

    def incr(self):
        self.value += 1
        return self.value

    def decr(self):
        self.value -= 1
        return self.value

    def __repr__(self):
        return "<ModelCounter: {value}>".format(value=self.value)


class Replica:
    def __init__(self, actor, payload):
        self.actor = actor
        self.vector_clock = VectorClock()
        self._payload = payload

    def __repr__(self):
        return "<Replica of {payload!r}; in {actor} with {vc}>".format(
            payload=self._payload,
            actor=self.actor,
            vc=self.vector_clock
        )

    def incr(self):
        self.vector_clock = self.vector_clock.bump(self.actor)
        self._payload.incr()

    def decr(self):
        self.vector_clock = self.vector_clock.bump(self.actor)
        self._payload.decr()

    @property
    def value(self):
        return self._payload.value

    @value.setter
    def value(self, val):
        self._payload.value = val


class CounterComparison(RuleBasedStateMachine):
    def __init__(self):
        super().__init__()
        # The 'subject' is the thing we're testing, the model keeps track of
        # what the subject state should be.
        self.model = ModelCounter()
        # TODO: Replace all subjects for replicas of a distributed counter.
        self.subjects = (Replica('A', ModelCounter()),
                         Replica('B', ModelCounter()))

    commands = Bundle('commands')
    counter_commands = st.sampled_from(['incr', 'decr'])

    @rule(target=commands, cmd=counter_commands)
    def command(self, cmd):
        return cmd

    replicas = Bundle('replicas')
    process_names = st.sampled_from([0, 1])

    @rule(target=replicas, name=process_names)
    def replica(self, name):
        return self.subjects[name]

    @rule(cmd=commands, replica=replicas)
    def run_command(self, cmd, replica):
        if cmd == 'incr':
            replica.incr()
            self.model.incr()
        elif cmd == 'decr':
            replica.decr()
            self.model.decr()
        else:
            assert False

    @rule(receiver=replicas)
    def run_synchronize(self, receiver):
        # The merge is "local" operation.  The receiver may alter its the
        # state, the sender state is unaltered.
        #
        # But we have only two replicas, and the rule command always updates
        # the model counter, which means that after merging, the receiver must
        # have the same value as the model.
        if self.subjects[0] is not receiver:
            sender = self.subjects[0]
        else:
            sender = self.subjects[1]
        state = dump_state(sender)
        perform_merge(receiver, state)
        assert get_value(receiver) == self.model.value


TestCounter = CounterComparison.TestCase
