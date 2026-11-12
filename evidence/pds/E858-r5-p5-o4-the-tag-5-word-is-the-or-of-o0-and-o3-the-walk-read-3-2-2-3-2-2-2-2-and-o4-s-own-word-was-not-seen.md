+++
id = "E858"
claim = "R5-pixel stage p5-o4 (Q276, 58 jobs in E838's shape: a triangle's pixel program writing tagged words to o0 to o7 in E709's command, state block word 4 at 0x00030001; frozen verdict 'the tag-5 word is OR(o0,o3) (walk, z-o3, l-o4, l-o6 and the replicate)'): the word read at the tag-5 pixels is the OR of the source instance's o0 (tag 1) and o3 (tag 4) words: with bit 4 on one output and bit 5 on every other, bits 5:4 of the tag-5 words read 3, 2, 2, 3, 2, 2, 2, 2 for o0 to o7 (16 held-out jobs, OR(o0,o3)'s vector; each other model of E850 is refuted by the w-0 entry alone), o3 written as tag 0 left no tag-5 word and 46 displaced tag-1 pairs, o4 written as tag 4, o6 as tag 3 and no o4 write at all each read the plain tag 5, and the replicate of w-3 agreed; the controls and the walk's positive controls passed (c-all4 5:1, c-v-a4 5:0, c-e709-x bits 5:4 = 3 at 28 of 28 tag-5 words, G-o1 0.996 of 488 sources, bit 4 at 887 of 887 and 486 of 486 own words); o4's own word was not seen, so the predicate rows on o4 (P4) are cannot tell by design, and the o3 predicate rows (P3) cannot tell by the frozen rule, their k = 0 x and y jobs reading different classes"
unit = "pds"
method = "R5-pixel stage p5-o4 of the question-closing pass, round 5 (decisions R5-3 a and pixel 2 a, plan closing5/pixel/exp-pixel-r5.md section 2, PREFLIGHT.md 3), dataset render-closing-r5-pixel, on the laptop (host cedar, direct cable), 2026-11-12, attempt out/20261112-091752 (stage started 09:17:52 Mac time, the first of three; run-r5p.log), kernel 7.3.0-resgx545, module srcversion 99CD90DA26E3AFF9C450517 (the rgn4 module of R4-pixel, installed = loaded, knobs at their defaults at the stage start), stock firmware sha256 6a00268e9d4ca552c02e52651a42a2b4db3887d7fe626f209888369985162b0a, tool ~/sgxfive-test-rgn4 (sha256 e6951558a93b4b7bc750eeae302997992d7ec6e26719bc527ba1ffc9c6fb779a, TOOL.sha256), not rebuilt; freeze FROZEN.sha256 (sha256 b4ea4eca...) and PREDICTIONS.sha256 (1e7700ff...) before the first job, FROZEN.commits pinning the resgx545 files read at f0d5b39 (which holds E850 and E851, cited by the predictions); every job with knob `stophang s2` (STATUS2 read after the debugfs reset and after the job: 0x400 at every read), a reset before each job, no fault, every job class ok, health ok after the stage, the bridge gate PASS; no stop and no lead decision during the run. The laptop's /tmp was filling while the session ran; the lead checked the 330 kept text files whole and found no write error in the logs, and at the fold every one of the 642 kept files of the attempt decompresses and its sha256 equals the raw sha256 the laptop logged. Each job `probe --tri pixel --temps 32 --pixels --dump-render DIR --width 64 --height 64 --vtx-coords 2 --blk 4=0x00030001 --slot pixpds=pds_iter_xy.bin:12 --slot vtxuse=vtx_coords.bin PROGRAM`, R4's p4-o4 command byte for byte; programs from bins/ (gen/r5_o4.py; c-e709 is E709's o4g-3 unchanged, c-u and c-v-a4 R4's programs byte for byte, the 48 new programs run in sgx-sim before the freeze, PREFLIGHT.md 7.5); predictions frozen in predictions/p5-o4.tsv (the nine models of E850, score/o5model.py); scored by the frozen score/score_r5.py p5-o4 (score/score_o5.py; R4's score_o4.py decode, pinned; scorekit copied from resgx545); the kept score-p5-o4.txt and gate-p5-o4.txt and the verdict line were reproduced byte for byte at the fold (2026-11-12) by the frozen scorer on the kept files; fold/posthoc_r5.py (its output fold/posthoc_r5.txt, sections A and B) is a post hoc reading at the fold, not frozen"
tiers = ["HW", "infer"]
date = "2026-11-12"
data = ["render-closing-r5-pixel:out/20261112-091752/p5-o4/", "render-closing-r5-pixel:fold/"]
terms = ["PDS_SIZE.BITS17_16", "Universal Scalable Shader Engine (USSE)"]
+++
**What ran.** E850 left nine bitwise models of the tag-5 word, each a rule over one instance's
output words, and no kept job that changed `o0`, `o2`, `o3`, `o5`, `o6` or `o7`. Stage p5-o4 ran
E838's job shape with new words: a walk w-0 to w-7 in which `o_j`'s word carries bit 4 and every
other output's word bit 5 (tags unchanged), so each model predicts its own vector of bits 5:4 at
the tag-5 words; four independent rows that change one output's tag (z-o3: `o3` = tag 0; l-o4:
`o4` = tag 4; l-o6: `o6` = tag 3; n-o4: no `o4` write); two predicate sets at k = 0, 3 and 7 in
both orders (P4 on `o4`, P3 on `o3`); a replicate of w-3; and eight controls first. Each
configuration is an x job and a y job (58 jobs). A configuration reads a class when both jobs
have at least 10 words of it and at most 2 of any other (R4's rule).

**Results [HW].** Frozen verdict, printed: "the tag-5 word is OR(o0,o3) (walk, z-o3, l-o4, l-o6
and the replicate)"; gate PASS. From `out/20261112-091752/score-p5-o4.txt`:

