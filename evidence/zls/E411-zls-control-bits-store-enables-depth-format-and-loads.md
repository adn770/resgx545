+++
id = "E411"
claim = "In a render with depth and stencil stored (CR_ISP_ZLSCTL 0x17100c), clearing bit 2 stores nothing, clearing bit 17 stops the stencil store, clearing bit 18 stops the depth store, setting bit 19 stores the depth as -1.0, bit 24 as 0x00ffffff and bit 25 as 0xffffffff on two pages, with the same stored pages in both of two runs for all 32 flips; with bit 1 set, bit 13 drops the stencil store and bit 14 stores the loaded depth, and neither does anything without bit 1, in two runs each"
unit = "zls"
method = "probes/zls/control-bits.toml (control-bits.sh) on the laptop (direct cable), linux fork f1fad0ed9d0e with the debug option on: A) the store setup of probes/zls/load-store.sh (kernel poke ta:7^=0x180, rd:1 = 0x3e000000, rd:11 = the control, rd:12 = 0x11000, rd:13 = 0xd000, stencil bases rd:14 = 0x80001000 and rd:15 = 0x80005000, a 16-page scratch buffer of 0.25f, the triangle at z 0.5 with depth test less) with each bit of 0x17100c flipped, twice (66 jobs with the controls); B) bits 1, 13 and 14 in every combination added to 0x17100c and to 0x11700a in a store arrangement and in a load arrangement (the load base on the scratch pages), twice (68 jobs)"
tiers = ["HW", "infer"]
date = "2026-11-07"
data = ["zls-control-bits"]
terms = ["CR_ISP_ZLSCTL", "CR_ISP_BGOBJVALS.STENCIL", "ISP2"]
+++

**Part A, the stores.** The control 0x17100c (bits 2, 3, 12, 16, 17, 18, 20 set) stores 5120 dwords:
page 4 (1024 dwords of 0, the stencil) and pages 12 to 15 (1024 dwords each of 1.0, the depth), and
the image is exact. Each flip, in both runs, left these stored pages:

| flip | image | stored pages |
|------|-------|--------------|
| bit 0 set | all 4096 pixels wrong (sentinel) | as the control |
| bits 1, 12 to 16, 20 to 23, 27 to 31 | exact | as the control |
| bit 2 cleared | exact | none (0 dwords) |
| bit 3 cleared | exact | page 4 640, 12 and 13 1024, 14 512 |
| bit 4 set | 480 (run 1) and 384 (run 2) wrong | pages 4 and 5 512, 12 and 14 1024 |
| bit 5 set | job faults, 3520 and 2976 wrong | page 4 512, 12 and 15 1024 |
| bit 6 set | job faults, 3872 and 3552 wrong | page 4 256, page 12 |
| bits 7 to 11 set | job faults, all pixels wrong | page 4 256, page 12 |
| bit 17 cleared | exact | pages 12 to 15 only (no stencil) |
| bit 18 cleared | exact | page 4 only (no depth) |
| bit 19 set | exact | as the control but the depth -1.0 (0xbf800000) |
| bit 24 set | exact | as the control but the depth 0x00ffffff |
| bit 25 set | exact | page 4, pages 12 and 13 hold 0xffffffff (14 and 15 not stored) |
| bit 26 set | exact | pages 12 and 13 only, 640 dwords each, first 0x0000f000 |

**Part B, bits 1, 13 and 14.** In the load arrangement (depth 0.25f loaded, the triangle at z 0.5,
depth test less) the load-only control 0x11700a leaves 936 pixels wrong (the triangle removed where
the loaded depth is nearer). With the store control 0x17100c alone or with bit 1, bit 13 or bit 14
added singly (0x17100e, 0x17300c, 0x17500c) and with bits 13 and 14 without bit 1 (0x17700c), no
pixel is wrong. With bit 1 and bit 13 (0x17300e) 512 pixels are wrong, with bit 1 and bit 14
(0x17500e) 1382, with all three (0x17700e) 1382, in both runs each. In the store arrangement the
same words store: 0x17100e, 0x17300c, 0x17500c and 0x17700c as 0x17100c; 0x17300e the depth pages
(1.0, 4 x 1024 dwords) and no stencil page; 0x17500e the stencil page and depth pages of 0x5eadbeef
(the target's sentinel 0xdeadbeef read as a depth: the loaded value); 0x17700e the depth pages of
0x5eadbeef and no stencil page.

**What it shows.** Bits 2, 17 and 18 of CR_ISP_ZLSCTL enable the stores (all, stencil, depth); bits
19, 24 and 25 change how the depth is stored (sign, 24-bit integer, a clamp), bits 3 and 4 change
which pages (the region) it stores; bits 5 to 11 set fault the job; bit 0 set leaves every pixel
unwritten. Bits 13 and 14 act only with bit 1 set: bit 13 drops the stencil store and bit 14 makes
the stored depth the loaded one, and each changes the render's pixels in the load arrangement
[infer: bit 1 turns the load on, bit 13 picks the stencil and bit 14 the depth].

**What it does not show.** The stencil load itself (no stencil value was loaded and read); the
effect of the bits on a partial render's reload (not run); two runs a flip, no third.

**Correction, 2026-11-08 (11.22).** The measurements above are unchanged. Their reading as a
"region" is superseded: bits 3 to 11 are the tile pitch G (E465), bit 24 the 24-bit and bit 25 the
16-bit stored depth format and bit 26 format 4, bit 19 the negated float (E466), and bits 13 and
14 with bit 1 load the stencil and the depth (E467). That bits 3 and 4 changed the stored pages
and bits 5 to 11 faulted the job is read as the pitch running out of the 16-page scratch buffer
[infer]: E465 recomputes the pages of the bit 3, bit 4 and bit 26 rows from its rule by hand and
they match; no run of 11.22 reproduced a fault, so the fault half is not shown.
