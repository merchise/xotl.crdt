===========
 Changelog
===========

Series 0.x
==========

Unreleased.  Release 0.2.0
--------------------------

Nothing yet.


2018-10-03.  Release 0.1.1
--------------------------

Correct distribution files.  No source changes.


2018-10-03.  Release 0.1.0
--------------------------

Initial release with the implementation of
`~xotl.crdt.counter.GCounter`:class:, `~xotl.crdt.counter.PNCounter`:class:,
`~xotl.crdt.register.LWWRegister`:class:, and several `sets
<xotl.crdt.sets>`:mod:.  We also include a kind-of vector clock implementation
in module `~xotl.crdt.clocks`:mod: (we use it as a primitive, so the GCounter,
for instance is just an adapter of the underlying vclock.)
