+++
id = "Q276"
question = "is a write to o4 to o7 stored at all in E709's command (state block word 4 at 0x00030001), now that their own words reach no pixel of any kept image (E871) and a read of them inside the instance (`mov r10, oN`, then o0 = r10) returned the word of o0 to o3, the register number modulo 4, whether o4 or o5 was written or not (E878, read post hoc: the frozen readback test is cannot tell), and does a predicate set by `xor.testtaz.chan0 !c0, p1, g25, #k` gate the write `p1 or.skipinv o4` (it gates o0's write per lane, and read post hoc o3's, E878)"
unit = "pds"
kind = "hw"
value = "high"
phase = 11
evidence = ["E709", "E570", "E406", "E742", "E759", "E772", "E808", "E838", "E850", "E858", "E081", "E871", "E878", "E880"]
terms = ["PDS_SIZE.BITS17_16"]
+++
Q023 asks which lanes write o4 to o7 in the four-output-room setup. E709 guarded o4 by a test of g25
against k and found tag-5 pixels (25 to 48 in each x or y job) and 17 to 29 pairs, all from
even-even source pixels, for every k, as for the unconditional job. The lane-0-only reading (pairs
only for k = 0) was right in 4 of 10 jobs (two configurations, x and y) and wrong in 6; the any-lane
reading cannot be told from 'the predicate does nothing'. The 5 configurations were not repeated,
so the differences in pair counts between them (17 to 29) are not read.

Open: whether `testtaz.chan0` with a predicate destination `!c0, p1` writes p1 per instance, for the
whole task (channel 0 only) or not at all in this encoding, and whether `p1 or.skipinv` is
predicated on it. A guard that cannot hold was not run.

To settle it: the same shader with k = 7 (g25 never equals it) and k = 3 on a job whose output is
read back, a store of p1 into a register (through a `mov` on the predicate), and the o4 write
guarded by g23 bit 4 (a test of a different register), all five with the setup of E709.

Post hoc 2026-11-09 (S1, E742; read after the run, not held out; the frozen verdict was cannot tell,
the control c-u showing the first unpredicated write in 5 of 497 sources). With k = 7 no source
shows the predicated write, with k = 0 a quarter do, all at even x and even y, and with k = 3 a
quarter, all at odd x and odd y, which reads as the predicate gating the write per pixel with g25
taking the pixel's place in its 2 x 2 quad; with g23 a quarter show it (not the half the frozen
prediction said), concentrated where x mod 8 < 4 and y mod 8 < 4. A frozen rerun is needed.

Post hoc 2026-11-10 (S1b, E759; repeat only, no held-out row). The order control c-u passed the
frozen criterion (tag-2 fraction at least 0.98) in 3 of 3 runs (0.990, 0.992 and 0.996), the first
write surviving at 5, 4 and 2 sources, (16,27) and (17,27) in all three. S1's post hoc readings
repeated in their numbers: g25 == 7 no tag 2 (0 of 486 landings), g25 == 0 a quarter, all at (even,
even) sources (0.253), g25 == 3 a quarter, all at (odd, odd) sources (0.248), g23 0.237; the frozen
HQ (g25 = the lane in the 2 x 2 quad) is consistent in 3 rows, as a repeat. A frozen test with a row
held out against that reading has not run.

