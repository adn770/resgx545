+++
id = "E880"
claim = "R6-pixel stages p6-l3 and p6-s (Q276 and Q023, 8 and 22 jobs; frozen verdicts 'H-Y1; x jobs 5:1, 5:1 (frozen 5:1)' and 'H-OR: 5:3 5:2 5:2 5:3 5:2 5:2 5:2 5:2 5:0; restore check (r-u G-o1) PASS'): in E709's command the o3 word that enters the tag-5 OR word is the word of lane 0 of the quad in the x job and of lane 1 in the y job: with o3 written as one word under `p1` (g25 == k) and another under `!p1`, the x job read the `!p1` word at k = 1 and 2 and the y job the `p1` word at k = 1 and the `!p1` word at k = 2 (H-Y1, held out; R5's k = 0 and k = 3 programs repeated R5's reading, the determinism control); in E406's full setup (ISP word 0 at 0x05d00200, render details dword 9 bit 0 set by the tool's `--kpoke rd:9=1`, state block word 4 at 0x00030001), whose eight-tag control again left tags 1 and 5 only (997 and 65, 992 and 70 words), the walk read bits 5:4 of the tag-5 word as 3, 2, 2, 3, 2, 2, 2, 2 for o0 to o7 and a program with no o4 write the plain tag 5 (H-OR, held out, 18 jobs; H-OWN4 refuted at s-0, s-3, s-4 and s-n4), so the tag-5 word E406 read as o4 on other pixels is the OR of o0 and o3 there too (E406 corrected); the restore check with dword 9 back at its default passed G-o1 (0.992 of 498 sources)"
unit = "pds"
method = "R6-pixel stages p6-l3 (optional set L3) and p6-s (optional set S, last) of the question-closing pass, round 6 (decisions R6-2 a and pixel 4 a and 5 a, plan closing6/pixel/exp-pixel-r6.md sections 2.5 and 2.6, PREFLIGHT.md 3), dataset render-closing-r6-pixel, on the laptop (host cedar, direct cable), 2026-11-12, attempt out/20261112-142113 (p6-l3 started 14:26:23 and p6-s 14:37:28 Mac time; run-r6p.log), the boot, module, firmware, tool, freeze and pins of E878 (FROZEN.sha256 e6371195..., FROZEN.commits at d9b2969); knob `stophang s2` on every job (STATUS2 0x400 at every read), a reset before each job, no fault, every job class ok, health ok after each stage, both gates PASS; no stop, no refreeze and no lead decision during the run. p6-l3: R5's p5-o4 command byte for byte (E858), R5's P3 programs p3-pa-k0 and p3-pa-k3 byte for byte (gen/r5_o4.py) and new p3-pa-k1 and p3-pa-k2 (gen/r6_rd.py, run in sgx-sim before the freeze), an x and a y job each; a job's label by R4's class rule (at least 10 tag-5 words of one label, no other above 2). p6-s: the same command with `--blk 1=0x05d00200 --kpoke rd:9=1` (the tool's own option: render details dword 9 of that job's render, applied once and dropped by the kernel; debugfs kpoke read empty before and after every such job, as the runner checked and logged), R5's walk programs (o5model.walk), R5's c-all4 words as c-s-all4 and n-o4 as s-n4; then R4's c-u program as r-u with `--kpoke rd:9=0` (dword 9's default). Predictions frozen in predictions/p6-l3.tsv (H-Y1, H-Y2, H-YN) and p6-s.tsv (H-OR, H-OWN4); scored by the frozen score/score_r6.py p6-l3 and p6-s (score/score_rd.py; R5's reader score_o5.read_cfg pinned); the kept score and gate files of both stages and the verdict lines were reproduced byte for byte at the fold (2026-11-12) by the frozen scorer on the kept files"
tiers = ["HW", "infer"]
date = "2026-11-12"
data = ["render-closing-r6-pixel:out/20261112-142113/p6-l3/", "render-closing-r6-pixel:out/20261112-142113/p6-s/"]
terms = ["PDS_SIZE.BITS17_16", "CR_REG_0148", "ISP0", "Universal Scalable Shader Engine (USSE)"]
+++
**What ran.** E858 showed that the word at the tag-5 pixels of E709's command is the OR of the
source instance's `o0` and `o3` words, with two things left: R5's predicated `o3` rows (P3) read
the `p1` word in the x job and the `!p1` word in the y job at k = 0, which no lane-0 reading
explains; and E406's full setup, where the eight-tag shader leaves tags 1 and 5 only and E406 read
tag 5 as `o4`'s, was never walked. Set L3 (stage p6-l3) runs R5's P3 programs at k = 0 and 3 again
(they must read as R5) and new ones at k = 1 and 2: `o3` gets tag 4 under `p1` (g25 == k, set by
`xor.testtaz.chan0 !c0, p1, g25, #k`) and tag 4 with bit 4 under `!p1`, so the tag-5 word reads 5:0
where the `o3` word is that of the lane k and 5:1 otherwise. Frozen: the x job 5:1 at k = 1 and 2
(its `o3` word is lane 0's, R5); the y job H-Y1 (lane 1: 5:0 at k = 1, 5:1 at k = 2), H-Y2 (lane 2:
the reverse) or H-YN (neither: 5:1 at both). Set S (stage p6-s) runs R5's walk under E406's setup:
H-OR (the tag-5 word is `o0` OR `o3`: 3, 2, 2, 3, 2, 2, 2, 2 and tag 5 with no `o4` write) against
H-OWN4 (`o4`'s own word: 2, 2, 2, 2, 1, 2, 2, 2 and no tag 5 with no `o4` write), with its control
c-s-all4 (E406's pattern: tags 2 to 4 at most 2 words a job, tag 5 at least 10, else the set is
void) and a restore check after it.

**Results [HW], p6-l3.** Frozen verdict, printed: "H-Y1; x jobs 5:1, 5:1 (frozen 5:1)"; the
controls PASS. From `out/20261112-142113/score-p6-l3.txt` (tag-5 label and words, x job / y job):

| row | x job | y job |
|---|---|---|
| p3-pa-k0 (control) | 5:0 (27) | 5:1 (39) |
| p3-pa-k1 | 5:1 (32) | 5:0 (43) |
| p3-pa-k2 | 5:1 (47) | 5:1 (38) |
| p3-pa-k3 (control) | 5:1 (37) | 5:1 (37) |

**Results [HW], p6-s.** Frozen verdict, printed: "H-OR: 5:3 5:2 5:2 5:3 5:2 5:2 5:2 5:2 5:0;
restore check (r-u G-o1) PASS"; gate PASS. From `out/20261112-142113/score-p6-s.txt`: c-s-all4
held tags 1 and 5 only, 997 and 65 words in the x job, 992 and 70 in the y job (E406's pattern);
the walk s-0 to s-7 read 5:3, 5:2, 5:2, 5:3, 5:2, 5:2, 5:2, 5:2 (54 to 70 tag-5 words a job, one
label in every job) and s-n4 the plain 5:0 (57, 54); r-u, with dword 9 back at its default, read a
tag-2 fraction of 0.992 of 498 sources (frozen at least 0.98). H-OWN4 is refuted by s-0 and s-3 (2
predicted, 3 read), s-4 (1 predicted) and s-n4 (no tag 5 predicted).

**What it shows.** In E709's command the `o3` word that enters the OR at a tag-5 pixel comes from
lane 0 of the quad in the x job and from lane 1 in the y job, which explains R5's k = 0 rows (the x
job's lane 0 wrote the `p1` word, the y job's lane 1 the `!p1` word); the two jobs' programs differ
in the coordinate their words carry and in the marker (gen/r5_o4.py), so why the lane differs is not
shown. Under E406's full setup the tag-5 word is the OR of `o0` and `o3` as well: the setup that
makes `o1` to `o3` stop landing on other pixels leaves one other-pixel word, and it is not `o4`'s.
E406's "o4 on other pixels" is corrected. Refuted by: a y-job label off H-Y1 at k = 1 or 2, a walk
entry off H-OR's vector under the setup (none).

**What it does not show.** Why the lane of the `o3` word depends on the job (x or y) and not on
the source pixel alone [infer: both jobs' pairs come from (even, even) sources, E858]; where `o4`
to `o7`'s own words go and whether a write to them is stored (E878); E406's other data rows (2 to
4: tags 1, 3, 5, 7) were not walked, nor ISP word 0 bit 27 in place of bit 26.
