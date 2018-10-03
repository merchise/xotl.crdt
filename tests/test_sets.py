#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#
from xotl.crdt.testing.sets import (
    GSetMachine,
    TPSetMachine,
    USetMachine,
    ORSetMachine,
)


TestGSet = GSetMachine.TestCase
TestTPSet = TPSetMachine.TestCase
TestUSet = USetMachine.TestCase
TestORset = ORSetMachine.TestCase
