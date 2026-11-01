+++
id = "Q017"
question = "why does g19 read 0x1a as a store's source but 0 through a mov and as the pixel?"
unit = "usse"
phase = 6
evidence = ["E085", "E086", "E372"]
terms = ["REGTYPE.FPCONSTANT", "USE.NUM_HW_SPECIAL_CONSTS"]
+++

Narrowed (E372): g19 reads by the instruction that reads it, the same in every pixel of the fill:
0 through `mov`, 0x11 as source 1 or 2 of `or` and `and`, and 0x1a as a store's source when each
pixel stores to its own dword and loads it back, two runs; g18 read alike through `mov`, `or` and
a store, g23 through `mov` and a store, and g17 and g20 through a store only. So 0x1a is not one
instance's value: it is what the store path reads (E372 answers how g19 reads, not why).

What is left: why the three paths differ, g19 through the other instruction groups and in
other task types, and what it names.
