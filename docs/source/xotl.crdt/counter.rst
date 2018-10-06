===============================================
 :mod:`xotl.crdt.counter` -- The Counter CRTDs
===============================================

.. automodule:: xotl.crdt.counter

.. autoclass:: GCounter

   .. rubric:: User API

   .. automethod:: incr

   .. property:: value

   .. rubric:: Internal CRDT API

   .. automethod:: merge

   .. automethod:: reset


.. autoclass:: PNCounter

   .. rubric:: User API

   .. automethod:: incr

   .. automethod:: decr

   .. property:: value

   .. rubric:: Internal CRDT API

   .. automethod:: merge

   .. automethod:: reset
