+++
id = "E871"
claim = "Offline reading of kept images (Q276; no new job, post hoc counts, no held-out row): in E709's command the own words of o4 to o7 reach no pixel of any kept image: in E858's walk rows w-4 to w-7, where only o_j's word carries bit 4 and every other output's word bit 5, 0 of the 12143 image words with the job's marker carry bit 4 (8 jobs), while the rows' positive controls w-0 to w-3 hold 1944, 1007, 106 and 78 such words (o0 to o3); every word of E858's 54 marker jobs is a word of o0 to o3 or an OR of them [infer for the few tag-6 and tag-3 OR words]; in E570's 68 jobs at ten target shapes (64 x 64 to 256 x 128, PDS_SIZE 0 to 3), whose shader tags o0 to o7 as 1 to 8, none of the 221662 single-image marker words is tag 8, and the tag-5 to tag-7 words (2393 pairs) never land at their source's place in another 32 x 16 tile, the way o1 to o3 land, but all come from (even, even) sources as E858's OR words; E081's o4 to o7 images equal the previous case's image at every non-background pixel (348, 348, 348 and 312 of as many in the x run, 348, 348, 312 and 276 in the y run), so they show no word of the oN write (E081 corrected)"
unit = "pds"
method = "Offline, 2026-11-12, round 6 planning and fold of the closing pass (plan closing6/pixel/exp-pixel-r6.md section 1, user decision R6-1 a: land the offline results before any freeze), no laptop, no job; standard-library scripts in closing6/pixel read published kept data only: o47_scan.py (output o47_scan.out) over E858's p5-o4 (render-closing-r5-pixel, attempt out/20261112-091752/p5-o4, markers bins/p5o4-markers.tsv, the frozen decode score/r4lib.py and score/score_o4.py imported unchanged) counts every word of both images of each marker job by marker, tag and bits 5:4 (E858 had printed bits 5:4 for paired words only); o47_e570.py (o47_e570.out) over E570's dumps (usse-output-room-tiles, tables o23-tiles, o23-order, o23-size, 34 configurations of an x and a y job) pairs the two images' words of each tag and splits them into own, regular (same place in another 32 x 16 tile) and irregular; o47_e081.py (o47_e081.out) over E081's raw images (usse-output-registers, oreg-x and oreg-y) compares each case's non-background pixels with case 0's and with the case before; explorations o47_disp.py, o47_p3.py and o47_mem.py (their .out files) are reported in the plan and not used for the claim; each count was made after E858's and E570's runs and their readings, and the walk's design, not a frozen prediction, fixes what a bit-4 word means: post hoc, not held out; every script re-run at the fold from its published copy (cited/closing6/pixel in resgx545-data) with output byte-identical to the kept .out files"
tiers = ["HW", "infer"]
date = "2026-11-12"
data = ["render-closing-r5-pixel:out/20261112-091752/p5-o4/", "render-closing-r5-pixel:bins/", "usse-output-room-tiles", "usse-output-registers", "cited-scratch:closing6/pixel/"]
terms = ["PDS_SIZE.BITS17_16", "Universal Scalable Shader Engine (USSE)"]
+++
**What was read.** E858 showed that the word at the tag-5 pixels of E709's command is the OR of
the source instance's `o0` and `o3` words and left open where the own words of `o4` to `o7` go
(Q276). Its walk was designed so that a bit marks one output: in row w-j only `o_j`'s word carries
bit 4 and every other output's word carries bit 5 (tags unchanged, `o1` written twice as R5).
Any image word with the job's marker and bit 4 set is therefore `o_j`'s word, or contains it by an
OR. E858's scorer printed bits 5:4 for the words of the paired pixels only; this reading counts
every word of both images of each row. Two older sets are read the same way: E570's 68 jobs at ten
target shapes and E081's one-register images. Nothing here was frozen before a run: the counts are
post hoc, and the walk's own rows w-0 to w-3 are their positive controls.

**Results [HW], E858's walk (`closing6/pixel/o47_scan.out`).** Words with the job's marker, both
jobs of each row:

