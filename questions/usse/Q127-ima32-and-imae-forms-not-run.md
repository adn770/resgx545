+++
id = "Q127"
question = "what do the extra i register of ima32, ima32 as a dual-issue secondary, and imae with a repeat, a u16 or z16 source or a .rsN shift do with the carry flags and with the 32-bit result?"
unit = "usse"
kind = "hw"
value = "low"
phase = 11
evidence = ["E469", "E470", "E471"]
terms = ["Universal Scalable Shader Engine (USSE)", "REGTYPE.FPINTERNAL"]
+++

E469 to E471: the plain `ima32`, its three sources (register, 7-bit immediate, constant), `.neg`,
`cie`, and `imae` with `coe` and `cie` are measured; the optional `i` register after the destination
of `ima32`, the dual-issue form (two 16-bit lanes), and the carry flags of `imae` with repeats, with
the `u16`/`z16` sources and with a `.rsN` shift are not. Also not run: a raw word of `ima32` with a
carry-out bit (the assembler refuses `coe`, which is not a hardware result), `cie` with an iN whose
bit 0 is clear and a high bit set (0x10000, 0x80000000) and with an iN other than i0, `.neg` with
`.s` on an immediate or a constant, immediates 4 to 126 and the banks `pa`, `sa`, `o`, `i` and `g`
as operands (only r-bank registers, c-bank constants and 7-bit immediates ran), and a destination
other than r10.

What is open: those forms. To settle it: the same corner-value tables over each, as E469 and
E471, one probe a form.
