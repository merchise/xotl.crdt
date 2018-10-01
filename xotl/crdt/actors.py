#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#
'''Utils to simplify interfacing with CRDTs.

All CRDTs implemented here define an `actor` keyword parameter ; which MUST be
a string.  This module provides a thread-local way to attach a thread (or
greenlet) to an 'actor'.  When an actor is attached to the thread
instantiating the CRDT, you may omit the `actor` argument.

You cannot attach two different names in the same thread/greenlet.  You cannot
detach an actor from a thread once attached.

'''
import inspect
from inspect import Parameter


def resolve_actor(f):
    '''Resolve the `actor` argument from the context.

    `f` must have a parameter called "actor" exactly.  The result will make it
    optional; so it must be a keyword-only parameter.

    '''
    from functools import wraps

    signature = inspect.signature(f)
    try:
        if signature.parameters['actor'].kind != Parameter.KEYWORD_ONLY:
            raise TypeError('actor must be a keyword-only parameter')
    except KeyError:
        return f
    else:
        @wraps(f)
        def _resolve_actor(*args, actor=Unset, **kwargs):
            if actor is Unset:
                actor = get_current_actor()
            return f(*args, actor=actor, **kwargs)
        return _resolve_actor


Unset = object()


def get_current_actor():
    # TODO: Actually implement the actor context.
    import threading
    return str(threading.get_ident())
