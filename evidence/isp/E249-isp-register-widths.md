+++
id = "E249"
claim = "Of the ISP registers, CR_ISP_RENDER takes bits 5:3 and 1:0, CR_ISP_CTL bits 24, 19:16, 8 and 5:0, CR_ISP_MSAA bits 31 and 1:0, the render origin and end registers 0x040c and 0x0410 bits 24:16 and 9:0, CR_ISP_BGOBJVALS bits 9:0, 0x04c4 bits 30:0 and the polygon-offset units bits 23:0; the visibility control and counters take no write, and 0x0444 and 0x0448 read the same values whatever is written"
unit = "isp"
method = "probes/platform/register-widths.toml on the laptop, linux fork with the debug option on: regwidth.c through /dev/mem writes each register with all ones, its prior value, zero and its prior value, reading after each write, with the firmware live and idle, in ten batches with a debugfs fill and the triangle checked after each; two runs"
tiers = ["HW", "infer"]
date = "2026-11-02"
data = ["platform-register-widths"]
terms = [
    "CR_ISP_RENDER", "CR_ISP_REGION_HEADER_BASE", "CR_ISP_CTL", "CR_ISP_LINE_SAMPLE_POS",
    "CR_ISP_POLY_OFFSET_UNITS", "CR_ISP_POLY_OFFSET_FACTOR", "CR_ISP_POLY_OFFSET_CLAMP",
    "CR_ISP_MSAA", "CR_ISP_VISIBILITY_CTRL", "CR_ISP_VISIBILITY_COUNT0", "CR_ISP_BGOBJDEPTH",
    "CR_ISP_BGOBJVALS", "CR_ISP_MULTISAMPLECTL", "CR_ISP_REG_04DC", "CR_ISP_REG_04E8",
    "CR_ISP_PARTIAL_REGION_BASE", "CR_ISP_SAMPLE_POS",
]
+++

**What runs.** The register census of E246, batches 1, 5 and 6.

| register | name | value before | bits that took a write | width | read 1 after zero |
|---|---|---|---|---|---|
| `0x0404` | `CR_ISP_RENDER` | `0x00000000` | 5:3, 1:0 | 5 | - |
| `0x0408` | `CR_ISP_REGION_HEADER_BASE` | `0x20004000` | 31:2 | 30 | - |
| `0x040c` | - | `0x00000000` | 24:16, 9:0 | 19 | - |
| `0x0410` | - | `0x00000000` | 24:16, 9:0 | 19 | - |
| `0x0414` | `CR_ISP_CTL` | `0x000f0100` | 24, 19:16, 8, 5:0 | 12 | - |
| `0x0418` | `CR_ISP_LINE_SAMPLE_POS` | `0x00000001` | 0 | 1 | - |
| `0x041c` | `CR_ISP_POLY_OFFSET_UNITS` | `0x00000000` | 23:0 | 24 | - |
| `0x0420` | `CR_ISP_POLY_OFFSET_FACTOR` | `0x00000000` | 31:0 | 32 | - |
| `0x0424` | `CR_ISP_POLY_OFFSET_CLAMP` | `0x00000000` | 31:0 | 32 | - |
| `0x042c` | `CR_ISP_MSAA` | `0x80000000` | 31, 1:0 | 3 | - |
| `0x0444` | - | `0x00002300` | 0x00000000 | 0 | 13, 9:8 |
| `0x0448` | - | `0x2000409c` | 0x00000000 | 0 | 29, 14, 7, 4:2 |
| `0x044c` | - | `0x00000000` | 0x00000000 | 0 | - |
| `0x0494` | `CR_ISP_VISIBILITY_CTRL` | `0x00000000` | 0x00000000 | 0 | - |
| `0x0498` | `CR_ISP_VISIBILITY_COUNT0` | `0x00000000` | 0x00000000 | 0 | - |
| `0x049c` | `CR_ISP_VISIBILITY_COUNT1` | `0x00000000` | 0x00000000 | 0 | - |
| `0x04a0` | `CR_ISP_VISIBILITY_COUNT2` | `0x00000000` | 0x00000000 | 0 | - |
| `0x04a4` | `CR_ISP_VISIBILITY_COUNT3` | `0x00000000` | 0x00000000 | 0 | - |
| `0x04a8` | `CR_ISP_VISIBILITY_COUNT4` | `0x00000000` | 0x00000000 | 0 | - |
| `0x04ac` | `CR_ISP_VISIBILITY_COUNT5` | `0x00000000` | 0x00000000 | 0 | - |
| `0x04b0` | `CR_ISP_VISIBILITY_COUNT6` | `0x00000000` | 0x00000000 | 0 | - |
| `0x04b4` | `CR_ISP_VISIBILITY_COUNT7` | `0x00000000` | 0x00000000 | 0 | - |
| `0x04b8` | `CR_ISP_BGOBJDEPTH` | `0x3f800000` | 31:0 | 32 | - |
| `0x04bc` | `CR_ISP_BGOBJVALS` | `0x00000300` | 9:0 | 10 | - |
| `0x04c4` | - | `0x00046400` | 30:0 | 31 | - |
| `0x04c8` | `CR_ISP_MULTISAMPLECTL` | `0x00000088` | 31:0 | 32 | - |
| `0x04dc` | `CR_ISP_REG_04DC` | `0x00000000` | 2:0 | 3 | - |
| `0x04e8` | `CR_ISP_REG_04E8` | `0x00000100` | 8, 0 | 2 | - |
| `0x050c` | `CR_ISP_PARTIAL_REGION_BASE` | `0x20005000` | 31:2 | 30 | - |
| `0x0520` | `CR_ISP_SAMPLE_POS` | `0x00000000` | 31:0 | 32 | - |

**Reading.** `CR_ISP_MSAA` takes exactly the bits its two fields name (the mode in 1:0, bit 31), so
it has no unexplained bit. `CR_ISP_CTL` takes 12 bits; the partial render's bit 8 is one of them.
The transfer path's render origin and end (0x040c, 0x0410) hold y (16-pixel tile rows) in 9:0, 10
bits, and x (32-pixel tile columns) in 24:16, 9 bits (E019, E020): each reaches 16384 pixels.
0x04c4, the background tag the 3D and transfer paths load, takes 31 bits. `CR_ISP_BGOBJVALS` takes
9:0, the stencil value and the two flags above it.

0x0444 and 0x0448 read 0x00002300 and 0x2000409c after every write, 0x044c reads 0: the host cannot
write these three. The visibility control word and the eight counters read 0 after every write. We
read the firmware's 0xff to the control word before a render (its glossary row) as a command rather
than a value it keeps [infer]; a bit that reads 0 after all ones may also be write-only or cleared
by the hardware (E246).

**Not shown.** What the fields of `CR_ISP_RENDER` and `CR_ISP_CTL` select beyond those named; where
0x0444 and 0x0448 take their values from.
