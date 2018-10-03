#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#
from xotl.crdt.clocks import VClock, Dot


def test_descend_regression1():
    v1 = VClock(dots=(Dot(actor='R0', counter=1, timestamp=0),
                      Dot(actor='R1', counter=1, timestamp=0)))
    v2 = VClock(dots=(Dot(actor='R0', counter=1, timestamp=0),))
    assert v1 >= v2


def test_descend_regression2():
    v1 = VClock(dots=(Dot(actor='R0', counter=1, timestamp=0),
                      Dot(actor='R1', counter=1, timestamp=0)))
    v2 = VClock(dots=(Dot(actor='R1', counter=1, timestamp=0),))
    assert v1 >= v2


def test_descend_regression3():
    v1 = VClock(dots=(Dot(actor='R0', counter=1, timestamp=0),
                      Dot(actor='R1', counter=1, timestamp=0),
                      Dot(actor='R2', counter=0, timestamp=0)))
    v2 = VClock(dots=(Dot(actor='R1', counter=1, timestamp=0),))
    assert v1 >= v2


def test_missing_present_dots_regression():
    v1 = VClock(dots=(Dot(actor='R0', counter=0, timestamp=0),))
    v2 = VClock(dots=(Dot(actor='R1', counter=1, timestamp=0),))
    assert v1 <= v2
    assert not (v1 >= v2)


def test_eq_of_empties1():
    v1 = VClock(dots=(Dot(actor='R0', counter=0, timestamp=0),))
    v2 = VClock(dots=(Dot(actor='R1', counter=0, timestamp=0),))

    assert v1 >= v2 >= v1
    assert v1 == v2
    assert v2 <= v1
    assert v1 <= v2
