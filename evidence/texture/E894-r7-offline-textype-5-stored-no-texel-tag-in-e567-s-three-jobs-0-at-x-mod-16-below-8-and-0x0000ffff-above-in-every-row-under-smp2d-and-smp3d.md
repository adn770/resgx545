+++
id = "E894"
claim = "Round 7 offline reading of E567's kept TEXTYPE 5 dumps (rt5-2d, rt5-3d-w5, rt5-3d-w15; a 16 x 16 texture whose dword i is 0xD0000000 | i, a 64 x 32 fill) [HW, post hoc]: no pixel of the 3 x 2048 holds a texel tag (0xD000xxxx); every row of every job stores 0x00000000 at x mod 16 = 0 to 7 and 0x0000ffff at 8 to 15 (32 identical rows a job, 1024 pixels of each value), the same under smp2d and smp3d at w 0.5 and 1.5, where TEXTYPE 4's rt4-2d of the same group returns tags (16 distinct rows); so TEXTYPE 5 at 16 x 16 did not return a dword of the texture, and its two values follow the column alone"
unit = "texture"
method = "Offline, no run (round 7, decision R7-1 a; ranking closing7/rank/rank-round7.md finding 5). The ranking's closing7/rank/q178_type5.py read the tool outputs (row dumps) of rt5-2d, rt5-3d-w5, rt5-3d-w15 and rt4-2d kept in resgx545-data texture/p1132/tx-types-risky (E567) and counted the rows, the distinct rows, the values and the value set at each x mod 16. Post hoc: read after E567 had recorded only the pixel hash and \"2 distinct values\", with no prediction frozen. Standard library only; re-run in this fold from its published copy (cited/closing7/rank/q178_type5.py) with the repository's .venv: output byte-identical to the kept q178_type5.out"
tiers = ["HW", "infer"]
date = "2026-11-12"
data = ["texture-p1132-tx-types-risky", "cited-scratch:closing7/rank/"]
terms = ["TEXTYPE"]
+++
**What was done.** E567 ran TEXTYPE 5 once, at 16 x 16, in three jobs of the types-risky group
(smp2d, and smp3d with w 0.5 and 1.5), and recorded one pixel hash (354d06c9...) and "2 distinct
values". The texture was E567's map texture: dword i holds 0xD0000000 | i, so a pixel that reads
a texel names its offset. The ranking read the kept row dumps (`closing7/rank/q178_type5.py`,
output `q178_type5.out`); this fold re-ran it from the published copy, byte-identical.

**Results [HW, read post hoc].** In each of the three jobs the 32 rows of the 64 x 32 fill are
identical, 1024 pixels hold 0x00000000 and 1024 hold 0x0000ffff: x mod 16 = 0 to 7 stores
0x00000000 and 8 to 15 stores 0x0000ffff in every row. No pixel holds a 0xD000xxxx tag. In the
same group TEXTYPE 4 (rt4-2d) returns tags (16 distinct rows, 0xd0000000 and up), as types 1, 3
and 7 do (E567, E725).

**What it shows.** [HW] At 16 x 16 TEXTYPE 5 did not return a dword of the texture for any of the
2048 pixels of a job, and what it returned depends on the column (x mod 16) and not on the row
or on the third coordinate. [infer] Type 5 is not a layout of the 32-bit texels as types 1, 3, 4
and 7 are: a value of 0 or 0xffff that follows the u coordinate alone reads as a compare or a
format of its own, so a map texture at other sizes would read no offset either.

**What it does not show.** Other sizes (8 x 8 to 64 x 64), whether the values depend on the
texture memory at all (a zeroed or all-ones texture was not run), how u maps to the column in
E567's program, and what type 5 is for. Nothing here was predicted before it was read.

**Correction 2026-11-12:** (the claim stands: it reports E567's 16 x 16 dumps.) The [infer] of
"What it shows", that type 5 is not a layout of the 32-bit texels and that a map texture at other
sizes would read no offset either, is refuted for the part that mattered: R7-geo's stage tx (E911)
ran type 5 with the program storing 0 and then 0xffffffff over the texture's first 112 dwords, and
the 16 x 16 image became 0x00000000 and 0x0000ffff in every pixel, so type 5 reads the texture
memory; at 8 x 8 its image alternates by row and at 32 and 64 it repeats E567's 16-column step.
The two values are what type 5 makes of the map fill's bits, not a step independent of the
texture. "Whether the values depend on the texture memory" in "What it does not show" is answered
by E911.
