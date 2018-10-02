#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#
from xotl.crdt.counter import GCounter, PNCounter
from xotl.crdt.testing.base import BaseCRDTMachine

from hypothesis.stateful import rule


class ModelCounter:
    '''A simple model counter.

    Both `GCounterMachine`:class: and `PNCounterMachine`:class: use a single
    instance of this model to keep the expected state of the set of replicas.

    '''
    def __init__(self):
        self.value = 0

    def incr(self):
        '''Increment the model's value by 1.'''
        self.value += 1
        return self.value

    def decr(self):
        '''Decrement the model's value by 1.'''
        self.value -= 1
        return self.value

    def __repr__(self):
        return "<ModelCounter: {value}>".format(value=self.value)


class CounterMachine(BaseCRDTMachine):
    def __init__(self):
        super().__init__()
        # The 'subject' is the thing we're testing, the model keeps track of
        # what the subject state should be.
        self.model = ModelCounter()

    @rule(replica=BaseCRDTMachine.replicas)
    def run_incr(self, replica):
        '''Increment the value of a single random `replica`.

        We also increment the model's.

        '''
        value = replica.value
        replica.incr()
        assert value + 1 == replica.value
        self.model.incr()


class GCounterMachine(CounterMachine):
    def __init__(self):
        super().__init__()
        self.subjects = self.create_subjects(GCounter)


class PNCounterMachine(CounterMachine):
    def __init__(self):
        super().__init__()
        self.subjects = self.create_subjects(PNCounter)

    @rule(replica=BaseCRDTMachine.replicas)
    def run_decr(self, replica):
        '''Decrement the value of a single random `replica`.

        We also decrement the model's.

        '''
        value = replica.value
        replica.decr()
        assert value - 1 == replica.value
        self.model.decr()
