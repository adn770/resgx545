+++
id = "Q137"
question = "do the rules of the test field of a class 9 test (zero part: bits 41 over 40; sign part: bits 43 over 42; the parts ANDed under join `a`, E499, ORed with an absent part true under join `o`, E529) hold for the shifts, the 8-bit and 16-bit lane operations, the other forms of the bitwise group and the other classes' tests, with the o join and with a chan field enc[38:36] other than 0 (E530), and is a word with several conditions, greater than zero among them, usable from compiler output?"
unit = "usse"
kind = "hw"
value = "low"
phase = 11
evidence = ["E499", "E498", "E529", "E530", "E1062"]
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
`o` join and the chan field: the merged questions below); the field value 0; input pairs whose results cover every
class of result (and with #7 had no negative result, xor with registers no positive nonzero one);
and whether a pass of our own backend may emit the combined words from the assembler's text forms,
which were not run as text. To settle it: the same table over those, with the rule as the hypothesis
and results of every class in every form.

**Correction 2026-11-10:** Q150 is merged into this question (retired as folded into Q137; a fold is not an answer), and its question is now a clause of the one above. Its question was: do the raw test words with the chan field enc[38:36] = 1 to 7 on 8-bit and 16-bit lane operations, on the fields other than the six run and with the o join read as the rule of the Test channels page says.

E530: seven raw and-test words with enc[38:36] = 1 to 7 and the a join, six field values and six
pairs each (36 jobs a table) on a 32-bit result: the prediction that the field is ignored failed in
all seven. The 252 readings are what the channel table of the assembler (chan0 to or02 for
enc[38:36] = 0 to 7) and the rule of the landed Test channels page (a channel with no lane reads 1:
taz 0, tanz 1, nat 0, pat 1) give, read after the data; a 32-bit test names chan0, and that advice
stands.

What the landed Test channels page already has [HW] is the lane operations through the assembler's
chan names (360 cases). What is open is smaller: the raw words with the chan field on 8-bit and
16-bit lane operations (where the other channels have lanes), on the fields other than the six run,
on result classes the six pairs did not give, and with the o join (E529). To settle it: the same
table on lane operations with distinct bytes in the operands, the byte under test known, with the
rule as the hypothesis.

**Correction 2026-11-10:** Q151 is merged into this question (retired as folded into Q137; a fold is not an answer), and its question is now a clause of the one above. Its question was: does the o join rule of E529 (enc[39] = 0: the two parts of the test field ORed, an absent part true) hold for the shifts, the 8-bit and 16-bit lane operations and the other classes' tests, and with a chan other than chan0, and does any compiler output need it?.

E529: with enc[39] = 0 the rule (an absent part true, the parts ORed) fits the 90 cases of the first
run, read after the run, and predicted 270 of 270 on or, xor and and #7 over other pairs; a one-part
field is always true under the o join. E499's AND is the a join.

What is open: the shifts, the lane operations, the other classes' tests (iadd32 and the like), the o
join with chan fields other than 0, the field value 0, and result classes that the pairs did not
give (the and #7 probe has no negative result). A compiler needs the o join only for a test of two
conditions, 'x is zero or negative', which the o join writes as one instruction (taz with nat, which
the assembler writes as `.testnoz`), a case E529's field 5 reads as predicted by the rule: 1 for the
results 0, 0x80000000 and 0xffffffff. To settle it: the same 15 values over those forms, with the
rule as the hypothesis.

Narrowed 2026-11-14 (round 16, session r16-usse, decision R16-5 a; E1062). Held out and holding (18
of 18 rows, E499's and E529's tables replicated as controls, every rival failing): the rule of the
two parts with the a join's AND and the o join's OR on shl, shr and asr with registers, or and rol
with #7, iadd32 and iaddu32 under both joins with the field values 0 to 15 (0 always true), and on
iadd8 and iadd16 with chan0 to or02 under both joins over the nine fields the assembler names; the
rows ran the assembler's text forms, whose words are the raw fields byte for byte (OQ137). sgx-sim
models these, naming E1062. What stays: the other classes' tests and whether another bit of a test
word inverts a source.
