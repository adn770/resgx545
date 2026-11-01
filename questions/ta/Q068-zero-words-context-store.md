+++
id = "Q068"
question = "do the twelve TA register words that are zero in our jobs save and resume the state of an interrupted TA?"
unit = "ta"
phase = 11
evidence = ["E054", "E056", "E182", "E183", "E245"]
terms = ["CR_REG_0324", "CR_TE_REG_02A8"]
+++

The words are 0 in every job; no value changes a pixel or is used as an address (E056, E182); three
read back address-shaped and four as full 32-bit values (E054); the firmware writes eleven of their
registers at one site each, copied from the command (E245). E183 reads them as state a TA saves and
resumes.

What is open (3d.md §7.2): no run interrupts a TA, so the reading is untested.

To settle it: a TA interrupted by a context switch, which needs a two-context test mode and a
context-switch path in the linux fork, neither written yet: the registers read after the store and
the words compared with what a resumed TA loads.
