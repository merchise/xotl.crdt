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

from xotl.crdt.cv.counter import Counter


class ModelCounter:
    def __init__(self):
        self.value = 0

    def incr(self):
        self.value += 1
        return self.value

    def __repr__(self):
        return "<ModelCounter: {value}>".format(value=self.value)


class CounterComparison(RuleBasedStateMachine):
    def __init__(self):
        super().__init__()
        # The 'subject' is the thing we're testing, the model keeps track of
        # what the subject state should be.
        self.model = ModelCounter()
        # TODO: Replace all subjects for replicas of a distributed counter.
        self.subjects = (Counter('A'), Counter('B'))

    commands = Bundle('commands')
    counter_commands = st.sampled_from(['incr', ])

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
            value = replica.value
            replica.incr()
            assert value + 1 == replica.value
            self.model.incr()
        else:
            assert False

    @rule(receiver=replicas)
    def run_synchronize(self, receiver):
        # The merge is a "local" operation.  The receiver may alter its the
        # state, the sender state is unaltered.  But we have only two
        # replicas, and the rule command always updates the model counter,
        # which means that after merging, the receiver must have the same
        # value as the model.
        if self.subjects[0] is not receiver:
            sender = self.subjects[0]
        else:
            sender = self.subjects[1]
        state = sender.state
        receiver.merge(state)
        assert receiver.value == self.model.value


TestCounter = CounterComparison.TestCase
