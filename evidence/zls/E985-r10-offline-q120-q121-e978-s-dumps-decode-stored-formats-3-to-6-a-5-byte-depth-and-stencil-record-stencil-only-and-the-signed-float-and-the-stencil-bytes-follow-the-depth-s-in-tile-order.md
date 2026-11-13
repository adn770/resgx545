+++
id = "E985"
claim = "Round 10 offline (Q120, Q121; no run): E978's kept dumps (a loaded index stencil, one x depth ramp, 64 x 32 and 96 x 48) decode for stored depth formats 3, 4, 5 and 6, every changed dword at both sizes [HW, SEMI: the rules were fitted on 64 x 32 and hashed before 96 x 48 was scored, after a coverage look at 96 x 48's format 3]: the tiles sit in blocks of 640 (formats 3, 5), 256 (4) and 512 (6) dwords, tile (tx, ty) in block 2 tw (ty >> 1) + 2 tx + (ty & 1) with tw the tiles across (equal to G + 1 in both dumps); formats 3 and 5 stored the same bytes, a 5-byte record a pixel (format 0's float with the sign bit set, little endian, then the pixel's stencil byte) in 16 chunks of 160 bytes, one a row, at fitted addresses (record P byte q at 1 + 17 g + 5 (2 - P mod 3) + q, g = P div 3, less 32 from 16 (g + 1) up); format 4 stores only stencil, in 8 groups of 80 bytes (two rows), each quad of a row a record of 0xf0 then its four stencil bytes from x + 3 down, at the same addresses; format 6 is one dword a pixel, x fastest, the float with the sign bit set (its row order untested: the depth varies in x only); format 7 is not decoded; the stencil byte paired with each pixel is byte j of the tile's loaded 128 dwords with j the depth's in-tile index (y0 x0 y1 x1 y2 x2 y3 x3 x4 from the lowest bit), 13 of 13 tiles, where the raster order and E466's format 2 order match none, but only lane-0 pixels (x and y even) and lane 1 at tile slots 2 and up carry a nonzero byte under the index fill"
unit = "zls"
method = "Offline, no run (round 10, decision R10-1 a of the seeds plan closing10/seeds/exp-seeds-r10.md, finding 5 and section 5). Data: r9-x stage zst's kept dumps (render-closing-r9-x out/20261113-081821/zst/: z120-ctl and z120-f3 to f7 at 64 x 32 ('s', G = 1) and 96 x 48 ('m', G = 2), each with the depth buffer filled 0xdeadbeef, the stencil loaded with dword i = i (bits 1 and 13) and stored (bit 17), the format-0 control's depth dump giving each pixel's float). The planner's scripts in closing10/seeds/q120/ (numpy, the repository's .venv): look.py (the changed dwords and their runs per format, look_s.out at 64 x 32), model3.py and ld.py (the fit's helpers), frozen_rules.md (the tile blocks, the format 3/5, 4 and 6 rules and the three stencil-order rivals H-DEPTHORD, H-RASTER and H-F2ORD, written from the 64 x 32 fit; sha256 86f0701a... in frozen_rules.sha256, file time 09:48:12), q120_score.py (predicts every byte from the control's depth and the index stencil, scores 64 x 32, checks the hash and only then scores 96 x 48; the rivals are tested on the stencil byte of 16 pixels per row whose record lies at a rival-neutral address, per tile with the slot free; output q120_score.out, 09:48:59) and stencil_store.py (the load and store stencil dumps per format, stencil_store.out). The planner's account: a coverage look at 96 x 48's format 3 came before the freeze. This fold re-ran q120_score.py and stencil_store.py with python -I -B and got byte-identical outputs"
tiers = ["HW", "infer"]
date = "2026-11-13"
data = ["render-closing-r9-x:out/20261113-081821/zst/", "cited-scratch:closing10/seeds/q120/"]
terms = ["CR_ISP_ZLSCTL", "CR_ISP_STENCIL_LOAD_BASE"]
+++
**What was done.** E978 stored formats 3 to 7 (CR_ISP_ZLSCTL bits 26:24) with an index stencil
loaded and stored, at 64 x 32 and 96 x 48, kept every dump and decoded none. The round 10 seeds
planner fitted the layouts on 64 x 32, wrote them and the stencil-order rivals down and froze the
file by hash, and then scored 96 x 48. This fold re-ran the scoring (byte-identical outputs).

