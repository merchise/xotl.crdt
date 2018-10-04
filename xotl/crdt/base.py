#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#
'''Base interfaces.'''

class CvRDT:
    '''Base class for Convergent Replicated Data Types.

    Basically this documents the expectation of each CvRDT.  Subclasses
    **must** implement the following methods and attributes.

    '''
    def __init__(self, *, actor: str) -> None:
        self.actor = actor
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

    @property
    def state(self):
        '''The current state of the CRDT.

        This is intended to specialize the way the CRDT transmits its state to
        other processes.

        The intention is that you use it before merging::

           replica1.merge(CvRDT.from_state(replica2.state))

        '''
        return self

    @classmethod
    def from_state(cls, state) -> 'CvRDT':
        '''Reconstruct a CvRDT from `state`:any:.'''
        return state

    def reset(self) -> None:
        '''Reset the internal state of value, usually to the initial state.

        .. warning:: This method should only be used within the boundaries of
           a coordination controlled layer.

           Notice it may not be sufficient for a majority of the nodes to
           agree on the value, but the whole set of nodes.  You probably only
           need to call this when removing/adding an actor from the cluster.

        '''
        self.init()


reconstruct = CvRDT.from_state
