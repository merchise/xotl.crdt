#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#
from hypothesis import given, strategies

from xotl.crdt.base import Process
from xotl.crdt.clocks import Dot, VClock

R0 = Process("R0", 0)
R1 = Process("R1", 1)
R2 = Process("R2", 2)

_PROCESSES = [Process("P-%02d" % i, i) for i in range(100)]
processes = strategies.sampled_from(_PROCESSES)


@strategies.composite
def clocks(draw):
    procs = draw(strategies.sets(processes, max_size=len(_PROCESSES)))
    dots = [Dot(proc, draw(strategies.integers(min_value=0))) for proc in procs]
    return VClock(dots)


@given(clocks(), clocks())
def test_equality_implies_hash(c1, c2):
    if c1 == c2:
        assert hash(c1) == hash(
            c2
        ), f"{c1} == {c2}, but their hashes differ: {hash(c1)} != {hash(c2)}"


def test_descend_regression1():
    v1 = VClock(dots=(Dot(process=R0, counter=1), Dot(process=R1, counter=1)))
    v2 = VClock(dots=(Dot(process=R0, counter=1),))
    assert v1 >= v2


def test_descend_regression2():
    v1 = VClock(dots=(Dot(process=R0, counter=1), Dot(process=R1, counter=1)))
    v2 = VClock(dots=(Dot(process=R1, counter=1),))
    assert v1 >= v2


def test_descend_regression3():
    v1 = VClock(
        dots=(
            Dot(process=R0, counter=1),
            Dot(process=R1, counter=1),
            Dot(process=R2, counter=0),
        )
    )
    v2 = VClock(dots=(Dot(process=R1, counter=1),))
    assert v1 >= v2


def test_missing_present_dots_regression():
    v1 = VClock(dots=(Dot(process=R0, counter=0),))
    v2 = VClock(dots=(Dot(process=R1, counter=1),))
    assert v1 <= v2
    assert not (v1 >= v2)


def test_eq_of_empties1():
    v1 = VClock(dots=(Dot(process=R0, counter=0),))
    v2 = VClock(dots=(Dot(process=R1, counter=0),))

    assert v1 >= v2 >= v1
    assert v1 == v2
    assert v2 <= v1
    assert v1 <= v2


def test_concurrence():
    v1 = VClock(dots=(Dot(process=R0, counter=1),))
    v2 = VClock(dots=(Dot(process=R1, counter=1),))

    assert v1 // v2 and v2 // v1

    v1 = VClock()
    assert not (v1 // v2)
