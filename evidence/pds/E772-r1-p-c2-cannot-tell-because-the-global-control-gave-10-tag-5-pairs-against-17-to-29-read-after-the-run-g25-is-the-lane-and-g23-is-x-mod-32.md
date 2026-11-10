+++
id = "E772"
claim = "R1-pixgeo stage p-c2 (41 jobs: 18 configurations of S1b's p-c program as an x job and a y job whose pixel words decode to their source pixel, the direct reads c-rd-g23 and c-rd-g25, the premise pair c-rd-pa and one replicate): the frozen verdict is CANNOT TELL, because the global control c-e709 (E709's o4g-3 unchanged) gave 10 tag-5 pairs against the frozen 17 to 29, so no held-out row was scored (the order controls c-u and c-u-r2 passed the frozen 0.98 with 0.990 and 0.994, and c-rd-pa held 1.000 of 1062 pixels); read after the run and not held out [infer over data]: under `xor.testtaz.chan0 !c0, p1, g25, #k` the tag-2 write landed only at (odd x, even y) for k = 1 (120 of 489 o1 sources, 0.245), only at (even, odd) for k = 2 (118 of 484) and never for k = 5 or 7 (0 of 479 and 0 of 487), the replicate the same; the direct read of g25 gave o0 = (x & 1) | (y & 1) << 1 in 1062 of 1062 written pixels and that of g23 gave o0 = x mod 32 in 1062 of 1062, so the masks 0x01, 0x08, 0x10 gave tag 2 at x bit 0, 3 and 4 and 0x20 and 0x100000 never; the o4 writes were tag 5 and never tag 5' under k = 0, 3, 7 and unpredicated (37, 42, 21 and 23 pairs); the tag-5 pair count of the 18 configurations ran from 10 to 42, 8 of 18 outside the frozen range"
unit = "pds"
method = "R1-pixgeo stage p-c2 of the question-closing pass, round 2 (decision R2-11; 41 jobs in the order of tables/p-c2.txt: the 18 configurations c-e709, c-u, c-u-r2, c-g23r4, c-k7, c-k0, c-g23, c-k1, c-k2, c-k5, c-g23r5, c-g23r3, c-g23r0, c-g23r20, c-o4-u, c-o4-k7, c-o4-k3 and c-o4-k0 each as an x and a y job (36 jobs), the direct reads c-rd-g23 and c-rd-g25, the premise pair c-rd-pa-x and c-rd-pa-y and the replicate c-k1-x-rep) of the dataset render-closing-r1-pixgeo, on the laptop (host cedar), 2026-11-10 from 09:37 laptop time (08:37 UTC), kernel 7.3.0-resgx545, module srcversion B21FDA82BD5E5CB5A627E3B (installed = loaded), stock firmware, tool ~/sgxfive-test-r1 (sha256 bf4f8be2d8a8fe50034559450928e05695dc96d396d4892f9b00ea6bc0d4f053), each job the probe --tri pixel with --temps 32 --pixels --width 64 --height 64 --vtx-coords 2 --blk 4=0x00030001, S1b's pixel PDS pds_iter_xy and vertex program vtx_coords and only the pixel program (r1c-NAME.bin) changed, a debugfs reset before each job, all 41 of class ok; the knob proofs the program sha256 and the job markers read from the o2 tags of the decoded words; the frozen predictions (predictions/p-c2.tsv, PREDICTIONS.sha256) from S1b's fits (the repeat rows c-k7, c-k0 and c-g23) and the proposal's hypotheses HQ-a, HQ-b, HQ-none, HG, HG-xy, HN-o4, HG-o4 and H-g25-7; scored by the frozen score/score_r1.py p-c2 (out/score-p-c2.txt), re-run on the kept files with the same SUMMARY; the post hoc numbers were computed after the run by scratch scripts that import the frozen scorer's decode (score_q276 c_decode and read_grid) and are not in the repository"
tiers = ["HW", "infer"]
date = "2026-11-10"
data = ["render-closing-r1-pixgeo:out/p-c2/"]
terms = ["PDS_SIZE.BITS17_16"]
+++
**What ran.** E742 and E759 read the predicate guard post hoc: g25 == 7 gave no tag-2 write, g25 ==
0 a quarter of the landings at (even, even) sources, g25 == 3 a quarter at (odd, odd), and the g23
test 0.237. The stage was the frozen test with rows held out: k = 1 and 2 (HQ-a against its
transpose HQ-b), k = 5 (HQ-none), the masks 0x01, 0x08, 0x20 and 0x100000 (HG against HG-xy), the o4
writes under k = 7, 3 and 0 and unpredicated (HN-o4, HG-o4, H-g25-7) and two direct reads of g23
and g25 through `or.skipinv o0, g, #0`. A mask above 127 does not assemble as an immediate, so the
new masks went through a register, validated by the control c-g23r4 (mask 0x10) against S1b's
immediate form c-g23.

