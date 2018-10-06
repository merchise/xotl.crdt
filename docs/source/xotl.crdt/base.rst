===================================================
 :mod:`xotl.crdt.base` -- Basic interfaces and API
===================================================

.. automodule:: xotl.crdt.base

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
      the value return will be of any effect.  Each CRDT implements methods to
      properly update its value.

      This is a read-only property.

   .. rubric:: Internal (coordination layer) CRDT API.

   Every CvRDT must implement this methods to initialize, and update its state
   upon requests from the coordination layer.

   .. automethod:: init

   .. automethod:: merge

   .. autoproperty:: state

   .. classmethod:: from_state

   .. automethod:: reset

   .. rubric:: Expectations for coordination

   Notice that you should call `~CvRDT.from_state`:any: for the *right*
   sub-class.

   .. note:: We're considering to remove ``state`` and ``from_state`` from
             this class; since they seem to be more related to transmission.
