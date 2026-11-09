+++
id = "Q132"
question = "where does a write to a temporary past the task's allocation go, and which instances' registers do the pixels that do not read the wrapped register read"
unit = "usse"
kind = "hw"
value = "low"
phase = 11
evidence = ["E486"]
terms = []
+++

E486: r(n) for n above the allocation T reads the marker of r(n mod T) in 88 to 99.6 percent of the
pixels of client pixel tasks (T = 8, 16, 32 and 64) and a write to r(n) did not change r(n mod T)
(4 of 4, T = 8 and 32 only).

What is open: whether the write lands in a neighbouring instance's register file (the rest of the
pixels read other values, leftovers or other markers), and what an allocation other than 8, 16, 32
and 64 does. To settle it: the same probe with every instance writing a different marker (pa0 or a
number from the instance) past its allocation and each instance reading its own and its
neighbours'.

Noted 2026-11-09: near duplicate of Q147, not merged (both ask where a write to a register past
the task's allocation lands (E486)). A merge or a fold decides which text survives.
