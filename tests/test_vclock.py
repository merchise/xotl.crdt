#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#
from xotl.crdt.clocks import VClock, Dot


def test_descend_regression():
    v1 = VClock(dots=(Dot(actor='R0', counter=1, timestamp=0),
                      Dot(actor='R1', counter=1, timestamp=0)))
    v2 = VClock(dots=(Dot(actor='R0', counter=1, timestamp=0),))
    assert v1 >= v2

    v1 = VClock(dots=(Dot(actor='R0', counter=1, timestamp=0),
                      Dot(actor='R1', counter=1, timestamp=0)))
    v2 = VClock(dots=(Dot(actor='R1', counter=1, timestamp=0),))
    assert v1 >= v2

    v1 = VClock(dots=(Dot(actor='R0', counter=1, timestamp=0),
                      Dot(actor='R1', counter=1, timestamp=0),
                      Dot(actor='R2', counter=0, timestamp=0)))
    v2 = VClock(dots=(Dot(actor='R1', counter=1, timestamp=0),))
    assert v1 >= v2
