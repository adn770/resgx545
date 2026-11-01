+++
id = "E093"
claim = "The three numbered modifiers act uniformly over all their values in 71 cases: .repeatN runs N times (1 to 16), mov and xor stepping every operand one register per iteration and touching no register past the Nth; ldad .fetchN loads N consecutive dwords into N registers (1 to 16), starting one element after the address with any fetch flag, by register offset too, and stepping the destination one register before any smlsi; imae .rsN shifts the sum right by N (0 to 7), arithmetically when signed; a fetch that would run past the task's temporaries (r29 or r30 with fetch4 over 32 temporaries) writes nothing"
unit = "usse"
method = "on the laptop, linux fork with the debug option on: probes/usse/numbered-modifiers.toml, probes family-repeat, family-fetch, family-fetch-dst, family-fetch-edge and family-rs, fills whose pixel program (wide_dump.s: sources r1-r16 preset to n * 0x01010101, destinations r20-r39 to markers) runs the instruction and stores the registers to scratch; two runs (the second is the follow-up run)"
tiers = ["HW"]
date = "2026-11-01"
data = ["usse-numbered-modifiers", "usse-numbered-modifiers-followup"]
terms = []
+++

**What runs.** 71 cases, each one value of a family: 32 repeat cases (`mov.repeatN r20, r1`
and `xor.repeatN r20, r1, r2`, N = 1 to 16), 16 `ldad.fetchN r20, [r46,+#0]` (N = 1 to 16),
4 fetch-destination cases, 3 edge cases and 16 `imae` cases on 0xff9c * 0x7b + 0x1234. After
the instruction every destination register and the first twelve sources are stored, so the
readback names the registers that changed. The fetches read scratch dword 64 on, which holds
the host's fill 0xd0000000 | index.

**Results.** Every case gave one value over all 2048 pixels.

- repeat: for all 32 cases the registers r20 to r(19 + N) hold the Nth iteration's result and
  every other destination keeps its marker. `mov.repeatN` writes r(20 + k) = r(1 + k);
  `xor.repeatN` writes r(20 + k) = r(1 + k) xor r(2 + k) (for N = 16 the last iteration reads
  the unset r17 as 0). Each operand steps one register per iteration.
- fetch: `ldad.fetchN` loads exactly N registers for every N from 1 to 16. Without a fetch
  flag it reads dword 64; with one it reads dwords 65 to 64 + N, one element after the
  address. The same by register offset (into r20 and into r30), where an offset of 0x00040001
  starts at dword 66. The destination steps by one register, before any smlsi.
- edge: with a destination of r28 and `fetch4`, r28 to r31 take dwords 65 to 68; with `fetch4`
  at r29 and at r30, which would run past r31, all of r28 to r31 keep their markers.
- rs: `imae.u.rsN` on 0xff9c * 0x7b + 0x1234 gives 0x7ae228 shifted right by N (0x3d7114,
  0x1eb88a, 0xf5c45, 0x7ae22, 0x3d711, 0x1eb88, 0xf5c4 for 1 to 7); `imae.s.rsN` gives
  0xffffe228 shifted arithmetically (0xfffff114, 0xfffff88a, 0xfffffc45, 0xfffffe22,
  0xffffff11, 0xffffff88, 0xffffffc4).

**Not shown.** The fetch edge case was only run for 32 temporaries, and the data do not say
whether a fetch that runs past the end faults or is dropped silently beyond "writes nothing".
Two runs, the second the follow-up run, agree.
