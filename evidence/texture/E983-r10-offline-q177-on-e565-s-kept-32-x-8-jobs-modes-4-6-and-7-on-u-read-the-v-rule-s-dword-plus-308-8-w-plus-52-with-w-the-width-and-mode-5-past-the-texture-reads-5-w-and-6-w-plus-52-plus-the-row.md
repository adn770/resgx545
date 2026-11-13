+++
id = "E983"
claim = "Round 10 offline (Q177; no run): on E565's kept 32 x 8 twiddled jobs bd-hb-ns-uv4, uv6 and uv7 (u and v in mode 4, 6, 7), never read for the offset, every pixel reads the dword the v rule names plus 308 (2048 of 2048 each), which is 8 W + 52 with W = 32 the width, where the height's 8 H + 52 (116), the square's 8 sqrt(W H) + 52 (180) and 4 (W + H) + 52 (212) miss every pixel [HW, SEMI: the jobs ran before E957 fitted 8 N + 52 on square textures, and the rivals, named by E957's open part, were not frozen by hash before this reading]; post hoc, in bd-hb-ns-uv5 (mode 5) the 128 pixels inside the texture read +308 too, left of the texture the rows inside it read 5 W + 52 + t and right of it 6 W + 52 + t (t the texel row, 212 to 219 and 244 to 251), and with v outside too the reads are dwords 20 (above, left), 21 (above, right), 22 (below, left) and 23 (below, right) at every column of that side [fitted, one size]"
unit = "texture"
method = "Offline, no run (round 10, decision R10-1 a of the seeds plan closing10/seeds/exp-seeds-r10.md, finding 2 and section 2). Data: E565's kept jobs bd-hb-ns-uv4 to uv7 (texture-p1132-tx-border: a 32 x 8 twiddled texture of 32-bit texels at the probe's named memory, dword i reads 0xD0000000 | i, u = -1.5 + (x + 1/2) / 16 over 64 columns, v = -1.5 + (y + 1/2) / 8 over 32 rows, both axes in the job's mode). The planner's scripts in closing10/seeds/q177/ (standard library): ns_read.py reads every pixel's dword less the texture's twiddled index of the v rule's texel (each axis wrapped by the v rule of E565 and E932: modes 4 and 5 repeat, 6 and 7 clamp) under two equivalent 32 x 8 layouts (8 x 8 Morton blocks along s, and E561's), output ns_read.out; u5_rows.py and u5_past.py list mode 5's reads per texel row left and right of the texture (u5_rows.out, u5_past.out); rivals.py prints each rival's offset at the sizes a held-out stage would run (rivals.out). This fold re-ran the four scripts with python -I -B and got byte-identical outputs. The 16 x 16 reads of E932 (140 and 156 relative to the texture outside it in mode 5) agree with the mode 5 form at t = 8, the planner's reading, not re-derived here"
tiers = ["HW", "infer"]
date = "2026-11-13"
data = ["texture-p1132-tx-border", "cited-scratch:closing10/seeds/q177/"]
terms = ["T0.ADDRMODE_U", "T0.ADDRMODE_V"]
+++
**What was done.** E957 measured the u-axis offset of T0 address modes 4 to 7 on square twiddled
textures only, +116, +180 and +308 dwords at 8 x 8, 16 x 16 and 32 x 32, and fitted 8 N + 52; it
left open whether N is the width, the height or the size. E565 had run a 32 x 8 texture with both
axes in modes 4 to 7 (bd-hb-ns-uv4 to uv7), whose dumps were kept but never read against an
offset. The round 10 seeds planner read them; this fold re-ran the scripts.

**Results [HW].** Every pixel of bd-hb-ns-uv4, uv6 and uv7 reads the v rule's texel index plus 308
dwords, 2048 of 2048 each (ns_read.out), inside the texture and past it on both axes. At 32 x 8 the
rivals part: the width's 8 W + 52 is 308, the height's 8 H + 52 is 116, the square's 8 sqrt(W H)
+ 52 is 180 and 4 (W + H) + 52 is 212; only the width's holds, on every pixel. These rows ran on
2026-11-09, before E957's fit, and E957's open part named the rivals, but nothing was frozen by hash
before this reading, so the verdict is SEMI.

**Mode 5, post hoc [fitted].** In bd-hb-ns-uv5 the 128 pixels inside the texture read +308 as in
the other modes. Left of the texture (s < 0) the texel rows inside it read 212 + t and right of it
(s >= 32) 244 + t, t = 0 to 7 the row (u5_rows.out): 5 W + 52 + t and 6 W + 52 + t, one dword a
row, the same across all of a side's columns. Above and below the texture (v outside too) the reads
are a constant per corner: dword 20 above left, 21 above right, 22 below left and 23 below right,
at every column of that side (u5_rows.out). The planner reads E932's 16 x 16 outside reads, 140 and
156, as the same
form at t = 8 (5 * 16 + 60, 6 * 16 + 60).

**What it shows.** [HW, SEMI] The offset that modes 4, 6 and 7 add on the u axis of a twiddled
32-bit texture follows the width, not the height or the size: 8 W + 52 dwords at W = 8, 16, 32
(E957)
and at 32 x 8 (here). [infer] Mode 5 past the texture reads a dword set by the side and the row,
not by u.

**What it does not show.** A held-out non-square size (8 x 32, 16 x 64, 64 x 16; the seeds plan's
stage addr3 freezes the rivals for them), widths other than 8 to 32, formats other than 32-bit
texels and texture types other than twiddled. Mode 5's form rests on one size and its two sides;
E932's values at 16 x 16 agree with it only through the planner's reading of one row. sgx-sim keeps
refusing modes 4 to 7 on u, naming E957 and this record.

**Correction 2026-11-13:** E1000 (r10-tex stage addr3) ran held-out shapes: 8 x 32 read + 308 and
16 x 64 + 564, the height's 8 H + 52, while 64 x 16 read the width's + 564 and E565's 32 x 8 form
replicated + 308. The claim's "8 W + 52 with W the width" holds only where the width is the longer
side; post hoc every read of E1000's eleven jobs is 8 max(W, H) + 52, and mode 5's reads past the
texture use max(W, H) for W. The measurements of E565's jobs are unchanged.
