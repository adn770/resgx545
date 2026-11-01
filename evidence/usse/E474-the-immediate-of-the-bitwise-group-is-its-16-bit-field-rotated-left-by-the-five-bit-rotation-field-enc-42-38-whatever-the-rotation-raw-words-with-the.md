+++
id = "E474"
claim = "The immediate of the bitwise group is its 16-bit field rotated left by the five-bit rotation field enc[42:38], whatever the rotation: raw words with the field 0xffff, 0x8001 and 0x1234 under each of the 32 rotation values build rotl(field, r) in 96 of 96 cases (rotating right fits 6, ignoring the rotation 3, using its low four bits 48), the 18 values the assembler encodes (0x80000001, 0xffff0000, 0x7fff8000, 0xff0000ff, 0x12340000 ...) arrive unchanged (18 of 18), ~#X complements the whole 32-bit operand after the rotation (19 of 19 on and, or and xor), and shl, shr, asr and rol by a rotated immediate use the whole 32-bit value as the amount (36 of 36: shl and shr give 0 and asr the sign for 32 and over, rol takes it mod 32)"
unit = "usse"
method = "on the laptop (direct cable), linux fork 6ee9501832af, module srcversion 14D099861204842EA496D85, tool sgxfive-test-1122 (sha256 ec423efc3d9aa34576553da70916be4ceb715a729cbc02cc4bd89fa052511244): probes/usse/rot-imm.toml (dump.s), 6 probes and 169 cases: the first three are raw words (`.long`) of `or r10, r1, #imm` with r1 = 0 and enc[42:38] set to 0 to 31 (96 cases), then 18 `or r10, r1, #X`, 19 `and/or/xor r10, r1, ~#X` and 36 shifts of 0x80000003 by an immediate; two runs of each (probe.py outside the data, the campaign runner the dataset, the same readback in all 169 cases)"
tiers = ["HW", "infer"]
date = "2026-11-08"
data = ["usse-rot-imm"]
terms = ["Universal Scalable Shader Engine (USSE)"]
+++

**What runs.** The raw words have the 16-bit field in the immediate bits of source 2 and the
rotation in enc[42:38]; r10 shows the immediate the hardware builds (`or` with r1 = 0). The text
probe assembles `or r10, r1, #X` for X in 0, 1, 0xffff, 0x10000, 0x8000, 0x7fff8000, 0x80000000,
0x80000001, 0xffff0000, 0xff0000ff, 0xfffe0001, 0x0001fffe, 0x00ff0000, 0xf000000f, 0xc0003fff,
0x00018000, 0x12340000 and 0x00040000; the assembler picks the first rotation that fits (the labels
of the data carry field and rotation, e.g. 0x00010000 is field 0x8000 rotation 1, 0x80000001 is
field 0xc000 rotation 17, 0x12340000 is field 0x91a0 rotation 13). The invert probe runs `and r10,
r1, ~#X` with r1 = 0xffffffff and `or` and `xor` with other r1, X among the rotated values. The
shifts run `shl/shr/asr/rol r10, r1, #X` with r1 = 0x80000003 and X in 3, 0x20, 0x40, 0x100,
0x10000, 0x80000001, 0x80000000, 0xffff0000, 0x7f.

**Results (campaign run).** Every field and every rotation 0 to 31 gives the field rotated left
(96 of 96), so the redundant encodings (the same value from two rotations) agree too. `~#0xffff0000`
with r1 = 0xffffffff gives 0x0000ffff, `~#0x80000001` gives 0x7ffffffe, `~#0x7fff8000` gives
0x80007fff: the complement is of the whole rotated operand (19 of 19; the complement of the field
taken before the rotation fits 0). Shifts: `shl r10, r1, #0x100` is 0 and `asr` by it is 0xffffffff
(the amount is 256, not the low 5 or 7 bits: those fit 13 and 21 of 36), `shl` by `#0x80000001`
is 0 (not by 1), `rol` by `#0x80000001` is 0x00000007 (the amount mod 32 = 1) and `rol` by
`#0x100` or `#0x10000` is r1 itself.

**What it shows.** [HW] The encodable set is `{rotl(m, r) : m < 2^16, 0 <= r < 32}` for the
bitwise group, `~` of the same, and the shift amount is the whole 32-bit value, so a shift by a
rotated immediate of 32 or more behaves like one by a register of that value. [infer] The values
the assembler refuses (0x00010001, 0x55555555, 0x12345678, `#0xffffffff` without `~#0`) are the
values outside that set, 17 or more cyclic bits (tools/usse-asm at 8665d77); not a hardware run.

**What it does not show.** Other instructions' immediates (the `ima32` ones are seven bits,
E469; the test ones are seven bits, E473; `mov` has its own 32-bit immediate). Sources other than
source 2. Only `or`, `and`, `xor` and the four shifts were run.
