+++
id = "Q137"
question = "do the test field's two parts of a class 9 test (zero: bits 41 over 40; sign: bits 43 over 42; the two ANDed under join `a`) hold for the shifts, the other chan fields, the other forms of the bitwise group and the other classes' tests, and is a word with several conditions, greater than zero among them, usable from compiler output?"
unit = "usse"
kind = "hw"
value = "low"
phase = 11
evidence = ["E499", "E498"]
terms = ["Universal Scalable Shader Engine (USSE)"]
+++

E499: the test field enc[43:40] of `and.test.chan0 !c0, p0, r1, r2` gives, for the 15 values, the
AND of a zero part and a sign part (90 of 90, a fit after the run) with enc[39] = 1 (join `a`) and
chan0 in all 732 raw test words run; that rule predicted all 450 cases of a run on other forms
(`or`, `xor` and `rol` with registers, `and` and `xor` with #7, 90 cases each, join `a`, chan0 only,
six input pairs each); the sixteen test words with bit 43 set give the plain condition ANDed with
pat (96 of 96, also a fit after the run). E498 has the iadd32 and iaddu32 results of the single
conditions the assembler writes.

What is open: the `o` join (enc[39] = 0) with a two-part field (not run), the rule on `shl`, `shr`
and `asr`, on `or` and `rol` with #7, on the chan fields other than chan0, on 8-bit and 16-bit lane
operations and for the iadd32 and iaddu32 sum tests with combined conditions; the field value 0;
input pairs whose results cover every class of result (and with #7 had no negative result, xor with
registers no positive nonzero one); and whether a pass of our own backend may emit the combined
words (the assembler writes none). To settle it: the same table over those, with the rule as the
hypothesis and results of every class in every form.
