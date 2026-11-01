+++
id = "Q165"
question = "why does a coordinate size and format word that describes sets the vertex program does not write (size code 5 over two or three outputs, a format bit for an absent set) fault or hang at N = 2, 3 and 8 outputs and complete at N = 5, 6, 9 and 11"
unit = "ta"
kind = "hw"
value = "low"
phase = 11
evidence = ["E541"]
terms = ["PB_OBJ.FORMAT", "PB_OBJ.SET_MASKS"]
+++

E541's `alt` pattern, 3 of its 7 jobs failing (size codes 5, 3 and 1 over the sets and format bits
for the sets 0 and 2; at N = 2 and 3 a single set of code 5 with its format bit) faulted at N = 2
outputs, hung at N = 3 and N = 8 and completed at N = 5, 6, 9, 11. At N = 2 and 3 the first set
describes four components over two and three outputs; at N = 5 and 6 it describes 4 + 3 components
over 5 and 6 outputs and completes, and at N = 8, where 4 + 3 fit in 8, it hung. The same code 5
over two and three outputs without a format bit (n2-s5, n3-s5) completed. One run each.

Open: whether a hang is the described components exceeding the outputs, the flagged absent set, or
the number of sets of four (N = 8 has two full sets), and which cases fault and which hang.

To settle it: sizes 1 to 5 over one set at N = 1 to 4, a flagged absent set at N = 1 to 11, repeated
three times each. No kernel change.
