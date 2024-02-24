#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#
from dataclasses import dataclass, field
from typing import Any

from hypothesis import assume
from hypothesis import strategies as st
from hypothesis.stateful import Bundle, consumes, rule
from xotl.tools.symbols import Unset

from xotl.crdt.sets import GSet, ORSet, TwoPhaseSet, USet
from xotl.crdt.testing.base import ModelBasedCRDTMachine, SyncBasedCRDTMachine

atoms = (
    st.integers()
    | st.booleans()
    |
    # float('nan') == float('nan') is False
    st.floats(allow_nan=False)
)

molecules = st.tuples(atoms)
values = atoms | molecules


class Set:
    "A model set"

    def __init__(self):
        self.reset()

    def reset(self, item=Unset):
        "Empty the set"
        self.value = set()
        if item is not Unset:
            self.add(item)

    def add(self, item):
        "Add item to the set."
        self.value.add(item)


class GSetMachine(ModelBasedCRDTMachine):
    """The stateful machinery to test the `~xotl.crdt.sets.GSet`:class:."""

    def __init__(self):
        super().__init__()
        self.model = Set()
        self.subjects = self.create_subjects(GSet)

    @rule(replica=ModelBasedCRDTMachine.replicas, item=values)
    def add_item(self, replica, item):
        "A an item to an arbitrary replica"
        self.model.add(item)
        replica.add(item)

    @rule(item=values)
    def reset_all_replicas_with_item(self, item):
        "Reset all replicas with a the set ``{item}``"
        print(f"Reseting the replicas (and model) with item: {item}")
        self.model.reset(item)
        for replica in self.subjects:
            replica.reset({item})


class TPSetMachine(SyncBasedCRDTMachine):
    """The stateful machinery to test the `~xotl.crdt.sets.TwoPhaseSet`:class:."""

    def __init__(self):
        super().__init__()
        self.subjects = self.create_subjects(TwoPhaseSet)

    items = Bundle("items")

    @rule(target=items, value=st.integers())
    def generate_item(self, value):
        return value

    @rule(replica=SyncBasedCRDTMachine.replicas, item=items)
    def add_item(self, replica, item):
        replica.add(item)

    @rule(replica=SyncBasedCRDTMachine.replicas, item=items)
    def remove_item(self, replica, item):
        "Remove an item (if present) from an arbitrary replica"
        replica.remove(item)

    @rule(item=items)
    def reset_all_replicas_with_item(self, item):
        "Reset all replicas with the set ``{item}``."
        print("Resetting the replicas with item: {item}")
        for replica in self.subjects:
            replica.reset({item})
            assert item in replica.value, f"{item} is not present in {replica}"


@dataclass(unsafe_hash=True)
class Item:
    payload: Any
    already_added: bool = field(default=False, compare=False)
    already_removed: bool = field(default=False, compare=False)

    def __repr__(self):
        sign = "+" if self.already_added else ""
        sign += "-" if self.already_removed else ""
        return f"<{self.payload}{sign}>"


class SyncBasedSetMachine(SyncBasedCRDTMachine):
    """Test sets with `items <Item>`:class:.

    See sub-classes `USetMachine`:class: and `ORSetMachine`:class:.

    """

    items = Bundle("items")

    @rule(target=items, value=st.integers(min_value=0))
    def generate_item(self, value):
        return Item(payload=value)

    @rule(item=items)
    def reset_all_replicas_with_item(self, item):
        "Reset all replicas with the set ``{item}``."
        print("Resetting the replicas with item: {item}")
        for replica in self.subjects:
            replica.reset({item})
            assert item in replica.value, f"{item} is not present in {replica}"


class USetMachine(SyncBasedSetMachine):
    """Test machinery for `~xotl.crdt.sets.USet`:class:."""

    def __init__(self):
        super().__init__()
        self.subjects = self.create_subjects(USet)
        print("************ New USet case *************")

    added_items = Bundle("added_items")

    # We consume an item from the 'items' bundle and add it to the 'added
    # items'.  The remove_item method takes only from the last bundle.
    #
    # This only ensures the item was previously added; but we don't know to
    # which replica.  Furthermore, we don't know if the replicas were reset
    # after adding items.  So this strategy doesn't remove the possibility of
    # trying to remove an item which is not in the replica; and that's OK.
    #
    # At the same time we reduce the chance of generating invalid examples
    # (i.e not passing the assume in add_item)

    @rule(
        replica=SyncBasedCRDTMachine.replicas,
        item=consumes(SyncBasedSetMachine.items),
        target=added_items,
    )
    def add_item(self, replica, item):
        """A an item to an arbitrary replica.

        This method `consumes <hypothesis.stateful.consumes>`:func: the item
        generated in the bundle ``added_items`` and places the same item into
        the bundle ``added_items``; `remove_item`:meth: below takes items from
        the bundle ``added_items``.  This only ensures the item was previously
        added but we don't know to which replica.  Furthermore, we don't know
        if the replicas were reset after adding items.  So this strategy
        doesn't remove the possibility of trying to remove an item which is
        not in the replica; and that's OK.  At the same time we reduce the
        chance of generating invalid examples.

        """
        assume(not item.already_added)
        print(f"Adding item {item}")
        replica.add(item)
        item.already_added = True
        return item

    @rule(replica=SyncBasedCRDTMachine.replicas, item=added_items)
    def remove_item(self, replica, item):
        "Remove an item (if present) from a replica."
        print(f"Remove item {item}; if present in {replica}")
        item.already_removed = item in replica.value
        replica.remove(item)

    def teardown(self):
        super().teardown()
        print("------------ End USet case -------------")


class ORSetMachine(SyncBasedSetMachine):
    def __init__(self):
        super().__init__()
        self.subjects = self.create_subjects(ORSet)
        print("************ New ORSet case *************")

    @rule(
        replica=SyncBasedCRDTMachine.replicas,
        item=consumes(SyncBasedSetMachine.items),
    )
    def add_item(self, replica, item):
        assume(not item.already_added)
        print(f"Adding item {item} in replica {replica}")
        replica.add(item)

    @rule(replica=SyncBasedCRDTMachine.replicas, item=SyncBasedSetMachine.items)
    def remove_item(self, replica, item):
        print(f"Remove item {item}; if present in {replica}")
        replica.remove(item)
        print(f"       Result: {replica}")

    @rule(
        replica1=SyncBasedCRDTMachine.replicas,
        replica2=SyncBasedCRDTMachine.replicas,
        item=SyncBasedSetMachine.items,
    )
    def simulate_concurrent_add_remove(self, replica1, replica2, item):
        """Simulates add of item in `replica1` concurrent with removal in `replica2`."""
        assume(replica1 is not replica2)
        self.run_synchronize()
        replica1.add(item)
        replica2.remove(item)
        self.run_synchronize()
        assert item in replica1.value, f"{item} not in {replica1}"
        assert item in replica2.value, f"{item} not in {replica1}"

    def teardown(self):
        super().teardown()
        print("------------ End ORSet case -------------")