| row | words with bit 4, by tag | words without |
|---|---|---|
| w-0 | tag 1: 1845, tag 5: 96, tag 3: 3 | 1096 |
| w-1 | tag 2: 983, tag 12: 11, tag 6: 11, tag 3: 2 | 2044 |
| w-2 | tag 3: 106 | 2941 |
| w-3 | tag 5: 72, tag 6: 6 | 3004 |
| w-4, w-5, w-6, w-7 | none | 3048, 3033, 3030, 3032 |

0 of 12143 words in the 8 jobs of w-4 to w-7 carry bit 4, and no job holds a word of another job's
marker. Read with E858's OR: tag 5 is `o0` OR `o3`, tag 6 `o1` OR `o3` and the few tag-3 words
with bits 5:4 = 3 `o0` OR `o1` [infer for tag 6 and tag 3: few words], so every word of the 54
marker jobs is a word of `o0` to `o3` or an OR of them.

**Results [HW], E570's jobs (`closing6/pixel/o47_e570.out`).** E570's shader writes all eight
outputs, tag j + 1 at `o_j`, with no private bit. A pair is "regular" when its word sits at its
source's place in another 32 x 16 tile (how `o1` to `o3` land, E570), "irregular" otherwise:

| tag | own | regular | irregular | irregular sources |
|---|---|---|---|---|
| 1 (`o0`) | 64116 | 0 | 0 | |
| 2 (`o1`) | 0 | 14342 | 40 | |
| 3 (`o2`) | 2 | 3318 | 1597 | (even, even) but 4 |
| 4 (`o3`) | 0 | 1480 | 11 | |
| 5, 6, 7 | 0 | 0 | 1818, 247, 328 | (even, even), 2393 of 2393 |
| 8 (`o7`) | 0 | 0 | 0 | |

Single-image words with the job's marker, by tag 1 to 7: 147078, 42439, 16905, 6244, 6405, 1138
and 1453, 221662 in all, and no tag-8 word; 8 is the one tag no OR of tags 1 to 4 can make. Tags
5 to 7 never land the regular way, at any of the ten shapes: they are the irregular words from
(even, even) sources, as E858's OR words (5 = 1 | 4, 6 = 2 | 4, 7 = 3 | 4) [infer: E570's words
carry no private bit, so the OR reading of its tags 5 to 7 rests on E858's walk].

**Results [HW], E081's images (`closing6/pixel/o47_e081.out`).** E081 wrote `pa0` (x run) or
`pa1` (y run) to one register `oN` with no `o0` write and no marker, one run a case, the cases in
order. The `o4`, `o5`, `o6` and `o7` images equal the image of the case before at every
non-background pixel: 348 of 348, 348 of 348, 348 of 348 and 312 of 312 in the x run, 348, 348,
312 and 276 of as many in the y run. No pixel of those images holds a word that differs from what
the previous case left; with E373 (an output a job does not write keeps what the job before left)
they read as leftovers [infer]. E081's claim gets a dated correction.

**What it shows.** In E709's command no word that only `o4` to `o7` could have written reaches the
image: the bit that marks them is absent in 12143 of 12143 words where the same design shows the
bit of `o0` to `o3` in 3135 words. A larger target or another PDS_SIZE does not bring them out
either (E570: no tag 8, no regular tag 5 to 7). So the image cannot answer where those words go,
and the predicate clause of Q276 cannot be read from image pairs: a run must read an output back
inside the instance (the plan's stage p6-rd). Refuted by: one marker word with bit 4 in w-4 to w-7,
a tag-8 word or a regular tag-5 to tag-7 pair in E570's data (none).

**What it does not show.** Whether an `o4` to `o7` write is stored at all (readable back by `mov
r10, oN`), and whether the predicate gates it; why `o0` and `o3` combine and at which pixels; why
the pair counts wander (Q276). The three readings are counts on kept data, made after the runs and
their readings, not a frozen test. E081's words carry no marker, so its own-pixel words cannot be
told from a write of the same value there; that the `o4` to `o7` images show no write rests on
"no pixel differs from the case before" together with E858's marked walk. The explorations of the
plan (displacements of the OR words, the P3 lane pattern, the parameter-buffer dumps) are not
results here.
