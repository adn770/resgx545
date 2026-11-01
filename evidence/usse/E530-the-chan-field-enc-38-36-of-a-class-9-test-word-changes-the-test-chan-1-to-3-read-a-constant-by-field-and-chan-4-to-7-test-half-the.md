+++
id = "E530"
claim = "The chan field enc[38:36] of an and test word with the a join changes what the test reads: the prediction written before the runs (the chan field does not change a test of a 32-bit result, p0 as for chan0) failed for each of the seven values 1 to 7 (the readings fit 26, 26, 26, 32, 30, 32, 30 of the 36 cases of the six fields 1, 2, 4, 8, 9, 0xa over six input pairs); chan 1, 2 and 3 read the same constant for every input pair (taz 0, tanz 1, nat 0, pat 1, taz with pat 0, tanz with pat 1: 36 of 36 equal across the six pairs and the three values), chan 4 and chan 6 read tanz and pat as the result's (true when the result is nonzero, true when it is not negative) and taz and nat as false in all six pairs (the same readings in the two tables), and chan 5 and chan 7 read taz and nat as the result's and tanz and pat as true in all six pairs (the same readings in the two tables)"
unit = "usse"
method = "on the laptop (direct cable), linux fork 6ee9501832af, module srcversion 14D099861204842EA496D85, tool sgxfive-test-1126 (sha256 751f7223c8c731a08d75cfc3920a5d1050488ca3bdc426be45b7c431e600f82e): seven raw tables probes/usse/rawchan-1.toml to rawchan-7.toml (probes usse-rawchan-N-and, 36 jobs each: and.testtaz.chan0 !c0, p0, r1, r2 as the word 0x48081181000C0082 with enc[38:36] = N, enc[39] = 1 and enc[43:40] = 1, 2, 4, 8, 9 and 0xa, six input pairs (0, 0), (1, 1), (5, 3), (0x7fffffff, 0xffffffff), (0x80000000, 0x80000000), (0xffffffff, 0xffffffff) with results 0, 1, 1, 0x7fffffff, 0x80000000, 0xffffffff); raw tables, run last, one at a time with a health triangle after each, no job failed to recover; the prediction (p0 as for chan0: the chan field does not change a test of a 32-bit result) and its alternative (the test of byte N & 3 of the result) were written before the runs and both failed (verdict NONE in all seven; the byte reading fits 14, 14, 18, 26, 16, 18, 22 of 36); the readings below are read from the data after the runs and are not a prediction; recounted by a script outside the kit"
tiers = ["HW", "infer"]
date = "2026-11-08"
data = ["usse-rawchan-1", "usse-rawchan-2", "usse-rawchan-3", "usse-rawchan-4", "usse-rawchan-5", "usse-rawchan-6", "usse-rawchan-7"]
terms = ["Universal Scalable Shader Engine (USSE)"]
+++

**What runs.** The raw words are the test word of E499 with the three bits enc[38:36] set to N. The
assembler writes chan1, chan2 and chan3 as such words (.chan1 gives 0x48081191000C0082), and N = 4,
5, 6 and 7 are the words it writes for `.andall`, `.orall`, `.and02` and `.or02` (checked with
usse-asm on the host after the runs; the tables ran them as raw words). Six field values (1, 2, 4,
8, 9, 0xa), six pairs, 36 jobs a table.

**Results.** Readings by field (taz = 1, tanz = 2, nat = 4, pat = 8, 9 = taz with pat, 0xa = tanz
with pat; six pairs, 1 = p0 set). Chan 1, 2, 3: 000000, 111111, 000000, 111111, 000000, 111111. Chan
4 and 6: 000000, 011111, 000000, 111100, 000000, 011100. Chan 5 and 7: 100000, 111111, 000011,
111111, 100000, 111111. For comparison chan0 with the a join (E499): 100000, 011111, 000011, 111100,
100000, 011100.

**What it shows.** [HW] The chan field is not ignored by a 32-bit and test: none of the seven
non-zero values reads as chan0 as a table over the six fields. Per field the readings of chan4 and
chan6 equal chan0's for tanz, pat and tanz with pat (011111, 111100, 011100) and those of chan5 and
chan7 for taz, nat and taz with pat (100000, 000011, 100000), so a 32-bit test of those conditions
gives the same result on them, and `chan0` is the safe form for any test of a 32-bit value. [infer]
Read after the data, not predicted: the channel table of the assembler
(crates/usse-isa/src/kinds.rs: enc[38:36] = chan0, chan1, chan2, chan3, andall, orall, and02, or02)
and the simulator's predicate rule (a channel with no lane reads 1: taz 0, tanz 1, nat 0, pat 1;
that rule is the one on the landed *Test channels* page, which predates E530 and was not predicted
for these runs) account for all 252 readings (36 in each of the seven tables): chan1 to chan3 are
channels with no lane, a constant per field; chan4 and chan6 (the and joins, `andall` and `and02`)
are tanz and pat from the result with taz and nat false, since the channels with no lane make taz
and nat false; chan5 and chan7 (the or joins, `orall` and `or02`) are taz and nat from the result
with tanz and pat true. That is a reading of the data with an existing rule, not a test of it: the
prediction ignored the field, and failed because a 32-bit result has channel 0 only.

**What it does not show.** The o join with a chan other than 0, other fields than the six, other ops
than and with two registers, and the 8-bit and 16-bit lane forms as raw words (the *Test channels*
page already has [HW] readings of lane operations through the assembler's chan names, 360 cases:
what is not is the raw word on lanes). Opens Q150.
