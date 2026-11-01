+++
id = "Q127"
question = "what do the extra i register of ima32, ima32 as a dual-issue secondary, and imae with a repeat, a u16 or z16 source or a .rsN shift do with the carry flags and with the 32-bit result?"
unit = "usse"
kind = "hw"
value = "low"
phase = 11
evidence = ["E469", "E470", "E471", "E493", "E494", "E495", "E496", "E501", "E525", "E526", "E527", "E528", "E595", "E597"]
terms = ["Universal Scalable Shader Engine (USSE)", "REGTYPE.FPINTERNAL"]
+++

E469 to E471: the plain `ima32`, its three sources (register, 7-bit immediate, constant), `.neg`,
`cie`, and `imae` with `coe` and `cie` are measured. E493 to E496 and E501 add: the extra `i`
operand (the high word, for `.u` and `.s`, on generic register operands r1 to r3 with the
destination r10 and K = 0 to 2: E525, E526; E527 and E528 use it in the compares; Q135 asks the
rest), `cie` with iN other than i0 and with a high bit set (the eight values of E494), `imae` with
`cie` and `coe` on i1, `.neg` on `.s` with an immediate and a constant (the seven `.s` forms of
E495), 17 more immediates (22 of 128 have run), the banks `pa`, `sa`, `o`, `i` and `g` as operands
with the value 0 (nonzero values in i0 to i2 only), and the destinations r0, r9, r18, r28, r30, r31,
sa0, o0, i1 and i2 (not pa0, which is not written: E496).

What is open: the dual-issue form (two 16-bit lanes), the carry flags of `imae` with repeats, with
the `u16`/`z16` sources and with a `.rsN` shift, `u16`/`z16` and `.rsN` on `ima32`, values other
than 0 held in pa, sa, o and g as operands, the immediates not run (9 to 14, 18 to 30, 34 to 62, 66
to 99 and 101 to 124, and 3 in source 3), `.neg` forms not run (E495 lists them), `ima32.s`
destinations, `imae` with i2 (the assembler refuses it, [infer]), and the rest of what the extra
operand does (Q135). To settle it: the same corner-value tables over each, as E469 and E471, one
probe a form.

Narrowed in 11.36 (not retired). In client pixel tasks, the extra operand `i0` of `ima32.u` and `.s`
was run with every one of the 15 partitions of {d, a, b, c} into registers (300 of 300 jobs, E597)
and in the 64-bit compares on five more register triples and with a previous compare's high word in
i0 (256 of 256, E595): the sources are read before the write, i0 is the high word, and the test
reads the fresh one. Not run in a firmware task (the verifier refuses the form).
