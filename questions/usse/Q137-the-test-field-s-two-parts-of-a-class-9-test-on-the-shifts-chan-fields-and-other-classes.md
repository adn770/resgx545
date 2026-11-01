+++
id = "Q137"
question = "do the rules of the test field of a class 9 test (zero part: bits 41 over 40; sign part: bits 43 over 42; the parts ANDed under join `a`, E499, ORed with an absent part true under join `o`, E529) hold for the shifts, the 8-bit and 16-bit lane operations, the other forms of the bitwise group and the other classes' tests, and is a word with several conditions, greater than zero among them, usable from compiler output?"
unit = "usse"
kind = "hw"
value = "low"
phase = 11
evidence = ["E499", "E498", "E529", "E530"]
terms = ["Universal Scalable Shader Engine (USSE)"]
+++

E499: the test field enc[43:40] of `and.test.chan0 !c0, p0, r1, r2` gives, for the 15 values, the
AND of a zero part and a sign part (90 of 90, a fit after the run) with enc[39] = 1 (join `a`) and
chan0 in all 732 raw test words run; that rule predicted all 450 cases of a run on other forms
(`or`, `xor` and `rol` with registers, `and` and `xor` with #7, 90 cases each, join `a`, chan0 only,
six input pairs each); the sixteen test words with bit 43 set give the plain condition ANDed with
pat (96 of 96, also a fit after the run). E498 has the iadd32 and iaddu32 results of the single
conditions the assembler writes.

Narrowed in 11.27: the `o` join is run (E529: enc[39] = 0 and chan0 ORs the two parts and counts an
absent part true, a one-part field is always true; a rule read from 90 readbacks and predicted on
270 more) and the chan fields 1 to 7 are run (E530: none reads as chan0 as a table, and the readings
fit the rule of *Test channels*); the assembler writes both joins and the two-condition fields
(`.testtoz`, `.testnoz`, `.testnaz`, `.testpanz`, checked with usse-asm on the host), run on the
hardware as raw words only.

What is open: the rule on `shl`, `shr` and `asr`, on `or` and `rol` with #7, on 8-bit and 16-bit
lane operations and for the iadd32 and iaddu32 sum tests with combined conditions (the same for the
`o` join: Q151; the chan field: Q150); the field value 0; input pairs whose results cover every
class of result (and with #7 had no negative result, xor with registers no positive nonzero one);
and whether a pass of our own backend may emit the combined words from the assembler's text forms,
which were not run as text. To settle it: the same table over those, with the rule as the hypothesis
and results of every class in every form.
