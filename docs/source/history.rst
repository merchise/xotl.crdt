===========
 Changelog
===========

Series 0.x
==========

2018-10-16.  Release 0.2.0
--------------------------

- Replace 'process' for 'actor' across the code-base.

- Extract the state dump/reconstruction from `~xotl.crdt.base.CvRDT`:class:;
  add functions `~xotl.crdt.base.get_state`:func: and
  `~xotl.crdt.base.from_state`:func:.

- Add `~xotl.crdt.base.Process`:class: to capture the required interface of
  processes.

- Remove the timestamp from the internal vector clock.  The timestamp is only
  used in `~xotl.crdt.register.LWWRegister`:class:; it was wasteful to have it
  everywhere else unused.


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
