#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#
'''Base interfaces.'''
from dataclasses import dataclass


@dataclass(frozen=True, order=True)
class Process:
    '''Represents a process or node that holds replicated objects.

    We require (for some CRDTs) that processes are uniquely named and totally
    ordered across the cluster.  So when adding/removing a process you should
    take measures for not reusing old names.

    '''
    order: int
    name: str

    def __init__(self, name: str, order: int) -> None:
        object.__setattr__(self, 'name', name)
        object.__setattr__(self, 'order', order)

    def __repr__(self):
        return f"Process({self.name!r}, {self.order!r})"

    def __eq__(self, other) -> bool:
        if isinstance(other, Process):
            return self.name == other.name
        else:
            return NotImplemented


class CvRDT:
    '''Base class for Convergent Replicated Data Types.

    Basically this documents the expectation of each CvRDT.  Subclasses
    **must** implement the following methods and attributes.

    '''
    def __init__(self, *, process: Process) -> None:
        self.process = process
        self.init()

    def init(self) -> None:
        '''Set the initial state of a newly create CRDT.'''

    def merge(self, other: 'CvRDT') -> None:
        '''Update the CvRDT to account for the another replica's state.

        '''
        raise NotImplementedError

    @property
    def value(self):
        '''The current value that is managed by this CRDT.

        This could be any type of value.  But you *must* never assume changes
        to the value return will be of any effect.  Each CRDT implements
        methods to properly update its value.

        This is a read-only property.

        '''
        raise NotImplementedError

    def reset(self) -> None:
        '''Reset the internal state of value, usually to the initial state.

        '''
        self.init()

    def __le__(self, other):
        '''Compares two replicas for '<=' in the semilattice.

        This is **NOT** a relation of the `value`:any:.

        '''
        return NotImplemented

    def __eq__(self, other) -> bool:
        '''Compares two replicas for '==' in the semilattice.

        This is **NOT** a relation of the `value`:any:.

        '''
        return NotImplemented


def get_state(crdt: CvRDT) -> bytes:
    '''Dumps the crdt in a way that is amenable for transmission/storage.

    '''
    import pickle
    return pickle.dumps(crdt)


def from_state(state: bytes) -> CvRDT:
    '''Reconstruct the CRDT from its dumped state.

    `state` should be the result of calling `get_state`:func:.  The following
    property should always hold::

        assert crdt == from_state(get_state(crdt))

    '''
    import pickle
    res = pickle.loads(state)
    if not isinstance(res, CvRDT):
        raise ValueError('Invalid state')
    else:
        return res
