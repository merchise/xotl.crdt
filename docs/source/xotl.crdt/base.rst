===================================================
 :mod:`xotl.crdt.base` -- Basic interfaces and API
===================================================

.. module:: xotl.crdt.base

.. rubric:: Common interface for all CRDTs.

.. autoclass:: CvRDT

   .. rubric:: User facing API

   The methods and properties in this sub-section are those expected all CRDTs
   expose to the users.  These must be programmed to keep the expected
   semantics of the CRDT.

   This base class, only describe them in an abstract way, sub-classes must
   provide their own implementation.

   .. data:: value

      The current value that is managed by this CRDT.

      This could be any type of value.  But you *must* never assume changes to
      the value will be of any effect.  Each CRDT implements methods to
      properly update its value.

      This is a read-only property.

   .. rubric:: Internal (coordination layer) CRDT API.

   Every CvRDT must implement these methods to initialize and update its state
   upon requests from the coordination layer.

   .. automethod:: merge

   .. automethod:: __le__

   .. automethod:: __eq__

   .. warning:: The following two methods should only be used within the
      boundaries of a coordinated controlled layer.  They may alter the
      internal state of CRDT in a way that could break the expected semantics
      unless you take measures to ensure it.

   .. automethod:: init

   .. automethod:: reset


.. autoclass:: Process


.. rubric:: Transmitting and receiving the CRDT state

The following two functions allow for CRDT to be transmitted from one process
to another and/or saved in a file.  They use `pickle`:mod:; which means you're
responsible for enforcing the required security.

.. autofunction:: get_state

.. autofunction:: from_state
