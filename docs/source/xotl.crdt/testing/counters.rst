=======================================================
 :mod:`xotl.crdt.testing.counters` -- Testing counters
=======================================================

.. module:: xotl.crdt.testing.counters

Create the rule-based machines to test `~xotl.crdt.counter.GCounter`:class:
and `~xotl.crdt.counter.PNCounter`:class:.


.. autoclass:: ModelCounter
   :members: incr, decr


.. class:: GCounterMachine

   The stateful machinery for `~xotl.crdt.counter.GCounter`:class:.

   .. automethod:: run_incr


.. class:: PNCounterMachine

   The stateful machinery for `~xotl.crdt.counter.PNCounter`:class:.

   .. automethod:: run_incr

   .. automethod:: run_decr
