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
from xoutil.future.itertools import continuously_slides as slide, product

from xotl.crdt.base import from_state, get_state, Process

from hypothesis import strategies as st
from hypothesis.stateful import Bundle, RuleBasedStateMachine, rule


REPLICA_NODES = list(range(5))


class BaseCRDTMachine(RuleBasedStateMachine):
    '''Base CRDT machine.

    It defines the `~hypothesis.stateful.Bundle`:class: 'replica' that chooses
    any of the replicas under test.  It doesn't perform any assertions.

    See subclasses `ModelBasedCRDTMachine`:class: and
    `SyncBasedCRDTMachine`:class:.

    '''
    replicas = Bundle('replicas')
    process_names = st.sampled_from(REPLICA_NODES)

    @rule(target=replicas, name=process_names)
    def replica(self, name):
        return self.subjects[name]

    @rule(crdt=replicas)
    def from_state_get_state(self, crdt):
        assert crdt == from_state(get_state(crdt))

    def create_subjects(self, cls):
        '''Return a tuple of instances of `cls`.

        :param cls: a callable that takes keyword argument 'process' and
                    returns a replica object.

        :returns: a tuple containing the result of several calls to `cls` with
                  different process names.

        '''
        return tuple(cls(process=Process(f'R{i}', i)) for i in REPLICA_NODES)


class ModelBasedCRDTMachine(BaseCRDTMachine):
    '''Model based CRDT rule-based state machine.

    Defines the rule `run_synchronize` which receives a replica that will
    receive the state of all other replicas merge it with its own state and
    compare its value with model's value.

    Subclasses must implement an ``__init__`` that sets attributes ``model``
    and ``subjects``.  You may build the subjects with method
    `~BaseCRDTMachine.create_subjects`:meth:.

    '''
    @rule(receiver=BaseCRDTMachine.replicas)
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
            state = get_state(sender)
            before_merge.append(deepcopy(receiver))
            receiver.merge(from_state(state))
            assert sender <= receiver
        model = self.model
        assert receiver.value == model.value, \
            f"{receiver.value} != {model.value}"


class SyncBasedCRDTMachine(BaseCRDTMachine):
    '''Synchronization based state machine.

    Subclasses must implement an ``__init__`` the to the attributes
    ``subjects``.  You may build the subjects with method
    `~BaseCRDTMachine.create_subjects`:meth:.

    '''
    @rule()
    def run_synchronize(self):
        '''Synchronize all replicas and test they reach a consistent value.

        All replicas are *randomly* placed in a line::

             R1  R3  R0  R2

        We transmit the state from the first to the second (``R1 -> R3``),
        then the second to the third (``R3 -> R0``), and so on.  Afterwards,
        we go backwards (``R2 -> R0 ...``) in a second pass.

        When the dust is settled we check all replicas have agreed in the
        final value, and that for any pair of replicas `a` and `b`, ``a <= b
        <= a`` is True.

        Notice that there are replicas who never exchange messages; yet they
        must have reached the same conclusion.

        '''
        replicas = [which for which in self.subjects]
        shuffle(replicas)
        before = deepcopy(replicas)  # noqa
        for sender, receiver in slide(replicas):
            state = get_state(sender)
            receiver.merge(from_state(state))
            assert sender <= receiver
        for sender, receiver in slide(reversed(replicas)):
            state = get_state(sender)
            receiver.merge(from_state(state))
            assert sender <= receiver
        first = replicas[0]
        assert all(r.value == s.value for r, s in product(replicas, replicas))
        print(f'Agreement reached: {first.value}')
        assert all(r <= s <= r for r, s in product(replicas, replicas))

    def teardown(self):
        # Most likely, subclasses won't make checks; so let's perform a last
        # sync before finishing.
        self.run_synchronize()
        super().teardown()
