+++
id = "E499"
claim = "Bit 43 of a class 9 test word is the pat bit of the test field enc[43:40] (taz 1, tanz 2, nat 4, pat 8), not an invert: the sixteen test words the assembler writes (and, or, xor and rol, with r2 or #7, testtaz and testtanz), run as raw words, give the test of op(r1, source 2) (96 of 96), the same words with bit 43 set give the plain condition ANDed with pat (96 of 96: taz with pat is taz, tanz with pat is nonzero and positive; the invert of source 2 fits 53 of 96, the condition ORed with pat 48 and no effect 79); all 15 values 1 to 15 of the field on `and` r1, r2 over six input pairs (90 of 90 cases) give, with enc[39] = 1 (join `a`) and chan0 in all 732 raw test words run, the AND of a zero part (tanz if bit 41, else taz if bit 40) and a sign part (pat if bit 43, else nat if bit 42), a rule read out of those 90 cases (so a fit to them: the plain AND of the set conditions fits 69 of 90 and the OR 57), and the same rule, written down before the next table, predicted all 450 cases of a table run afterwards on other forms (all 15 values over six input pairs for `or`, `xor` and `rol` with registers and for `and` and `xor` with #7: 5 forms, 90 cases each, join `a` and chan0 only: 450 of 450; the `o` join with a two-part field was not run)"
unit = "usse"
method = "on the laptop (direct cable), linux fork 6ee9501832af, module srcversion 14D099861204842EA496D85, tool sgxfive-test-1124 (sha256 58907b06a8e9030472a809cd669d2c3823946fd67aaf4775f942704a90f6a5ae): probes/usse/raw25.toml probes test-plain and test-bit43 (raw `.long` words of the class 9 tests, 96 cases each: 16 words over 6 input pairs), probes/usse/rawcond.toml (90 cases: one `and` test word with the field enc[43:40] = 1 to 15, 6 input pairs) and probes/usse/rawcond2.toml (5 probes of 90 cases: the same on `or`, `xor` and `rol` with registers and `and` and `xor` with #7); RAW: run in the last tables, each after a health triangle (the campaign runner's baseline before and after each probe), no job failed; the campaign runner once for each table, no probe.py first run. The runner's verdicts for test-bit43 and rawcond were NONE (my three hypotheses for bit 43, the invert, the condition ORed with pat and no effect, fit 53, 48 and 79 of 96; for the combinations the plain AND and OR fit 69 and 57 of 90); the AND-with-pat reading and the pair rule were read out of those two probes after their runs, so the fit of the rule to the 90 cases of rawcond is circular and the 96 of 96 of test-bit43 is a fit as well; rawcond2 then ran with the rule as its hypothesis (written before the run) and settled on it in all five probes. All counts were recomputed from the readbacks by a script written after the runs (not kept in the tree), and the data of all runs are kept as ran. Every one of the 732 raw test words of the four tables (raw25 test-plain and test-bit43 96 each, rawcond 90, rawcond2 450) has enc[39] = 1 and enc[38:36] = 0: the join was never varied"
tiers = ["HW", "infer"]
date = "2026-11-08"
data = ["usse-raw25", "usse-rawcond", "usse-rawcond2"]
terms = ["Universal Scalable Shader Engine (USSE)"]
+++

**What runs.** The word of `and.testtaz.chan0 !c0, p0, r1, r2` (0x48081181000C0082) and the fifteen
others of E473's list, run as `.long` followed by `mov r10, #0; p0 mov r10, #1`; r10 is 1 when p0
was set. The non-test forms `and r10, r1, ~r2` and `and r10, r1, r2` differ in bit 43
(0x0000080000000000), so bit 43 is what `~` sets there; in the test words bits 43:40 hold the test:
taz 1, tanz 2, nat 4, pat 8 (the plain words end 0x...1181 for taz and 0x...1281 for tanz). Inputs
(r1, r2) of test-plain and test-bit43: (0, 0), (1, 1), (0xffffffff, 0xffffffff), (0x80000000,
0x80000000), (0xf0f0f0f0, 0x0f0f0f0f) and (7, 0xfffffff8); the #7 forms use r1 only. rawcond runs
`and` with the field set to each of 1 to 15 over the pairs (0, 0), (1, 1), (5, 3), (0x7fffffff,
0xffffffff), (0x80000000, 0x80000000) and (0xffffffff, 0xffffffff), whose results are 0, 1, 1,
0x7fffffff, 0x80000000 and 0xffffffff. rawcond2 runs the same 15 values on `or`, `xor` and `rol`
with r2 over the pairs (0, 0), (1, 1), (0xffffffff, 0), (0x80000000, 0), (0x7fffffff, 0x80000000)
and (0x80000000, 0x80000000), and on `and` and `xor` with #7 over r1 = 0, 7, 0xffffffff, 0x80000000,
0xfffffff8 and 0x7ffffff8.

