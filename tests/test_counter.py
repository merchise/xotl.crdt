#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# Copyright (c) Merchise Autrement [~º/~] and Contributors
# All rights reserved.
#
# This is free software; you can do what the LICENCE file allows you to.
#
from xotl.crdt.testing.counters import GCounterMachine
from xotl.crdt.testing.counters import PNCounterMachine


TestGCounter = GCounterMachine.TestCase
TestPNCounter = PNCounterMachine.TestCase
