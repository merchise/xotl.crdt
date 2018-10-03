#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#
from xotl.crdt.sets import GSet
from xotl.crdt.testing.base import ModelBasedCRDTMachine

from hypothesis import strategies as st
from hypothesis.stateful import rule


atoms = (
    st.integers() |
    st.booleans() |
    # float('nan') == float('nan') is False
    st.floats(allow_nan=False)
)

molecules = st.tuples(atoms)
values = atoms | molecules


class Set:
    def __init__(self):
        self.value = set()

    def add(self, item):
        self.value.add(item)


class GSetMachine(ModelBasedCRDTMachine):
    def __init__(self):
        super().__init__()
        self.model = Set()
        self.subjects = self.create_subjects(GSet)

    @rule(replica=ModelBasedCRDTMachine.replicas, item=values)
    def add_item(self, replica, item):
        self.model.add(item)
        replica.add(item)
