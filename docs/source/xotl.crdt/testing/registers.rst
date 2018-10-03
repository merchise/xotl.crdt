=========================================================
 :mod:`xotl.crdt.testing.registers` -- Testing registers
=========================================================

.. module:: xotl.crdt.testing.registers


.. autoclass:: LWWRegisterMachine

   .. automethod:: run_set

   .. automethod:: run_synchronize


.. autoclass:: LWWRegisterConcurrentMachine

   .. automethod:: run_possibly_concurrent_set

   .. automethod:: tick

   .. automethod:: run_synchronize
