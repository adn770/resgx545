+++
id = "E742"
claim = "Two o1 writes under complementary predicates (the !p1 write tagged 2' first, the p1 write tagged 2 second, p1 set by a test of g25) were run with E709's layout; the controls were E709's o4 job (22 tag-5 pairs, inside the frozen 17 to 29) and both writes unpredicated, which the design required to show the second write at every source pixel and which showed it at 492 of 497 and the first write at 5, one cluster (sources (16,25), (16,27), (17,27), (18,27), (19,27)), so the frozen verdict is cannot tell; read after the run, with k = 7 no pixel got tag 2, with k = 0 a quarter did, all at even x and even y, with k = 3 a quarter at odd x and odd y, and the replicate of the k = 7 x job differs from it in 36 dwords"
unit = "pds"
method = "S1 stage p-c (13 jobs, 12 conditions; paths relative to render/closing-s1/ of the dataset: E709's x/y pair layout with new programs that write o1 twice under complementary predicates, the and.testtanz immediates decimal; c-e709 and c-u first), a debugfs reset before each, on the laptop (direct cable), 2026-11-09, kernel 7.3.0-resgx545, module B21FDA82BD5E5CB5A627E3B, stock firmware, tool ~/sgxfive-test-s1 (sha256 d776afbc...); programs bins/s1c-* frozen with the tables; scored by the frozen score/score_s1.py p-c (out/score-p-c.txt); the fractions by position and the replicate comparison by analysis/scripts/pixel_c_*.py, written after the run"
tiers = ["HW", "infer"]
date = "2026-11-09"
data = ["render-closing-s1:out/p-c/"]
terms = ["PDS_SIZE.BITS17_16"]
+++
**What ran.** Q276 asks whether a predicate set from g25 gates the write at all (E709's o4 writes
and pairs were the same for every k). Frozen: HN (both writes land, the second wins: tag 2'
nowhere), HA (all or nothing per job), HP (per pixel: a quarter at k = 0 to 3, none at k = 7, a half
at g23). Controls: c-e709 (17 to 29 tag-5 pairs) and c-u (both writes unpredicated: tag 2
everywhere).

**Frozen verdict.** cannot tell: controls failed or void (c-e709 22 pairs: passed; c-u 0.990, tag 2
everywhere required) (out/score-p-c.txt).

**Results [HW].** c-e709: 22 tag-5 pairs. c-u: tag 2 at 492 source pixels, tag 2' at 5, contiguous
((16,25), (16,27), (17..19,27)), x and y jobs agreeing. One run.

**Why the control failed: the hardware, against an exact criterion.** The premise "the second
unpredicated write lands at every pixel" is false at 5 of 497 sources in this run; the decode is
consistent there (x and y tags agree). Whether it repeats is not known.

**Post hoc [infer].** k = 7: 0 tag 2 of 483; k = 0: 124 of 493 (0.252), all at sources with even x
and even y; k = 3: 120 of 483 (0.248), all at odd x and odd y; g23: 0.253 where the frozen HP said
0.5, concentrated where x mod 8 < 4 and y mod 8 < 4. By the proposal's rules HN and HA would be
refuted and HP holds but for g23: the predicate gates o1 per pixel with g25 reading the pixel's
place in the 2 x 2 quad. In c-k0, 5 sources show both tags. c-k7-x-rep differs from c-k7-x in 36
dwords, which the scorer did not compare. A frozen rerun confirms.

**Not shown.** What g23 and g25 hold beyond the quad position; why five sources took the first
write.

**Correction 2026-11-10:** S1b's p-c (E759) repeated the order control three times and the
first-write oddity partly repeats: the sources that kept the first write were five in the first
rerun ((16,25), (16,27), (17..19,27), as here), four in the second and two in the third, with
(16,27) and (17,27) in all three; the tag-2 fraction was 0.990, 0.992 and 0.996. 'Whether it repeats
is not known' is therefore: it repeats at a few sources, not at the same five. The post-hoc g23
fraction read 0.237 (here 0.253) and c-k7-x-rep differed from c-k7-x in 61 dwords (here 36), so the
repeat of those numbers is approximate; the k = 7, 0 and 3 readings repeated in nearly the same
numbers (0.000, 0.253 and 0.248) (S1 post hoc fits run again, not held out).

**Correction 2026-11-10:** The g23 reading "concentrated where x mod 8 < 4 and y mod 8 < 4" is
replaced, post hoc and from R1-pixgeo's own data (E772, whose frozen verdict was cannot tell): the
direct read of g23 gave o0 = x mod 32 in 1062 of 1062 pixels, and the tag-2 share of the mask 0x10
was 0.239 there and 0.237 in S1b, the share of the sources with x bit 4 set (the sources run over
x 10 to 54); as a per-source rule it also fits S1 and S1b's c-g23 (an offline recount of the
proposal, not re-checked here). The y bit played no part (the mask 0x100000 gave none). The
quad-position reading of g25 repeated as a lane id (E772), also post hoc.
