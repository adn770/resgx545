+++
id = "E878"
claim = "R6-pixel stage p6-rd (Q276, 58 jobs in E709's command: a triangle's pixel program writes R5's walk words to o0 to o7, then `mov.skipinv r10, oJ` and `mov.skipinv.end o0, r10`, so the own pixel shows what oJ held; frozen verdict 'cannot tell: rd entries rd-1, rd-2, rd-3, rd-4, rd-5, rd-6, rd-7 not decided'): every control passed (c-u G-o1 0.990 of 492 sources, c-all4 5:1, c-ow 1.0 and c-rd-0 1.0 of the 1062 TRI pixels, both c-prd-0 rows' lanes as frozen: the predicate gates an o0 write per lane), but no readback configuration reached the frozen class share of 90 percent of TRI in both jobs: the top label of each rd entry held 87 to 89 percent in the x job and 88 to 97 percent in the y job, the rest mostly words of the job from another source pixel (113 to 134 a job in the x jobs), so the rd vector, the independent rows, the replicate and the predicate rows are cannot tell; read after the run, not held out: the top labels are o1's, o2's and o3's own words at rd-1 to rd-3 and o0's, o1's, o2's and o3's words at rd-4 to rd-7 (H-MOD4's vector, 99.7 to 100 percent of the x jobs' own-source words), o4 read o0's word with no o4 write and with o4 written as tag 13, o5 written as tag 14 read o1's word, and the readback of o3 after `p1 or.skipinv o3` showed the predicated word on lane k only at k = 0 to 3 and on no lane at k = 7, while that of o4 showed o0's word on every lane"
unit = "pds"
method = "R6-pixel stage p6-rd of the question-closing pass, round 6 (decisions R6-2 a and pixel 2 a, plan closing6/pixel/exp-pixel-r6.md section 2, PREFLIGHT.md 3), dataset render-closing-r6-pixel, on the laptop (host cedar, direct cable), 2026-11-12, attempt out/20261112-142113 (stage started 14:21:13 Mac time, the first of five stages, the only attempt; run-r6p.log), kernel 7.3.0-resgx545, module srcversion 99CD90DA26E3AFF9C450517 (the rgn4 module of R4-pixel, installed = loaded, knobs at their defaults at the stage start), stock firmware sha256 6a00268e9d4ca552c02e52651a42a2b4db3887d7fe626f209888369985162b0a, tool ~/sgxfive-test-rgn4 (sha256 e6951558a93b4b7bc750eeae302997992d7ec6e26719bc527ba1ffc9c6fb779a, TOOL.sha256), not rebuilt; freeze FROZEN.sha256 (sha256 e6371195613a1d5cb4c80594e1c7caa79d1863564e0162437ff825c938dcbd4c) and PREDICTIONS.sha256 before the first job, FROZEN.commits pinning the resgx545 files read at d9b2969 (which holds E871 and E872, cited by the predictions); every job with knob `stophang s2` (STATUS2 0x400 at every read), a debugfs reset before each job, no fault, every job class ok, health ok after the stage, the bridge gate PASS; no stop, no refreeze and no lead decision during the run; the session's files on the laptop under ~/scratch/r6p, per-job work directories under ~/scratch/tmp, nothing in /tmp; at the fold all 1222 kept files of the attempt decompress to the raw sha256 and size the laptop logged. Each job `probe --tri pixel --temps 32 --pixels --dump-render DIR --width 64 --height 64 --vtx-coords 2 --blk 4=0x00030001 --slot pixpds=pds_iter_xy.bin:12 --slot vtxuse=vtx_coords.bin PROGRAM`, R5's p5-o4 command byte for byte; programs from bins/ (gen/r6_rd.py, R5's program builder gen/r5_o4.py pinned; every new program run in sgx-sim before the freeze); predictions frozen in predictions/p6-rd.tsv (score/rdmodel.py: H-STORE, H-FOUR, H-O0, H-MOD4, and gated, ignored, never per lane); scored by the frozen score/score_r6.py p6-rd (score/score_rd.py; R4's and R5's readers pinned; scorekit copied from resgx545); the kept score-p6-rd.txt, gate-p6-rd.txt and the verdict line were reproduced byte for byte at the fold (2026-11-12) by the frozen scorer on the kept files; fold/posthoc_r6.py sections A and B (output fold/posthoc_r6.txt), the frozen scorer's own reader run over every readback and predicate configuration, is a post hoc reading at the fold, not frozen"
tiers = ["HW", "infer"]
date = "2026-11-12"
data = ["render-closing-r6-pixel:out/20261112-142113/p6-rd/", "render-closing-r6-pixel:fold/"]
terms = ["PDS_SIZE.BITS17_16", "Universal Scalable Shader Engine (USSE)"]
+++
**What ran.** E871 showed that the own words of `o4` to `o7` reach no pixel of any kept image, so
Q276's question became whether such a write is stored at all. Stage p6-rd reads an output register
back inside the instance: rd-j is R5's walk row w-j (`o_j`'s word with bit 4, every other output's
with bit 5) followed by `mov.skipinv r10, o_j` and `mov.skipinv.end o0, r10`, so the own pixel
shows what `o_j` held (E373 ran `mov` from `o0` and `o1`). TRI is the 1062 pixels whose word is
their own in both jobs of c-rd-0. A configuration reads a class when one label holds at least 90
percent of TRI in both its x and y job: S (`o_j`'s own word), A0 (`o0`'s word, label 1:2), A4
(`o_(j-4)`'s word, j >= 5), X, O or W. Frozen models over j = 1 to 7: H-STORE (S everywhere),
H-FOUR (S at 1 to 3, not S at 4 to 7), H-O0 (A0 everywhere), H-MOD4 (S at 1 to 3, A0 at 4, A4 at
5 to 7). Beside them: n-rd-1 and n-rd-4 (no write to the register read), x-rd-4 and x-rd-5 (tags
13 and 14), a replicate of rd-4, and the predicate rows prd-3 and prd-4 at k = 0, 1, 2, 3 and 7
(`xor.testtaz.chan0 !c0, p1, g25, #k`, then `p1 or.skipinv o_j` with bit 4), scored per lane only
if rd-j read S. 14 controls first, every configuration an x and a y job.

**Results [HW].** Frozen verdict, printed: "cannot tell: rd entries rd-1, rd-2, rd-3, rd-4, rd-5,
rd-6, rd-7 not decided"; gate PASS. From `out/20261112-142113/score-p6-rd.txt`:

| row | read | frozen |
|---|---|---|
| c-u (G-o1) | tag-2 fraction 0.990 of 492 sources | >= 0.98 |
| c-all4 | 5:1 | 5:1 |
| c-ow, c-rd-0 | 1.0 and 1.0 of 1062 TRI pixels | >= 0.95 |
| c-prd-0 k = 1, k = 7 | lanes 1:2, 1:1, 1:2, 1:2 and 1:2 on all four | as read |
| rd-1 | x 2:1 949, D 113; y 2:1 1026, D 19, 6:3 16 | class at >= 90 percent |
| rd-2, rd-3 | 3:1 942 / 933, 4:1 926 / 945 | |
| rd-4 | 1:2 931 / 943 | |
| rd-5, rd-6, rd-7 | 2:2 933 / 1023, 3:2 946 / 937, 4:2 925 / 944 | |

(x job / y job, of 1062; "D" is a word with the job's marker that decodes to another source.) No
class reached 90 percent in both jobs, so every rd entry is undecided; n-rd-1, n-rd-4 and the
replicate are cannot tell, and x-rd-4, x-rd-5 and both predicate sets cannot tell by design (rd-j
did not read S). The controls show that the readback works and that the frozen predicate shape
gates an `o0` write per lane: c-rd-0 read `o0`'s first word through `r10` at every TRI pixel, and
c-prd-0 at k = 1 put the predicated word on lane 1 only, at k = 7 on no lane.

**Read after the run, post hoc (`fold/posthoc_r6.txt` sections A and B) [HW, not held out].** The
frozen reader, run over every configuration and printing each job's labels:

- The top label of each rd entry is S at rd-1 to rd-3 and A0 at rd-4, A4 at rd-5 to rd-7: the
  vector H-MOD4 (and so H-FOUR) predicts, in every one of the 14 jobs, at 87 to 89 percent of TRI
  in the x jobs and 88 to 97 percent in the y jobs. Among the TRI pixels whose word decodes to the
  pixel itself the top label holds 99.7 to 100 percent in the x jobs and 90 to 98 percent in the y
  jobs, where up to 85 own-source words of tag 2 with bits 2 read beside it.
- The D words are `o1`'s displaced word (tag 2, 88 to 90 a job in the x jobs) and OR words (tags 5
  to 7, E858), that is, the walk's other outputs landing on TRI pixels from other sources; c-rd-0
  writes no `o1` to `o3`, so its TRI has none [infer: the frozen 90 percent did not budget for
  them].
- n-rd-4 (no `o4` write) read `o0`'s word 1:2, as rd-4 and its replicate; x-rd-4 (`o4` written as
  tag 13) read 1:2 too, and x-rd-5 (`o5` as tag 14) read `o1`'s word 2:2: what was written to `o4`
  or `o5` never showed. n-rd-1 (no `o1` write) left the background word at 942 and 814 of the TRI
  pixels.
