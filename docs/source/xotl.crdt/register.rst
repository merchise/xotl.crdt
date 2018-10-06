==================================================
 :mod:`xotl.crdt.register` -- The Registers CRTDs
==================================================

.. automodule:: xotl.crdt.register


.. autoclass:: LWWRegister

   .. rubric:: User API

   .. automethod:: set(value)

   .. property:: value

   .. rubric:: Internal CRDT API

   .. automethod:: merge

   .. automethod:: reset

   .. automethod:: __lshift__