**Results.** test-plain: 96 of 96 equal the test of op(r1, source 2), so the raw path agrees with
the text path. test-bit43: the taz words (field 9) give the plain taz answers and the tanz words
(field 0xa) answer true for a positive nonzero result only: for `and` with r2 the six pairs read 0,
1, 0, 0, 0, 0 where the plain tanz word reads 0, 1, 1, 1, 0, 0. rawcond: the field values 1, 2, 4
and 8 read as their conditions; 5 (taz, nat) never; 6 (tanz, nat) as nat; 9 (taz, pat) as taz; 0xa
as tanz and pat; 3 as tanz; 7 as 6; 0xb as 0xa; 0xc as 8; 0xd as 9; 0xe and 0xf as 0xa. rawcond2:
the rule (zero part: tanz if bit 41, else taz if bit 40; sign part: pat if bit 43, else nat if bit
42; p0 = the AND of the parts present) predicted the readback of all five probes, 90 of 90 each; the
plain AND and OR of the set conditions fit fewer.

**What it shows.** [HW] Setting bit 43 in a class 9 test word changes the test: it does not invert
source 2 (the invert fits 53 of 96). The field is two parts, a zero part (bit 41 over bit 40) and a
sign part (bit 43 over bit 42), the parts present ANDed; tanz with pat is a one-instruction 'greater
than zero' test that the assembler does not write. The rule held on the forms of rawcond2 for these
six input pairs each. [HW] Every raw test word run has enc[39] = 1, the `a` join, and chan0
(enc[38:36] = 0), 732 words: 'ANDed' is the rule for the `a` join on chan0, and the `o` join
(enc[39] = 0) with a two-part field was not run. [infer] The refusal of `~` in a test (E473) fits
this: the bit that `~` sets in the non-test forms is the pat bit of a test word, so there is no
invert bit there; whether a test word has another way to invert a source was not run, and that the
refusal is an encoding limit and not an assembler gap stays an inference from this. [infer] The rule
on the other forms (the shifts `shl`, `shr` and `asr`, `or` and `rol` with #7, 8-bit and 16-bit lane
operations) and for chan fields other than chan0 is not run.

**What it does not show.** The `o` join (enc[39] = 0) with a field of 3 to 15, `.chan` fields other
than chan0, the shifts, the immediates other than #7, the field value 0, and the other classes'
tests (`iadd32` and the like were run with the single conditions the assembler writes, E498, not
with combined fields). The input pairs of a form give few distinct results, and not every class of
result in each: rawcond (`and`, r2) 5 results (zero, two positive, two negative); rawcond2 `and`
with #7 2 (0 and 7: no negative result, so the sign parts are only tested on a nonnegative result),
`or` 4 (0, 1, 0x80000000, 0xffffffff), `xor` with registers 3 (0, 0x80000000, 0xffffffff: no
positive nonzero result), `rol` 5 and `xor` with #7 6. So 'tanz with pat' on a positive nonzero
result is shown by test-bit43, rawcond and the forms with such a result only. Narrows nothing of
Q123, Q126 or Q127; Q137 keeps the open rest.

**Correction, 2026-11-08 (11.27).** The measurements above are unchanged. E529 ran the `o` join:
with enc[39] = 0 and chan0 the two parts of the field are ORed and a part absent from the field
counts as true (a rule read from the 90 readbacks of a first table, where the prediction 'ORed with
an absent part false' fitted 75 of 90, then predicted all 270 cases of `or`, `xor` and `and` with #7
over other pairs), so a one-part field is always true under the `o` join and 'ANDed' above is the
`a` join only. E530 ran the chan field: none of the values 1 to 7 reads as chan0 with the `a` join
(the prediction that it is ignored failed in seven of seven tables); the 252 readings fit the rule
of *Test channels*, read after the data. The statements above that the assembler writes one
condition at a time and does not write 'greater than zero' are wrong: usse-asm, run on the host
after the data with no hardware, assembles `and.testpanz.chan0 !c0, p0, r1, r2` to the field 0xa
(tanz with pat) with the `a` join, `.testnaz` to the field 5 with the `a` join and `.testnoz` and
`.testtoz` to the fields 5 and 1 with the `o` join, and `.andall`, `.orall`, `.and02` and `.or02` to
chan 4 to 7; the hardware ran those fields as raw words only. Still not run: the shifts, the other
classes' tests, the `o` join with a chan other than chan0, and the field value 0 (Q137).
