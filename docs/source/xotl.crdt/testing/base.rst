===================================================================
 :mod:`xotl.crdt.testing.base` -- Common definition to tests CRDTs
===================================================================

.. module:: xotl.crdt.testing.base

We use `hypothesis.stateful`:mod: to create sequences of possible actions over
any replica.  Each action is also record in a `model` object that maintains
the expected state all replicas must converge to if synchronized.

.. autoclass:: BaseCRDTMachine
   :members: create_subjects, run_synchronize
