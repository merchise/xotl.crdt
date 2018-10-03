.. xotl.crdt documentation master file, created by
   sphinx-quickstart on Sat Sep 29 08:40:52 2018.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

================================
 Prototype for CRDTs for Python
================================

We implement several CRDTs in Python.  Those implementations are prototypical,
meaning we don't intend them to be production-code, but to allow exploration
of the subtleties around CRDTs so that we can implement them elsewhere.

Main reference:

   Marc Shapiro, Nuno Preguiça, Carlos Baquero, and Marek Zawirski.  'A
   comprehensive study of Convergent and Commutative Replicated Data Types';
   [Research Report] RR-7506, 2011, pp.50. <inria-00555588>.

   -- Available at https://hal.inria.fr/inria-00555588v1

This package requires Python 3.6+, and has been tested in CPython 3.6 and
CPython 3.7.


.. toctree::
   :glob:
   :maxdepth: 2
   :caption: Contents:

   xotl.crdt/*
   xotl.crdt/testing/*
   history


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
