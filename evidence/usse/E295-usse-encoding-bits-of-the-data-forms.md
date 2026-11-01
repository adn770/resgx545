+++
id = "E295"
claim = "Of the 2,161 bits the 219 USSE forms leave neither identifying nor in a field, the 523 of 61 data forms (the moves, the bitwise group, integer multiply-add, the single and dot-product float forms, the colour and integer dot products, rlp, movc, movmsk, the masked tests, the video operations, idiv, eleven dual-issue pairs and both ldr forms) were flipped one at a time: each left the readback as the unflipped word did, except idiv's enc[47], which changed every destination r10 to r17"
unit = "usse"
method = "on the laptop, linux fork with the debug option on: probes/usse/encoding-bits.toml, encoding-bits-dual.toml, encoding-bits-load.toml and encoding-bits-followup.toml (written by tools/usse-asm/usse_bits.py), fills whose pixel program is dump.s with one base instruction as a raw .long (r1-r8 = 0x3fc01234, 0x40105678, 0x8001c003, 0x00ff7f80, 0x3f800001, 0xc0400002, 0x12345678, 0x7f7f0101; r10-r17 marked; a dual-issue secondary's i0-i2 loaded from r5-r7 and moved to r15-r17 after); case 0 is the base word, each other case the word with one unmapped bit flipped, a flip that decodes to another form left out (none did); readbacks compared with case 0's by usse_bits.py eval; one run, 523 flipped cases and 63 bases, and 38 rlp cases again with p0 set"
tiers = ["HW"]
date = "2026-11-02"
data = [
    "usse-encoding-bits", "usse-encoding-bits-dual", "usse-encoding-bits-load",
    "usse-encoding-bits-followup",
]
terms = []
+++

**What runs.** One probe per form, its base the instruction below; every unmapped bit of the
form (formdump's `bits_read`) flipped in its own case. The readback is the pixel (r10, or the
base's destination) and the sixteen stored registers, so a changed source, destination,
modifier or predicate shows. Bits (enc[n]) per form:

| base | unmapped bits | read |
|---|---|---|
| `mov r10, #0x12345678`; `mov r10, r1` | 35:34, 31:28; 54, 48, 39:34, 29:28, 20:14, 6:0 | none |
| `and`, `and.repeat2`, `shl`, `shr.repeat2` | 42:36, 20:14 each | none |
| `imae`, `ima16` (four operand formats), `ima32` | 52; 52; 47, 37; 52, 47; 47; 37:35 | none |
| `fsubflr`, `fdsx` (f32 and f16 sources) | 39, 34, 20:14 | none |
| `frcp`, `frcp.repeat2` | 54, 29:28, 20:14, 6:0 | none |
| `fdp`; `fdpc`; `fddpc` (f32 and f16) | 39, 34, 20:15; 39, 34, 20:18; 53, 47:46 | none |
| `sop2wm` | 34, 20:14 | none |
| `u8dot4`, `u8dot3`, `u16dot3`, `u8dot3+aadd` | 42:41, 37:34, 20:18, 15:14; 37:34, 20:18, 15:14; 37:34, 20:14; 20:18, 14 | none |
| `rlp`, `rlp.repeat2` (p0 set first) | 48, 43:35, 29:28, 6:0 | none |
| `movc` (three forms) | 38:35 | none |
| `movmsk` (five forms) | 36:34, 20:14; 36:35 (`.smsk`) | none |
| the masked tests (`xor`, `fadd`, `frcp`, `iadd8.sat`) | 38, 35:34; `frcp` also 48, 29:28, 6:0 | none |
| `adif`; `adifsum` | 56, 47, 43:39, 37:34, 20:14; 56, 43:39, 37:35 | none |
| `bilin`; `firv`; `firh` | 39:35; 43, 38:34; 34 | none |
| `idiv r10, r1, r2, drc0`, then `wdf drc0` | 51, 47, 43:40, 38:33, 20:14 | 47 |
| eleven dual-issue pairs (`fmad`, `mov`, `fddp`, `fssq` with `frcp`, `mov`, `fadd`, `fmad`) | 53, 48, 42, 35:34, 29:28, 20:14, 6:0 as each form has them | none |
| `ldr r10, #0, drc0`; `ldr r10, r1, drc0` | 50:49, 47:44, 42:40, 38:34, 31:30, 13:7; the same and 20:14 | none |

Every job completed. The bases gave what the simulator gives for them (their vectors match).

**idiv's enc[47].** The base writes the quotient of r1 by r2 to r10 (0) and the remainder to r11
(0x3fc01234). With enc[47] set the eight dwords r10 to r17 read 0, 0, 0x80, 0, 0, 0xa, 0,
0x8923: every destination from r10 on is written. 0x80 is r3 divided by r4 (0x8001c003 /
0x00ff7f80); the others fit no plain quotient or remainder of the inputs. What the bit selects
is open (Q079); the simulator stops on it.

**rlp.** The first run's rlp bases read p0 before anything set it: the pixel was mixed
(0x7f802468 on most pixels, 0x7f802469 on the rest), and the counts varied from case to case.
For `rlp` every case differed from case 0 (56 pixels of 0x7f802469) by those counts alone (19
of 19); for `rlp.repeat2`, whose case 0 had 1 such pixel, 4 of 19 differed (2 pixels each) and
the other 15 matched it. Run again with p0 set first, all 38 flipped cases matched their base.

**Not shown.** The other 1,638 unmapped bits: forms with no base here (the register forms of
the MOE group, wop, the lock form, phas, the emits, ldr's and str's second forms, ba, br,
bexception, lapc, the pclink moves, the remaining dual-issue pairs and the forms another form's
word shadows), and E296's state forms. One run.
