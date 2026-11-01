+++
id = "E497"
claim = "The six-instruction signed 32-bit compare of E472 needs no gap after the ima32: with one, three and six nops between ima32.u r11, r2, c56, r1 and the instruction that reads r11, a < b signed over the 16 pairs (0, 1), (1, 0), (0, 0), (0xffffffff, 0), (0, 0xffffffff), (0x80000000, 1), (1, 0x80000000), (0x7fffffff, 0x80000000), (0x80000000, 0x7fffffff), (0xffff, 0x10000), (0x10000, 0xffff), (0xffffffff, 0xffffffff), (0x80000001, 0x80000000), (0x7fffffff, 0xffffffff), (0xffffffff, 0x7fffffff) and (5, 5) is right in 48 of 48 cases (16 each: the pixel r10, a - b in r11, the word a xor t in r13 and r15 all as computed), where E472 ran the signed compare unpadded (64 of 64) and the unsigned compare with three nops (16 of 16)"
unit = "usse"
method = "on the laptop (direct cable), linux fork 6ee9501832af, module srcversion 14D099861204842EA496D85, tool sgxfive-test-1124 (sha256 58907b06a8e9030472a809cd669d2c3823946fd67aaf4775f942704a90f6a5ae): probes/usse/compare32-pad.toml (dump.s, 3 probes slt-padded (3 nops), slt-padded1 and slt-padded6, 16 pairs each); the campaign runner once for the table, no probe.py first run; the three probes were recounted from the readbacks (48 of 48)"
tiers = ["HW"]
date = "2026-11-08"
data = ["usse-compare32-pad"]
terms = ["Universal Scalable Shader Engine (USSE)"]
+++

**What runs.** The program of usse-compare32-slt (`t = ima32.u r11, r2, c56, r1`, `xor r12, r1, r2`,
`xor r13, r1, r11`, `and r12, r12, r13`, `xor r12, r12, r11`, `shr.testtanz.chan0 !c0, p0, r12,
#31`, `iadd32.testnat.chan0 !c0, p1, #0, r12`, and r10 and r15 from p0 and p1) with 1, 3 or 6 `nop`
after the ima32, over the 16 pairs listed (a = r1, b = r2).

**Results.** r10 = a < b signed, r11 = a - b mod 2^32, r13 = a xor t and r15 = r10 in 48 of 48 (the
readback words recounted: r10, r11, r13 and r15 per case).

**What it shows.** [HW] The padding result of E472 for the unsigned compare holds for the signed
one, and for one and six nops as well as three, for these 16 pairs. The pairs are not the 64 of
E472's unpadded run; the 16 here are the corner pairs listed.

**What it does not show.** `.nosched` on the ima32 in the compare (E495 has it for a plain reader),
padding of the unsigned compare with one or six nops, or of the two-instruction compare of E501, and
pairs other than the 16. Completes the 'signed padded' item E472 listed; narrows no question.
