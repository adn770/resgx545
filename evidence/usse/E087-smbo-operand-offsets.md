+++
id = "E087"
claim = "smbo's first value offsets the destination register number of the instructions after it (+1 writes r11, +2 r12, and a repeat moves every write), its third value offsets source 1 and its fourth source 2 (a store's source register included), the second value changes nothing the probes read; the offsets stay in force for the rest of the task; moest writes no register and no scratch dword in any case that completes (smbo's own offsets move the dump in one); and smoa with non-zero offsets does not fault by itself, but three cases fault the job in both runs (smoa #-1, #-2, #511, #-512 followed by the sixteen moest selectors, and smoa mirror on all four operands in two smr cases) and two in the first run only (smoa #1-#4 or smbo #1-#4 followed by the moest selectors)"
unit = "usse"
method = "on the laptop, linux fork with the debug option on: probes/usse/moe.toml, probes smbo-operands, moest-state, moest-dest, moest-store, smr-smoa and window, fills whose pixel program runs the instruction after smbo, moest or smoa on preset registers (r1-r8 = 0x11 to 0x88, r10-r17 = 0xa0a1a2a3 + 0x04040404 n) and dumps the registers to scratch; two runs (the second is the follow-up run)"
tiers = ["HW"]
date = "2026-11-01"
data = ["usse-moe", "usse-moe-followup"]
terms = []
+++

**What runs.** `smbo #d, #a, #b, #c` then `mov r10, r1` (or `mov.repeat2`, or `or r10, r1, r3`),
a dump of r10-r17 and r1-r8, and a final `mov.end o0, r10`. Thirteen cases vary one or more values
of smbo.

**Results.** smbo-operands, with the changes in the dump:

- `smbo #1, #0, #0, #0` then `mov r10, r1`: r11 = 0x11 and r10 keeps its preset; `#2` puts it
  in r12; under `mov.repeat2` the writes go to r11 and r12. The pixel is mixed: 1656 pixels
  show 0x11 and 392 the preset in the first run (1744 and 304 in the follow-up run), so the offset
  does not reach every instance's final `mov.end` alike.
- `smbo #0, #0, #1, #0` then `mov r10, r1`: r10 = 0x22, the value of r2: the third value
  offsets source 1. The final `mov.end o0, r10` then reads r11 (all 2048 pixels read
  0xa4a5a6a7), so the offset outlives the instruction after `smbo`. `or r10, r1, r3` gives
  0x33 = r2 | r3.
- `smbo #0, #0, #0, #1` then `mov r10, r1`: r10 = 0x11, but the dump's stores read one
  register up (dword 0 holds r11's value, dword 8 r2's): the fourth value offsets source 2, the
  store's register, for the rest of the task; `or r10, r1, r3` gives 0x55 = r1 | r4. With all
  four values 1, `or` gives 0x66 = r2 | r4 (pixels mixed: 1636 show 0x33 and 412 show 0x66;
  in the follow-up run 1792 show 0x33 and 256 show 0xa4a5a6a7).
- `smbo #0, #1, #0, #0` and `#0, #2, #0, #0`: nothing changes in the dump or the pixel for
  `mov` and `or`, whose sources are 1 and 2; no operand the probes read follows the second value.

**moest.** Nine cases of moest-state run `moest.skipinv rN, #n` for n = 0 to 15 at task start and
after `smlsi`, `smbo #4095, #2048, #1024, #7` and `smr`; in the six that complete in the first run,
the 16 destinations keep their presets in all but the smbo case (where the offsets move the dump
itself). moest-dest (10 cases: `moest r1, #2`, `#3`, `#8`, with and without .skipinv, on an internal
register, and after `smlsi`) leaves r1 or i0 at 0x0bad0000 in every pixel. moest-store (11 cases, a
register holding the scratch address, selectors 0 and 6, after `smr` and `smlsi`) gives the same
32-dword dump in all 11, with no extra scratch dword.

**Faults.** Three cases fault the job and lose the context in both runs: `smoa #-1, #-2, #511,
#-512, mirror, clamp, repeat, none` followed by the moest sequence, and `smr` with `smoa
mirror` on all four operands before a repeated `mov` (smr 4 with repeat8, smr 2 with repeat4).
Two more fault in the first run only: `smoa #1, #2, #3, #4, none, repeat, clamp, mirror` and
`smbo #1, #2, #3, #4`, each followed by the moest sequence. In the follow-up run both complete
with mixed pixels (0xacadaeaf on 1340 and 0xa0a1a2a3 on 708 after smoa; 1130 and 918 after
smbo) (Q016). smoa with non-zero offsets and mode none or repeat on one operand, and the clamp
mode, do not fault in the other cases of the smoa tables.

**Not shown.** Which of the faulting parts is the cause (moest after a changed MOE state, or
the mirror mode, or the combination). Where moest's result goes is open; the data show none
of it in registers or scratch.
