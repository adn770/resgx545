+++
id = "E284"
claim = "ISP word 2 is the stencil word: bits 27:25 compare the masked reference with the masked stencil (0 never, 1 less, 2 equal, 3 less or equal, 4 greater, 5 not equal, 6 greater or equal, 7 always), bits 15:8 mask both sides of the compare and bits 7:0 the bits written; bits 24:22, 21:19 and 18:16 are the operations on stencil fail, depth fail and pass, 0 keep, 1 zero, 2 replace with the reference, 3 increment clamped, 4 decrement clamped, 5 invert, 6 increment wrapping, 7 decrement wrapping; bits 31:28 change nothing; each probe ran once"
unit = "isp"
method = "probes/isp/stencil-word.toml on the laptop, linux fork with the debug option on: the 64x64 triangle with ISP word 2 in its state block, the background stencil set through CR_ISP_BGOBJVALS (render-details word 17 at 0x300 plus the value, a kernel poke); the compare and its mask on one object (reference 0x54, 0x55, 0x56 against 0x55); the operations and the write mask through two objects, the first (copy 0, green, depth less) applying its ISP word 2 and the second (copy 1, blue, depth always, stencil equal to a value, no writes) drawing where the stencil holds that value; every pixel read back; one run"
tiers = ["HW"]
date = "2026-11-02"
data = ["isp-stencil-word"]
terms = ["ISP2", "ISP2.SCMP_MODE", "ISP2.SCMP_MASK", "ISP2.SW_MASK", "ISP2.SOP1", "ISP2.SOP2", "ISP2.SOP3", "ISP0.SREF", "ISP0.ISP2_PRESENT", "CR_ISP_BGOBJVALS.STENCIL"]
+++

**What runs.** `isp-stencil-word-cmp`: one object with ISP word 0 0x01d00300 plus the reference
(bit 8 the word-2-present bit) against the background stencil 0x55, each compare 0 to 7 with the
reference at 0x54, 0x55 and 0x56 (no writes); the compare equal with the reference and compare
mask at (0x05, 0x0f), (0x05, 0xff), (0x50, 0xf0), (0x50, 0x0f); bits 28 to 31 flipped one at a
time on a passing compare. The other probes draw two objects from a background stencil s0: the
first with reference 0x55, compare always, each operation in one field; the second draws blue
where the stencil equals the probe's value r. The 36 pixels the second object covers outside the
first show s0.

**Results.** The compare probe (1062 = the triangle drawn, 0 = none):

| compare | 0x54 vs 0x55 | 0x55 vs 0x55 | 0x56 vs 0x55 |
|---|---|---|---|
| 0 | 0 | 0 | 0 |
| 1 | 1062 | 0 | 0 |
| 2 | 0 | 1062 | 0 |
| 3 | 1062 | 1062 | 0 |
| 4 | 0 | 0 | 1062 |
| 5 | 1062 | 0 | 1062 |
| 6 | 0 | 1062 | 1062 |
| 7 | 1062 | 1062 | 1062 |

Compare equal: reference 0x05 with mask 0x0f draws, with 0xff not; 0x50 with 0xf0 draws, with
0x0f not. Bits 28 to 31: all draw.

The depth-pass operation (bits 18:16) from s0 = 0x0f: the second object draws over the first's
1062 pixels for r = 0x0f with op 0, 0x00 with op 1, 0x55 with op 2, 0x10 with ops 3 and 6, 0x0e
with ops 4 and 7 and 0xf0 with op 5; for every other pair it draws none of them. From s0 = 0xff,
op 3 leaves 0xff and op 6 leaves 0x00; from s0 = 0, op 4 leaves 0 and op 7 leaves 0xff.

With the compare never (bits 27:25 at 0), replace in bits 24:22 writes 0x55 and replace in bits
21:19 or 18:16 writes nothing; with the first object's depth compare never and the stencil compare
always, only replace in bits 21:19 writes 0x55. Replace over s0 = 0xf0 with write mask 0x0f
leaves 0xf5, 0xf0 leaves 0x50, 0 leaves 0xf0 and 0xff leaves 0x55. Each value is read in one
probe only, each probe once.

**What it shows.** The stencil test passes when (reference & mask) compares with (stencil & mask) as
the field says, the reference on the left: 1 passes 0x54 against 0x55, 4 passes 0x56. Bits 24:22 act
when the stencil test fails, 21:19 when it passes and the depth test fails, 18:16 when both pass,
with the eight operations listed in the claim; increment and decrement clamp at 0xff and 0 in 3 and
4 and wrap in 6 and 7. The written bits are those of bits 7:0. These are the fields Mesa's csbgen
names ISP2.SCMP_MODE, SCMP_MASK, SOP1, SOP2, SOP3 and SW_MASK (C0720 to C0725); this answers the
first half of Q071.
