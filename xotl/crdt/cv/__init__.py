#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#
'''Convergent Replicated Data Types (CvRDT).
'''


def dump_state(replica):
    'Dump a serializable object that represents the state of the replica.'
    return replica


def perform_merge(local, state):
    '''Alter (if needed) the replica with another replica's state.'''
    if local.vector_clock >= state.vector_clock:
        pass
    elif local.vector_clock < state.vector_clock:
        local.value = state.value
        local.vector_clock = local.vector_clock.merge(state.vector_clock)
    else:
        local.value = local.value + state.value
        local.vector_clock = local.vector_clock.merge(state.vector_clock)


def get_value(replica):
    'Return the abstract value for the replica.'
    return replica.value