- prd-3: the readback of `o3` showed the predicated word (4:1) on lane k only at k = 0, 1, 2 and 3
  and on no lane at k = 7, in both jobs, at 84 to 91 percent of each lane: the frozen "gated"
  pattern, below the frozen lane share of 95 percent. prd-4: `o4` read `o0`'s word (1:0, the
  base word) on every lane at every k.

**What it shows.** The frozen test decides nothing: its class share was set without room for the
words the walk's other outputs leave on TRI pixels, and every rd entry fell up to 3 points short in
at least one job. Read post hoc, with the same reader: a `mov` from `o1`, `o2` or `o3` returns the
word written there, and a `mov` from `o4` to `o7` returns the word of `o0` to `o3` (the register
number modulo 4) whatever was written to `o4` or `o5`, so no read of `o4` to `o7` shows a word of
their own [infer: the vector and the independent rows agree, none held out]. The predicate gates
the `o3` write per lane, as E808 showed for `o1` [post hoc]. Refuted by: a frozen rerun with the
class share counted over own-source words in which rd-4 reads S, or x-rd-4 shows tag 13.

**What it does not show.** Whether an `o4` to `o7` write is stored anywhere (no read of it shows
its word, which fits a write that is dropped and a read that is aliased alike); whether the
predicate gates the `o4` write (its readback never shows `o4`'s word, so the clause cannot be read
this way either); why a read of an unwritten `o1` gives the background word; why the y jobs hold
own-source tag-2 words at TRI pixels. None of the post hoc readings is held out.
