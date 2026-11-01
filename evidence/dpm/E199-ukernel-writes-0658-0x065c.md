+++
id = "E199"
claim = "The microkernel writes register 0x065c only with 1 and 0, four times, in the partial-render routine (0xc23-0xdbe) and its resume (0xdbf-0xe09), and register 0x0658 three times, 1 in the partial-render routine and 0 in the resume and in the 3D kick routine (0x112b-0x12db); it reads neither, and the writes of 1 are skipped under bits of one secondary attribute"
unit = "dpm"
method = "the cut ukernel image (firmware-images, 00_ukernel.bin) disassembled with usse-dis, and the forward dataflow of the whole image (firmware-edm-dataflow) for every access to registers 0x0658 and 0x065c, with the code around the sites read by hand; our disassembly of the firmware, for interoperability; facts only, no code"
tiers = ["RE"]
date = "2026-11-01"
data = ["firmware-edm-dataflow", "firmware-images"]
terms = ["CR_DPM_SPM_SWITCH", "CR_DPM_PARTIAL_RENDER"]
+++

**What was read.** The dataflow table lists every register access of the 6637 instructions by
register, kind, value and routine (E013). For registers 0x0658 and 0x065c it holds seven rows, all
writes, no read. I read the instructions at each site in the disassembly (the register index is the
dword index 406 for 0x0658 and 407 for 0x065c, times 4).

**Results.**

| register | value | instruction | routine |
|---|---|---|---|
| 0x065c | 1 | 0xc75 | 0xc23-0xdbe (partial render) |
| 0x065c | 0 | 0xc93 | 0xc23-0xdbe |
| 0x0658 | 1 | 0xcbe | 0xc23-0xdbe |
| 0x065c | 1 | 0xde3 | 0xdbf-0xe09 (resume) |
| 0x0658 | 0 | 0xde5 | 0xdbf-0xe09 |
| 0x065c | 0 | 0xdee | 0xdbf-0xe09 |
| 0x0658 | 0 | 0x124b | 0x112b-0x12db (3D kick) |

So 0x065c is written four times and 0x0658 three, with these values and no others. In the partial
render routine the write of 1 to 0x065c is skipped when bit 1 of secondary attribute 8 is set, and
the write of 1 to 0x0658 is skipped when bit 10 of the same attribute is set; the write of 0 to
0x065c follows later in the routine whichever way the first branch went. In the resume the write of
1 to 0x065c is skipped under the same bit 1, read from the resume's working copy of that attribute;
the write of 0 to 0x0658 follows it after a store to another register (0x0698), and the write of 0
to 0x065c comes after a wait loop on register 0x012c, near the end of the routine (0xe09). The 3D
kick routine clears 0x0658 once, close to its end.

**What it shows.** The registers are set and cleared by the firmware itself, around a partial
render, and no firmware path reads either one back. The host's own writes are not part of this
reading.

**Not shown.** The meaning of secondary attribute 8's bits 1 and 10, which the firmware sets and
tests in several routines. Accesses through a computed register index are not counted (E013 lists 14
register-supplied addresses it could not resolve), so a write through such an address is not
excluded. Whether the hardware reads either register is a question for the registers' own effect
(E204).