Note 2026-11-10 (R1-pixgeo, E772; the frozen verdict is cannot tell, the question stays open). The
frozen test with held-out rows ran (41 jobs) and scored nothing: its global control c-e709 (E709's
configuration unchanged) gave 10 tag-5 pairs against the frozen 17 to 29, which voids the stage by
its own rule, although the order controls (0.990, 0.994) and the premise of the direct reads (1.000)
passed. Read after the run, so not a result [infer over the stage's data]: g25 is a lane id of the
2 x 2 quad (the direct read of g25 equals (x & 1) | (y & 1) << 1 in 1062 of 1062 pixels; k = 1 wrote
only at (odd x, even y), k = 2 only at (even, odd), k = 5 and 7 never, a replicate the same), g23
carries x mod 32 (the direct read, 1062 of 1062; the masks gave x bits 0, 3, 4 and nothing for bit 5
and the y bit), and the o4 write is tag 5 and never tag 5' at k = 0, 3, 7 and unpredicated, that is,
not gated. That answers the first half of the question as "not gated" and the second as "the lane
whose id equals k writes o1" on post hoc readings only; the stage's tag-5 pair counts ran from 10 to
42 over its 18 configurations, so E709's 17 to 29 was too narrow a control. Open: a frozen rerun
with the same rows and a control range from the stage's own counts.

Narrowed 2026-11-10 (R3-pixel, E808; not retired). The frozen rerun with controls scoped to their
group held E772's post hoc readings, frozen as a model, in all 29 rows it scored: g25 is the
instance's lane in its 2x2 quad, g23 = x mod 32 and g24 = y mod 16 (held out, at three triangles),
and a predicate set by `xor.testtaz.chan0 !c0, p1, g25, #k` gates the o1 write per instance (the
lane whose id equals k writes). The o4 clause is not settled: every o4 word was tag 5 in both write
orders, also where 5' was the later write, so the swapped-order control failed and its three rows
are cannot tell, and tag 5 alone in the original order (k = 0, 3 and 7) cannot tell a predicate that
is ignored from a write that lands whatever the order (E772's 'not gated' does not follow). Open:
whether the predicate gates `p1 or.skipinv o4`, and which of two o4 writes lands, and why.

Note 2026-11-11 (round 4, a reading of E808's data and of the generator; [data] and [source] for
the facts, [infer] for V1 to V3). Both order rules are refuted for the o4 clause: with the 5' write
first and 5 last (4 configurations) and with 5 first and 5' last (4 configurations) every o4 word
read was tag 5 (25 to 51 words a job, tag 5' in none), so "the last write wins" and "the first write
wins" are each contradicted by four configurations. What can decide is the value: the generator's
tags are 5 and 13 (0xd, 5'), which differ in bit 3 only (`gen/r3_c.py`). Readings that fit all 16
jobs: V1 the path drops bit 3 of the word (13 lands as 5); V2 a word with bit 3 set does not land;
V3 the two writes combine (AND gives 5, the smaller wins). OR is refuted (it gives 13). Tag 8 (o7)
never appears in the pairs of E570 and E709 (tags 5 to 7 only), which V1 and V2 also predict. The
predicate clause cannot be read until this is known: with k = 7 the p1 write never runs, the !p1 write
carries 13, and 5 was read all the same. No offline check separates V1 to V3; the planned stage
p4-o4 separates them with tags that differ in one other bit (the bit-4 and bit-5 marker variants).

Narrowed 2026-11-11 (R4-pixel p4-o4, E838; the question line is reworded, the question is not
retired). The question line asked "does a predicate set by `xor.testtaz.chan0 !c0, p1, g25, #k`
gate the write `p1 or.skipinv o4` at all (E709: the o4 writes and their 120 pairs are the same for
k = 0, 1, 2, 3 and for no guard), and which instances run when it does". With words that differ
in bit 4 or 5 as well as bit 3, every value configuration held out read the plain tag-5 word, also
a program that wrote only tag 5 with bit 4 (v-a4), or only tag 13: none of the 12 frozen models
(V1 drops bit 3, V2 refuses a word with bit 3, V3 as written, by five combine rules) fits, frozen
verdict "family REFUTED", and the 12 predicate jobs are cannot tell by their frozen gate. Read at
the fold, post hoc: no word of any of the 36 jobs had bit 4 or 5 set, and none had tag 4 (o3) or
8 (o7). Two readings fit and neither is tested [infer]: the path that brings o4 out clears bits
5:3; or the tag-5 words are not o4's but tag 1 (o0) OR tag 4 (o3). Open: which reading holds (a
run that changes o0's or o3's tag and leaves o4 alone separates them); then, with words that
reach the image, the predicate clause.

Note 2026-11-12 (E850, an offline reading of E808's and E838's kept images; post hoc against
E838's reading, no held-out row; the question stays open). The first of E838's two readings, "the
path that brings o4 out clears bits 5:3", is refuted on kept data: the 1525 tag-5 words of E808's
44 jobs whose marker has a bit at 5:4 all keep it, and E838's c-e709-x (every output 0xcf0 | tag)
read 0xcf5 at 39 of 39; bit 4 is absent only when `o4` alone carries it (v-a4). So the other
outputs' words decide those bits [infer]. Of 821 bitwise models declared before the check (OR,
AND, XOR over subsets of one instance's `o0` to `o7`, MUX of one output's bits 2:0 with another's
bits 5:3), 9 fit all 8 kept configurations: OR(o0, o3), AND(o4, o6), XOR(o0, o2, o6), XOR(o3, o5,
o6) and MUX(o4's bits 2:0, bits 5:3 of o0, o2, o3, o5 or o6). No kept job changes `o0`, `o2`,
`o3`, `o5`, `o6` or `o7`, so a run is needed: a walk that puts bit 4 on one output at a time
separates all nine (plan closing5/pixel/exp-pixel-r5.md, stage p5-o4). The question line's "bits
5:3 clear" is true of E838's marker-layout jobs only, and its "E709's four-output setup" means
E709's command (state block word 4 at 0x00030001), not E406's full setup with the ISP word 0 and
`CR_REG_0148` bits; both are reworded when the question is next narrowed.

Narrowed 2026-11-12 (R5-pixel p5-o4, E858; the question line is reworded, the question is not
retired). The line read "which of the pixel words of E709's four-output setup are o4's own (E838:
whatever a triangle's pixel program wrote to o4, tag 13, tag 5 with bit 4 or 5, alone or with the
plain tag-5 word in either order, every word at the tag-5 pixels was the plain tag 5 with bits 5:3
clear, and no tag-4 word was ever read), and does a predicate set by `xor.testtaz.chan0 !c0, p1,
g25, #k` gate the write `p1 or.skipinv o4`, and which instances run when it does". The walk of
p5-o4 (bit 4 on one output, bit 5 on the others, 16 held-out jobs) read bits 5:4 = 3, 2, 2, 3, 2,
2, 2, 2 at the tag-5 words for o0 to o7, OR(o0, o3)'s vector, and the independent rows and the
replicate agreed (frozen verdict "the tag-5 word is OR(o0,o3)"): none of the tag-5 words is o4's,
so the first half is answered "none", and the predicate clause cannot be read in this shape (P4
cannot tell by design). Of E850's nine models the other eight are refuted; E850's family check
had assumed o4 written at the source lane in three predicated configurations (its correction of
2026-11-12). Post hoc, not held out: the o3 predicate rows (P3) fit a gated o3 write at k = 3 and
7 in both orders and refute "the last write lands" in the swapped order, while at k = 0 the x jobs
read the p1 word and the y jobs the !p1 word, unexplained. Open: where o4 to o7's own words land
(a run that reads them, for example with o0 and o3 written as tag 0 so that no OR reaches the
tag-5 pixels), then whether the predicate gates the o4 write; the line says "E709's command"
rather than "four-output setup", as E850's note asked.

Narrowed 2026-11-12 (E871, an offline reading of kept images, post hoc counts, no held-out row; the
question line is reworded, the question is not retired). The line read "where do the own words of o4
to o7 go in E709's command (state block word 4 at 0x00030001), now that the word at the tag-5 pixels
is the OR of the source instance's o0 and o3 words (E858: the walk read OR(o0,o3)'s vector and a
program with no o4 write read tag 5), and does a predicate set by `xor.testtaz.chan0 !c0, p1, g25,
#k` gate the write `p1 or.skipinv o4`". The walk of E858 marks one output by bit 4: in the rows w-4
to w-7 none of the 12143 words with the job's marker carries it, while the rows w-0 to w-3 hold
1944, 1007, 106 and 78 such words, and every word of the 54 marker jobs is a word of o0 to o3 or an
OR of them. E570's 68 jobs at ten target shapes hold no tag-8 word in 221662 marker words, and their
tag-5 to tag-7 words never land at their source's place in another tile (the way o1 to o3 land) but
come from (even, even) sources, as E858's OR words. E081's o4 to o7 images equal the previous case's
image at every non-background pixel: leftovers (E373), not writes (E081 corrected). So "where do
they go" has the offline answer "on no pixel, at any shape tried", and the predicate clause cannot
be read from image pairs. Open: whether an o4 to o7 write is stored at all, read back inside the
instance (`mov r10, oN`, then o0 = r10: the plan's stage p6-rd, closing6/pixel/exp-pixel-r6.md
section 2), then, if o4 reads back, whether the predicate gates its write per lane.

Narrowed 2026-11-12 (R6-pixel p6-rd, p6-l3 and p6-s, E878 and E880; the question line is reworded,
the question is not retired). The line read "is a write to o4 to o7 stored at all in E709's command
(state block word 4 at 0x00030001), now that their own words reach no pixel of any kept image (E871:
0 of 12143 marked words of E858's walk rows w-4 to w-7, no tag-8 word in E570's 68 jobs) and the
word at the tag-5 pixels is the OR of the source instance's o0 and o3 words (E858), and does a
predicate set by `xor.testtaz.chan0 !c0, p1, g25, #k` gate the write `p1 or.skipinv o4`". Stage
p6-rd read each output register back inside the instance with every control passing (the readback
through `r10` 1.0 of TRI, the predicate gating an `o0` write per lane as frozen), but no readback
configuration reached the frozen share of 90 percent of TRI in both jobs (87 to 89 percent in the x
jobs: words the walk's other outputs leave on TRI pixels from other sources), so its frozen verdict
is cannot tell and the predicate rows are cannot tell by design. Read post hoc with the same reader
(E878, not held out): `o1` to `o3` read back their own words, `o4` to `o7` the words of `o0` to `o3`
(H-MOD4's vector), also with no `o4` write and with `o4` written as tag 13 or `o5` as tag 14; the
readback of `o3` after `p1 or.skipinv o3` showed the predicated word on lane k only, and that of
`o4` showed `o0`'s word on every lane. Decision R6-6 a retires the `o4`-predicate clause if `o4`
does not read back; the reading that it does not is post hoc, the frozen test cannot tell, so the
clause is kept and narrowed, not retired. Set L3 (E880, held out): the `o3` word in the tag-5 OR is
lane 0's in the x job and lane 1's in the y job (H-Y1), which explains R5's P3 rows at k = 0. Set S
(E880, held out): in E406's full setup the tag-5 word is the OR of `o0` and `o3` too (E406
corrected). Open: whether an `o4` to `o7` write is stored anywhere (a frozen rerun of rd-4, n-rd-4
and x-rd-4 with the class share taken over the own-source words would decide the readback; if `o4`
reads as `o0` there, nothing in this command observes an `o4` write and the predicate clause can be
retired as not observable), and why the lane of the OR's `o3` word depends on the job.
