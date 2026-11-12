+++
id = "E911"
claim = "R7-geo stage tx, type 5 (Q178; E725's 64 x 32 map-texture fill, dword i of the texture 0xD0000000 | i; 6 jobs, no fault): TEXTYPE 5 reads the texture memory: with the program zeroing the texture's first 112 dwords before its sample the 16 x 16 image is 0x00000000 in all 2048 pixels, with it setting them to 0xffffffff 0x0000ffff in all 2048, where the plain 16 x 16 control gives E894's image (0 at x mod 16 below 8, 0x0000ffff above, every row alike), so H-STEP's premise that the image does not follow the texture failed 2 of 2; at 32 x 32 and 64 x 64 the image is E894's 16-column step again (H-FIX16, 2 of 3) and not a step at half the width (H-STEP, 0 of 3), and at 8 x 8 it is constant along each row and alternates by row (0 in even rows, 0x0000ffff in odd ones, post hoc), which neither rival predicted; frozen verdicts 'Q178 H-STEP (memory: the image does not follow the texture) held is not supported: 0 held, 2 FAILED', 'Q178 type 5 H-STEP held is not supported: 0 held, 3 FAILED' and 'Q178 type 5 H-FIX16 held is not supported: 2 held, 1 FAILED'"
unit = "texture"
method = "R7-geo stage tx of the question-closing pass, round 7 (decisions R7-2 a, R7-7 a, decision 5 a of closing7/rank/rank-round7.md; plan R7-4), dataset render-closing-r7-geo, on the laptop (host cedar), 2026-11-12, attempt out/20261112-211113 (stage started 21:12:26 Mac time), kernel, module 41E2F5C756F96D20F7109A4, firmware and tool t4 as E910's, which reports the stage's other twelve rows; jobs `probe --temps 32 --coords --pixels` of bins/r7g-ty5-*.bin (templates/tx_map.s with E725's generator at 8 x 8, 16 x 16, 32 x 32 and 64 x 64; the two memory rows add, before the sample, stores of 0 or 0xffffffff to the texture's first 112 dwords, the most a 256-word probe takes: README deviation 3), the health fill and triangle after every job, every job class ok, health ok after each. Frozen before the first job: H-STEP (0 where x mod w < w / 2, 0x0000ffff above, constant in y, independent of the texture memory; fitted on E567's one 16 x 16 image, E894 [infer]), H-FIX16 (E894's 16-column step at every size), and, for the memory rows, 'the image equals the plain 16 x 16 control' (H-STEP's premise; a difference reads H-MEM); the plain 16 x 16 row is a control with E894's image. The memory rows are scored rows of their own claim, not controls that gate the type 1, 3 and 4 rows. Scored by the frozen score/score_g.py tx (score-tx.txt); at the fold the output re-ran byte-identical and the kept files matched the laptop's sha256 (fold/reproduce.sh). Post hoc at the fold, not frozen: fold/tx_read.py prints each type 5 image's values, distinct rows and x and y periods"
tiers = ["HW", "infer"]
date = "2026-11-12"
data = ["render-closing-r7-geo:out/20261112-211113/tx/", "render-closing-r7-geo:fold/"]
terms = ["TEXTYPE"]
+++
**What ran.** E894 read E567's three 16 x 16 TEXTYPE 5 jobs post hoc: no pixel holds a texel tag,
0 at x mod 16 = 0 to 7 and 0x0000ffff at 8 to 15 in every row, and inferred that type 5 is no
layout of the 32-bit texels. Stage tx froze that image as H-STEP (the step at half the width,
independent of the texture memory) and ran type 5 at 8 x 8, 32 x 32 and 64 x 64 (H-STEP against
H-FIX16, a step every 16 columns whatever the size), with two memory rows at 16 x 16: the same
program storing 0, then 0xffffffff, over the texture's first 112 dwords before it samples. H-STEP
predicts no change from the plain 16 x 16 image; any change means the image follows the memory.

**Frozen verdict (as printed).** `SUMMARY: Q178 H-STEP (memory: the image does not follow the
texture): ... held is not supported: 0 held, 2 FAILED, 0 cannot tell of 2`; `Q178 type 5 H-STEP
held is not supported: 0 held, 3 FAILED, 0 cannot tell of 3`; `Q178 type 5 H-FIX16 held is not
supported: 2 held, 1 FAILED, 0 cannot tell of 3`. The control (plain 16 x 16, E894's image)
passed.

**Results [HW].** From `score-tx.txt` and `fold/tx_read.py` (post hoc: values, distinct rows,
periods):

| row | image | frozen match |
|---|---|---|
| 16 x 16 (control) | 0 at x mod 16 < 8, 0x0000ffff above; 32 identical rows | E894's image |
| 16 x 16, first 112 dwords stored 0 | 0x00000000 in all 2048 pixels | differs (H-MEM) |
| 16 x 16, first 112 dwords stored 0xffffffff | 0x0000ffff in all 2048 pixels | differs (H-MEM) |
| 32 x 32, 64 x 64 | as the 16 x 16 control (period 16 in x, rows alike) | H-FIX16 |
| 8 x 8 | rows alike along x; 0 in even rows, 0x0000ffff in odd rows | none |

No pixel of any row holds a 0xD000xxxx tag; the values are 0x00000000 and 0x0000ffff only.

**What it shows.** [HW] TEXTYPE 5 reads the texture memory: what each pixel returns changes with
the dwords the program stored over the texture, every pixel of the 16 x 16 image following the
first 112 dwords. So the memory control of the stage failed in the sense that matters for it:
H-STEP's premise is refuted, the 0 / 0x0000ffff patterns are what type 5 makes of the map fill's
bits, not a step of its own, and the H-FIX16 match at 32 and 64 is a pattern of this fill, not a
rule independent of the texture. The image depends on the size: a 16-column step at 16 to 64 and a
2-row alternation at 8. [infer] Type 5 returns one of two values from the texels' bits (a compare
or a narrow format), not a 32-bit texel as types 1, 3, 4 and 7 do; E894's inference that it reads
no texel memory is withdrawn.

**What it does not show.** Which bits of which texel each pixel reads (the fill's dwords all share
0xD000 in their high half), whether the texture or the state words (format, filter) set the two
values, and what type 5 is for. The memory rows changed 112 dwords, not the whole texture.
