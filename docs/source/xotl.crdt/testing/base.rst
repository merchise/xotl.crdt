===================================================================
 :mod:`xotl.crdt.testing.base` -- Common definition to tests CRDTs
===================================================================

.. module:: xotl.crdt.testing.base

We use `hypothesis.stateful`:mod: to create sequences of possible actions over
any replica.

There are two approaches:

Based on a test-model

  Each action is also record in a `model` object that maintains the expected
  state a replica must reach when `synchronized.

  .. autoclass:: ModelBasedCRDTMachine
     :members: run_synchronize

Based on a "full" synchronization

  The synchronization is done by a `gossip protocol
  <SyncBasedCRDTMachine.run_synchronize>`:meth:; after synchronization all
  replicas must have the same value.  Notice this **is not** coordination for
  agreement.

.. autoclass:: SyncBasedCRDTMachine
     :members: run_synchronize


.. autoclass:: BaseCRDTMachine
   :members: create_subjects
