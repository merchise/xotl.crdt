=========================================
 :mod:`xotl.crdt.sets` -- The Sets CRTDs
=========================================

.. automodule:: xotl.crdt.sets

.. autoclass:: GSet

   .. rubric:: User API

   .. automethod:: add

   .. property:: value

   .. rubric:: Internal CRDT API

   .. automethod:: merge

   .. automethod:: reset


.. autoclass:: TwoPhaseSet

   .. rubric:: User API

   .. automethod:: add

   .. automethod:: remove

   .. property:: value

   .. rubric:: Internal CRDT API

   .. automethod:: merge

   .. automethod:: reset


.. autoclass:: USet

   .. rubric:: User API

   .. automethod:: add

   .. automethod:: remove

   .. property:: value

   .. rubric:: Internal CRDT API

   .. automethod:: merge

   .. automethod:: reset


.. autoclass:: ORSet

   .. rubric:: User API

   .. automethod:: add

   .. automethod:: remove

   .. property:: value

   .. rubric:: Internal CRDT API

   .. automethod:: merge

   .. automethod:: reset