**Results [HW, SEMI]** (q120_score.out; every changed dword of the depth buffer, every predicted
byte, and no predicted byte left at the fill):

| format | 64 x 32 (fit) | 96 x 48 (after the freeze) |
|---|---|---|
| 3 | 2560 of 2560 dwords | 5760 of 5760 |
| 5 | 2560 of 2560 | 5760 of 5760 |
| 6 | 2048 of 2048 | 4608 of 4608 |
| 4 | 640 of 640 | 1440 of 1440 |

- **Tiles.** A packed format puts tile (tx, ty) in block 2 tw (ty >> 1) + 2 tx + (ty & 1): two tile
  rows form a macro row, x outer. Blocks are 640 dwords (3, 5), 256 (4) and 512 (6). tw is the
  tiles across, which equals G + 1 in both dumps, so the two are not told apart. The block rule was
  fitted together with the stencil's slot, not on its own.
- **Formats 3 and 5** stored the same bytes. A tile is 16 chunks of 160 bytes, chunk r holding row
  r; pixel x's record is 5 bytes, format 0's float with bit 31 set (little endian), then the
  pixel's stencil byte. Record P's byte q lies at 1 + 17 g + 5 (2 - P mod 3) + q in the chunk, g = P
  div 3, less 32 when that is 16 (g + 1) or more. The address rule is fitted; no mechanism is known
  [infer].
- **Format 4** stores no depth. 160 of each block's 256 dwords hold 8 groups of 80 bytes, group n
  rows 2n and 2n + 1; record m = 8 (y & 1) + x div 4 is 0xf0 then the stencil bytes of x = 4 (m
  mod 8) + 3, + 2, + 1, + 0, at the same addresses with P = m. The 0xf0 was the same everywhere in
  these dumps (one depth ramp); what sets it is not known.
- **Format 6** is one dword a pixel, x fastest in rows of 32: the float with bit 31 set, and no
  stencil. The depth varies only in x, so the row order is assumed.
- **Format 7** does not decode. At 64 x 32 it changes 784 dwords in three runs, and the run from
  dword 256 starts with format 4's words (look_s.out) [infer: a form that depends on the stencil
  data].
- No format 3 to 7 wrote the stencil store (stencil_store.out, as E978).

**The stencil order (Q121).** The stencil byte that formats 3, 5 and 4 pair with pixel (x, y) of a
tile is byte j of the tile's 128 loaded dwords (dword j >> 2, lane j & 3) with j the depth's
in-tile index, y0 x0 y1 x1 y2 x2 y3 x3 x4 from the lowest bit (H-DEPTHORD): 13 of 13 tiles of both
sizes, every row with a nonzero byte (8 or 16 a tile). The raster order (j = 32 y + x) and E466's
format 2 order (y0 y1 x0 y2 x1 y3 x2 x3 x4) match no row of any tile. So the lane of pixel (x, y)
is y0 | x0 << 1. The index fill makes dword i read i, so only lane 0 (bits 7:0, x and y even) and
lane 1 (bits 15:8) at tile slots 2 and up hold nonzero bytes: the order is tested on those pixels,
and the zero bytes of the other lanes agree with any order.

**What it shows.** [HW, SEMI] Formats 3 and 5 store a 40-bit record a pixel, the negated float
depth then the stencil byte; 4 stores the stencil alone with a marker byte a quad; 6 stores the
negated float alone; all in the same macro-row block order. The stencil buffer's bytes follow the
depth's in-tile order on the pixels the index fill tells apart. [infer] The sign bit set on the
stored float is format 0's bit 19 negation applied by these formats, or a flag of their own.

**What it does not show.** Held-out rows: other sizes, depth ramps in y and over the whole 0 to 1
range, other stencil fills (the seeds plan's stage zst2), edge tiles; what parts 3 from 5, what
the 0xf0 encodes and format 7's layout; lanes 1 to 3 of the stencil order on a fill that varies
them, and the stencil test (the seeds plan's stage st1). sgx-pipe keeps refusing formats 3 to 7 and
the stencil's in-tile order, naming this record.