| rows | read (tag-5 words, x and y job) | OR(o0, o3) frozen |
|---|---|---|
| c-e709, c-u, c-v-a4 | 5:0 (28 and 30, 44 and 40, 29 and 40) | 5:0 |
| c-all4 (every output bit 4) | 5:1 (45, 30) | 5:1 (all nine) |
| w-0 / w-3 | 5:3 (29, 67 / 34, 38) | 3 |
| w-1, w-2, w-4 to w-7 | 5:2 (20 to 62 words a job) | 2 |
| replicate of w-3 | 5:3 | 3 |
| z-o3 | no tag-5 word, 46 displaced tag-1 pairs | displaced tag 1 |
| l-o4, l-o6, n-o4 | 5:0 (39, 23; 38, 35; 37, 39) | 5 |
| P4 (12 jobs) | 5:0 at every k and order | cannot tell by design |

The walk read 3, 2, 2, 3, 2, 2, 2, 2: OR(o0, o3)'s vector. AND(o4, o6), XOR(o3, o5, o6) and the
MUX models with `o2`, `o3`, `o5`, `o6` predicted 2 at w-0, XOR(o0, o2, o6) and MUX(o4; o0) 1:
each is refuted by w-0 alone, and the walk agrees with OR(o0, o3) at all eight entries. Controls:
c-e709-x's tag-5 words had bits 5:4 = 3 at 28 of 28 (E709's 0xcf5, as E850's 39 of 39); G-o1, the
tag-2 fraction of c-u, 0.996 of 488 sources; the walk's positive controls, bit 4 at 887 of 887
own-pixel tag-1 words of w-0 and 486 of 486 tag-2 words of w-1.

**Reported beside the walk, not frozen [HW].** The scorer prints, per walk row, bits 5:4 of the
words of each tag. Tag-3 words carry `o2`'s bits (1 at w-2, 2 elsewhere) and tag-12 words `o1`'s
(1 at w-1); tag-6 words, 0 to 3 a row, read 3 at w-1 and w-3 and 2 elsewhere, which is what
OR(o1, o3) (tag 2 OR tag 4) gives [infer, few words].

**The predicate rows on `o3`, post hoc (not held out; `fold/posthoc_r5.txt` section B).** P3
writes `o3` = tag 4 under `p1` and tag 4 with bit 4 under `!p1`. The frozen predictions under
OR(o0, o3), with the pair source at lane 0 (E808): gated reads 5:0 at k = 0 and 5:1 at k = 3 and
7 in both orders; ignored (the last write lands) reads 5:1 in the order `p1` first and 5:0 in the
other. Read: 5:1 in both jobs at k = 3 and 7 in both orders (8 jobs), which "ignored" misses in the
swapped order (4 jobs); at k = 0 the x jobs read 5:0 and the y jobs 5:1, in both orders, so those
two rows are undecided and the frozen set is cannot tell. A y job at k = 0 reading the `!p1` word
fits neither a gated write at lane 0 nor an ignored one [infer: in the y job the `o3` word of the
tag-5 pixel may come from another instance of the quad].

**E850's family check against this run (`fold/posthoc_r5.txt` section A).** E850 modelled every
one of its 8 configurations with `o4` written at the pair source. Three of them guard the `o4`
write by `p1` with k other than 0: E709's o4g-3 (`p1 or.skipinv o4` with g25 == 3, the c-e709-x
configuration) and R3's k3 and k5/k7 (`p1 or.skipinv o4` with g25 == k). The pair sources are
lane 0, so if the predicate gates `o4` as E808 showed it gates `o1`, those jobs never wrote `o4` at
the source, and the six models that read `o4` fit them only on E850's assumption. This run does not
tell whether the predicate gates `o4` (its word does not reach the image), but it does not need to:
the walk's programs are unpredicated, and n-o4, with no `o4` write at all, read the plain tag 5 as
OR(o0, o3) predicts. E850 gets a dated correction.

**What it shows.** In E709's command shape the word at the tag-5 pixels is OR of the source
instance's `o0` and `o3` words, not a word of `o4`: tag 1 OR tag 4 is 5, which is also why no
tag-4 word was ever read (E838). Every result of E808, E838 and E850 on the "o4 words" is a result
on that OR. Refuted by: a walk entry off OR(o0, o3)'s vector, or a tag-5 word with `o3` = tag 0
(none of 16 and none).

**What it does not show.** Where the own words of `o4` to `o7` go (no tag-8 word is read; tags 7,
12 and 15 are rare) and whether the predicate gates `p1 or.skipinv o4`: P4 cannot be read while
`o4` does not reach the image. Why two outputs combine at one pixel, by what path, and why the pair
counts wander (Q276). The P3 reading is post hoc and its k = 0 y jobs are not explained. All of it
is in E709's command (state block word 4 = 0x00030001), not E406's full setup with the ISP word 0
and `CR_REG_0148` bits.
