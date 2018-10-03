#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#
from copy import deepcopy
from random import shuffle
from xotl.crdt.base import reconstruct

from hypothesis import strategies as st
from hypothesis.stateful import Bundle, RuleBasedStateMachine, rule


REPLICA_NODES = list(range(5))


class BaseCRDTMachine(RuleBasedStateMachine):
    '''Base CRDT rule-based state machine.

    It defines the `~hypothesis.stateful.Bundle`:class: 'replica' that chooses
    any of the replicas under test.

    Also defines the rule `run_synchronize` which receives a replica that will
    receive the state of all other replicas merge it with its own state and
    compare its value with model's value.

    Subclasses must implement an ``__init__`` that sets attributes ``model``
    and ``subjects``.  You may build the subjects with method
    `create_subjects`:meth:.

    '''
    replicas = Bundle('replicas')
    process_names = st.sampled_from(REPLICA_NODES)

    @rule(target=replicas, name=process_names)
    def replica(self, name):
        return self.subjects[name]

    @rule(receiver=replicas)
    def run_synchronize(self, receiver):
        '''Command that synchronizes `receiver`.

        `receiver` is any of the replica objects; this command simulates the
        actions of it receiving the state of all other replicas *in any order*
        and compares the resulting state with expected state.

        '''
        senders = [which for which in self.subjects if receiver is not which]
        shuffle(senders)
        before_merge = []
        for sender in senders:
            state = sender.state
            before_merge.append(deepcopy(receiver))
            receiver.merge(reconstruct(state))
            assert sender <= receiver
        model = self.model
        assert receiver.value == model.value, \
            f"{receiver.value} != {model.value}"

    def create_subjects(self, cls):
        '''Return a tuple of instances of `cls`.

        :param cls: a callable that takes keyword argument 'actor' and returns
                    a replica object.

        :returns: a tuple containing the result of several calls to `cls` with
                  different actor names.

        '''
        return tuple(cls(actor=f'R{i}') for i in REPLICA_NODES)