**Frozen verdict.** `SUMMARY: cannot tell: global controls failed or void (c-e709 tag-5 pairs
17..29: 10; order controls (frozen minimum {'c-u': 0.98, 'c-u-r2': 0.98}):
{'c-u': 0.9897959183673469, 'c-u-r2': 0.9938775510204082}); void []`. The frozen rule made a
failed global control void for the whole stage, so no row, held out, repeat or replicate, was
scored. Nothing in the post hoc part below is a frozen result.

**Controls [HW].** c-e709, E709's configuration unchanged: 10 tag-5 pairs (frozen 17 to 29, the
range of E709's five jobs). c-u: tag-2 fraction 0.990 (485 against 5 first-write survivors); c-u-r2
0.994 (487 against 3). c-rd-pa: 1062 pixels, o0 = pa0/pa1 decodes to the pixel's own position in
1.000, so the direct reads' premise (o0 lands at its pixel) held. The replicate c-k1-x-rep read the
tag-2 fraction 0.247 against 0.245 with the same parity class.

**Read after the run [infer over data; not held out, not frozen].**
- g25. c-k1: tag 2 in 120 of 489 o1 sources (0.245), all at (odd x, even y); c-k2: 118 of 484
  (0.244), all at (even, odd); c-k0 (a repeat of S1b's fit): 125 of 491, all at (even, even); c-k5
  and c-k7: none. The direct read c-rd-g25 of 1062 written pixels equals (x & 1) | (y & 1) << 1 in
  1062 (the transpose: 0.508); the values 0 to 3 occur 261 to 273 times each. This is HQ-a of the
  frozen table: a lane id in the 2 x 2 quad, the predicate true for the instance whose lane equals
  k, the write absent for k above 3.
- g23. c-rd-g23: o0 = x mod 32 in 1062 of 1062 pixels (x from 8 to 54), equal to x in 714 (those
  with x below 32), never equal to y << 16 | x, the high half zero everywhere. The mask rows fit it
  in every case: 0x01 gave tag 2 in 236 of 474 sources (0.498, all at odd x), 0x08 in 213 of 489
  (0.436), the register form of 0x10 in 114 of 476 (0.239; S1b's immediate form, c-g23, 110 of 464,
  0.237) and 0x20 in 0 of 486, although the stage's sources run over x 10 to 54 and 334 of the 486
  have x bit 5 set; 0x100000 in 0 of 477. HG's x bit 5 miss is therefore the width of what g23
  carries (x mod 32), not a failure of the mask; the sources' x range was read before this
  statement. The earlier reading of E742 and E759 (x mod 8 below 4 and y mod 8 below 4) is replaced
  by x bit 4 of the source.
- o4. Under k = 0, 3 and 7 and unpredicated the o4 landings were all tag 5 (the p1-true write's
  tag) and never tag 5': 37, 42, 21 and 23 pairs, the o1 writes of those jobs unpredicated. HN-o4
  (the o4 write is not gated) fits all four rows; HG-o4 (5' at k = 7 and 3) and H-g25-7 (5' at k = 3
  and 0) do not. This repeats E709's reading, that the o4 writes and pairs are the same for every
  k, at k = 7 where the o1 write never lands.
- The tag-5 pair count over the 18 configurations: 10, 13, 14, 15, 15, 16, 17, 20, 21, 21, 21, 22,
  23, 27, 28, 29, 37 and 42. E709's 17 to 29 was five configurations of one family; the spread over
  the stage's 18 is wider, so the failed control reads as a range too narrow for the quantity, not
  as a changed baseline [infer: the quantity's cause was not read].

**Not shown.** Nothing frozen: every hypothesis row of the stage is untested by its own rule. A
rerun with a pair-count control of 10 to 42 and the same rows would make the readings above frozen;
the direct reads, whose premise held, are the nearest to a test already. Which instances run when
the predicate gates a write (Q276's second half) is read only as the 2 x 2 lane id, from the
stage's own post hoc numbers.
